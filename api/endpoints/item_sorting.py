from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from core.security import get_current_user, get_current_active_user
from db.models import User, ItemSortingWeights, Item
from crud import crud_item_sorting
from schemas.item import ItemInDB
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.get("/metrics/current")
def get_current_metrics(
    time_window_minutes: int = Query(30, ge=5, le=1440, description="时间窗口（分钟）"),
    db: Session = Depends(get_db)
):
    """获取当前时间段的商品指标数据"""
    now = datetime.utcnow()
    time_window_start = now - timedelta(minutes=time_window_minutes)
    time_window_end = now
    
    metrics = crud_item_sorting.get_item_metrics_by_period(db, time_window_start, time_window_end)
    
    result = []
    for metric in metrics:
        result.append({
            "item_id": metric.item_id,
            "item_title": metric.item.title if metric.item else "未知商品",
            "time_window_start": metric.time_window_start.isoformat(),
            "time_window_end": metric.time_window_end.isoformat(),
            "views_count": metric.views_count,
            "likes_count": metric.likes_count,
            "favorites_count": metric.favorites_count,
            "messages_count": metric.messages_count,
            "seller_activity_score": metric.seller_activity_score,
            "position_rank": metric.position_rank
        })
    
    return {
        "success": True,
        "time_window_minutes": time_window_minutes,
        "metrics_count": len(result),
        "metrics": result
    }

@router.get("/metrics/history/{item_id}")
def get_item_metrics_history(
    item_id: int,
    limit: int = Query(10, ge=1, le=50, description="获取记录数量"),
    db: Session = Depends(get_db)
):
    """获取商品的历史指标记录"""
    metrics = crud_item_sorting.get_item_metrics_history(db, item_id, limit)
    
    result = []
    for metric in metrics:
        result.append({
            "id": metric.id,
            "item_id": metric.item_id,
            "time_window_start": metric.time_window_start.isoformat(),
            "time_window_end": metric.time_window_end.isoformat(),
            "views_count": metric.views_count,
            "likes_count": metric.likes_count,
            "favorites_count": metric.favorites_count,
            "messages_count": metric.messages_count,
            "seller_activity_score": metric.seller_activity_score,
            "position_rank": metric.position_rank,
            "created_at": metric.created_at.isoformat()
        })
    
    return {
        "success": True,
        "item_id": item_id,
        "metrics_count": len(result),
        "metrics": result
    }

@router.get("/weights/current")
def get_current_weights(
    time_period: Optional[str] = Query(None, description="时间周期标识"),
    limit: int = Query(100, ge=1, le=500, description="获取记录数量"),
    db: Session = Depends(get_db)
):
    """获取当前时间周期的商品权重数据"""
    if not time_period:
        # 如果没有指定时间周期，使用当前时间生成
        now = datetime.utcnow()
        time_period = now.strftime("%Y-%m-%d-%H:%M")
    
    weights_query = db.query(crud_item_sorting.ItemSortingWeights).filter(
        crud_item_sorting.ItemSortingWeights.time_period == time_period
    ).order_by(crud_item_sorting.ItemSortingWeights.final_weight.desc()).limit(limit)
    
    weights = weights_query.all()
    
    result = []
    for weight in weights:
        result.append({
            "id": weight.id,
            "item_id": weight.item_id,
            "item_title": weight.item.title if weight.item else "未知商品",
            "time_period": weight.time_period,
            "base_weight": weight.base_weight,
            "trend_weight": weight.trend_weight,
            "position_weight": weight.position_weight,
            "final_weight": weight.final_weight,
            "ranking_position": weight.ranking_position,
            "created_at": weight.created_at.isoformat()
        })
    
    return {
        "success": True,
        "time_period": time_period,
        "weights_count": len(result),
        "weights": result
    }

