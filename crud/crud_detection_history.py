from sqlalchemy.orm import Session
from db.models import MerchantDetectionHistory
from typing import List, Optional, Dict, Any
from datetime import datetime

def create_detection_history(
    db: Session,
    user_id: int,
    detection_type: str = "manual",
    behavior_data: Dict[str, Any] = None,
    ai_analysis: Dict[str, Any] = None,
    active_items_count: int = 0,
    is_merchant: bool = False,
    confidence: float = 0.0,
    ai_reason: str = None,
    processed: bool = False
) -> MerchantDetectionHistory:
    """创建检测历史记录"""
    detection_history = MerchantDetectionHistory(
        user_id=user_id,
        detection_type=detection_type,
        behavior_data=behavior_data,
        ai_analysis=ai_analysis,
        active_items_count=active_items_count,
        is_merchant=is_merchant,
        confidence=confidence,
        ai_reason=ai_reason,
        processed=processed
    )
    db.add(detection_history)
    db.commit()
    db.refresh(detection_history)
    return detection_history

def get_detection_histories(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    detection_type: Optional[str] = None
) -> List[MerchantDetectionHistory]:
    """获取检测历史记录"""
    query = db.query(MerchantDetectionHistory)
    
    if user_id:
        query = query.filter(MerchantDetectionHistory.user_id == user_id)
    
    if detection_type:
        query = query.filter(MerchantDetectionHistory.detection_type == detection_type)
    
    return query.order_by(MerchantDetectionHistory.created_at.desc()).offset(skip).limit(limit).all()

def get_detection_history_by_id(db: Session, history_id: int) -> Optional[MerchantDetectionHistory]:
    """根据ID获取检测历史记录"""
    return db.query(MerchantDetectionHistory).filter(MerchantDetectionHistory.id == history_id).first()

def update_detection_history(
    db: Session,
    history_id: int,
    **kwargs
) -> Optional[MerchantDetectionHistory]:
    """更新检测历史记录"""
    detection_history = get_detection_history_by_id(db, history_id)
    if detection_history:
        for key, value in kwargs.items():
            if hasattr(detection_history, key):
                setattr(detection_history, key, value)
        db.commit()
        db.refresh(detection_history)
    return detection_history

def delete_detection_history(db: Session, history_id: int) -> bool:
    """删除检测历史记录"""
    detection_history = get_detection_history_by_id(db, history_id)
    if detection_history:
        db.delete(detection_history)
        db.commit()
        return True
    return False

def get_detection_stats(db: Session) -> Dict[str, Any]:
    """获取检测统计信息"""
    total_detections = db.query(MerchantDetectionHistory).count()
    merchant_detections = db.query(MerchantDetectionHistory).filter(
        MerchantDetectionHistory.is_merchant == True
    ).count()
    processed_detections = db.query(MerchantDetectionHistory).filter(
        MerchantDetectionHistory.processed == True
    ).count()
    
    return {
        "total_detections": total_detections,
        "merchant_detections": merchant_detections,
        "processed_detections": processed_detections,
        "pending_detections": total_detections - processed_detections
    }
