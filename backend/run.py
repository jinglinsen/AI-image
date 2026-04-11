#!/usr/bin/env python3
import os
import logging
from app import app, db
from config import config

def setup_logging():
    """设置日志配置"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )

def create_app():
    """创建Flask应用"""
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("数据库表初始化完成")
    
    return app

if __name__ == '__main__':
    setup_logging()
    app = create_app()
    
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"启动Amazon AIGC助手后端服务...")
    print(f"运行地址: http://{host}:{port}")
    print(f"调试模式: {debug}")
    
    app.run(host=host, port=port, debug=debug)
