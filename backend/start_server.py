#!/usr/bin/env python3
"""
Amazon AIGC助手后端服务启动脚本
"""
import os
import logging
from app import create_app

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

if __name__ == '__main__':
    setup_logging()
    
    # 创建Flask应用
    app = create_app()
    
    # 启动定时任务
    try:
        from scheduler import setup_scheduler
        setup_scheduler(app)
        logging.info("✅ 定时任务调度器已启动")
    except Exception as e:
        logging.error(f"❌ 定时任务启动失败: {e}")
    
    # 获取配置
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("🚀 Amazon AIGC助手后端服务")
    print("=" * 60)
    print(f"📍 运行地址: http://{host}:{port}")
    print(f"🔧 调试模式: {debug}")
    print(f"📊 数据库: SQLite")
    print(f"🤖 AI模型: Nano Banana")
    print("=" * 60)
    print("🎯 支持的图片类型:")
    print("   • 产品主图 - 纯白背景专业产品照")
    print("   • 信息图 - 功能特性可视化展示")
    print("   • 生活方式图 - 真实使用场景")
    print("   • 尺寸图 - 产品尺寸对比")
    print("   • 产品细节图 - 特写展示")
    print("   • 多角度图 - 全方位展示")
    print("   • 使用说明图 - 操作指导")
    print("   • 对比图 - 竞品优势")
    print("   • 包装图 - 产品包装")
    print("=" * 60)
    print("🌍 支持的市场:")
    print("   • 🇺🇸 美国 - 功能性和家庭场景")
    print("   • 🇬🇧 英国 - 经典优雅风格")
    print("   • 🇩🇪 德国 - 品质工艺导向")
    print("   • 🇯🇵 日本 - 精致简约美学")
    print("   • 🇮🇳 印度 - 性价比实用性")
    print("=" * 60)
    print("✅ 服务就绪，等待请求...")
    
    app.run(host=host, port=port, debug=debug)
