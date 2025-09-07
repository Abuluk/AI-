"""
商贩检测配置的CRUD操作
"""

from sqlalchemy.orm import Session
from db.models import MerchantDetectionConfig
from typing import List, Optional, Dict, Any


def get_detection_config(db: Session, key: str) -> Optional[MerchantDetectionConfig]:
    """获取检测配置"""
    return db.query(MerchantDetectionConfig).filter(
        MerchantDetectionConfig.key == key,
        MerchantDetectionConfig.is_active == True
    ).first()


def get_all_detection_configs(db: Session) -> List[MerchantDetectionConfig]:
    """获取所有检测配置"""
    return db.query(MerchantDetectionConfig).filter(
        MerchantDetectionConfig.is_active == True
    ).all()


def create_detection_config(db: Session, key: str, value: str, description: str = None) -> MerchantDetectionConfig:
    """创建检测配置"""
    config = MerchantDetectionConfig(
        key=key,
        value=value,
        description=description
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def update_detection_config(db: Session, key: str, value: str, description: str = None) -> Optional[MerchantDetectionConfig]:
    """更新检测配置"""
    config = get_detection_config(db, key)
    if config:
        config.value = value
        if description is not None:
            config.description = description
        db.commit()
        db.refresh(config)
    return config


def delete_detection_config(db: Session, key: str) -> bool:
    """删除检测配置（软删除）"""
    config = get_detection_config(db, key)
    if config:
        config.is_active = False
        db.commit()
        return True
    return False


def get_detection_config_value(db: Session, key: str, default_value: Any = None) -> Any:
    """获取配置值"""
    config = get_detection_config(db, key)
    if config:
        try:
            # 尝试转换为整数
            if config.value.isdigit():
                return int(config.value)
            # 尝试转换为浮点数
            try:
                return float(config.value)
            except ValueError:
                pass
            # 尝试转换为布尔值
            if config.value.lower() in ['true', 'false']:
                return config.value.lower() == 'true'
            # 返回字符串
            return config.value
        except:
            return config.value
    return default_value


def set_detection_config_value(db: Session, key: str, value: Any, description: str = None) -> MerchantDetectionConfig:
    """设置配置值"""
    config = get_detection_config(db, key)
    if config:
        return update_detection_config(db, key, str(value), description)
    else:
        return create_detection_config(db, key, str(value), description)


def init_default_configs(db: Session):
    """初始化默认配置"""
    default_configs = [
        {
            "key": "monitor_top_n",
            "value": "50",
            "description": "监控每个分类和首页排序前N个商品"
        },
        {
            "key": "threshold_items",
            "value": "10",
            "description": "在售商品数阈值，超过此数量将进行AI分析"
        },
        {
            "key": "analysis_days",
            "value": "30",
            "description": "分析用户最近N天的行为数据"
        },
        {
            "key": "ai_confidence_threshold",
            "value": "0.7",
            "description": "AI判断为商贩的置信度阈值"
        },
        {
            "key": "auto_set_pending",
            "value": "true",
            "description": "是否自动将识别出的商贩设为待认证状态"
        },
        {
            "key": "auto_timeout_days",
            "value": "7",
            "description": "疑似商家超时自动处理天数，超过此天数未确认将自动设为待认证"
        },
        {
            "key": "detection_schedule_enabled",
            "value": "false",
            "description": "是否启用定时检测"
        },
        {
            "key": "detection_schedule_time",
            "value": "02:00",
            "description": "定时检测时间（24小时制，格式：HH:MM）"
        }
    ]
    
    for config_data in default_configs:
        existing_config = get_detection_config(db, config_data["key"])
        if not existing_config:
            create_detection_config(
                db,
                config_data["key"],
                config_data["value"],
                config_data["description"]
            )
