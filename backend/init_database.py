"""
数据库初始化脚本
创建默认管理员账号和初始邀请码
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db, User, InviteCode
from services.user_service import UserService
from services.invite_service import InviteService
from datetime import datetime
import secrets
import string

def init_database():
    """初始化数据库"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        print("正在创建数据库表...")
        db.create_all()
        print("数据库表创建完成")
        
        # 检查是否已有管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("\n正在创建默认管理员账号...")
            try:
                # 创建管理员账号
                result = UserService.create_admin_user(
                    phone='13800138000',
                    email='admin@aigc.com',
                    username='admin',
                    password='admin123'
                )
                
                if result and result.get('success'):
                    admin_user = result['user']
                    print(f"[OK] 管理员账号创建成功")
                    print(f"  用户名: admin")
                    print(f"  密码: admin123")
                    print(f"  邮箱: admin@aigc.com")
                else:
                    error_msg = result.get('error') if result else '未知错误'
                    print(f"[错误] 管理员账号创建失败: {error_msg}")
                    return
            except Exception as e:
                print(f"[错误] 创建管理员账号时出错: {str(e)}")
                return
        else:
            print(f"\n管理员账号已存在: {admin_user.username}")
        
        # 检查邀请码数量
        unused_codes_count = InviteCode.query.filter_by(status='unused').count()
        
        if unused_codes_count < 10:
            print(f"\n当前未使用的邀请码数量: {unused_codes_count}")
            print("正在生成初始邀请码...")
            
            try:
                # 生成10个邀请码
                success, message, codes_list = InviteService.generate_invite_codes(
                    admin_id=admin_user.id,
                    count=10
                )
                
                if success:
                    print(f"[OK] {message}")
                    print("\n邀请码列表:")
                    for code in codes_list:
                        print(f"  - {code}")
                else:
                    print(f"[错误] {message}")
            except Exception as e:
                print(f"[错误] 生成邀请码时出错: {str(e)}")
        else:
            print(f"\n当前有 {unused_codes_count} 个未使用的邀请码")
        
        print("\n数据库初始化完成！")
        print("\n系统默认账号:")
        print("=" * 50)
        print("管理员账号:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("=" * 50)
        print("\n请在首次登录后立即修改默认密码！")

if __name__ == '__main__':
    init_database()

