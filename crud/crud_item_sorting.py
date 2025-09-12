from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from db.models import ItemSortingMetrics, ItemSortingWeights, SortingConfig, Item, UserBehavior, User
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import math

def get_sorting_config(db: Session, config_key: str) -> Optional[Dict]:
    """获取排序配置"""
    config = db.query(SortingConfig).filter(
        SortingConfig.config_key == config_key,
        SortingConfig.is_active == True
    ).first()
    if config and config.config_value:
        return config.config_value
    return None

def update_sorting_config(db: Session, config_key: str, config_value: Dict, description: str = None):
    """更新排序配置"""
    config = db.query(SortingConfig).filter(SortingConfig.config_key == config_key).first()
    if config:
        config.config_value = config_value
        if description:
            config.description = description
        config.updated_at = func.now()
    else:
        config = SortingConfig(
            config_key=config_key,
            config_value=config_value,
            description=description
        )
        db.add(config)
    db.commit()
    return config

def create_item_metrics(db: Session, item_id: int, time_window_start: datetime, 
                       time_window_end: datetime, metrics_data: Dict) -> ItemSortingMetrics:
    """创建商品指标记录"""
    metrics = ItemSortingMetrics(
        item_id=item_id,
        time_window_start=time_window_start,
        time_window_end=time_window_end,
        views_count=metrics_data.get('views_count', 0),
        likes_count=metrics_data.get('likes_count', 0),
        favorites_count=metrics_data.get('favorites_count', 0),
        messages_count=metrics_data.get('messages_count', 0),
        seller_activity_score=metrics_data.get('seller_activity_score', 0.0),
        position_rank=metrics_data.get('position_rank')
    )
    db.add(metrics)
    db.commit()
    db.refresh(metrics)
    return metrics

def get_item_metrics_by_period(db: Session, time_window_start: datetime, 
                              time_window_end: datetime) -> List[ItemSortingMetrics]:
    """获取指定时间段的商品指标"""
    return db.query(ItemSortingMetrics).filter(
        ItemSortingMetrics.time_window_start == time_window_start,
        ItemSortingMetrics.time_window_end == time_window_end
    ).all()

def get_item_metrics_history(db: Session, item_id: int, limit: int = 10) -> List[ItemSortingMetrics]:
    """获取商品的历史指标记录"""
    return db.query(ItemSortingMetrics).filter(
        ItemSortingMetrics.item_id == item_id
    ).order_by(desc(ItemSortingMetrics.time_window_end)).limit(limit).all()

def calculate_seller_activity_score(db: Session, item_id: int, time_window_start: datetime, 
                                  time_window_end: datetime) -> float:
    """计算卖家活跃度分数"""
    # 获取商品信息
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return 0.0
    
    owner_id = item.owner_id
    
    # 计算卖家在该时间段内的活跃度
    # 1. 发布商品数量
    items_published = db.query(Item).filter(
        Item.owner_id == owner_id,
        Item.created_at >= time_window_start,
        Item.created_at <= time_window_end
    ).count()
    
    # 2. 回复消息数量
    messages_replied = db.query(UserBehavior).filter(
        UserBehavior.user_id == owner_id,
        UserBehavior.behavior_type == 'message',
        UserBehavior.created_at >= time_window_start,
        UserBehavior.created_at <= time_window_end
    ).count()
    
    # 3. 登录活跃度（基于最后登录时间）
    user = db.query(User).filter(User.id == owner_id).first()
    login_score = 0.0
    if user and user.last_login:
        time_diff = datetime.utcnow() - user.last_login
        if time_diff.days <= 1:
            login_score = 1.0
        elif time_diff.days <= 7:
            login_score = 0.7
        elif time_diff.days <= 30:
            login_score = 0.3
        else:
            login_score = 0.1
    
    # 综合计算活跃度分数
    activity_score = (
        items_published * 0.4 +  # 发布商品权重40%
        messages_replied * 0.3 +  # 回复消息权重30%
        login_score * 0.3  # 登录活跃度权重30%
    )
    
    return min(activity_score, 10.0)  # 限制最大分数为10

