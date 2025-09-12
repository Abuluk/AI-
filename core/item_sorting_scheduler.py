from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from db.session import SessionLocal
from crud import crud_item_sorting
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ItemSortingScheduler:
    """商品排序定时任务调度器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """启动调度器"""
        if not self.is_running:
            # 每30分钟运行一次排序算法
            self.scheduler.add_job(
                func=self.run_sorting_task,
                trigger=IntervalTrigger(minutes=30),
                id='item_sorting_task',
                name='商品排序算法任务',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("商品排序调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("商品排序调度器已停止")
    
    def run_sorting_task(self):
        """运行排序任务"""
        db = SessionLocal()
        try:
            logger.info("开始运行商品排序算法...")
            result = crud_item_sorting.run_sorting_algorithm(db, time_window_minutes=30)
            logger.info(f"商品排序算法运行完成: {result}")
        except Exception as e:
            logger.error(f"商品排序算法运行失败: {str(e)}")
        finally:
            db.close()
    
    def run_manual_sorting(self, time_window_minutes: int = 30):
        """手动运行排序算法"""
        db = SessionLocal()
        try:
            logger.info(f"手动运行商品排序算法，时间窗口: {time_window_minutes}分钟")
            result = crud_item_sorting.run_sorting_algorithm(db, time_window_minutes)
            logger.info(f"手动排序算法运行完成: {result}")
            return result
        except Exception as e:
            logger.error(f"手动排序算法运行失败: {str(e)}")
            raise e
        finally:
            db.close()

# 全局调度器实例
sorting_scheduler = ItemSortingScheduler()

def start_sorting_scheduler():
    """启动排序调度器"""
    sorting_scheduler.start()

def stop_sorting_scheduler():
    """停止排序调度器"""
    sorting_scheduler.stop()

def run_manual_sorting(time_window_minutes: int = 30):
    """手动运行排序算法"""
    return sorting_scheduler.run_manual_sorting(time_window_minutes)

