"""
商贩检测管理API端点
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from db.session import get_db
from core.security import get_current_user
from db.models import User
from crud.crud_merchant_detection import (
    get_all_detection_configs, get_detection_config_value, set_detection_config_value,
    init_default_configs, get_detection_config
)
from db.models import MerchantDetectionHistory
from sqlalchemy import and_
from crud.crud_detection_history import (
    get_detection_histories, get_detection_stats, create_detection_history
)
from core.merchant_detection import get_detection_system
from core.scheduler import manual_detection

router = APIRouter()


@router.get("/configs")
def get_detection_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有检测配置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    configs = get_all_detection_configs(db)
    return [{
        "key": config.key,
        "value": config.value,
        "description": config.description,
        "is_active": config.is_active,
        "created_at": config.created_at,
        "updated_at": config.updated_at
    } for config in configs]


@router.put("/configs/{key}")
def update_detection_config(
    key: str,
    config_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新检测配置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    value = config_data.get("value")
    description = config_data.get("description")
    
    if value is None:
        raise HTTPException(status_code=400, detail="配置值不能为空")
    
    config = set_detection_config_value(db, key, value, description)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return {"message": "配置更新成功", "config": {
        "key": config.key,
        "value": config.value,
        "description": config.description
    }}


@router.post("/configs/init")
def initialize_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """初始化默认配置"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    init_default_configs(db)
    return {"message": "默认配置初始化成功"}


@router.get("/configs/{key}")
def get_config_value(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取配置值"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    config = get_detection_config(db, key)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    return {
        "key": config.key,
        "value": config.value,
        "description": config.description
    }


@router.post("/detect")
async def manual_detection_endpoint(
    detection_params: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """手动触发商贩检测"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取检测参数
    top_n = detection_params.get("top_n", 50)
    threshold_items = detection_params.get("threshold_items", 3)  # 降低默认阈值
    analysis_days = detection_params.get("analysis_days", 30)
    
    try:
        # 执行检测
        detection_results = await manual_detection(
            top_n=top_n,
            threshold_items=threshold_items,
            analysis_days=analysis_days
        )
        
        # 处理检测结果
        processed_count = 0
        merchant_count = 0
        
        for result in detection_results:
            ai_analysis = result.get("ai_analysis", {})
            if ai_analysis.get("is_merchant", False):
                merchant_count += 1
            processed_count += 1
        
        return {
            "message": "检测完成",
            "total_analyzed": processed_count,
            "detected_merchants": merchant_count,
            "results": detection_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测执行失败: {str(e)}")


@router.post("/analyze-user/{user_id}")
async def analyze_single_user(
    user_id: int,
    analysis_days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """分析单个用户"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        # 首先检查用户是否已经是商家
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if user.is_merchant or user.is_pending_merchant or user.is_pending_verification:
            return {
                "user_id": user_id,
                "message": "该用户已经是商家或待认证状态，无需检测",
                "user_status": {
                    "is_merchant": user.is_merchant,
                    "is_pending_merchant": user.is_pending_merchant,
                    "is_pending_verification": user.is_pending_verification
                },
                "analysis_days": analysis_days,
                "analyzed_at": datetime.now().isoformat()
            }
        
        detection_system = get_detection_system(db)
        
        # 分析用户行为
        behavior_data = await detection_system.analyze_user_behavior(user_id, analysis_days)
        
        # AI判断
        ai_result = await detection_system.get_ai_judgment(behavior_data)
        
        return {
            "user_id": user_id,
            "behavior_data": behavior_data,
            "ai_analysis": ai_result,
            "analysis_days": analysis_days,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户分析失败: {str(e)}")


@router.get("/stats")
def get_detection_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取检测统计信息"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取配置值
    monitor_top_n = get_detection_config_value(db, "monitor_top_n", 50)
    threshold_items = get_detection_config_value(db, "threshold_items", 10)
    analysis_days = get_detection_config_value(db, "analysis_days", 30)
    schedule_enabled = get_detection_config_value(db, "detection_schedule_enabled", False)
    
    # 统计当前在售商品数超过阈值的用户数
    from sqlalchemy import func
    from db.models import Item
    
    high_activity_users = db.query(Item.owner_id, func.count(Item.id).label('item_count')).filter(
        Item.status == "online",
        Item.sold == False
    ).group_by(Item.owner_id).having(
        func.count(Item.id) >= threshold_items
    ).count()
    
    return {
        "schedule_enabled": schedule_enabled,
        "monitor_top_n": monitor_top_n,
        "threshold_items": threshold_items,
        "analysis_days": analysis_days,
        "high_activity_users": high_activity_users,
        "last_updated": datetime.now().isoformat()
    }


@router.get("/histories")
def get_detection_histories_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = Query(None),
    detection_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取检测历史记录"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    histories = get_detection_histories(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        detection_type=detection_type
    )
    
    return {
        "histories": histories,
        "total": len(histories),
        "skip": skip,
        "limit": limit
    }


@router.get("/histories/stats")
def get_detection_histories_stats_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取检测历史统计"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    stats = get_detection_stats(db)
    return stats


@router.post("/histories/{history_id}/confirm-merchant")
def confirm_merchant(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员确认疑似商家，将其设为待认证状态"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from crud.crud_detection_history import get_detection_history_by_id, update_detection_history
    from db.models import User
    
    # 获取检测历史记录
    history = get_detection_history_by_id(db, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    
    if history.processed:
        raise HTTPException(status_code=400, detail="该记录已处理")
    
    # 更新用户状态为待认证
    user = db.query(User).filter(User.id == history.user_id).first()
    if user:
        user.is_pending_verification = True
        db.commit()
    
    # 标记检测记录为已处理
    update_detection_history(db, history_id, processed=True)
    
    return {"message": "用户已设为待认证状态"}


@router.post("/histories/{history_id}/reject-merchant")
def reject_merchant(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员拒绝疑似商家，标记为已处理"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from crud.crud_detection_history import get_detection_history_by_id, update_detection_history
    
    # 获取检测历史记录
    history = get_detection_history_by_id(db, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    
    if history.processed:
        raise HTTPException(status_code=400, detail="该记录已处理")
    
    # 标记检测记录为已处理
    update_detection_history(db, history_id, processed=True)
    
    return {"message": "已拒绝该用户为商家"}


@router.post("/auto-process-timeout")
def auto_process_timeout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """自动处理超时的疑似商家"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from crud.crud_detection_history import get_detection_histories, update_detection_history
    from db.models import User
    from datetime import datetime, timedelta
    
    # 获取超时配置
    timeout_days = get_detection_config_value(db, "auto_timeout_days", 7)
    timeout_days = int(timeout_days)
    
    # 计算超时时间点
    timeout_date = datetime.now() - timedelta(days=timeout_days)
    
    # 获取超时未处理的疑似商家记录
    timeout_histories = db.query(MerchantDetectionHistory).filter(
        and_(
            MerchantDetectionHistory.is_merchant == True,
            MerchantDetectionHistory.processed == False,
            MerchantDetectionHistory.created_at <= timeout_date
        )
    ).all()
    
    processed_count = 0
    for history in timeout_histories:
        # 更新用户状态为待认证
        user = db.query(User).filter(User.id == history.user_id).first()
        if user:
            user.is_pending_verification = True
        
        # 标记检测记录为已处理
        update_detection_history(db, history.id, processed=True)
        processed_count += 1
    
    if processed_count > 0:
        db.commit()
    
    return {
        "message": f"已自动处理 {processed_count} 个超时的疑似商家",
        "processed_count": processed_count
    }
