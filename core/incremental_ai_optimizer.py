# core/incremental_ai_optimizer.py
# 增量AI特征优化器 - 只处理新增数据，减少大模型计算量

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import asyncio
import aiohttp
import os
import logging
from datetime import datetime
import hashlib
import base64

class IncrementalAIOptimizer:
    """增量AI特征优化器 - 只处理新增数据，减少大模型计算量"""
    
    def __init__(self, ai_provider: str = "xunfei"):
        self.ai_provider = ai_provider
        self.logger = logging.getLogger(__name__)
        
        # AI配置
        self.app_id = os.getenv("XUNFEI_APP_ID")
        self.api_key = os.getenv("XUNFEI_API_KEY")
        self.api_secret = os.getenv("XUNFEI_API_SECRET")
        self.spark_url = os.getenv("XUNFEI_SPARK_URL")
        
        # 请求限制
        self.max_request_size = 1000  # 单次请求最大数据量
        self.request_timeout = 30  # 请求超时时间
        
    async def optimize_incremental_features(self, 
                                          incremental_data: pd.DataFrame,
                                          incremental_users: List[int],
                                          incremental_items: List[int]) -> Dict[str, Any]:
        """优化增量特征矩阵"""
        try:
            self.logger.info(f"开始优化增量特征: 新增用户 {len(incremental_users)}, 新增物品 {len(incremental_items)}")
            
            if len(incremental_data) == 0:
                self.logger.warning("没有增量数据需要优化")
                return {"user_features": None, "item_features": None, "optimization_info": "no_data"}
            
            # 构建增量用户-物品矩阵
            incremental_matrix = self._build_incremental_matrix(incremental_data)
            
            # 准备AI分析数据
            ai_input_data = self._prepare_ai_input(incremental_matrix, incremental_users, incremental_items)
            
            # 调用AI进行特征优化
            ai_optimized_features = await self._call_ai_for_feature_optimization(ai_input_data)
            
            # 解析AI返回的优化特征
            optimized_user_features, optimized_item_features = self._parse_ai_features(ai_optimized_features)
            
            self.logger.info(f"增量特征优化完成: 用户特征 {optimized_user_features.shape if optimized_user_features is not None else 'None'}, 物品特征 {optimized_item_features.shape if optimized_item_features is not None else 'None'}")
            
            return {
                "user_features": optimized_user_features,
                "item_features": optimized_item_features,
                "optimization_info": {
                    "incremental_users": len(incremental_users),
                    "incremental_items": len(incremental_items),
                    "matrix_shape": incremental_matrix.shape,
                    "ai_provider": self.ai_provider,
                    "optimization_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"增量特征优化失败: {e}")
            return {"user_features": None, "item_features": None, "error": str(e)}
    
    def _build_incremental_matrix(self, incremental_data: pd.DataFrame) -> np.ndarray:
        """构建增量用户-物品矩阵"""
        try:
            if len(incremental_data) == 0:
                return np.array([])
            
            # 创建用户-物品评分矩阵
            matrix = incremental_data.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating', 
                fill_value=0.0,
                aggfunc='max'
            )
            
            # 确保矩阵是数值类型
            matrix = matrix.astype(np.float32)
            
            self.logger.info(f"增量矩阵构建完成: {matrix.shape}")
            return matrix.values
            
        except Exception as e:
            self.logger.error(f"构建增量矩阵失败: {e}")
            return np.array([])
    
    def _prepare_ai_input(self, 
                         matrix: np.ndarray, 
                         user_ids: List[int], 
                         item_ids: List[int]) -> Dict[str, Any]:
        """准备AI输入数据"""
        try:
            # 将矩阵转换为可读格式
            matrix_data = []
            for i, user_id in enumerate(user_ids):
                for j, item_id in enumerate(item_ids):
                    if i < matrix.shape[0] and j < matrix.shape[1]:
                        rating = float(matrix[i, j])
                        if rating > 0:  # 只包含有交互的数据
                            matrix_data.append({
                                "user_id": user_id,
                                "item_id": item_id,
                                "rating": rating
                            })
            
            # 限制数据量避免API调用过大
            if len(matrix_data) > self.max_request_size:
                matrix_data = matrix_data[:self.max_request_size]
                self.logger.warning(f"数据量过大，截取前 {self.max_request_size} 条记录")
            
            ai_input = {
                "data_type": "incremental_user_item_matrix",
                "matrix_data": matrix_data,
                "user_ids": user_ids[:50],  # 限制用户ID数量
                "item_ids": item_ids[:50],  # 限制物品ID数量
                "matrix_shape": matrix.shape,
                "optimization_type": "feature_enhancement",
                "request_timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"AI输入数据准备完成: 矩阵数据 {len(matrix_data)} 条, 用户 {len(ai_input['user_ids'])}, 物品 {len(ai_input['item_ids'])}")
            
            return ai_input
            
        except Exception as e:
            self.logger.error(f"准备AI输入数据失败: {e}")
            return {}
    
    async def _call_ai_for_feature_optimization(self, ai_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """调用AI进行特征优化"""
        try:
            # 构建AI提示词
            prompt = self._build_feature_optimization_prompt(ai_input_data)
            
            # 调用AI服务
            if self.ai_provider == "xunfei":
                ai_result = await self._call_xunfei_ai(prompt)
            else:
                raise ValueError(f"不支持的AI提供商: {self.ai_provider}")
            
            # 解析AI返回结果
            optimized_features = self._parse_ai_response(ai_result)
            
            self.logger.info("AI特征优化调用成功")
            return optimized_features
            
        except Exception as e:
            self.logger.error(f"AI特征优化调用失败: {e}")
            return {"error": str(e)}
    
    def _build_feature_optimization_prompt(self, ai_input_data: Dict[str, Any]) -> str:
        """构建特征优化提示词"""
        matrix_data = ai_input_data.get("matrix_data", [])
        user_ids = ai_input_data.get("user_ids", [])
        item_ids = ai_input_data.get("item_ids", [])
        matrix_shape = ai_input_data.get("matrix_shape", (0, 0))
        
        # 构建用户-物品交互数据描述
        interactions_text = "\n".join([
            f"用户 {item['user_id']} 对物品 {item['item_id']} 的评分: {item['rating']}"
            for item in matrix_data[:20]  # 只显示前20条
        ])
        
        prompt = f"""作为一位专业的推荐系统专家，请基于以下增量用户-物品交互数据，生成优化后的用户特征向量和物品特征向量。

增量交互数据（矩阵形状: {matrix_shape}）：
{interactions_text}

用户ID列表: {user_ids[:10]}
物品ID列表: {item_ids[:10]}

请分析这些增量数据，并生成：
1. 用户特征向量：每个用户的偏好特征（如价格敏感度、质量偏好、活跃度等）
2. 物品特征向量：每个物品的特征（如流行度、质量等级、价格区间等）

请以JSON格式返回结果：
{{
    "user_features": {{
        "feature_dimension": 8,
        "features": [
            {{
                "user_id": 用户ID,
                "feature_vector": [特征值1, 特征值2, ..., 特征值8]
            }}
        ]
    }},
    "item_features": {{
        "feature_dimension": 8,
        "features": [
            {{
                "item_id": 物品ID,
                "feature_vector": [特征值1, 特征值2, ..., 特征值8]
            }}
        ]
    }},
    "optimization_insights": "优化说明和特征解释"
}}

重要：
- 特征向量维度固定为8
- 特征值范围在0-1之间
- 只返回输入数据中存在的用户ID和物品ID的特征
- 特征向量应该反映用户的偏好模式和物品的属性特征"""

        return prompt
    
    async def _call_xunfei_ai(self, prompt: str) -> str:
        """调用讯飞AI服务"""
        try:
            if not all([self.app_id, self.api_key, self.api_secret, self.spark_url]):
                raise Exception("讯飞AI配置不完整")
            
            # 这里应该调用实际的讯飞AI API
            # 为了演示，我们返回一个模拟的优化结果
            return self._generate_mock_ai_response()
            
        except Exception as e:
            self.logger.error(f"调用讯飞AI失败: {e}")
            raise e
    
    def _generate_mock_ai_response(self) -> str:
        """生成模拟AI响应（用于演示）"""
        mock_response = {
            "user_features": {
                "feature_dimension": 8,
                "features": [
                    {
                        "user_id": 1,
                        "feature_vector": [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8]
                    },
                    {
                        "user_id": 2,
                        "feature_vector": [0.6, 0.8, 0.5, 0.7, 0.6, 0.9, 0.5, 0.7]
                    }
                ]
            },
            "item_features": {
                "feature_dimension": 8,
                "features": [
                    {
                        "item_id": 1,
                        "feature_vector": [0.7, 0.5, 0.8, 0.6, 0.4, 0.9, 0.7, 0.5]
                    },
                    {
                        "item_id": 2,
                        "feature_vector": [0.5, 0.7, 0.6, 0.8, 0.9, 0.3, 0.6, 0.8]
                    }
                ]
            },
            "optimization_insights": "基于增量数据分析，生成了反映用户偏好和物品属性的特征向量"
        }
        
        return json.dumps(mock_response, ensure_ascii=False)
    
    def _parse_ai_response(self, ai_result: str) -> Dict[str, Any]:
        """解析AI返回结果"""
        try:
            # 尝试从AI返回的文本中提取JSON
            import re
            json_match = re.search(r'\{.*\}', ai_result, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
                return ai_data
            else:
                raise Exception("无法解析AI返回的JSON")
                
        except Exception as e:
            self.logger.error(f"解析AI响应失败: {e}")
            return {"error": str(e)}
    
    def _parse_ai_features(self, ai_optimized_features: Dict[str, Any]) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """解析AI优化的特征向量"""
        try:
            user_features = None
            item_features = None
            
            # 解析用户特征
            if "user_features" in ai_optimized_features:
                user_features_data = ai_optimized_features["user_features"]
                if "features" in user_features_data:
                    user_features_list = user_features_data["features"]
                    if user_features_list:
                        # 构建用户特征矩阵
                        user_ids = [item["user_id"] for item in user_features_list]
                        feature_vectors = [item["feature_vector"] for item in user_features_list]
                        user_features = np.array(feature_vectors, dtype=np.float32)
                        
                        self.logger.info(f"解析用户特征完成: {user_features.shape}")
            
            # 解析物品特征
            if "item_features" in ai_optimized_features:
                item_features_data = ai_optimized_features["item_features"]
                if "features" in item_features_data:
                    item_features_list = item_features_data["features"]
                    if item_features_list:
                        # 构建物品特征矩阵
                        item_ids = [item["item_id"] for item in item_features_list]
                        feature_vectors = [item["feature_vector"] for item in item_features_list]
                        item_features = np.array(feature_vectors, dtype=np.float32)
                        
                        self.logger.info(f"解析物品特征完成: {item_features.shape}")
            
            return user_features, item_features
            
        except Exception as e:
            self.logger.error(f"解析AI特征失败: {e}")
            return None, None
    
    def get_optimization_statistics(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        return {
            "ai_provider": self.ai_provider,
            "max_request_size": self.max_request_size,
            "request_timeout": self.request_timeout,
            "configuration_status": "complete" if all([self.app_id, self.api_key, self.api_secret, self.spark_url]) else "incomplete"
        }

# 全局优化器实例
incremental_ai_optimizer = IncrementalAIOptimizer()



