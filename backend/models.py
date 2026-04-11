from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# 这里不导入app，而是在需要时从外部传入db实例
db = None

class GenerationTask(db.Model):
    """图片生成任务表"""
    __tablename__ = 'generation_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
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

class ApiUsage(db.Model):
    """API使用统计表"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
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