@router.get("/sorted-items")
def get_dynamically_sorted_items(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    time_period: Optional[str] = Query(None, description="时间周期标识"),
    db: Session = Depends(get_db)
):
    """获取按动态权重排序的商品列表"""
    skip = (page - 1) * size
    
    items = crud_item_sorting.get_items_with_dynamic_sorting(
        db, skip, size, time_period
    )
    
    # 转换为响应格式
    result = []
    for item in items:
        item_data = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "category": item.category,
            "condition": item.condition,
            "location": item.location,
            "images": item.images,
            "status": item.status,
            "sold": item.sold,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "views": item.views,
            "like_count": item.like_count or 0,
            "favorited_count": item.favorited_count or 0,
            "owner_id": item.owner_id,
            "is_merchant_item": item.is_merchant_item or False
        }
        
        # 添加权重信息（如果可用）
        if time_period:
            weight = db.query(crud_item_sorting.ItemSortingWeights).filter(
                crud_item_sorting.ItemSortingWeights.item_id == item.id,
                crud_item_sorting.ItemSortingWeights.time_period == time_period
            ).first()
            
            if weight:
                item_data["sorting_weight"] = {
                    "base_weight": weight.base_weight,
                    "trend_weight": weight.trend_weight,
                    "position_weight": weight.position_weight,
                    "final_weight": weight.final_weight,
                    "ranking_position": weight.ranking_position
                }
        
        result.append(item_data)
    
    return {
        "success": True,
        "page": page,
        "size": size,
        "time_period": time_period,
        "items_count": len(result),
        "items": result
    }

# 新增：获取排序状态（最近一次运行信息）
@router.get("/status")
def get_sorting_status(
    db: Session = Depends(get_db)
):
    """获取最近一次排序运行的状态信息。"""
    # 最近一次权重记录的时间周期
    latest_weight = db.query(crud_item_sorting.ItemSortingWeights)\
        .order_by(crud_item_sorting.ItemSortingWeights.created_at.desc())\
        .first()

    if not latest_weight:
        return {
            "success": True,
            "current_time_period": None,
            "last_run_time": None,
            "items_processed": 0,
            "algorithm_status": "idle"
        }

    latest_time_period = latest_weight.time_period
    last_run_time = latest_weight.created_at
    items_processed = db.query(crud_item_sorting.ItemSortingWeights)\
        .filter(crud_item_sorting.ItemSortingWeights.time_period == latest_time_period)\
        .count()

    return {
        "success": True,
        "current_time_period": latest_time_period,
        "last_run_time": last_run_time.isoformat() if last_run_time else None,
        "items_processed": items_processed,
        "algorithm_status": "idle"
    }

# 新增：获取排序运行历史（按 time_period 聚合）
@router.get("/history")
def get_sorting_history(
    days: int = Query(7, ge=1, le=90, description="历史天数范围"),
    db: Session = Depends(get_db)
):
    """获取按时间周期聚合的排序运行历史。"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # 查询指定时间范围内的权重记录，并按 time_period 聚合
    weights = db.query(
        crud_item_sorting.ItemSortingWeights.time_period,
        func.min(crud_item_sorting.ItemSortingWeights.created_at).label("first_created"),
        func.max(crud_item_sorting.ItemSortingWeights.created_at).label("last_created"),
        func.count(crud_item_sorting.ItemSortingWeights.id).label("items_processed")
    ).filter(
        crud_item_sorting.ItemSortingWeights.created_at >= cutoff
    ).group_by(
        crud_item_sorting.ItemSortingWeights.time_period
    ).order_by(
        func.max(crud_item_sorting.ItemSortingWeights.created_at).desc()
    ).all()

    history = []
    for idx, row in enumerate(weights):
        # 运行时长：同一 time_period 内第一条与最后一条权重记录的时间差（秒）
        duration_seconds = None
        if row.first_created and row.last_created:
            try:
                duration_seconds = int((row.last_created - row.first_created).total_seconds())
            except Exception:
                duration_seconds = None
        history.append({
            "id": idx + 1,
            "created_at": row.last_created.isoformat() if row.last_created else None,
            "time_period": row.time_period,
            "items_processed": int(row.items_processed),
            "duration": duration_seconds,
            "status": "success"
        })

    return {
        "success": True,
        "days": days,
        "records": history
    }

@router.post("/run-algorithm")
def run_sorting_algorithm(
    time_window_minutes: int = Query(30, ge=5, le=1440, description="时间窗口（分钟）"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """运行商品排序算法（需要管理员权限）"""
    # 检查用户权限
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        # 运行排序算法
        result = crud_item_sorting.run_sorting_algorithm(db, time_window_minutes)
        
        return {
            "success": True,
            "message": "排序算法运行成功",
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"排序算法运行失败: {str(e)}"
        )

@router.get("/config")
def get_sorting_config(db: Session = Depends(get_db)):
    """获取排序配置"""
    configs = {}
    
    # 获取各种配置
    config_keys = [
        "time_window_minutes",
        "weight_factors",
        "trend_calculation",
        "position_algorithm"
    ]
    
    for key in config_keys:
        config = crud_item_sorting.get_sorting_config(db, key)
        if config:
            configs[key] = config
    
    return {
        "success": True,
        "configs": configs
    }

@router.put("/config")
def update_sorting_config(
    config_data: Dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新排序配置（需要管理员权限）"""
    # 检查用户权限
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        config_key = config_data.get("config_key")
        config_value = config_data.get("config_value")
        description = config_data.get("description")
        
        if not config_key or config_value is None:
            raise HTTPException(status_code=400, detail="配置键和值不能为空")
        
        # 更新配置
        crud_item_sorting.update_sorting_config(db, config_key, config_value, description)
        
        return {
            "success": True,
            "message": f"配置 {config_key} 更新成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"配置更新失败: {str(e)}"
        )

