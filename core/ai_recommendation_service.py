# core/ai_recommendation_service.py
# AI推荐服务 - 并发处理优化版本

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis
from sqlalchemy.orm import Session
from db.models import User, Item
from crud import crud_user_behavior, crud_ai_recommendation
import traceback
import os

@dataclass
class AIRequest:
    """AI请求数据类"""
    user_id: int
    limit: int
    behavior_sequence: List[Dict[str, Any]]
    available_items: List[Item]
    timestamp: float
    future: asyncio.Future
    priority: int = 1  # 1=高优先级, 2=普通, 3=低优先级

class AIRecommendationService:
    """AI推荐服务 - 支持并发处理、缓存和限流"""
    
    def __init__(self):
        # 并发控制
        self.max_concurrent_requests = 3  # 最大并发AI请求数
        self.current_requests = 0
        self.request_queue = asyncio.PriorityQueue()
        self.processing_requests = {}  # 正在处理的请求
        
        # 缓存配置
        try:
            self.redis_client = redis.Redis(
                host='localhost', 
                port=6379, 
                db=1,  # 使用db1避免与其他数据冲突
                decode_responses=True
            )
            self.redis_available = True
            # 测试连接
            self.redis_client.ping()
        except Exception as e:
            print(f"Redis连接失败，将使用内存缓存: {e}")
            self.redis_available = False
            self.memory_cache = {}
        
        self.cache_ttl = 1800  # 30分钟缓存
        
        # 限流配置
        self.rate_limiter = defaultdict(list)  # {user_id: [timestamp, ...]}
        self.max_requests_per_minute = 3  # 每用户每分钟最多3次请求
        
        # 启动处理任务
        self.worker_task = None
        self.start_worker()
    
    def start_worker(self):
        """启动AI请求处理工作任务"""
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._process_requests())
    
    async def _process_requests(self):
        """处理AI请求队列"""
        while True:
            try:
                # 从队列获取请求
                priority, request = await self.request_queue.get()
                
                if self.current_requests >= self.max_concurrent_requests:
                    # 如果并发数已满，等待
                    await asyncio.sleep(1)
                    # 重新放回队列
                    await self.request_queue.put((priority, request))
                    continue
                
                # 处理请求
                self.current_requests += 1
                try:
                    result = await self._process_single_request(request)
                    request.future.set_result(result)
                except Exception as e:
                    request.future.set_exception(e)
                finally:
                    self.current_requests -= 1
                    
            except Exception as e:
                print(f"处理AI请求队列异常: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_request(self, request: AIRequest) -> Dict[str, Any]:
        """处理单个AI请求"""
        try:
            # 检查缓存
            cache_key = self._get_cache_key(request.user_id, request.behavior_sequence)
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                print(f"用户 {request.user_id} 使用缓存结果")
                return cached_result
            
            # 调用AI分析
            from api.endpoints.ai_strategy import analyze_user_behavior_and_recommend
            
            # 创建临时数据库会话
            from db.session import get_db
            db = next(get_db())
            
            try:
                result = await analyze_user_behavior_and_recommend(
                    db, request.behavior_sequence, 
                    crud_ai_recommendation.get_ai_recommendation_settings(db),
                    request.limit
                )
                
                # 缓存结果
                await self._cache_result(cache_key, result)
                
                return result
            finally:
                db.close()
                
        except Exception as e:
            print(f"处理AI请求失败: {e}")
            traceback.print_exc()
            raise e
    
    def _get_cache_key(self, user_id: int, behavior_sequence: List[Dict[str, Any]]) -> str:
        """生成缓存键"""
        # 基于用户ID和行为序列哈希生成缓存键
        behavior_hash = hashlib.md5(
            json.dumps(behavior_sequence, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        return f"ai_recommend:{user_id}:{behavior_hash}"
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存结果"""
        try:
            if self.redis_available:
                cached_data = self.redis_client.get(cache_key)
                if cached_data:
                    return json.loads(cached_data)
            else:
                # 使用内存缓存
                if cache_key in self.memory_cache:
                    cache_data = self.memory_cache[cache_key]
                    if time.time() - cache_data['timestamp'] < self.cache_ttl:
                        return cache_data['data']
                    else:
                        # 缓存过期，删除
                        del self.memory_cache[cache_key]
            return None
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """缓存结果"""
        try:
            if self.redis_available:
                self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(result, ensure_ascii=False)
                )
            else:
                # 使用内存缓存
                self.memory_cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                # 清理过期缓存
                self._cleanup_memory_cache()
        except Exception as e:
            print(f"缓存结果失败: {e}")
    
    def _cleanup_memory_cache(self):
        """清理过期的内存缓存"""
        if len(self.memory_cache) > 1000:  # 限制缓存大小
            current_time = time.time()
            expired_keys = [
                key for key, value in self.memory_cache.items()
                if current_time - value['timestamp'] > self.cache_ttl
            ]
            for key in expired_keys:
                del self.memory_cache[key]
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """检查用户请求限流"""
        current_time = time.time()
        user_requests = self.rate_limiter[user_id]
        
        # 清除1分钟前的请求记录
        user_requests[:] = [
            req_time for req_time in user_requests 
            if current_time - req_time < 60
        ]
        
        if len(user_requests) >= self.max_requests_per_minute:
            return False
        
        user_requests.append(current_time)
        return True
    
    def _get_request_priority(self, user_id: int, behavior_count: int) -> int:
        """获取请求优先级"""
        # 行为数据越多，优先级越高
        if behavior_count >= 20:
            return 1  # 高优先级
        elif behavior_count >= 10:
            return 2  # 普通优先级
        else:
            return 3  # 低优先级
    
    async def get_ai_recommendations(
        self, 
        db: Session,
        user_id: int, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """获取AI推荐 - 异步并发版本"""
        try:
            # 检查限流
            if not self._check_rate_limit(user_id):
                return {
                    "success": False,
                    "message": "请求过于频繁，请稍后再试",
                    "recommendations": [],
                    "analysis": None,
                    "market_insights": None,
                    "recommendation_type": "rate_limited"
                }
            
            # 获取用户行为数据
            settings = crud_ai_recommendation.get_ai_recommendation_settings(db)
            behavior_sequence = crud_user_behavior.get_user_behavior_sequence(
                db, user_id, 
                limit=settings.get("sequence_length", 10),
                days=settings.get("behavior_days", 30)
            )
            
            # 如果行为数据不足，返回基础推荐
            if len(behavior_sequence) < settings.get("min_behavior_count", 3):
                from api.endpoints.ai_strategy import get_basic_recommendations
                return get_basic_recommendations(db, limit)
            
            # 检查是否有相同的请求正在处理
            request_key = f"{user_id}_{limit}_{len(behavior_sequence)}"
            if request_key in self.processing_requests:
                # 等待正在处理的请求完成
                return await self.processing_requests[request_key]
            
            # 创建AI请求
            future = asyncio.Future()
            priority = self._get_request_priority(user_id, len(behavior_sequence))
            
            # 获取可用商品
            from api.endpoints.ai_strategy import get_available_items_for_ai
            available_items = get_available_items_for_ai(db, settings)
            
            request = AIRequest(
                user_id=user_id,
                limit=limit,
                behavior_sequence=behavior_sequence,
                available_items=available_items,
                timestamp=time.time(),
                future=future,
                priority=priority
            )
            
            # 标记正在处理
            self.processing_requests[request_key] = future
            
            try:
                # 添加到队列
                await self.request_queue.put((priority, request))
                
                # 等待结果，设置超时
                result = await asyncio.wait_for(future, timeout=60.0)
                return result
                
            finally:
                # 移除处理标记
                self.processing_requests.pop(request_key, None)
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "message": "AI分析超时，请稍后重试",
                "recommendations": [],
                "analysis": None,
                "market_insights": None,
                "recommendation_type": "timeout"
            }
        except Exception as e:
            print(f"AI推荐服务异常: {e}")
            traceback.print_exc()
            # 返回基础推荐作为备用
            from api.endpoints.ai_strategy import get_basic_recommendations
            return get_basic_recommendations(db, limit)
    
    def get_service_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "current_requests": self.current_requests,
            "max_concurrent_requests": self.max_concurrent_requests,
            "queue_size": self.request_queue.qsize(),
            "processing_requests": len(self.processing_requests),
            "cache_available": self.redis_available,
            "memory_cache_size": len(self.memory_cache) if not self.redis_available else None
        }

# 全局AI推荐服务实例
ai_recommendation_service = AIRecommendationService()
