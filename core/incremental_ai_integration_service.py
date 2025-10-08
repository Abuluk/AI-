# core/incremental_ai_integration_service.py
# 增量AI集成服务 - 统一管理AI特征优化和推荐生成

import asyncio
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from core.ai_feature_cache import AIFeatureCache
from core.incremental_ai_optimizer import IncrementalAIOptimizer

class IncrementalAIIntegrationService:
    """增量AI集成服务 - 统一管理AI特征优化和推荐生成"""
    
    def __init__(self, cache_dir: str = "/data/cache/ai_features"):
        self.cache = AIFeatureCache(cache_dir)
        self.ai_optimizer = IncrementalAIOptimizer()
        
        # 日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 服务状态
        self.is_initialized = False
        self.last_update_time = None
        self.total_optimizations = 0
        
    async def initialize(self):
        """初始化服务"""
        try:
            self.logger.info("初始化增量AI集成服务...")
            
            # 检查缓存状态
            cache_stats = self.cache.get_feature_statistics()
            self.logger.info(f"缓存状态: {cache_stats['cache_status']}")
            
            # 检查AI优化器状态
            optimizer_stats = self.ai_optimizer.get_optimization_statistics()
            self.logger.info(f"AI优化器状态: {optimizer_stats['configuration_status']}")
            
            self.is_initialized = True
            self.logger.info("增量AI集成服务初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化服务失败: {e}")
            raise e
    
    async def process_incremental_data(self, new_behavior_data: pd.DataFrame) -> Dict[str, Any]:
        """处理增量数据 - 主要入口函数"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.logger.info(f"开始处理增量数据: {len(new_behavior_data)} 条记录")
            
            # 1. 获取增量数据
            incremental_data, incremental_users, incremental_items = self.cache.get_incremental_data(new_behavior_data)
            
            if len(incremental_data) == 0:
                self.logger.info("没有增量数据需要处理")
                return {
                    "status": "no_incremental_data",
                    "message": "没有新的用户或物品数据需要处理",
                    "processed_records": 0
                }
            
            # 2. 调用AI优化增量特征
            ai_optimization_result = await self.ai_optimizer.optimize_incremental_features(
                incremental_data, incremental_users, incremental_items
            )
            
            if "error" in ai_optimization_result:
                self.logger.error(f"AI优化失败: {ai_optimization_result['error']}")
                return {
                    "status": "ai_optimization_failed",
                    "error": ai_optimization_result["error"],
                    "processed_records": len(incremental_data)
                }
            
            # 3. 更新特征矩阵缓存
            user_features = ai_optimization_result.get("user_features")
            item_features = ai_optimization_result.get("item_features")
            
            if user_features is not None and item_features is not None:
                self.cache.update_features(
                    user_features, item_features, incremental_users, incremental_items
                )
                
                self.total_optimizations += 1
                self.last_update_time = datetime.now()
                
                self.logger.info(f"增量特征优化完成: 用户特征 {user_features.shape}, 物品特征 {item_features.shape}")
                
                return {
                    "status": "success",
                    "message": "增量特征优化完成",
                    "processed_records": len(incremental_data),
                    "incremental_users": len(incremental_users),
                    "incremental_items": len(incremental_items),
                    "user_features_shape": user_features.shape,
                    "item_features_shape": item_features.shape,
                    "optimization_timestamp": datetime.now().isoformat()
                }
            else:
                self.logger.warning("AI优化返回的特征为空")
                return {
                    "status": "empty_features",
                    "message": "AI优化返回的特征为空",
                    "processed_records": len(incremental_data)
                }
                
        except Exception as e:
            self.logger.error(f"处理增量数据失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processed_records": 0
            }
    
    async def get_optimized_recommendations(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """获取基于AI优化特征的推荐结果"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # 获取用户特征
            user_features = self.cache.user_features_matrix
            if user_features is None:
                return {
                    "status": "no_features",
                    "message": "用户特征矩阵不存在",
                    "recommendations": []
                }
            
            # 检查用户ID是否在特征矩阵中
            if user_id >= user_features.shape[0]:
                return {
                    "status": "user_not_found",
                    "message": f"用户 {user_id} 不在特征矩阵中",
                    "recommendations": []
                }
            
            # 获取用户特征向量
            user_feature_vector = user_features[user_id]
            
            # 获取物品特征
            item_features = self.cache.item_features_matrix
            if item_features is None:
                return {
                    "status": "no_item_features",
                    "message": "物品特征矩阵不存在",
                    "recommendations": []
                }
            
            # 计算用户与所有物品的相似度
            similarities = []
            for item_id in range(item_features.shape[0]):
                item_feature_vector = item_features[item_id]
                similarity = self._calculate_cosine_similarity(user_feature_vector, item_feature_vector)
                similarities.append((item_id, similarity))
            
            # 排序并获取top推荐
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_recommendations = similarities[:limit]
            
            recommendations = [
                {
                    "item_id": item_id,
                    "score": float(similarity),
                    "algorithm": "ai_enhanced_incremental",
                    "feature_based": True
                }
                for item_id, similarity in top_recommendations
            ]
            
            return {
                "status": "success",
                "user_id": user_id,
                "recommendations": recommendations,
                "total_items": item_features.shape[0],
                "algorithm": "ai_enhanced_incremental",
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取推荐结果失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "recommendations": []
            }
    
    def _calculate_cosine_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """计算余弦相似度"""
        try:
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            self.logger.error(f"计算余弦相似度失败: {e}")
            return 0.0
    
    async def batch_process_recommendations(self, user_ids: List[int], limit: int = 10) -> Dict[str, Any]:
        """批量处理推荐请求"""
        try:
            self.logger.info(f"批量处理推荐请求: {len(user_ids)} 个用户")
            
            results = {}
            for user_id in user_ids:
                result = await self.get_optimized_recommendations(user_id, limit)
                results[str(user_id)] = result
            
            return {
                "status": "success",
                "total_users": len(user_ids),
                "results": results,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"批量处理推荐失败: {e}")
            return {
                "status": "error",
                "error": str(e),
                "results": {}
            }
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        try:
            cache_stats = self.cache.get_feature_statistics()
            optimizer_stats = self.ai_optimizer.get_optimization_statistics()
            
            return {
                "service_status": "active" if self.is_initialized else "inactive",
                "last_update_time": self.last_update_time.isoformat() if self.last_update_time else None,
                "total_optimizations": self.total_optimizations,
                "cache_statistics": cache_stats,
                "optimizer_statistics": optimizer_stats,
                "feature_matrices": {
                    "user_features_shape": self.cache.user_features_matrix.shape if self.cache.user_features_matrix is not None else None,
                    "item_features_shape": self.cache.item_features_matrix.shape if self.cache.item_features_matrix is not None else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取服务统计信息失败: {e}")
            return {
                "service_status": "error",
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            health_status = {
                "service": "healthy" if self.is_initialized else "unhealthy",
                "cache": "healthy" if self.cache.user_features_matrix is not None else "empty",
                "ai_optimizer": "healthy" if self.ai_optimizer.get_optimization_statistics()["configuration_status"] == "complete" else "incomplete",
                "timestamp": datetime.now().isoformat()
            }
            
            # 检查特征矩阵质量
            if self.cache.user_features_matrix is not None:
                user_matrix = self.cache.user_features_matrix
                health_status["user_features_quality"] = {
                    "shape": user_matrix.shape,
                    "has_nan": bool(np.isnan(user_matrix).any()),
                    "has_inf": bool(np.isinf(user_matrix).any()),
                    "mean": float(np.mean(user_matrix)),
                    "std": float(np.std(user_matrix))
                }
            
            if self.cache.item_features_matrix is not None:
                item_matrix = self.cache.item_features_matrix
                health_status["item_features_quality"] = {
                    "shape": item_matrix.shape,
                    "has_nan": bool(np.isnan(item_matrix).any()),
                    "has_inf": bool(np.isinf(item_matrix).any()),
                    "mean": float(np.mean(item_matrix)),
                    "std": float(np.std(item_matrix))
                }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                "service": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def clear_cache_and_reset(self):
        """清空缓存并重置服务"""
        try:
            self.logger.info("清空缓存并重置服务...")
            
            self.cache.clear_cache()
            self.is_initialized = False
            self.last_update_time = None
            self.total_optimizations = 0
            
            self.logger.info("缓存清空和服务重置完成")
            
        except Exception as e:
            self.logger.error(f"清空缓存和重置服务失败: {e}")
            raise e

# 全局服务实例
incremental_ai_service = IncrementalAIIntegrationService()

# 命令行接口
async def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("用法: python incremental_ai_integration_service.py <command> [args...]")
        print("命令:")
        print("  health_check                    - 健康检查")
        print("  statistics                      - 获取统计信息")
        print("  process_data <json_data>        - 处理增量数据")
        print("  get_recommendations <user_id>   - 获取推荐结果")
        print("  batch_recommendations <user_ids> - 批量获取推荐结果")
        print("  clear_cache                     - 清空缓存")
        return
    
    command = sys.argv[1]
    
    try:
        await incremental_ai_service.initialize()
        
        if command == "health_check":
            result = await incremental_ai_service.health_check()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "statistics":
            result = incremental_ai_service.get_service_statistics()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "process_data":
            if len(sys.argv) < 3:
                print("错误: 需要提供JSON数据")
                return
            
            json_data = sys.argv[2]
            data = json.loads(json_data)
            df = pd.DataFrame(data)
            
            result = await incremental_ai_service.process_incremental_data(df)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "get_recommendations":
            if len(sys.argv) < 3:
                print("错误: 需要提供用户ID")
                return
            
            user_id = int(sys.argv[2])
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            
            result = await incremental_ai_service.get_optimized_recommendations(user_id, limit)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "batch_recommendations":
            if len(sys.argv) < 3:
                print("错误: 需要提供用户ID列表")
                return
            
            user_ids = json.loads(sys.argv[2])
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            
            result = await incremental_ai_service.batch_process_recommendations(user_ids, limit)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif command == "clear_cache":
            await incremental_ai_service.clear_cache_and_reset()
            print("缓存已清空，服务已重置")
            
        else:
            print(f"未知命令: {command}")
            
    except Exception as e:
        print(f"执行命令失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())



