from sqlalchemy.orm import Session
from db.models import AIRecommendationConfig
from typing import List, Optional, Dict, Any
from datetime import datetime

def get_ai_config(db: Session, config_key: str) -> Optional[AIRecommendationConfig]:
    """获取AI推荐配置"""
    return db.query(AIRecommendationConfig).filter(
        AIRecommendationConfig.config_key == config_key,
        AIRecommendationConfig.is_active == True
    ).first()

def create_or_update_ai_config(
    db: Session, 
    config_key: str, 
    config_value: Dict[str, Any],
    description: Optional[str] = None
) -> AIRecommendationConfig:
    """创建或更新AI推荐配置"""
    config = db.query(AIRecommendationConfig).filter(
        AIRecommendationConfig.config_key == config_key
    ).first()
    
    if config:
        config.config_value = config_value
        config.description = description
        config.updated_at = datetime.utcnow()
    else:
        config = AIRecommendationConfig(
            config_key=config_key,
            config_value=config_value,
            description=description
        )
        db.add(config)
    
    db.commit()
    db.refresh(config)
    return config

def get_all_ai_configs(db: Session) -> List[AIRecommendationConfig]:
    """获取所有AI推荐配置"""
    return db.query(AIRecommendationConfig).filter(
        AIRecommendationConfig.is_active == True
    ).all()

def delete_ai_config(db: Session, config_key: str) -> bool:
    """删除AI推荐配置"""
    config = db.query(AIRecommendationConfig).filter(
        AIRecommendationConfig.config_key == config_key
    ).first()
    
    if config:
        config.is_active = False
        config.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

def get_ai_recommendation_settings(db: Session) -> Dict[str, Any]:
    """获取AI推荐设置"""
    settings = {}
    
    # 默认设置
    default_settings = {
        "sequence_length": 10,  # 用户行为序列长度
        "recommendation_count": 10,  # 推荐商品数量
        "category_weight": 0.4,  # 分类权重
        "price_weight": 0.3,  # 价格权重
        "condition_weight": 0.2,  # 成色权重
        "location_weight": 0.1,  # 地区权重
        "enable_ai_analysis": True,  # 是否启用AI分析
        "ai_model_version": "v1.0",  # AI模型版本
        "min_behavior_count": 3,  # 最少行为记录数
        "behavior_days": 30,  # 行为记录天数
        # 商品选择范围配置
        "item_selection": {
            "sort_orders": [  # 排序方式配置
                {"name": "按价格升序", "field": "price", "order": "asc", "limit": 20, "enabled": True},
                {"name": "按价格降序", "field": "price", "order": "desc", "limit": 20, "enabled": True},
                {"name": "按浏览量", "field": "views", "order": "desc", "limit": 20, "enabled": True},
                {"name": "按点赞数", "field": "like_count", "order": "desc", "limit": 20, "enabled": True},
                {"name": "按发布时间", "field": "created_at", "order": "desc", "limit": 20, "enabled": True}
            ],
            "category_limits": {  # 分类限制配置
                "1": {"limit": 10, "enabled": True, "name": "分类1"},
                "2": {"limit": 10, "enabled": True, "name": "分类2"},
                "3": {"limit": 10, "enabled": True, "name": "分类3"},
                "4": {"limit": 10, "enabled": True, "name": "分类4"},
                "5": {"limit": 10, "enabled": True, "name": "分类5"},
                "6": {"limit": 10, "enabled": True, "name": "分类6"},
                "7": {"limit": 10, "enabled": True, "name": "分类7"},
                "8": {"limit": 10, "enabled": True, "name": "分类8"},
                "9": {"limit": 10, "enabled": True, "name": "分类9"},
                "10": {"limit": 10, "enabled": True, "name": "分类10"}
            },
            "max_total_items": 100,  # 最大总商品数
            "enable_category_filter": True,  # 是否启用分类过滤
            "enable_sort_filter": True  # 是否启用排序过滤
        }
    }
    
    # 从数据库获取配置
    configs = get_all_ai_configs(db)
    for config in configs:
        if config.config_key in default_settings:
            settings[config.config_key] = config.config_value
    
    # 合并默认设置
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
    
    return settings
