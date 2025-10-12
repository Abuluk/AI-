# core/ai_feature_cache.py
# AI特征矩阵缓存系统 - 支持增量更新和矩阵合并

import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
import hashlib
from pathlib import Path
import logging

class AIFeatureCache:
    """AI特征矩阵缓存系统 - 支持增量更新和矩阵合并"""
    
    def __init__(self, cache_dir: str = "/data/cache/ai_features"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 缓存文件路径
        self.user_features_file = self.cache_dir / "user_features_matrix.pkl"
        self.item_features_file = self.cache_dir / "item_features_matrix.pkl"
        self.metadata_file = self.cache_dir / "feature_metadata.json"
        self.incremental_file = self.cache_dir / "incremental_features.pkl"
        
        # 日志配置
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 加载现有缓存
        self.metadata = self._load_metadata()
        self.user_features_matrix = self._load_user_features()
        self.item_features_matrix = self._load_item_features()
        
    def _load_metadata(self) -> Dict[str, Any]:
        """加载特征元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"加载元数据失败: {e}")
        
        return {
            "last_update": None,
            "user_count": 0,
            "item_count": 0,
            "feature_dimension": 0,
            "ai_model_version": "bailian-ai-enhanced-v2.0",
            "total_updates": 0,
            "last_incremental_update": None
        }
    
    def _load_user_features(self) -> Optional[np.ndarray]:
        """加载用户特征矩阵"""
        if self.user_features_file.exists():
            try:
                with open(self.user_features_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                self.logger.warning(f"加载用户特征矩阵失败: {e}")
        return None
    
    def _load_item_features(self) -> Optional[np.ndarray]:
        """加载物品特征矩阵"""
        if self.item_features_file.exists():
            try:
                with open(self.item_features_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                self.logger.warning(f"加载物品特征矩阵失败: {e}")
        return None
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存元数据失败: {e}")
    
    def _save_user_features(self, matrix: np.ndarray):
        """保存用户特征矩阵"""
        try:
            with open(self.user_features_file, 'wb') as f:
                pickle.dump(matrix, f)
            self.logger.info(f"用户特征矩阵已保存: {matrix.shape}")
        except Exception as e:
            self.logger.error(f"保存用户特征矩阵失败: {e}")
    
    def _save_item_features(self, matrix: np.ndarray):
        """保存物品特征矩阵"""
        try:
            with open(self.item_features_file, 'wb') as f:
                pickle.dump(matrix, f)
            self.logger.info(f"物品特征矩阵已保存: {matrix.shape}")
        except Exception as e:
            self.logger.error(f"保存物品特征矩阵失败: {e}")
    
    def get_incremental_data(self, new_user_behaviors: pd.DataFrame) -> Tuple[pd.DataFrame, List[int], List[int]]:
        """获取增量数据 - 只返回新增的用户和物品数据"""
        try:
            # 获取现有用户和物品ID
            existing_users = set()
            existing_items = set()
            
            if self.metadata.get("user_count", 0) > 0:
                # 从现有特征矩阵中获取用户ID
                if self.user_features_matrix is not None:
                    existing_users = set(range(self.user_features_matrix.shape[0]))
            
            if self.metadata.get("item_count", 0) > 0:
                # 从现有特征矩阵中获取物品ID
                if self.item_features_matrix is not None:
                    existing_items = set(range(self.item_features_matrix.shape[0]))
            
            # 获取新数据中的用户和物品ID
            new_users = set(new_user_behaviors['user_id'].unique())
            new_items = set(new_user_behaviors['item_id'].unique())
            
            # 计算增量用户和物品
            incremental_users = list(new_users - existing_users)
            incremental_items = list(new_items - existing_items)
            
            # 过滤出只包含增量用户和物品的数据
            incremental_data = new_user_behaviors[
                (new_user_behaviors['user_id'].isin(incremental_users)) |
                (new_user_behaviors['item_id'].isin(incremental_items))
            ].copy()
            
            self.logger.info(f"增量数据统计: 新增用户 {len(incremental_users)}, 新增物品 {len(incremental_items)}, 增量记录 {len(incremental_data)}")
            
            return incremental_data, incremental_users, incremental_items
            
        except Exception as e:
            self.logger.error(f"获取增量数据失败: {e}")
            return new_user_behaviors, [], []
    
    def build_user_item_matrix(self, behaviors_df: pd.DataFrame) -> np.ndarray:
        """构建用户-物品交互矩阵"""
        try:
            # 创建用户-物品评分矩阵
            matrix = behaviors_df.pivot_table(
                index='user_id', 
                columns='item_id', 
                values='rating', 
                fill_value=0.0,
                aggfunc='max'  # 如果有重复，取最大值
            )
            
            # 确保矩阵是数值类型
            matrix = matrix.astype(np.float32)
            
            self.logger.info(f"用户-物品矩阵构建完成: {matrix.shape}")
            return matrix.values
            
        except Exception as e:
            self.logger.error(f"构建用户-物品矩阵失败: {e}")
            return np.array([])
    
    def merge_feature_matrices(self, 
                             old_matrix: Optional[np.ndarray], 
                             new_matrix: np.ndarray, 
                             matrix_type: str) -> np.ndarray:
        """合并新旧特征矩阵"""
        try:
            if old_matrix is None or old_matrix.size == 0:
                self.logger.info(f"首次创建{matrix_type}特征矩阵")
                return new_matrix
            
            # 获取矩阵维度
            old_shape = old_matrix.shape
            new_shape = new_matrix.shape
            
            self.logger.info(f"合并{matrix_type}矩阵: 旧矩阵 {old_shape}, 新矩阵 {new_shape}")
            
            # 如果维度不匹配，需要扩展矩阵
            if len(old_shape) == 2 and len(new_shape) == 2:
                # 2D矩阵合并
                max_rows = max(old_shape[0], new_shape[0])
                max_cols = max(old_shape[1], new_shape[1])
                
                # 创建扩展后的矩阵
                merged_matrix = np.zeros((max_rows, max_cols), dtype=np.float32)
                
                # 填充旧矩阵数据
                merged_matrix[:old_shape[0], :old_shape[1]] = old_matrix
                
                # 填充新矩阵数据（新数据会覆盖旧数据）
                merged_matrix[:new_shape[0], :new_shape[1]] = new_matrix
                
            else:
                # 1D向量合并
                max_len = max(old_shape[0], new_shape[0])
                merged_matrix = np.zeros(max_len, dtype=np.float32)
                merged_matrix[:old_shape[0]] = old_matrix
                merged_matrix[:new_shape[0]] = new_matrix
            
            self.logger.info(f"{matrix_type}矩阵合并完成: {merged_matrix.shape}")
            return merged_matrix
            
        except Exception as e:
            self.logger.error(f"合并{matrix_type}矩阵失败: {e}")
            return new_matrix if new_matrix is not None else old_matrix
    
    def normalize_matrix(self, matrix: np.ndarray, method: str = "minmax") -> np.ndarray:
        """归一化特征矩阵"""
        try:
            if matrix.size == 0:
                return matrix
            
            if method == "minmax":
                # Min-Max归一化到[0,1]
                matrix_min = np.min(matrix)
                matrix_max = np.max(matrix)
                if matrix_max > matrix_min:
                    normalized = (matrix - matrix_min) / (matrix_max - matrix_min)
                else:
                    normalized = matrix
                    
            elif method == "zscore":
                # Z-score标准化
                matrix_mean = np.mean(matrix)
                matrix_std = np.std(matrix)
                if matrix_std > 0:
                    normalized = (matrix - matrix_mean) / matrix_std
                else:
                    normalized = matrix
                    
            elif method == "l2":
                # L2归一化
                norms = np.linalg.norm(matrix, axis=1, keepdims=True)
                norms[norms == 0] = 1  # 避免除零
                normalized = matrix / norms
                
            else:
                normalized = matrix
            
            self.logger.info(f"矩阵归一化完成: 方法={method}, 形状={normalized.shape}")
            return normalized.astype(np.float32)
            
        except Exception as e:
            self.logger.error(f"矩阵归一化失败: {e}")
            return matrix
    
    def update_features(self, 
                       new_user_matrix: np.ndarray, 
                       new_item_matrix: np.ndarray,
                       incremental_users: List[int],
                       incremental_items: List[int]):
        """更新特征矩阵缓存"""
        try:
            # 合并用户特征矩阵
            merged_user_matrix = self.merge_feature_matrices(
                self.user_features_matrix, new_user_matrix, "用户"
            )
            
            # 合并物品特征矩阵
            merged_item_matrix = self.merge_feature_matrices(
                self.item_features_matrix, new_item_matrix, "物品"
            )
            
            # 归一化处理
            normalized_user_matrix = self.normalize_matrix(merged_user_matrix, "minmax")
            normalized_item_matrix = self.normalize_matrix(merged_item_matrix, "minmax")
            
            # 保存更新后的矩阵
            self._save_user_features(normalized_user_matrix)
            self._save_item_features(normalized_item_matrix)
            
            # 更新元数据
            self.metadata.update({
                "last_update": datetime.now().isoformat(),
                "user_count": normalized_user_matrix.shape[0],
                "item_count": normalized_item_matrix.shape[0],
                "feature_dimension": normalized_user_matrix.shape[1] if len(normalized_user_matrix.shape) > 1 else 1,
                "total_updates": self.metadata.get("total_updates", 0) + 1,
                "last_incremental_update": datetime.now().isoformat(),
                "incremental_users_count": len(incremental_users),
                "incremental_items_count": len(incremental_items)
            })
            
            self._save_metadata()
            
            # 更新内存中的矩阵
            self.user_features_matrix = normalized_user_matrix
            self.item_features_matrix = normalized_item_matrix
            
            self.logger.info(f"特征矩阵更新完成: 用户矩阵 {normalized_user_matrix.shape}, 物品矩阵 {normalized_item_matrix.shape}")
            
        except Exception as e:
            self.logger.error(f"更新特征矩阵失败: {e}")
            raise e
    
    def get_feature_statistics(self) -> Dict[str, Any]:
        """获取特征矩阵统计信息"""
        stats = {
            "cache_status": "active" if self.user_features_matrix is not None else "empty",
            "metadata": self.metadata.copy(),
            "user_matrix_shape": self.user_features_matrix.shape if self.user_features_matrix is not None else None,
            "item_matrix_shape": self.item_features_matrix.shape if self.item_features_matrix is not None else None,
            "cache_size_mb": self._get_cache_size_mb()
        }
        
        if self.user_features_matrix is not None:
            stats.update({
                "user_matrix_stats": {
                    "mean": float(np.mean(self.user_features_matrix)),
                    "std": float(np.std(self.user_features_matrix)),
                    "min": float(np.min(self.user_features_matrix)),
                    "max": float(np.max(self.user_features_matrix))
                }
            })
        
        if self.item_features_matrix is not None:
            stats.update({
                "item_matrix_stats": {
                    "mean": float(np.mean(self.item_features_matrix)),
                    "std": float(np.std(self.item_features_matrix)),
                    "min": float(np.min(self.item_features_matrix)),
                    "max": float(np.max(self.item_features_matrix))
                }
            })
        
        return stats
    
    def _get_cache_size_mb(self) -> float:
        """获取缓存文件大小（MB）"""
        total_size = 0
        for file_path in [self.user_features_file, self.item_features_file, self.metadata_file]:
            if file_path.exists():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def clear_cache(self):
        """清空缓存"""
        try:
            for file_path in [self.user_features_file, self.item_features_file, self.metadata_file]:
                if file_path.exists():
                    file_path.unlink()
            
            self.user_features_matrix = None
            self.item_features_matrix = None
            self.metadata = {
                "last_update": None,
                "user_count": 0,
                "item_count": 0,
                "feature_dimension": 0,
                "ai_model_version": "bailian-ai-enhanced-v2.0",
                "total_updates": 0,
                "last_incremental_update": None
            }
            
            self.logger.info("缓存已清空")
            
        except Exception as e:
            self.logger.error(f"清空缓存失败: {e}")

# 全局缓存实例
feature_cache = AIFeatureCache()




