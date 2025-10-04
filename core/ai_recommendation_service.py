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
        
        # 缓存配置 - 可配置的缓存时间
        self.cache_ttl = int(os.getenv("AI_CACHE_TTL", "900"))  # 默认15分钟缓存
        self.short_cache_ttl = int(os.getenv("AI_SHORT_CACHE_TTL", "300"))  # 5分钟短缓存
        self.long_cache_ttl = int(os.getenv("AI_LONG_CACHE_TTL", "1800"))  # 30分钟长缓存
        
        # 冷却期配置 - 防止频繁调用AI
        self.cooldown_ttl = int(os.getenv("AI_COOLDOWN_TTL", "300"))  # 默认5分钟冷却期
        
        # 限流配置
        self.rate_limiter = defaultdict(list)  # {user_id: [timestamp, ...]}
        self.max_requests_per_minute = 3  # 每用户每分钟最多3次请求
        
        # 启动处理任务
        self.worker_task = None
        # 延迟启动，避免在模块导入时创建事件循环
        self._worker_started = False
    
    def start_worker(self):
        """启动AI请求处理工作任务"""
        if not self._worker_started and (self.worker_task is None or self.worker_task.done()):
            try:
                self.worker_task = asyncio.create_task(self._process_requests())
                self._worker_started = True
            except RuntimeError:
                # 如果没有运行的事件循环，延迟启动
                pass
    
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
            cache_key = self._get_cache_key(request.user_id, request.behavior_sequence, request.limit)
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                print(f"用户 {request.user_id} 使用缓存结果 (行为数据: {len(request.behavior_sequence)}条)")
                return cached_result
            
            # 检查是否在冷却期内（防止频繁调用AI）
            cooldown_key = f"cooldown:{request.user_id}:{request.limit}"
            cooldown_result = await self._get_cached_result(cooldown_key)
            if cooldown_result:
                print(f"用户 {request.user_id} 在冷却期内，返回基础推荐")
                return self._get_basic_recommendations(request.available_items, request.limit)
            
            # 直接调用AI分析，不通过ai_strategy模块
            result = await self._analyze_user_behavior_and_recommend(
                request.behavior_sequence, 
                request.available_items,
                    request.limit
                )
                
            # 根据行为数据量确定缓存时间
            cache_ttl = self._get_cache_ttl(len(request.behavior_sequence))
            await self._cache_result(cache_key, result, cache_ttl)
            
            # 设置冷却期（固定时间，防止频繁更新）
            cooldown_ttl = min(cache_ttl, self.cooldown_ttl)  # 使用配置的冷却期时间
            await self._cache_result(cooldown_key, {"cooldown": True}, cooldown_ttl)
            
            print(f"用户 {request.user_id} AI分析完成，已缓存 {cache_ttl}秒，冷却期 {cooldown_ttl}秒")
            return result
                
        except Exception as e:
            print(f"处理AI请求失败: {e}")
            traceback.print_exc()
            raise e
    
    async def _analyze_user_behavior_and_recommend(
        self, 
        behavior_sequence: List[Dict[str, Any]], 
        available_items: List[Item],
        limit: int
    ) -> Dict[str, Any]:
        """基于用户行为序列进行AI分析推荐"""
        try:
            # 构建AI分析prompt - 只包含有效的商品浏览行为
            valid_behaviors = []
            for item in behavior_sequence[:10]:
                # 只包含有关联商品的行为，或者分类点击行为
                if item['item_id'] is not None or item['behavior_type'] == 'category_click':
                    if item['behavior_type'] == 'category_click' and item.get('behavior_data', {}).get('category_name'):
                        # 分类点击行为，使用分类名称
                        valid_behaviors.append(f"- 浏览了分类: {item['behavior_data']['category_name']} (行为: {item['behavior_type']})")
                    elif item['item_id'] is not None:
                        # 商品浏览行为
                        valid_behaviors.append(f"- {item['title']} (成色: {item['condition']}, 行为: {item['behavior_type']})")
            
            sequence_text = "\n".join(valid_behaviors) if valid_behaviors else "用户暂无有效的浏览行为记录"
            
            # 传给AI的商品信息，包含ID、标题和成色
            items_text = "\n".join([
                f"- ID:{item.id} {item.title} (成色: {item.condition})"
                for item in available_items
            ])
            
            prompt = f"""作为一位专业的商品推荐专家，请基于用户的浏览行为序列，从当前在售商品中推荐最合适的商品。

用户浏览行为序列（按时间倒序）：
{sequence_text}

当前在售商品（部分）：
{items_text}

请分析用户的兴趣偏好，包括：
1. 偏好的商品分类（基于分类点击行为）
2. 商品成色偏好
3. 浏览模式分析

然后从在售商品中选择{limit}个最符合用户偏好的商品进行推荐。

请以JSON格式返回结果：
{{
    "analysis": "用户偏好分析（100字以内）",
    "market_insights": "市场洞察和建议（50字以内）",
    "recommendations": [
        {{
            "item_id": 商品ID（必须是上面列表中的ID数字）,
            "reason": "推荐理由（20字以内）"
        }}
    ]
}}

重要：请确保推荐的商品ID必须是上面商品列表中显示的ID数字。"""

            # 调用AI分析
            app_id = os.getenv("XUNFEI_APP_ID")
            api_key = os.getenv("XUNFEI_API_KEY")
            api_secret = os.getenv("XUNFEI_API_SECRET")
            spark_url = os.getenv("XUNFEI_SPARK_URL")
            
            if not all([app_id, api_key, api_secret, spark_url]):
                raise Exception("AI配置不完整")
            
            # 调用讯飞AI
            from api.endpoints.ai_strategy import call_xunfei_v3_chat_async
            ai_result = await call_xunfei_v3_chat_async(app_id, api_key, api_secret, spark_url, prompt)
            
            # 解析AI返回结果
            try:
                # 尝试从AI返回的文本中提取JSON
                import re
                json_match = re.search(r'\{.*\}', ai_result, re.DOTALL)
                if json_match:
                    ai_data = json.loads(json_match.group())
                else:
                    raise Exception("无法解析AI返回的JSON")
            except:
                # 如果解析失败，返回基础推荐
                return self._get_basic_recommendations(available_items, limit)
            
            # 获取推荐的商品详情
            recommended_items = []
            for rec in ai_data.get("recommendations", []):
                item_id = rec.get("item_id")
                if item_id:
                    # 尝试将字符串ID转换为整数
                    try:
                        item_id = int(item_id)
                    except (ValueError, TypeError):
                        # 如果转换失败，尝试通过商品名称查找
                        item_name = str(item_id)
                        item = next((item for item in available_items if item.title == item_name), None)
                        if not item:
                            continue
                    else:
                        item = next((item for item in available_items if item.id == item_id), None)
                    
                    if item:
                        # 处理图片路径
                        processed_images = []
                        if item.images:
                            images = item.images.split(',')
                            for img in images:
                                img = img.strip()
                                if img:
                                    from config import get_full_image_url
                                    full_url = get_full_image_url(img)
                                    if full_url:
                                        processed_images.append(full_url)
                        
                        recommended_items.append({
                            "id": item.id,
                            "title": item.title,
                            "description": item.description,
                            "price": item.price,
                            "category": item.category,
                            "condition": item.condition,
                            "location": item.location,
                            "like_count": item.like_count,
                            "views": item.views,
                            "created_at": item.created_at.isoformat() if item.created_at else None,
                            "image_urls": processed_images,
                            "ai_reason": rec.get("reason", "AI智能推荐")
                        })
            
            return {
                "success": True,
                "recommendations": recommended_items,
                "analysis": ai_data.get("analysis", "基于您的浏览行为进行智能推荐"),
                "market_insights": ai_data.get("market_insights", "为您推荐最符合偏好的商品"),
                "recommendation_type": "ai_behavior_based"
            }
            
        except Exception as e:
            print(f"AI行为分析推荐失败: {e}")
            traceback.print_exc()
            return self._get_basic_recommendations(available_items, limit)
    
    def _get_basic_recommendations(self, available_items: List[Item], limit: int) -> Dict[str, Any]:
        """获取基础推荐商品（热门商品）"""
        try:
            # 按浏览量和点赞数排序
            sorted_items = sorted(available_items, key=lambda x: (x.views, x.like_count), reverse=True)
            recommended_items = sorted_items[:limit]
            
            # 转换为字典格式
            result = []
            for item in recommended_items:
                # 处理图片路径
                processed_images = []
                if item.images:
                    images = item.images.split(',')
                    for img in images:
                        img = img.strip()
                        if img:
                            from config import get_full_image_url
                            full_url = get_full_image_url(img)
                            if full_url:
                                processed_images.append(full_url)
                
                result.append({
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "price": item.price,
                    "category": item.category,
                    "condition": item.condition,
                    "location": item.location,
                    "like_count": item.like_count,
                    "views": item.views,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "image_urls": processed_images,
                    "ai_reason": "热门商品推荐"
                })
            
            return {
                "success": True,
                "recommendations": result,
                "analysis": "基于热门商品的基础推荐",
                "market_insights": "为您推荐当前最受欢迎的商品",
                "recommendation_type": "basic"
            }
            
        except Exception as e:
            print(f"获取基础推荐失败: {e}")
            return {
                "success": False,
                "recommendations": [],
                "analysis": None,
                "market_insights": None,
                "message": "推荐服务暂时不可用",
                "recommendation_type": "fallback"
            }
    
    def _get_available_items_for_ai(self, db: Session, settings: Dict[str, Any]) -> List[Item]:
        """根据配置获取AI推荐可用的商品"""
        try:
            item_selection = settings.get("item_selection", {})
            if not item_selection.get("enable_sort_filter", True) and not item_selection.get("enable_category_filter", True):
                # 如果都不启用，返回所有在售商品
                return db.query(Item).filter(
                    Item.status == "online",
                    Item.sold == False
                ).limit(item_selection.get("max_total_items", 100)).all()
            
            all_items = []
            used_item_ids = set()
            
            # 按排序方式获取商品
            if item_selection.get("enable_sort_filter", True):
                sort_orders = item_selection.get("sort_orders", [])
                for sort_config in sort_orders:
                    if not sort_config.get("enabled", True):
                        continue
                    
                    field = sort_config.get("field", "price")
                    order = sort_config.get("order", "asc")
                    limit = sort_config.get("limit", 20)
                    
                    # 构建排序查询
                    if order == "desc":
                        order_func = getattr(Item, field).desc()
                    else:
                        order_func = getattr(Item, field).asc()
                    
                    items = db.query(Item).filter(
                        Item.status == "online",
                        Item.sold == False
                    ).order_by(order_func).limit(limit).all()
                    
                    # 添加未重复的商品
                    for item in items:
                        if item.id not in used_item_ids:
                            all_items.append(item)
                            used_item_ids.add(item.id)
            
            # 按分类获取商品
            if item_selection.get("enable_category_filter", True):
                category_limits = item_selection.get("category_limits", {})
                for category_id, category_config in category_limits.items():
                    if not category_config.get("enabled", True):
                        continue
                    
                    limit = category_config.get("limit", 10)
                    items = db.query(Item).filter(
                        Item.status == "online",
                        Item.sold == False,
                        Item.category == int(category_id)
                    ).order_by(Item.created_at.desc()).limit(limit).all()
                    
                    # 添加未重复的商品
                    for item in items:
                        if item.id not in used_item_ids:
                            all_items.append(item)
                            used_item_ids.add(item.id)
            
            # 限制总数量
            max_total = item_selection.get("max_total_items", 100)
            return all_items[:max_total]
            
        except Exception as e:
            print(f"获取商品选择范围失败: {e}")
            # 出错时返回默认商品
            return db.query(Item).filter(
                Item.status == "online",
                Item.sold == False
            ).limit(100).all()
    
    def _get_cache_key(self, user_id: int, behavior_sequence: List[Dict[str, Any]], limit: int = 10) -> str:
        """生成缓存键 - 基于用户ID和推荐数量，不包含行为内容"""
        # 简化的缓存键：只基于用户ID和推荐数量
        # 这样在固定时间内，相同用户和推荐数量的请求都会使用同一个缓存
        return f"ai_recommend:{user_id}:{limit}"
    
    def _get_cache_ttl(self, behavior_count: int) -> int:
        """根据行为数据量确定缓存时间"""
        if behavior_count >= 15:
            return self.long_cache_ttl  # 行为数据丰富，使用长缓存
        elif behavior_count >= 5:
            return self.cache_ttl  # 行为数据中等，使用标准缓存
        else:
            return self.short_cache_ttl  # 行为数据较少，使用短缓存
    
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
                    ttl = cache_data.get('ttl', self.cache_ttl)
                    if time.time() - cache_data['timestamp'] < ttl:
                        return cache_data['data']
                    else:
                        # 缓存过期，删除
                        del self.memory_cache[cache_key]
            return None
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int = None):
        """缓存结果"""
        try:
            if ttl is None:
                ttl = self.cache_ttl
                
            if self.redis_available:
                self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(result, ensure_ascii=False)
                )
            else:
                # 使用内存缓存
                self.memory_cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time(),
                    'ttl': ttl
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
                if current_time - value['timestamp'] > value.get('ttl', self.cache_ttl)
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
            # 确保worker已启动
            if not self._worker_started:
                self.start_worker()
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
                print(f"用户 {user_id} 行为数据不足 ({len(behavior_sequence)}条 < {settings.get('min_behavior_count', 3)}条)，返回基础推荐")
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
            available_items = self._get_available_items_for_ai(db, settings)
            
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
            "memory_cache_size": len(self.memory_cache) if not self.redis_available else None,
            "cache_config": {
                "default_ttl": self.cache_ttl,
                "short_ttl": self.short_cache_ttl,
                "long_ttl": self.long_cache_ttl
            }
        }
    
    def clear_cache(self, user_id: int = None) -> Dict[str, Any]:
        """清理缓存"""
        try:
            if self.redis_available:
                if user_id:
                    # 清理特定用户的缓存
                    pattern = f"ai_recommend:{user_id}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        return {"success": True, "message": f"已清理用户 {user_id} 的 {len(keys)} 个缓存", "cleared_count": len(keys)}
                    else:
                        return {"success": True, "message": f"用户 {user_id} 没有缓存数据", "cleared_count": 0}
                else:
                    # 清理所有AI推荐缓存
                    pattern = "ai_recommend:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        return {"success": True, "message": f"已清理所有 {len(keys)} 个AI推荐缓存", "cleared_count": len(keys)}
                    else:
                        return {"success": True, "message": "没有AI推荐缓存数据", "cleared_count": 0}
            else:
                # 清理内存缓存
                if user_id:
                    # 清理特定用户的缓存
                    pattern = f"ai_recommend:{user_id}:"
                    keys_to_remove = [key for key in self.memory_cache.keys() if key.startswith(pattern)]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                    return {"success": True, "message": f"已清理用户 {user_id} 的 {len(keys_to_remove)} 个缓存", "cleared_count": len(keys_to_remove)}
                else:
                    # 清理所有AI推荐缓存
                    keys_to_remove = [key for key in self.memory_cache.keys() if key.startswith("ai_recommend:")]
                    for key in keys_to_remove:
                        del self.memory_cache[key]
                    return {"success": True, "message": f"已清理所有 {len(keys_to_remove)} 个AI推荐缓存", "cleared_count": len(keys_to_remove)}
        except Exception as e:
            return {"success": False, "message": f"清理缓存失败: {str(e)}", "cleared_count": 0}
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            if self.redis_available:
                pattern = "ai_recommend:*"
                keys = self.redis_client.keys(pattern)
                return {
                    "cache_type": "redis",
                    "total_keys": len(keys),
                    "keys": keys[:10] if keys else [],  # 只显示前10个键
                    "sample_keys_count": min(10, len(keys))
                }
            else:
                keys = [key for key in self.memory_cache.keys() if key.startswith("ai_recommend:")]
                return {
                    "cache_type": "memory",
                    "total_keys": len(keys),
                    "keys": keys[:10] if keys else [],  # 只显示前10个键
                    "sample_keys_count": min(10, len(keys))
                }
        except Exception as e:
            return {"cache_type": "error", "error": str(e)}

# 全局AI推荐服务实例
ai_recommendation_service = AIRecommendationService()