def collect_item_metrics_for_period(db: Session, time_window_start: datetime, 
                                   time_window_end: datetime) -> List[ItemSortingMetrics]:
    """收集指定时间段内所有商品的指标数据"""
    # 获取该时间段内所有在售商品
    items = db.query(Item).filter(
        Item.status == "online",
        Item.sold == False,
        Item.created_at <= time_window_end  # 商品在该时间段结束前已创建
    ).all()
    
    metrics_list = []
    for item in items:
        # 计算浏览量（基于UserBehavior记录）
        views_count = db.query(UserBehavior).filter(
            UserBehavior.item_id == item.id,
            UserBehavior.behavior_type == 'view',
            UserBehavior.created_at >= time_window_start,
            UserBehavior.created_at <= time_window_end
        ).count()
        
        # 计算点赞数
        likes_count = db.query(UserBehavior).filter(
            UserBehavior.item_id == item.id,
            UserBehavior.behavior_type == 'like',
            UserBehavior.created_at >= time_window_start,
            UserBehavior.created_at <= time_window_end
        ).count()
        
        # 计算收藏数
        favorites_count = db.query(UserBehavior).filter(
            UserBehavior.item_id == item.id,
            UserBehavior.behavior_type == 'favorite',
            UserBehavior.created_at >= time_window_start,
            UserBehavior.created_at <= time_window_end
        ).count()
        
        # 计算消息数
        messages_count = db.query(UserBehavior).filter(
            UserBehavior.item_id == item.id,
            UserBehavior.behavior_type == 'message',
            UserBehavior.created_at >= time_window_start,
            UserBehavior.created_at <= time_window_end
        ).count()
        
        # 计算卖家活跃度分数
        seller_activity_score = calculate_seller_activity_score(
            db, item.id, time_window_start, time_window_end
        )
        
        # 创建指标记录
        metrics_data = {
            'views_count': views_count,
            'likes_count': likes_count,
            'favorites_count': favorites_count,
            'messages_count': messages_count,
            'seller_activity_score': seller_activity_score
        }
        
        metrics = create_item_metrics(db, item.id, time_window_start, time_window_end, metrics_data)
        metrics_list.append(metrics)
    
    return metrics_list

def calculate_trend_weight(current_metrics: ItemSortingMetrics, 
                          previous_metrics: Optional[ItemSortingMetrics]) -> float:
    """计算趋势权重（基于与上一周期的对比）"""
    if not previous_metrics:
        return 1.0  # 如果没有历史数据，返回默认权重
    
    # 计算各项指标的增长率
    views_growth = calculate_growth_rate(current_metrics.views_count, previous_metrics.views_count)
    likes_growth = calculate_growth_rate(current_metrics.likes_count, previous_metrics.likes_count)
    favorites_growth = calculate_growth_rate(current_metrics.favorites_count, previous_metrics.favorites_count)
    messages_growth = calculate_growth_rate(current_metrics.messages_count, previous_metrics.messages_count)
    activity_growth = calculate_growth_rate(current_metrics.seller_activity_score, previous_metrics.seller_activity_score)
    
    # 综合趋势分数（加权平均）
    trend_score = (
        views_growth * 0.3 +
        likes_growth * 0.25 +
        favorites_growth * 0.2 +
        messages_growth * 0.15 +
        activity_growth * 0.1
    )
    
    # 将趋势分数转换为权重（1.0为基准，大于1.0表示上升趋势）
    trend_weight = 1.0 + (trend_score * 0.5)  # 最大权重为1.5
    return max(0.5, min(trend_weight, 1.5))  # 限制权重范围

def calculate_growth_rate(current: int, previous: int) -> float:
    """计算增长率"""
    if previous == 0:
        return 1.0 if current > 0 else 0.0
    return (current - previous) / previous

