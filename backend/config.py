import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/aigc_assistant?charset=utf8mb4')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,          # 增加连接池大小
        'max_overflow': 30,       # 允许超出连接池的连接数
        'pool_timeout': 30,       # 连接超时时间
        'pool_recycle': 3600,     # 连接回收时间（1小时）
        'pool_pre_ping': True,    # 连接前ping检查
    }
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # API配置
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    API_BASE_URL = os.getenv('API_BASE_URL', 'https://openrouter.ai/api/v1')
    HTTP_REFERER = os.getenv('HTTP_REFERER', 'https://aigc-assistant.com')
    X_TITLE = os.getenv('X_TITLE', 'Amazon AIGC Assistant')
    
    # Google Generative AI配置
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_MODEL_NAME = os.getenv('GOOGLE_MODEL_NAME', 'gemini-2.5-flash')
    
    # 模型配置
    MODEL_NAME = os.getenv('MODEL_NAME', 'nano-banana/nano-banana')
    MAX_INPUT_IMAGES = int(os.getenv('MAX_INPUT_IMAGES', 10))
    DEFAULT_QUALITY = int(os.getenv('DEFAULT_QUALITY', 85))
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 120))
    
    # 成本控制
    MAX_DAILY_REQUESTS = int(os.getenv('MAX_DAILY_REQUESTS', 1000))
    COST_ALERT_THRESHOLD = float(os.getenv('COST_ALERT_THRESHOLD', 100.0))
    
    # OSS配置
    OSS_ACCESS_ID = os.getenv('OSS_ACCESS_ID')
    OSS_ACCESS_KEY = os.getenv('OSS_ACCESS_KEY')
    OSS_ENDPOINT = os.getenv('OSS_ENDPOINT')  # 修正为正确的区域
    OSS_BUCKET = os.getenv('OSS_BUCKET')
    # OSS开关：直接设置为False禁用OSS上传（开发环境使用本地存储）
    OSS_ENABLED = os.getenv('OSS_ENABLED', True)  # 改为 True 可启用OSS上传
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 生产环境的额外安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost:3306/aigc_assistant_test?charset=utf8mb4'
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
