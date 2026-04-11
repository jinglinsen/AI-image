"""
金币系统服务
"""
from models.database import db, User, SystemSettings, CoinTransaction
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CoinService:
    """金币服务类"""
    
    # 金币设置的key
    COIN_MODE_KEY = 'coin_mode'  # 金币模式: 'fixed' 或 'daily'
    COIN_INIT_AMOUNT_KEY = 'coin_init_amount'  # 初始金币数量（方式1）
    COIN_DAILY_AMOUNT_KEY = 'coin_daily_amount'  # 每日金币数量（方式2）
    COIN_PER_IMAGE_KEY = 'coin_per_image'  # 每张图片消耗金币数
    
    @staticmethod
    def get_setting(key, default=None):
        """获取系统设置"""
        try:
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                return setting.value
            return default
        except Exception as e:
            logger.error(f"获取系统设置失败 {key}: {e}")
            return default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """设置系统设置"""
        try:
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                if description:
                    setting.description = description
            else:
                setting = SystemSettings(
                    key=key,
                    value=str(value),
                    description=description
                )
                db.session.add(setting)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"设置系统设置失败 {key}: {e}")
            return False
    
    @staticmethod
    def get_coin_settings():
        """获取金币系统设置"""
        return {
            'mode': CoinService.get_setting(CoinService.COIN_MODE_KEY, 'fixed'),
            'init_amount': int(CoinService.get_setting(CoinService.COIN_INIT_AMOUNT_KEY, '100')),
            'daily_amount': int(CoinService.get_setting(CoinService.COIN_DAILY_AMOUNT_KEY, '10')),
            'per_image': int(CoinService.get_setting(CoinService.COIN_PER_IMAGE_KEY, '1'))
        }
    
    @staticmethod
    def update_coin_settings(mode, init_amount=None, daily_amount=None, per_image=None):
        """更新金币系统设置"""
        try:
            CoinService.set_setting(CoinService.COIN_MODE_KEY, mode, '金币模式: fixed=固定初始, daily=每日重置')
            
            if init_amount is not None:
                CoinService.set_setting(CoinService.COIN_INIT_AMOUNT_KEY, init_amount, '新用户初始金币数量')
            
            if daily_amount is not None:
                CoinService.set_setting(CoinService.COIN_DAILY_AMOUNT_KEY, daily_amount, '每日重置金币数量')
            
            if per_image is not None:
                CoinService.set_setting(CoinService.COIN_PER_IMAGE_KEY, per_image, '每张图片消耗金币数')
            
            return True, "设置保存成功"
        except Exception as e:
            logger.error(f"更新金币设置失败: {e}")
            return False, f"设置保存失败: {str(e)}"
    
    @staticmethod
    def initialize_user_coins(user_id):
        """初始化新用户金币"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            settings = CoinService.get_coin_settings()
            init_amount = settings['init_amount']
            
            user.coins = init_amount
            user.total_coins_earned = init_amount
            user.last_coin_reset_at = datetime.utcnow()
            
            # 记录交易
            transaction = CoinTransaction(
                user_id=user_id,
                amount=init_amount,
                balance_after=init_amount,
                transaction_type='init',
                description='新用户初始化金币'
            )
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"用户 {user_id} 初始化金币: {init_amount}")
            return True, f"初始化成功，获得 {init_amount} 金币"
        except Exception as e:
            db.session.rollback()
            logger.error(f"初始化用户金币失败: {e}")
            return False, f"初始化失败: {str(e)}"
    
    @staticmethod
    def add_coins(user_id, amount, transaction_type='admin_recharge', description=None, operated_by=None):
        """给用户添加金币"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            user.coins += amount
            user.total_coins_earned += amount
            
            # 记录交易
            transaction = CoinTransaction(
                user_id=user_id,
                amount=amount,
                balance_after=user.coins,
                transaction_type=transaction_type,
                description=description or f"管理员充值 {amount} 金币",
                operated_by=operated_by
            )
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"用户 {user_id} 增加金币: {amount}, 余额: {user.coins}")
            return True, f"充值成功，当前余额: {user.coins}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加金币失败: {e}")
            return False, f"充值失败: {str(e)}"
    
    @staticmethod
    def deduct_coins(user_id, amount, task_id=None, description=None):
        """扣除用户金币"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            if user.coins < amount:
                return False, f"金币不足，当前余额: {user.coins}"
            
            user.coins -= amount
            user.total_coins_spent += amount
            
            # 记录交易
            transaction = CoinTransaction(
                user_id=user_id,
                amount=-amount,
                balance_after=user.coins,
                transaction_type='image_generation',
                description=description or f"生成图片消耗 {amount} 金币",
                task_id=task_id
            )
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"用户 {user_id} 扣除金币: {amount}, 余额: {user.coins}")
            return True, f"扣除成功，剩余余额: {user.coins}"
        except Exception as e:
            db.session.rollback()
            logger.error(f"扣除金币失败: {e}")
            return False, f"扣除失败: {str(e)}"
    
    @staticmethod
    def check_coins_sufficient(user_id, required_amount):
        """检查用户金币是否充足"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在", 0
            
            return user.coins >= required_amount, user.coins >= required_amount, user.coins
        except Exception as e:
            logger.error(f"检查金币余额失败: {e}")
            return False, "检查失败", 0
    
    @staticmethod
    def get_user_coins(user_id):
        """获取用户金币余额"""
        try:
            user = User.query.get(user_id)
            if not user:
                return 0
            return user.coins
        except Exception as e:
            logger.error(f"获取用户金币失败: {e}")
            return 0
    
    @staticmethod
    def reset_daily_coins():
        """每日金币重置（方式2）"""
        try:
            settings = CoinService.get_coin_settings()
            
            # 只在每日模式下执行
            if settings['mode'] != 'daily':
                logger.info("当前不是每日模式，跳过金币重置")
                return 0
            
            daily_amount = settings['daily_amount']
            today = datetime.utcnow().date()
            
            # 查找所有需要重置的用户（今天还没重置过的）
            users = User.query.filter(
                db.or_(
                    User.last_coin_reset_at == None,
                    db.func.date(User.last_coin_reset_at) < today
                )
            ).all()
            
            reset_count = 0
            for user in users:
                user.coins = daily_amount
                user.total_coins_earned += daily_amount
                user.last_coin_reset_at = datetime.utcnow()
                
                # 记录交易
                transaction = CoinTransaction(
                    user_id=user.id,
                    amount=daily_amount,
                    balance_after=daily_amount,
                    transaction_type='daily_reset',
                    description=f'每日重置金币 {daily_amount}'
                )
                db.session.add(transaction)
                reset_count += 1
            
            db.session.commit()
            logger.info(f"每日金币重置完成，共重置 {reset_count} 个用户")
            return reset_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"每日金币重置失败: {e}")
            return 0
    
    @staticmethod
    def batch_recharge_coins(user_ids, amount, operated_by=None):
        """批量充值金币"""
        try:
            success_count = 0
            failed_users = []
            
            for user_id in user_ids:
                success, message = CoinService.add_coins(
                    user_id, 
                    amount, 
                    'admin_recharge',
                    f'管理员批量充值 {amount} 金币',
                    operated_by
                )
                if success:
                    success_count += 1
                else:
                    failed_users.append(user_id)
            
            return True, f"批量充值完成，成功 {success_count} 个", failed_users
        except Exception as e:
            logger.error(f"批量充值失败: {e}")
            return False, f"批量充值失败: {str(e)}", []
    
    @staticmethod
    def get_transaction_history(user_id, limit=50):
        """获取用户交易记录"""
        try:
            transactions = CoinTransaction.query.filter_by(user_id=user_id)\
                .order_by(CoinTransaction.created_at.desc())\
                .limit(limit)\
                .all()
            return [t.to_dict() for t in transactions]
        except Exception as e:
            logger.error(f"获取交易记录失败: {e}")
            return []

