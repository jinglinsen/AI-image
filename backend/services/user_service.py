"""
用户服务模块
处理用户注册、登录、密码管理等业务逻辑
"""
from models.database import db, User, InviteCode
from utils.auth import hash_password, verify_password, generate_token
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类"""
    
    @staticmethod
    def create_admin_user(phone, email, username, password):
        """
        创建管理员账号（用于系统初始化）
        
        Args:
            phone: 手机号
            email: 邮箱
            username: 用户名
            password: 密码
            
        Returns:
            dict: {success: bool, message: str, user: User}
        """
        try:
            # 检查是否已存在
            if User.query.filter_by(username=username).first():
                return {
                    'success': False,
                    'error': '用户名已存在'
                }
            
            # 创建管理员用户
            user = User(
                phone=phone,
                email=email,
                username=username,
                password_hash=hash_password(password),
                is_admin=True,
                status='active'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': '管理员账号创建成功',
                'user': user
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_phone(phone):
        """验证手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        验证密码强度
        至少6位，包含字母和数字
        """
        if len(password) < 6:
            return False, "密码至少6位"
        if not re.search(r'[a-zA-Z]', password):
            return False, "密码必须包含字母"
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        return True, ""
    
    @staticmethod
    def register_user(phone, email, username, password, invite_code):
        """
        用户注册
        
        Args:
            phone: 手机号
            email: 邮箱
            username: 用户名
            password: 密码
            invite_code: 邀请码
            
        Returns:
            tuple: (success, message, user_data)
        """
        # 验证手机号格式
        if not UserService.validate_phone(phone):
            return False, "手机号格式不正确", None
        
        # 验证邮箱格式
        if not UserService.validate_email(email):
            return False, "邮箱格式不正确", None
        
        # 验证密码强度
        valid, msg = UserService.validate_password(password)
        if not valid:
            return False, msg, None
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return False, "用户名长度需在3-20个字符之间", None
        
        # 检查手机号是否已注册
        if User.query.filter_by(phone=phone).first():
            return False, "手机号已被注册", None
        
        # 检查邮箱是否已注册
        if User.query.filter_by(email=email).first():
            return False, "邮箱已被注册", None
        
        # 检查用户名是否已被使用
        if User.query.filter_by(username=username).first():
            return False, "用户名已被使用", None
        
        # 验证邀请码
        invite = InviteCode.query.filter_by(code=invite_code).first()
        if not invite:
            return False, "邀请码不存在", None
        if invite.status == 'used':
            return False, "邀请码已被使用", None
        
        try:
            # 创建用户
            user = User(
                phone=phone,
                email=email,
                username=username,
                password_hash=hash_password(password),
                invite_code_used=invite_code,
                is_admin=False,
                status='active'
            )
            db.session.add(user)
            db.session.flush()  # 立即写入，生成user.id
            
            # 标记邀请码已使用
            invite.status = 'used'
            invite.used_by = user.id
            invite.used_at = datetime.utcnow()
            
            db.session.commit()
            
            # 初始化用户金币
            try:
                from services.coin_service import CoinService
                CoinService.initialize_user_coins(user.id)
                logger.info(f"用户 {user.id} 金币初始化成功")
            except Exception as e:
                logger.error(f"用户 {user.id} 金币初始化失败: {e}")
                # 金币初始化失败不影响注册
            
            return True, "注册成功", user.to_dict()
            
        except Exception as e:
            db.session.rollback()
            return False, f"注册失败: {str(e)}", None
    
    @staticmethod
    def login_user(username_or_email, password):
        """
        用户登录
        
        Args:
            username_or_email: 用户名或邮箱
            password: 密码
            
        Returns:
            tuple: (success, message, token, user_data)
        """
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            return False, "用户不存在", None, None
        
        # 检查账户状态
        if user.status != 'active':
            return False, "账户已被停用", None, None
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return False, "密码错误", None, None
        
        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        # 生成Token
        token = generate_token(user.id, user.is_admin)
        
        return True, "登录成功", token, user.to_dict()
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            tuple: (success, message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, "用户不存在"
        
        # 验证旧密码
        if not verify_password(old_password, user.password_hash):
            return False, "旧密码错误"
        
        # 验证新密码强度
        valid, msg = UserService.validate_password(new_password)
        if not valid:
            return False, msg
        
        # 更新密码
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        return True, "密码修改成功"
    
    @staticmethod
    def reset_password_by_admin(admin_id, target_user_id, new_password):
        """
        管理员重置用户密码
        
        Args:
            admin_id: 管理员ID
            target_user_id: 目标用户ID
            new_password: 新密码
            
        Returns:
            tuple: (success, message)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限"
        
        # 查找目标用户
        target_user = User.query.get(target_user_id)
        if not target_user:
            return False, "目标用户不存在"
        
        # 验证新密码强度
        valid, msg = UserService.validate_password(new_password)
        if not valid:
            return False, msg
        
        # 重置密码
        target_user.password_hash = hash_password(new_password)
        db.session.commit()
        
        return True, "密码重置成功"
    
    @staticmethod
    def get_user_info(user_id):
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 用户信息
        """
        user = User.query.get(user_id)
        if not user:
            return None
        return user.to_dict()
    
    @staticmethod
    def get_all_users(admin_id, page=1, per_page=20):
        """
        管理员获取所有用户列表
        
        Args:
            admin_id: 管理员ID
            page: 页码
            per_page: 每页数量
            
        Returns:
            tuple: (success, message, user_list, pagination_info)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限", None, None
        
        # 分页查询
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return True, "获取成功", users, pagination_info
    
    @staticmethod
    def delete_user(admin_id, target_user_id):
        """
        管理员删除用户
        
        Args:
            admin_id: 管理员ID
            target_user_id: 目标用户ID
            
        Returns:
            tuple: (success, message)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限"
        
        # 不能删除自己
        if admin_id == target_user_id:
            return False, "不能删除自己的账户"
        
        # 查找目标用户
        target_user = User.query.get(target_user_id)
        if not target_user:
            return False, "目标用户不存在"
        
        # 不能删除其他管理员
        if target_user.is_admin:
            return False, "不能删除管理员账户"
        
        try:
            # 删除用户（关联数据会根据外键约束处理）
            db.session.delete(target_user)
            db.session.commit()
            return True, "用户删除成功"
        except Exception as e:
            db.session.rollback()
            return False, f"删除失败: {str(e)}"
    
    @staticmethod
    def get_user_stats(admin_id, target_user_id):
        """
        获取用户统计信息
        
        Args:
            admin_id: 管理员ID
            target_user_id: 目标用户ID
            
        Returns:
            tuple: (success, message, stats)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限", None
        
        user = User.query.get(target_user_id)
        if not user:
            return False, "用户不存在", None
        
        stats = {
            'user_info': user.to_dict(),
            'total_tasks': user.generation_tasks.count(),
            'total_images': user.generated_images.count(),
            'total_history': user.generation_history.count(),
            'api_calls': user.api_usage.count(),
            'total_cost': sum(api.cost_estimate for api in user.api_usage)
        }
        
        return True, "获取成功", stats

