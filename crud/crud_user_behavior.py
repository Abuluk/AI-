from sqlalchemy.orm import Session
from db.models import UserBehavior, Item
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

def create_user_behavior(
    db: Session, 
    user_id: int, 
    behavior_type: str, 
    item_id: Optional[int] = None,
    behavior_data: Optional[Dict[str, Any]] = None
) -> UserBehavior:
    """创建用户行为记录"""
    behavior = UserBehavior(
        user_id=user_id,
        item_id=item_id,
        behavior_type=behavior_type,
        behavior_data=behavior_data
    )
    db.add(behavior)
    db.commit()
    db.refresh(behavior)
    return behavior

def get_user_recent_behaviors(
    db: Session, 
    user_id: int, 
    behavior_type: str = "view",
    limit: int = 10,
    days: int = 30
) -> List[UserBehavior]:
    """获取用户最近的行为记录"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    behaviors = db.query(UserBehavior).filter(
        UserBehavior.user_id == user_id,
        UserBehavior.behavior_type == behavior_type,
        UserBehavior.created_at >= cutoff_date,
        UserBehavior.item_id.isnot(None)
    ).order_by(UserBehavior.created_at.desc()).limit(limit).all()
    
    return behaviors

def get_user_behavior_sequence(
    db: Session, 
    user_id: int, 
    limit: int = 20,
    days: int = 30
) -> List[Dict[str, Any]]:
    """获取用户行为序列，用于AI分析"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 获取所有行为记录，包括没有关联商品的行为
    behaviors = db.query(UserBehavior).filter(
        UserBehavior.user_id == user_id,
        UserBehavior.created_at >= cutoff_date
    ).order_by(UserBehavior.created_at.desc()).limit(limit).all()
    
    # 转换为序列格式
    sequence = []
    for behavior in behaviors:
        if behavior.item:
            # 有关联商品的行为
            sequence.append({
                "item_id": behavior.item.id,
                "title": behavior.item.title,
                "category": behavior.item.category,
                "price": behavior.item.price,
                "condition": behavior.item.condition,
                "behavior_type": behavior.behavior_type,
                "timestamp": behavior.created_at.isoformat(),
                "behavior_data": behavior.behavior_data
            })
        else:
            # 没有关联商品的行为（如搜索、页面浏览等）
            sequence.append({
                "item_id": None,
                "title": behavior.behavior_data.get('title', '未知') if behavior.behavior_data else '未知',
                "category": behavior.behavior_data.get('category', '其他') if behavior.behavior_data else '其他',
                "price": behavior.behavior_data.get('price', 0) if behavior.behavior_data else 0,
                "condition": behavior.behavior_data.get('condition', '未知') if behavior.behavior_data else '未知',
                "behavior_type": behavior.behavior_type,
                "timestamp": behavior.created_at.isoformat(),
                "behavior_data": behavior.behavior_data
            })
    
    return sequence

def get_user_behavior_stats(
    db: Session, 
    user_id: int, 
    days: int = 30
) -> Dict[str, Any]:
    """获取用户行为统计"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # 统计各种行为类型
    stats = {}
    behavior_types = ["view", "click", "favorite", "like", "search"]
    
    for behavior_type in behavior_types:
        count = db.query(UserBehavior).filter(
            UserBehavior.user_id == user_id,
            UserBehavior.behavior_type == behavior_type,
            UserBehavior.created_at >= cutoff_date
        ).count()
        stats[behavior_type] = count
    
    # 获取最常浏览的分类
    category_stats = db.query(
        Item.category,
        db.func.count(UserBehavior.id).label('count')
    ).join(UserBehavior).filter(
        UserBehavior.user_id == user_id,
        UserBehavior.behavior_type == "view",
        UserBehavior.created_at >= cutoff_date,
        Item.category.isnot(None)
    ).group_by(Item.category).order_by(db.func.count(UserBehavior.id).desc()).limit(5).all()
    
    stats["top_categories"] = [{"category": cat, "count": count} for cat, count in category_stats]
    
    return stats

def cleanup_old_behaviors(db: Session, days: int = 90) -> int:
    """清理旧的行为记录"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    deleted_count = db.query(UserBehavior).filter(
        UserBehavior.created_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted_count