def calculate_position_weight(current_position: int, previous_position: Optional[int], 
                             total_items: int) -> float:
    """计算位置权重（基于对抗曲线算法）"""
    if previous_position is None:
        return 1.0  # 如果没有历史位置，返回默认权重
    
    # 计算位置变化
    position_change = previous_position - current_position  # 正数表示排名上升
    
    # 对抗曲线算法：位置变化越大，权重调整越大
    # 使用对数函数来平滑权重变化
    if position_change > 0:  # 排名上升
        weight_adjustment = math.log(1 + position_change) * 0.2
    elif position_change < 0:  # 排名下降
        weight_adjustment = -math.log(1 + abs(position_change)) * 0.15
    else:  # 排名不变
        weight_adjustment = 0.0
    
    # 考虑当前排名位置的影响（排名越靠前，权重调整越小）
    position_factor = 1.0 - (current_position / total_items) * 0.3
    
    position_weight = 1.0 + (weight_adjustment * position_factor)
    return max(0.7, min(position_weight, 1.3))  # 限制权重范围

def calculate_final_weight(base_weight: float, trend_weight: float, position_weight: float) -> float:
    """计算最终权重"""
    # 加权组合各项权重
    final_weight = (
        base_weight * 0.4 +      # 基础权重40%
        trend_weight * 0.35 +    # 趋势权重35%
        position_weight * 0.25   # 位置权重25%
    )
    return final_weight

def create_item_weight(db: Session, item_id: int, time_period: str, 
                      base_weight: float, trend_weight: float, position_weight: float,
                      final_weight: float, ranking_position: int = None) -> ItemSortingWeights:
    """创建商品权重记录"""
    weight = ItemSortingWeights(
        item_id=item_id,
        time_period=time_period,
        base_weight=base_weight,
        trend_weight=trend_weight,
        position_weight=position_weight,
        final_weight=final_weight,
        ranking_position=ranking_position
    )
    db.add(weight)
    db.commit()
    db.refresh(weight)
    return weight

def calculate_smart_score(item: Item) -> float:
    """计算商品的智能评分（当没有权重数据时使用）"""
    score = 0.0
    
    # 浏览量权重 (30%)
    views_score = min(item.views or 0, 100) / 100.0 * 0.3
    score += views_score
    
    # 点赞数权重 (25%)
    likes_score = min(item.like_count or 0, 50) / 50.0 * 0.25
    score += likes_score
    
    # 收藏数权重 (20%)
    favorites_score = min(item.favorited_count or 0, 20) / 20.0 * 0.2
    score += favorites_score
    
    # 价格合理性权重 (15%) - 价格越低分数越高
    if item.price > 0:
        price_score = max(0, 1 - (item.price / 1000)) * 0.15  # 假设1000为高价阈值
        score += price_score
    
    # 新鲜度权重 (10%) - 越新分数越高
    if item.created_at:
        days_old = (datetime.utcnow() - item.created_at).days
        freshness_score = max(0, 1 - (days_old / 30)) * 0.1  # 30天内为新鲜
        score += freshness_score
    
    return score

def get_items_with_dynamic_sorting(db: Session, skip: int = 0, limit: int = 100,
                                 current_time_period: str = None, 
                                 category: Optional[int] = None,
                                 search: Optional[str] = None,
                                 location: Optional[str] = None) -> List[Item]:
    """获取按动态权重排序的商品列表"""
    if not current_time_period:
        # 如果没有指定时间周期，使用当前时间生成
        now = datetime.utcnow()
        current_time_period = now.strftime("%Y-%m-%d-%H:%M")
    
    # 构建基础查询条件
    base_query = db.query(Item).filter(
        Item.status == "online",
        Item.sold == False
    )
    
    # 应用过滤条件
    if category is not None:
        base_query = base_query.filter(Item.category == category)
    
    if search is not None and search.strip():
        base_query = base_query.filter(
            or_(
                Item.title.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%")
            )
        )
    
    if location is not None and location.strip():
        base_query = base_query.filter(Item.location.ilike(f"%{location}%"))
    
    # 获取最新的权重记录
    weights_query = db.query(ItemSortingWeights).filter(
        ItemSortingWeights.time_period == current_time_period
    ).order_by(desc(ItemSortingWeights.final_weight))
    
    # 如果有权重记录，按权重排序
    if weights_query.count() > 0:
        weighted_items = []
        # 获取所有符合条件的商品ID
        filtered_item_ids = [item.id for item in base_query.all()]
        
        for weight in weights_query.all():
            if weight.item_id in filtered_item_ids:
                item = db.query(Item).filter(Item.id == weight.item_id).first()
                if item and item.status == "online" and not item.sold:
                    weighted_items.append(item)
                    if len(weighted_items) >= limit:
                        break
        
        # 如果权重排序的商品不够，补充其他商品
        if len(weighted_items) < limit:
            remaining_limit = limit - len(weighted_items)
            used_ids = [item.id for item in weighted_items]
            
            additional_items = base_query.filter(
                ~Item.id.in_(used_ids)
            ).order_by(desc(Item.created_at)).limit(remaining_limit).all()
            
            weighted_items.extend(additional_items)
        
        return weighted_items[skip:skip + limit]
    else:
        # 如果没有权重记录，使用智能评分排序
        all_items = base_query.all()
        
        # 计算每个商品的智能评分并排序
        items_with_scores = []
        for item in all_items:
            score = calculate_smart_score(item)
            items_with_scores.append((item, score))
        
        # 按评分降序排序
        items_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回指定范围的商品
        sorted_items = [item for item, score in items_with_scores]
        return sorted_items[skip:skip + limit]

