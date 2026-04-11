from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# 创建数据库实例
db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    invite_code_used = db.Column(db.String(20), index=True)  # 使用的邀请码
    status = db.Column(db.String(20), default='active')  # active, suspended
    coins = db.Column(db.Integer, default=0)  # 金币余额
    total_coins_earned = db.Column(db.Integer, default=0)  # 累计获得金币
    total_coins_spent = db.Column(db.Integer, default=0)  # 累计消费金币
    last_coin_reset_at = db.Column(db.DateTime)  # 最后一次金币重置时间（方式2使用）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    
    # 关联关系
    generation_tasks = db.relationship('GenerationTask', backref='user', lazy='dynamic')
    generated_images = db.relationship('GeneratedImage', backref='user', lazy='dynamic')
    generation_history = db.relationship('GenerationHistory', backref='user', lazy='dynamic')
    api_usage = db.relationship('ApiUsage', backref='user', lazy='dynamic')
    created_invite_codes = db.relationship('InviteCode', foreign_keys='InviteCode.created_by', backref='creator', lazy='dynamic')
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'phone': self.phone,
            'email': self.email,
            'username': self.username,
            'is_admin': self.is_admin,
            'status': self.status,
            'coins': self.coins,
            'total_coins_earned': self.total_coins_earned,
            'total_coins_spent': self.total_coins_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }
        if include_sensitive:
            data['invite_code_used'] = self.invite_code_used
        return data

