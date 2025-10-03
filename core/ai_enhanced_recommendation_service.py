# AI增强推荐服务
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from db.models import Item
from config import get_full_image_url
from core.clients.ai_hadoop_client import AIHadoopClient

class AIEnhancedRecommendationService:
    """AI增强推荐服务 - 使用AIHadoopClient获取Hadoop端的AI增强推荐数据"""
    
    def __init__(self, vm_ip="192.168.174.128", api_port=8080):
        # 使用AIHadoopClient获取推荐数据
        self.ai_client = AIHadoopClient(vm_ip, api_port)
        
        # 添加缓存机制
        self.cache = {}  # 推荐结果缓存
        self.cache_ttl = 1800  # 缓存30分钟（AI推荐更新频率较低）
    
    def get_ai_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """获取AI增强推荐结果 - 带缓存机制"""
        try:
            # 检查缓存
            cache_key = f"ai_recommendations_{user_id}_{limit}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    print(f"使用缓存的AI增强推荐: user_id={user_id}")
                    return cached_data
                else:
                    # 缓存过期，删除
                    del self.cache[cache_key]
            
            # 从AI客户端获取新的推荐结果
            result = self.ai_client.get_ai_recommendations(user_id, limit)
            
            # 只缓存成功的结果（不缓存错误）
            if "error" not in result:
                self.cache[cache_key] = (result, time.time())
                print(f"AI增强推荐结果已缓存: user_id={user_id}, 缓存时间={self.cache_ttl}秒")
                
                # 清理过期缓存
                self._cleanup_cache()
            
            return result
            
        except Exception as e:
            print(f"获取AI增强推荐失败: {e}")
            return {"error": f"获取AI增强推荐失败: {str(e)}"}
    
    def get_recommended_items(self, db: Session, user_id: int, limit: int = 10) -> List[Item]:
        """获取AI增强推荐的商品对象列表"""
        try:
            # 获取AI增强推荐结果
            recommendation_result = self.get_ai_recommendations(user_id, limit)
            
            if "error" in recommendation_result:
                print(f"获取AI增强推荐失败: {recommendation_result['error']}")
                return []
            
            # 提取推荐的商品ID - 处理AI推荐服务的实际返回格式
            recommended_ids = []
            
            # 直接检查 recommendations 字段（这是AI推荐服务实际返回的格式）
            if "recommendations" in recommendation_result:
                recommendations = recommendation_result["recommendations"]
                if isinstance(recommendations, list):
                    # 格式: {"recommendations": [151, 146, 167]} - 这是实际的API返回格式
                    try:
                        recommended_ids = [int(x) for x in recommendations]
                        print(f"成功解析AI推荐商品ID: {recommended_ids}")
                    except Exception as e:
                        print(f"解析推荐商品ID失败: {e}")
                        
            # 备用：检查其他可能的格式
            if not recommended_ids and "detailed_scores" in recommendation_result:
                try:
                    recommended_ids = [int(score["item_id"]) for score in recommendation_result["detailed_scores"]]
                    print(f"从detailed_scores提取商品ID: {recommended_ids}")
                except Exception as e:
                    print(f"从detailed_scores提取商品ID失败: {e}")
            
            if not recommended_ids:
                print(f"用户 {user_id} 没有AI增强推荐商品")
                return []
            
            # 限制推荐数量
            recommended_ids = recommended_ids[:limit]
            
            # 从数据库获取商品详情
            items = db.query(Item).filter(
                Item.id.in_(recommended_ids),
                Item.status == "online",
                Item.sold == False
            ).all()
            
            # 按推荐顺序排序
            item_dict = {item.id: item for item in items}
            sorted_items = []
            for item_id in recommended_ids:
                if item_id in item_dict:
                    sorted_items.append(item_dict[item_id])
            
            print(f"成功获取 {len(sorted_items)} 个AI增强推荐商品")
            return sorted_items
            
        except Exception as e:
            print(f"获取AI增强推荐商品失败: {e}")
            return []
    
    def _cleanup_cache(self):
        """清理过期的缓存"""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, (cached_data, timestamp) in self.cache.items():
            if current_time - timestamp >= self.cache_ttl:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"清理了 {len(expired_keys)} 个过期的AI增强推荐缓存")
    
    def test_connection(self) -> bool:
        """测试与AI推荐服务的连接 - 直接调用AIHadoopClient"""
        return self.ai_client.test_connection()

# 创建全局实例
ai_enhanced_recommendation_service = AIEnhancedRecommendationService()