def update_item_position_rank(db: Session, metrics_list: List[ItemSortingMetrics]):
    """更新商品在指标记录中的排名位置"""
    # 按综合分数排序（浏览量+点赞+收藏+消息+活跃度）
    sorted_metrics = sorted(metrics_list, key=lambda m: (
        m.views_count * 0.3 +
        m.likes_count * 0.25 +
        m.favorites_count * 0.2 +
        m.messages_count * 0.15 +
        m.seller_activity_score * 0.1
    ), reverse=True)
    
    # 更新排名位置
    for rank, metrics in enumerate(sorted_metrics, 1):
        metrics.position_rank = rank
        db.commit()

def run_sorting_algorithm(db: Session, time_window_minutes: int = 30) -> Dict:
    """运行完整的排序算法"""
    now = datetime.utcnow()
    time_window_start = now - timedelta(minutes=time_window_minutes)
    time_window_end = now
    
    # 生成时间周期标识
    time_period = now.strftime("%Y-%m-%d-%H:%M")
    
    # 1. 收集当前时间段的指标数据
    current_metrics = collect_item_metrics_for_period(db, time_window_start, time_window_end)
    
    # 2. 更新排名位置
    update_item_position_rank(db, current_metrics)
    
    # 3. 计算权重并生成排序
    previous_time_period = (now - timedelta(minutes=time_window_minutes)).strftime("%Y-%m-%d-%H:%M")
    
    weights_created = 0
    for metrics in current_metrics:
        # 获取上一周期的指标数据
        previous_metrics = db.query(ItemSortingMetrics).filter(
            ItemSortingMetrics.item_id == metrics.item_id,
            ItemSortingMetrics.time_window_start == time_window_start - timedelta(minutes=time_window_minutes),
            ItemSortingMetrics.time_window_end == time_window_start
        ).first()
        
        # 获取上一周期的排名位置
        previous_weight = db.query(ItemSortingWeights).filter(
            ItemSortingWeights.item_id == metrics.item_id,
            ItemSortingWeights.time_period == previous_time_period
        ).first()
        
        previous_position = previous_weight.ranking_position if previous_weight else None
        
        # 计算各项权重
        base_weight = 1.0  # 基础权重
        trend_weight = calculate_trend_weight(metrics, previous_metrics)
        position_weight = calculate_position_weight(
            metrics.position_rank, previous_position, len(current_metrics)
        )
        final_weight = calculate_final_weight(base_weight, trend_weight, position_weight)
        
        # 创建权重记录
        create_item_weight(
            db, metrics.item_id, time_period,
            base_weight, trend_weight, position_weight, final_weight
        )
        weights_created += 1
    
    # 4. 更新最终排名位置
    weights_query = db.query(ItemSortingWeights).filter(
        ItemSortingWeights.time_period == time_period
    ).order_by(desc(ItemSortingWeights.final_weight))
    
    for rank, weight in enumerate(weights_query.all(), 1):
        weight.ranking_position = rank
        db.commit()
    
    return {
        "success": True,
        "time_period": time_period,
        "metrics_collected": len(current_metrics),
        "weights_created": weights_created,
        "time_window_minutes": time_window_minutes
    }
