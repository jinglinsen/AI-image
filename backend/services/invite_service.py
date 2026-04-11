"""
邀请码服务模块
处理邀请码生成、管理等业务逻辑
"""
from models.database import db, User, InviteCode
from utils.auth import generate_invite_code
from datetime import datetime

class InviteService:
    """邀请码服务类"""
    
    @staticmethod
    def generate_invite_codes(admin_id, count=1):
        """
        批量生成邀请码
        
        Args:
            admin_id: 管理员ID
            count: 生成数量
            
        Returns:
            tuple: (success, message, codes_list)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限", None
        
        if count < 1 or count > 100:
            return False, "生成数量必须在1-100之间", None
        
        codes_list = []
        try:
            for _ in range(count):
                # 生成唯一的邀请码
                while True:
                    code = generate_invite_code()
                    # 检查是否已存在
                    if not InviteCode.query.filter_by(code=code).first():
                        break
                
                invite = InviteCode(
                    code=code,
                    created_by=admin_id,
                    status='unused'
                )
                db.session.add(invite)
                codes_list.append(code)
            
            db.session.commit()
            return True, f"成功生成{count}个邀请码", codes_list
            
        except Exception as e:
            db.session.rollback()
            return False, f"生成失败: {str(e)}", None
    
    @staticmethod
    def get_invite_codes(admin_id, status=None, page=1, per_page=50):
        """
        获取邀请码列表
        
        Args:
            admin_id: 管理员ID
            status: 状态过滤 (unused/used/None表示全部)
            page: 页码
            per_page: 每页数量
            
        Returns:
            tuple: (success, message, codes_list, pagination_info)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限", None, None
        
        # 构建查询
        query = InviteCode.query
        if status:
            query = query.filter_by(status=status)
        
        # 按创建时间倒序
        query = query.order_by(InviteCode.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        codes = []
        for invite in pagination.items:
            code_dict = invite.to_dict()
            # 添加创建者信息
            creator = User.query.get(invite.created_by)
            if creator:
                code_dict['creator_username'] = creator.username
            
            # 添加使用者信息
            if invite.used_by:
                user = User.query.get(invite.used_by)
                if user:
                    code_dict['user_username'] = user.username
                    code_dict['user_email'] = user.email
            
            codes.append(code_dict)
        
        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
        
        return True, "获取成功", codes, pagination_info
    
    @staticmethod
    def get_invite_code_stats(admin_id):
        """
        获取邀请码统计信息
        
        Args:
            admin_id: 管理员ID
            
        Returns:
            tuple: (success, message, stats)
        """
        # 验证管理员权限
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return False, "没有管理员权限", None
        
        total = InviteCode.query.count()
        used = InviteCode.query.filter_by(status='used').count()
        unused = InviteCode.query.filter_by(status='unused').count()
        
        stats = {
            'total': total,
            'used': used,
            'unused': unused,
            'usage_rate': round(used / total * 100, 2) if total > 0 else 0
        }
        
        return True, "获取成功", stats

