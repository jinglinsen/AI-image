"""
定时任务调度器
用于处理每日金币重置等定时任务
"""
import schedule
import time
import logging
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

def setup_scheduler(app):
    """设置定时任务"""
    
    def reset_daily_coins_job():
        """每日金币重置任务"""
        with app.app_context():
            try:
                from services.coin_service import CoinService
                logger.info("开始执行每日金币重置任务...")
                count = CoinService.reset_daily_coins()
                logger.info(f"每日金币重置完成，共重置 {count} 个用户")
            except Exception as e:
                logger.error(f"每日金币重置失败: {e}")
    
    # 每天凌晨0点执行金币重置
    schedule.every().day.at("00:00").do(reset_daily_coins_job)
    
    logger.info("定时任务已设置:")
    logger.info("- 每日金币重置: 每天 00:00")
    
    def run_scheduler():
        """运行定时任务循环"""
        logger.info("定时任务调度器已启动")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    # 在后台线程中运行调度器
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return scheduler_thread

if __name__ == '__main__':
    # 用于测试
    from app import create_app
    app = create_app()
    setup_scheduler(app)
    
    print("定时任务测试运行中...")
    print("按 Ctrl+C 退出")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n定时任务已停止")