@router.get("/analytics/trend")
def get_sorting_trend_analytics(
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    db: Session = Depends(get_db)
):
    """获取排序趋势分析数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取指定时间范围内的权重数据
    weights = db.query(crud_item_sorting.ItemSortingWeights).filter(
        crud_item_sorting.ItemSortingWeights.created_at >= start_date,
        crud_item_sorting.ItemSortingWeights.created_at <= end_date
    ).order_by(crud_item_sorting.ItemSortingWeights.created_at).all()
    
    # 按时间周期分组
    trend_data = {}
    for weight in weights:
        time_period = weight.time_period
        if time_period not in trend_data:
            trend_data[time_period] = {
                "time_period": time_period,
                "total_items": 0,
                "avg_final_weight": 0.0,
                "top_items": []
            }
        
        trend_data[time_period]["total_items"] += 1
        trend_data[time_period]["avg_final_weight"] += weight.final_weight
        
        # 记录前10名商品
        if weight.ranking_position and weight.ranking_position <= 10:
            trend_data[time_period]["top_items"].append({
                "item_id": weight.item_id,
                "item_title": weight.item.title if weight.item else "未知商品",
                "final_weight": weight.final_weight,
                "ranking_position": weight.ranking_position
            })
    
    # 计算平均权重
    for period_data in trend_data.values():
        if period_data["total_items"] > 0:
            period_data["avg_final_weight"] /= period_data["total_items"]
    
    return {
        "success": True,
        "analysis_days": days,
        "trend_data": list(trend_data.values())
    }

@router.get("/analytics/item/{item_id}")
def get_item_sorting_analytics(
    item_id: int,
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    db: Session = Depends(get_db)
):
    """获取单个商品的排序分析数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 获取商品信息
    item = db.query(crud_item_sorting.Item).filter(crud_item_sorting.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 获取权重历史
    weights = db.query(crud_item_sorting.ItemSortingWeights).filter(
        crud_item_sorting.ItemSortingWeights.item_id == item_id,
        crud_item_sorting.ItemSortingWeights.created_at >= start_date,
        crud_item_sorting.ItemSortingWeights.created_at <= end_date
    ).order_by(crud_item_sorting.ItemSortingWeights.created_at).all()
    
    # 获取指标历史
    metrics = crud_item_sorting.get_item_metrics_history(db, item_id, days * 2)
    
    # 构建分析数据
    weight_history = []
    for weight in weights:
        weight_history.append({
            "time_period": weight.time_period,
            "base_weight": weight.base_weight,
            "trend_weight": weight.trend_weight,
            "position_weight": weight.position_weight,
            "final_weight": weight.final_weight,
            "ranking_position": weight.ranking_position,
            "created_at": weight.created_at.isoformat()
        })
    
    metrics_history = []
    for metric in metrics:
        metrics_history.append({
            "time_window_start": metric.time_window_start.isoformat(),
            "time_window_end": metric.time_window_end.isoformat(),
            "views_count": metric.views_count,
            "likes_count": metric.likes_count,
            "favorites_count": metric.favorites_count,
            "messages_count": metric.messages_count,
            "seller_activity_score": metric.seller_activity_score,
            "position_rank": metric.position_rank
        })
    
    return {
        "success": True,
        "item_id": item_id,
        "item_title": item.title,
        "analysis_days": days,
        "weight_history": weight_history,
        "metrics_history": metrics_history
    }
