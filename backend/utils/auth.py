"""
认证工具模块
提供密码哈希、Token生成验证、装饰器等功能
"""
import jwt as pyjwt  # 明确导入为pyjwt避免命名冲突
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# JWT配置
JWT_SECRET_KEY = 'your-secret-key-change-in-production-2024'  # 生产环境应从环境变量读取
TOKEN_EXPIRATION_DAYS = 15

def hash_password(password):
    """
    密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password, password_hash):
    """
    验证密码
    
    Args:
        password: 明文密码
        password_hash: 哈希后的密码
        
    Returns:
        bool: 密码是否正确
    """
    return check_password_hash(password_hash, password)

def generate_token(user_id, is_admin=False):
    """
    生成JWT Token
    
    Args:
        user_id: 用户ID
        is_admin: 是否管理员
        
    Returns:
        str: JWT Token
    """
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=TOKEN_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    token = pyjwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """
    验证Token并返回用户信息
    
    Args:
        token: JWT Token
        
    Returns:
        dict: 包含user_id和is_admin的字典，失败返回None
    """
    try:
        payload = pyjwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return {
            'user_id': payload['user_id'],
            'is_admin': payload.get('is_admin', False)
        }
    except pyjwt.ExpiredSignatureError:
        return None  # Token过期
    except pyjwt.InvalidTokenError:
        return None  # Token无效

def generate_invite_code(length=8):
    """
    生成随机邀请码
    
    Args:
        length: 邀请码长度，默认8位
        
    Returns:
        str: 邀请码
    """
    # 生成包含大写字母和数字的随机邀请码
    characters = string.ascii_uppercase + string.digits
    # 排除容易混淆的字符: O, 0, I, 1
    characters = characters.replace('O', '').replace('0', '').replace('I', '').replace('1', '')
    return ''.join(random.choice(characters) for _ in range(length))

def token_required(f):
    """
    装饰器：要求API请求必须携带有效Token
    
    使用方法:
        @token_required
        def protected_api():
            user_id = request.user_id  # 可以直接访问user_id
            is_admin = request.is_admin
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        token = None
        
        # 从Authorization Header获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            logger.info(f"🔑 Authorization Header: {auth_header[:50]}...")
            try:
                # 格式: "Bearer <token>"
                token = auth_header.split(' ')[1]
                logger.info(f"🔑 提取的Token: {token[:20]}... (长度: {len(token)})")
            except IndexError:
                logger.error("❌ Token格式错误")
                return jsonify({'error': 'Token格式错误'}), 401
        else:
            logger.error("❌ 请求头中没有Authorization")
        
        if not token:
            logger.error("❌ Token为空")
            return jsonify({'error': '缺少认证Token'}), 401
        
        # 验证Token
        user_info = verify_token(token)
        if not user_info:
            logger.error("❌ Token验证失败")
            return jsonify({'error': 'Token无效或已过期'}), 401
        
        logger.info(f"✅ Token验证成功，用户ID: {user_info['user_id']}")
        
        # 将用户信息附加到request对象
        request.user_id = user_info['user_id']
        request.is_admin = user_info['is_admin']
        
        return f(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """
    装饰器：要求API请求必须是管理员权限
    
    使用方法:
        @admin_required
        def admin_api():
            user_id = request.user_id
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Authorization Header获取Token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Token格式错误'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证Token'}), 401
        
        # 验证Token
        user_info = verify_token(token)
        if not user_info:
            return jsonify({'error': 'Token无效或已过期'}), 401
        
        # 检查管理员权限
        if not user_info.get('is_admin', False):
            return jsonify({'error': '需要管理员权限'}), 403
        
        # 将用户信息附加到request对象
        request.user_id = user_info['user_id']
        request.is_admin = user_info['is_admin']
        
        return f(*args, **kwargs)
    
    return decorated_function

