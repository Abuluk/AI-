"""
定时任务系统
用于定期执行商贩检测任务
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from db.session import SessionLocal
from core.merchant_detection import get_detection_system
from core.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """定时任务调度器"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        
    async def start(self):
        """启动调度器"""
        self.running = True
        logger.info("任务调度器已启动")
        
        # 启动商贩检测任务
        asyncio.create_task(self._merchant_detection_task())
        
    async def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("任务调度器已停止")
        
    async def _merchant_detection_task(self):
        """商贩检测定时任务"""
        while self.running:
            try:
                # 检查是否启用定时检测
                db = SessionLocal()
                try:
                    from crud.crud_merchant_detection import get_detection_config_value
                    schedule_enabled = get_detection_config_value(db, "detection_schedule_enabled", "false")
                    schedule_time = get_detection_config_value(db, "detection_schedule_time", "02:00")
                    
                    if schedule_enabled.lower() == "true":
                        # 解析检测时间
                        hour, minute = map(int, schedule_time.split(":"))
                        
                        # 检查是否到了检测时间
                        now = datetime.now()
                        if now.hour == hour and now.minute < minute + 5:  # 在指定时间前后5分钟内执行
                            await self._run_merchant_detection()
                            # 执行后等待到下一个小时
                            await asyncio.sleep(3600)  # 等待1小时
                        else:
                            # 每分钟检查一次
                            await asyncio.sleep(60)
                    else:
                        # 如果未启用定时检测，等待5分钟再检查
                        await asyncio.sleep(300)
                        
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"商贩检测任务执行失败: {e}")
                await asyncio.sleep(300)  # 出错后等待5分钟再试
    
    async def _run_merchant_detection(self):
        """执行商贩检测"""
        logger.info("开始执行商贩检测任务")
        
        db = SessionLocal()
        try:
            from crud.crud_merchant_detection import get_detection_config_value
            
            # 从数据库配置中获取参数
            top_n = int(get_detection_config_value(db, "monitor_top_n", "50"))
            threshold_items = int(get_detection_config_value(db, "threshold_items", "10"))
            analysis_days = int(get_detection_config_value(db, "analysis_days", "30"))
            
            detection_system = get_detection_system(db)
            
            # 执行检测
            detection_results = await detection_system.detect_merchants(
                top_n=top_n,
                threshold_items=threshold_items,
                analysis_days=analysis_days
            )
            
            logger.info(f"检测到 {len(detection_results)} 个潜在商贩")
            
            # 记录检测结果（检测结果已经在detect_merchants中保存到历史记录）
            self._log_detection_result(detection_results)
            
        except Exception as e:
            logger.error(f"商贩检测执行失败: {e}")
        finally:
            db.close()
    
    def _log_detection_result(self, detection_results: list):
        """记录检测结果"""
        # 这里可以添加详细的日志记录逻辑
        logger.info(f"商贩检测完成: 检测到 {len(detection_results)} 个用户")
        
        # 可以记录到数据库或文件
        for result in detection_results:
            user_id = result["user_id"]
            ai_analysis = result["ai_analysis"]
            logger.info(f"用户 {user_id}: AI判断={'是商贩' if ai_analysis.get('is_merchant') else '非商贩'}, 置信度={ai_analysis.get('confidence', 0)}")


# 全局调度器实例
scheduler = TaskScheduler()


async def start_scheduler():
    """启动调度器"""
    await scheduler.start()


async def stop_scheduler():
    """停止调度器"""
    await scheduler.stop()


# 手动触发检测的函数（用于测试或手动执行）
async def manual_detection(top_n: int = 50, threshold_items: int = 3, analysis_days: int = 30):
    """手动触发商贩检测"""
    logger.info("手动触发商贩检测")
    
    db = SessionLocal()
    try:
        detection_system = get_detection_system(db)
        
        # 执行检测
        detection_results = await detection_system.detect_merchants(
            top_n=top_n,
            threshold_items=threshold_items,
            analysis_days=analysis_days
        )
        
        logger.info(f"检测到 {len(detection_results)} 个潜在商贩")
        
        # 返回检测结果（不自动处理）
        return detection_results
        
    except Exception as e:
        logger.error(f"手动检测失败: {e}")
        return []
    finally:
        db.close()