class InviteCode(db.Model):
    """邀请码表"""
    __tablename__ = 'invite_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    used_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    used_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='unused')  # unused, used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联使用者
    user = db.relationship('User', foreign_keys=[used_by], backref='used_invite_code')
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'created_by': self.created_by,
            'used_by': self.used_by,
            'used_at': self.used_at.isoformat() if self.used_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GenerationTask(db.Model):
    """图片生成任务表"""
    __tablename__ = 'generation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID
    user_input = db.Column(db.Text, nullable=False)  # JSON格式的用户输入
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 进度百分比
    total_images = db.Column(db.Integer, default=0)  # 需要生成的图片总数
    error_message = db.Column(db.Text)  # 错误信息
    parent_task_id = db.Column(db.String(36), index=True)  # 父任务ID（用于重新生成）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联生成的图片
    generated_images = db.relationship('GeneratedImage', backref='task', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'total_images': self.total_images,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class GeneratedImage(db.Model):
    """生成的图片表"""
    __tablename__ = 'generated_images'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), db.ForeignKey('generation_tasks.task_id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID
    image_type = db.Column(db.String(50), nullable=False)  # main, infographic, lifestyle等
    filename = db.Column(db.String(255), nullable=False)  # 生成的图片文件名
    image_url = db.Column(db.String(500))  # 完整的图片URL（OSS或本地）
    storage_type = db.Column(db.String(20), default='local')  # 存储类型：oss或local
    prompt_used = db.Column(db.Text, nullable=False)  # 使用的提示词
    model_used = db.Column(db.String(50), default='nano-banana')  # 使用的模型
    parent_image_id = db.Column(db.Integer, db.ForeignKey('generated_images.id'))  # 父图片ID（重新生成时）
    generation_params = db.Column(db.Text)  # JSON格式的生成参数
    user_rating = db.Column(db.Integer)  # 用户评分 1-5
    is_favorite = db.Column(db.Boolean, default=False)  # 是否收藏
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 自引用关系（父子图片）
    children = db.relationship('GeneratedImage', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'image_type': self.image_type,
            'filename': self.filename,
            'url': self.image_url if self.image_url else f'/api/image/{self.filename}',
            'storage_type': self.storage_type,
            'model_used': self.model_used,
            'parent_image_id': self.parent_image_id,
            'user_rating': self.user_rating,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GenerationContext(db.Model):
    """生成上下文记忆表"""
    __tablename__ = 'generation_contexts'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), nullable=False, index=True)
    context_type = db.Column(db.String(50), nullable=False)  # product_info, style_preference, feedback_history等
    context_data = db.Column(db.Text, nullable=False)  # JSON格式的上下文数据
    weight = db.Column(db.Float, default=1.0)  # 权重，用于优化提示词
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'context_type': self.context_type,
            'context_data': json.loads(self.context_data) if self.context_data else {},
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserFeedback(db.Model):
    """用户反馈表"""
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('generated_images.id'), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # like, dislike, regenerate, download
    feedback_data = db.Column(db.Text)  # JSON格式的详细反馈
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联图片
    image = db.relationship('GeneratedImage', backref='feedback')
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_id': self.image_id,
            'feedback_type': self.feedback_type,
            'feedback_data': json.loads(self.feedback_data) if self.feedback_data else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GenerationHistory(db.Model):
    """生成历史记录表"""
    __tablename__ = 'generation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID
    task_id = db.Column(db.String(36), db.ForeignKey('generation_tasks.task_id'), nullable=False, index=True)
    title = db.Column(db.String(200))  # 任务标题（产品名称）
    is_pinned = db.Column(db.Boolean, default=False)  # 是否置顶
    
    # 用户输入参数
    product_form = db.Column(db.Text)  # 产品形态 (改用Text避免过长)
    selected_image_types = db.Column(db.Text)  # JSON格式的选择图片类型
    main_prompt = db.Column(db.Text)  # 主提示词
    product_images = db.Column(db.Text)  # JSON格式的产品图片
    reference_images_by_type = db.Column(db.Text)  # JSON格式的按类型分组的参考图片
    competitors = db.Column(db.Text)  # JSON格式的竞争对手信息
    selected_size = db.Column(db.String(20))  # 图片尺寸
    selected_ratio = db.Column(db.String(10))  # 图片比例
    selected_model = db.Column(db.String(50))  # 使用的模型
    
    # 生成结果
    generated_image_count = db.Column(db.Integer, default=0)  # 生成的图片数量
    success_count = db.Column(db.Integer, default=0)  # 成功生成的图片数量
    generation_time = db.Column(db.Float)  # 生成耗时（秒）
    
    # 用户交互
    user_rating = db.Column(db.Integer)  # 用户对整体结果的评分 1-5
    user_notes = db.Column(db.Text)  # 用户备注
    is_favorite = db.Column(db.Boolean, default=False)  # 是否收藏此次生成
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联生成任务
    task = db.relationship('GenerationTask', backref='history')
    
    def _get_generated_images(self):
        """安全地获取生成的图片列表，避免关联查询阻塞"""
        try:
            if self.task and hasattr(self.task, 'generated_images'):
                return [img.to_dict() for img in self.task.generated_images]
        except Exception as e:
            # 如果关联查询失败，记录错误但不阻塞
            import logging
            logging.warning(f"获取生成图片失败: {e}")
        return []
    
    def to_dict(self):
        # 解析product_form
        try:
            product_form_data = json.loads(self.product_form) if self.product_form else {}
        except:
            product_form_data = {}
            
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'title': self.title,
            'is_pinned': self.is_pinned,
            'product_form': self.product_form,
            'selected_image_types': json.loads(self.selected_image_types) if self.selected_image_types else [],
            'main_prompt': self.main_prompt,
            'product_images': json.loads(self.product_images) if self.product_images else [],
            'reference_images_by_type': json.loads(self.reference_images_by_type) if self.reference_images_by_type else {},
            'competitors': json.loads(self.competitors) if self.competitors else [],
            'selected_size': self.selected_size,
            'selected_ratio': self.selected_ratio,
            'selected_model': self.selected_model,
            'generated_image_count': self.generated_image_count,
            'success_count': self.success_count,
            'generation_time': self.generation_time,
            'user_rating': self.user_rating,
            'user_notes': self.user_notes,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 包含生成的图片（安全处理，避免关联查询阻塞）
            'generated_images': self._get_generated_images(),
            # 兼容前端：提供generation_params字段
            'generation_params': {
                'productForm': product_form_data,
                'selectedImageTypes': json.loads(self.selected_image_types) if self.selected_image_types else [],
                'mainPrompt': self.main_prompt,
                'productImages': json.loads(self.product_images) if self.product_images else [],
                'referenceImagesByType': json.loads(self.reference_images_by_type) if self.reference_images_by_type else {},
                'competitors': json.loads(self.competitors) if self.competitors else [],
                'selectedSize': self.selected_size,
                'selectedRatio': self.selected_ratio,
                'selectedModel': self.selected_model
            }
        }

class ApiUsage(db.Model):
    """API使用统计表"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)  # 用户ID
    task_id = db.Column(db.String(36), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    api_endpoint = db.Column(db.String(255), nullable=False)
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=1)
    cost_estimate = db.Column(db.Float, default=0.0)  # 成本估算
    response_time = db.Column(db.Float)  # 响应时间（秒）
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'model_name': self.model_name,
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'image_count': self.image_count,
            'cost_estimate': self.cost_estimate,
            'response_time': self.response_time,
            'success': self.success,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemSettings(db.Model):
    """系统设置表"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CoinTransaction(db.Model):
    """金币交易记录表"""
    __tablename__ = 'coin_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    amount = db.Column(db.Integer, nullable=False)  # 金币数量，正数为增加，负数为扣除
    balance_after = db.Column(db.Integer, nullable=False)  # 交易后余额
    transaction_type = db.Column(db.String(20), nullable=False)  # init, daily_reset, admin_recharge, image_generation, refund
    description = db.Column(db.String(200))
    task_id = db.Column(db.String(36), index=True)  # 关联的任务ID（如果是生图扣除）
    operated_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # 操作人（管理员充值时使用）
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关联
    user = db.relationship('User', foreign_keys=[user_id], backref='coin_transactions')
    operator = db.relationship('User', foreign_keys=[operated_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'task_id': self.task_id,
            'operated_by': self.operated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
