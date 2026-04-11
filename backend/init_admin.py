"""
管理员初始化脚本
创建默认管理员账户和初始邀请码
"""
import sys
import os

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.database import db, User, InviteCode
from utils.auth import hash_password, generate_invite_code

def init_admin():
    """初始化管理员账户"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已存在管理员
        admin = User.query.filter_by(is_admin=True).first()
        
        if admin:
            print("管理员账户已存在:")
            print(f"  用户名: {admin.username}")
            print(f"  邮箱: {admin.email}")
            print(f"  创建时间: {admin.created_at}")
            return
        
        print("开始创建默认管理员账户...")
        
        # 创建默认管理员
        admin_user = User(
            phone='13800138000',
            email='admin@aigc.com',
            username='admin',
            password_hash=hash_password('admin123'),
            is_admin=True,
            status='active',
            invite_code_used='SYSTEM'
        )
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            
            print("✓ 管理员账户创建成功!")
            print(f"  用户名: {admin_user.username}")
            print(f"  密码: admin123")
            print(f"  邮箱: {admin_user.email}")
            print(f"  手机: {admin_user.phone}")
            print("\n⚠️  请登录后立即修改默认密码！")
            
            # 生成初始邀请码
            print("\n开始生成初始邀请码...")
            codes = []
            for i in range(10):
                while True:
                    code = generate_invite_code()
                    # 检查是否已存在
                    if not InviteCode.query.filter_by(code=code).first():
                        break
                
                invite = InviteCode(
                    code=code,
                    created_by=admin_user.id,
                    status='unused'
                )
                db.session.add(invite)
                codes.append(code)
            
            db.session.commit()
            
            print(f"✓ 成功生成{len(codes)}个邀请码:")
            for i, code in enumerate(codes, 1):
                print(f"  {i}. {code}")
            
            print("\n初始化完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ 初始化失败: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    init_admin()

