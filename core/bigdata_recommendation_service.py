# 大数据推荐服务
import requests
import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from db.models import Item
from config import get_full_image_url

class BigDataRecommendationService:
    """大数据推荐服务 - 集成Hadoop推荐系统"""
    
    def __init__(self, hadoop_ip="192.168.174.128", hadoop_port=8080):
        self.hadoop_base_url = f"http://{hadoop_ip}:{hadoop_port}"
        self.cache = {}  # 简单的内存缓存
        self.cache_ttl = 1200  # 缓存20分钟（大数据推荐相对稳定）
    
    def get_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """获取大数据推荐结果"""
        try:
            # 检查缓存
            cache_key = f"recommendations_{user_id}_{limit}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    print(f"使用缓存的大数据推荐: user_id={user_id}")
                    return cached_data
            
            # 请求Hadoop推荐API
            response = requests.get(
                f"{self.hadoop_base_url}/recommendations/{user_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"大数据推荐成功: user_id={user_id}, 推荐数量={len(result.get('recommendations', []))}")
                
                # 缓存结果
                self.cache[cache_key] = (result, time.time())
                print(f"大数据推荐结果已缓存: user_id={user_id}, 缓存时间={self.cache_ttl}秒")
                
                # 清理过期缓存
                self._cleanup_cache()
                return result
            else:
                print(f"大数据推荐失败: user_id={user_id}, 状态码={response.status_code}")
                return {"error": f"推荐服务错误: {response.status_code}"}
                
        except requests.exceptions.Timeout:
            print(f"大数据推荐超时: user_id={user_id}")
            return {"error": "推荐服务超时"}
        except requests.exceptions.ConnectionError:
            print(f"大数据推荐连接失败: user_id={user_id}")
            return {"error": "推荐服务不可用"}
        except Exception as e:
            print(f"大数据推荐异常: user_id={user_id}, 错误={e}")
            return {"error": f"推荐服务异常: {str(e)}"}
    
    def get_recommended_items(self, db: Session, user_id: int, limit: int = 10) -> List[Item]:
        """获取推荐的商品对象列表"""
        try:
            # 获取推荐结果
            recommendation_result = self.get_recommendations(user_id, limit)
            
            if "error" in recommendation_result:
                print(f"获取推荐失败: {recommendation_result['error']}")
                return []
            
            # 提取推荐的商品ID
            recommended_ids = recommendation_result.get("recommendations", [])
            if not recommended_ids:
                print(f"用户 {user_id} 没有推荐商品")
                return []
            
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
            
            print(f"成功获取 {len(sorted_items)} 个推荐商品")
            return sorted_items
            
        except Exception as e:
            print(f"获取推荐商品失败: {e}")
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
            print(f"清理了 {len(expired_keys)} 个过期的大数据推荐缓存")
    
    def test_connection(self) -> bool:
        """测试与Hadoop服务的连接"""
        try:
            response = requests.get(f"{self.hadoop_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

# 创建全局实例
bigdata_recommendation_service = BigDataRecommendationService()
