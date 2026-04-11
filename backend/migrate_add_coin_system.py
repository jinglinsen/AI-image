"""
数据库迁移脚本：添加金币系统相关字段和表
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            # 获取数据库连接
            connection = db.engine.connect()
            
            # 检查并添加users表的新字段
            logger.info("检查users表...")
            
            # 添加coins字段
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 0"))
                logger.info("✓ 添加 users.coins 字段")
            except Exception as e:
                if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                    logger.info("✓ users.coins 字段已存在")
                else:
                    raise
            
            # 添加total_coins_earned字段
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN total_coins_earned INTEGER DEFAULT 0"))
                logger.info("✓ 添加 users.total_coins_earned 字段")
            except Exception as e:
                if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                    logger.info("✓ users.total_coins_earned 字段已存在")
                else:
                    raise
            
            # 添加total_coins_spent字段
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN total_coins_spent INTEGER DEFAULT 0"))
                logger.info("✓ 添加 users.total_coins_spent 字段")
            except Exception as e:
                if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                    logger.info("✓ users.total_coins_spent 字段已存在")
                else:
                    raise
            
            # 添加last_coin_reset_at字段
            try:
                connection.execute(db.text("ALTER TABLE users ADD COLUMN last_coin_reset_at DATETIME"))
                logger.info("✓ 添加 users.last_coin_reset_at 字段")
            except Exception as e:
                if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                    logger.info("✓ users.last_coin_reset_at 字段已存在")
                else:
                    raise
            
            connection.commit()
            connection.close()
            
            # 创建新表
            logger.info("\n检查并创建新表...")
            db.create_all()
            logger.info("✓ 所有表创建/检查完成")
            
            # 初始化系统设置
            from models.database import SystemSettings
            logger.info("\n初始化系统设置...")
            
            default_settings = [
                ('coin_mode', 'fixed', '金币模式: fixed=固定初始, daily=每日重置'),
                ('coin_init_amount', '100', '新用户初始金币数量'),
                ('coin_daily_amount', '10', '每日重置金币数量'),
                ('coin_per_image', '1', '每张图片消耗金币数')
            ]
            
            for key, value, description in default_settings:
                existing = SystemSettings.query.filter_by(key=key).first()
                if not existing:
                    setting = SystemSettings(key=key, value=value, description=description)
                    db.session.add(setting)
                    logger.info(f"✓ 初始化设置: {key} = {value}")
                else:
                    logger.info(f"✓ 设置已存在: {key}")
            
            db.session.commit()
            
            # 为现有用户初始化金币
            from models.database import User
            from services.coin_service import CoinService
            
            logger.info("\n为现有用户初始化金币...")
            users_without_coins = User.query.filter(
                (User.coins == None) | (User.coins == 0)
            ).all()
            
            init_amount = 100  # 默认初始金币
            for user in users_without_coins:
                if user.coins is None or user.coins == 0:
                    user.coins = init_amount
                    user.total_coins_earned = init_amount
                    logger.info(f"✓ 用户 {user.username} 初始化金币: {init_amount}")
            
            db.session.commit()
            
            logger.info("\n" + "="*50)
            logger.info("数据库迁移完成！")
            logger.info("="*50)
            logger.info("\n金币系统已启用：")
            logger.info("- 默认模式: 固定初始金币")
            logger.info("- 新用户初始金币: 100")
            logger.info("- 每张图片消耗: 1 金币")
            logger.info("\n可以在管理后台的'系统设置'中修改这些配置\n")
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()

