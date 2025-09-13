from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form, BackgroundTasks
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from crud import crud_item
from schemas.item import ItemCreate, ItemInDB, SiteConfigSchema
from core.security import get_current_user, get_current_active_user, get_current_user_optional
from db.models import User, SiteConfig
import os
import uuid
from db.models import Item
from sqlalchemy import or_
from core.spark_ai import spark_ai_service
import json
from fastapi.encoders import jsonable_encoder
from crud.crud_item import like_item, unlike_item
from db.models import ItemLike, MerchantDisplayConfig
from config import get_image_base_url, get_full_image_url
from crud.crud_merchant import get_merchant_display_config
from crud import crud_item_sorting

router = APIRouter()

def get_items_with_merchant_display(
    normal_items: List[Item], 
    merchant_items: List[Item], 
    display_frequency: int, 
    target_size: int
) -> List[Item]:
    """根据展示频率混合普通商品和商家商品"""
    result = []
    normal_index = 0
    merchant_index = 0
    items_added = 0
    
    # 按展示频率插入商家商品
    while items_added < target_size and (normal_index < len(normal_items) or merchant_index < len(merchant_items)):
        # 添加普通商品
        if normal_index < len(normal_items):
            result.append(normal_items[normal_index])
            normal_index += 1
            items_added += 1
            
            # 检查是否需要插入商家商品（每隔display_frequency个普通商品后插入一个商家商品）
            if (items_added % display_frequency == 0 and merchant_index < len(merchant_items)):
                merchant_item = merchant_items[merchant_index % len(merchant_items)]
                # 创建新的对象避免重复引用
                import copy
                new_merchant_item = copy.deepcopy(merchant_item)
                new_merchant_item.is_promoted = True  # 标记为推广商品
                result.append(new_merchant_item)
                merchant_index += 1
                items_added += 1
                
                # 如果已经达到目标数量，跳出循环
                if items_added >= target_size:
                    break
        else:
            # 如果普通商品用完了，继续添加商家商品
            if merchant_index < len(merchant_items):
                merchant_item = merchant_items[merchant_index % len(merchant_items)]
                import copy
                new_merchant_item = copy.deepcopy(merchant_item)
                new_merchant_item.is_promoted = True
                result.append(new_merchant_item)
                merchant_index += 1
                items_added += 1
            else:
                break
    
    return result[:target_size]

# 公共端点 - 获取AI分析的低价好物推荐
@router.get("/ai-cheap-deals")
def get_ai_cheap_deals(
    limit: int = Query(10, ge=1, le=20, description="获取商品数量"),
    db: Session = Depends(get_db)
):
    """获取AI分析的低价好物推荐"""
    try:
        # 获取当前在售的商品
        items = db.query(Item).filter(
            Item.status == "online",
            Item.sold == False
        ).order_by(Item.price.asc()).limit(limit).all()
        
        # 转换为字典格式
        items_data = []
        for item in items:
            items_data.append({
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.condition,
                "description": item.description,
                "category": item.category,
                "location": item.location,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "user": {
                    "id": item.owner_id,
                    "username": item.owner.username if item.owner else "未知用户"
                } if item.owner else None
            })
        
        # 调用AI服务进行分析
        ai_result = spark_ai_service.analyze_price_competition(items_data)
        
        if ai_result.get("success"):
            # 将AI推荐的商品与数据库中的商品信息合并
            recommendations = ai_result.get("recommendations", [])
            enhanced_recommendations = []
            
            for rec in recommendations:
                # 在数据库中找到对应的商品
                matching_item = next(
                    (item for item in items_data if item["title"] == rec["title"]), 
                    None
                )
                
                if matching_item:
                    enhanced_recommendations.append({
                        **matching_item,
                        "ai_reason": rec.get("reason", ""),
                        "ai_price": rec.get("price", matching_item["price"])
                    })
            
            return {
                "success": True,
                "analysis": ai_result.get("analysis", ""),
                "market_insights": ai_result.get("market_insights", ""),
                "recommendations": enhanced_recommendations,
                "total_items_analyzed": len(items_data)
            }
        else:
            # 如果AI服务失败，返回简单的低价商品列表
            return {
                "success": False,
                "message": ai_result.get("message", "AI分析服务暂时不可用"),
                "fallback_recommendations": items_data[:5],  # 返回前5个最低价的商品
                "total_items_analyzed": len(items_data)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取AI推荐失败: {str(e)}"
        )

@router.get("/promoted")
def get_promoted_items(db: Session = Depends(get_db)):
    """获取推广商品列表（公开接口）"""
    # 从SiteConfig中获取推广商品ID列表
    config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
    if not config or not config.value:
        return []
    
    try:
        promoted_ids = json.loads(config.value)
        if not promoted_ids:
            return []
        
        # 获取推广商品详情，只返回在售且未售出的商品
        promoted_items = db.query(Item).filter(
            Item.id.in_(promoted_ids),
            Item.status == "online",
            Item.sold == False
        ).all()
        
        # 按配置的顺序返回
        result = []
        for item_id in promoted_ids:
            item = next((item for item in promoted_items if item.id == item_id), None)
            if item:
                # 处理图片路径
                if item.images:
                    images = item.images.split(',')
                    processed_images = []
                    for img in images:
                        img = img.strip()
                        if img:
                            # 使用统一的图片URL处理函数
                            full_url = get_full_image_url(img)
                            if full_url:
                                processed_images.append(full_url)
                    item.images = ','.join(processed_images)
                
                result.append(item)
        
        return result
    except Exception as e:
        print(f"获取推广商品失败: {e}")
        return []

@router.get("/site_config/activity_banner", response_model=SiteConfigSchema)
def get_activity_banner(db: Session = Depends(get_db)):
    config = db.query(SiteConfig).filter(SiteConfig.key == "activity_banner").first()
    if not config or not config.value:
        return SiteConfigSchema(key="activity_banner", value=None)
    return SiteConfigSchema(key="activity_banner", value=json.loads(config.value))

@router.get("/with_promoted")
def get_items_with_promoted(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="商品分类"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    location: Optional[str] = Query(None, description="地区过滤"),
    order_by: Optional[str] = Query("created_at_desc", description="排序方式"),
    user_id: Optional[int] = Query(None, description="用户ID（用于获取个人展示配置）"),
    db: Session = Depends(get_db)
):
    """获取商品列表，支持间隔显示推广商品和商家商品"""
    # 获取商家商品展示配置
    display_frequency = 5  # 默认展示频率
    if user_id:
        # 获取用户个人配置
        user_config = get_merchant_display_config(db, user_id)
        if user_config:
            display_frequency = user_config.display_frequency
    else:
        # 获取全局默认配置
        default_config = get_merchant_display_config(db, None)
        if default_config:
            display_frequency = default_config.display_frequency
    
    # 获取推广商品配置
    promoted_config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
    interval_config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_interval").first()
    
    promoted_items = []
    interval = 5  # 默认间隔
    
    if interval_config and interval_config.value:
        try:
            interval = int(interval_config.value)
        except ValueError:
            interval = 5
    
    if promoted_config and promoted_config.value:
        try:
            promoted_ids = json.loads(promoted_config.value)
            if promoted_ids:
                # 获取推广商品详情
                promoted_items = db.query(Item).filter(
                    Item.id.in_(promoted_ids),
                    Item.status == "online",
                    Item.sold == False
                ).all()
                
                # 处理推广商品图片路径
                for item in promoted_items:
                    if item.images:
                        images = item.images.split(',')
                        processed_images = []
                        for img in images:
                            img = img.strip()
                            if img:
                                full_url = get_full_image_url(img)
                                if full_url:
                                    processed_images.append(full_url)
                        item.images = ','.join(processed_images)
        except Exception as e:
            print(f"获取推广商品配置失败: {e}")
    
    # 构建查询条件
    query = db.query(Item).filter(Item.status.in_(["online", "active"]), Item.sold == False)
    
    # 分类过滤
    if category is not None and category != "":
        try:
            category_id = int(category)
            query = query.filter(Item.category == category_id)
        except ValueError:
            pass
    
    # 搜索过滤
    if search is not None and search != "":
        query = query.filter(
            or_(
                Item.title.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%")
            )
        )
    
    # 地区过滤
    if location is not None and location != "":
        query = query.filter(Item.location.ilike(f"%{location}%"))
    
    # 排序
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        query = query.order_by(Item.created_at.desc())
    
    # 分离普通商品和商家商品
    skip = (page - 1) * size
    all_items = query.offset(skip).limit(size * 3).all()  # 获取更多商品以便混合
    
    # 分离普通商品和商家商品
    normal_items = []
    merchant_items = []
    promoted_ids = [item.id for item in promoted_items] if promoted_items else []
    
    for item in all_items:
        if item.id in promoted_ids:
            continue  # 跳过推广商品
        elif item.is_merchant_item:
            merchant_items.append(item)
        else:
            normal_items.append(item)
    
    # 处理图片路径
    for item in normal_items + merchant_items:
        if item.images:
            images = item.images.split(',')
            processed_images = []
            for img in images:
                img = img.strip()
                if img:
                    full_url = get_full_image_url(img)
                    if full_url:
                        processed_images.append(full_url)
            item.images = ','.join(processed_images)
    
    # 混合普通商品和商家商品
    mixed_items = get_items_with_merchant_display(normal_items, merchant_items, display_frequency, size)
    
    # 插入推广商品
    result = []
    promoted_index = 0
    mixed_index = 0
    items_added = 0
    
    # 第一个位置总是推广商品（如果有的话）
    if promoted_items and promoted_index < len(promoted_items):
        promoted_item = promoted_items[promoted_index]
        promoted_item.is_promoted = True
        result.append(promoted_item)
        promoted_index += 1
        items_added += 1
    
    # 按间隔插入推广商品
    while items_added < size and mixed_index < len(mixed_items):
        # 添加混合商品
        result.append(mixed_items[mixed_index])
        mixed_index += 1
        items_added += 1
        
        # 检查是否需要插入推广商品（每隔interval个商品后插入一个推广商品）
        if (items_added % interval == 0 and promoted_items and promoted_index < len(promoted_items)):
            promoted_item = promoted_items[promoted_index % len(promoted_items)]
            # 创建新的对象避免重复引用
            import copy
            new_promoted_item = copy.deepcopy(promoted_item)
            new_promoted_item.is_promoted = True
            result.append(new_promoted_item)
            promoted_index += 1
            items_added += 1
            
            # 如果已经达到目标数量，跳出循环
            if items_added >= size:
                break
    
    # 如果还有剩余位置，继续添加混合商品
    while items_added < size and mixed_index < len(mixed_items):
        result.append(mixed_items[mixed_index])
        mixed_index += 1
        items_added += 1
    
    # 限制返回数量
    return result[:size]

# 公共端点 - 获取所有商品（无需认证）
@router.get("", response_model=List[ItemInDB])
def get_all_items(
    # 支持小程序前端的参数格式
    page: Optional[int] = Query(None, ge=1, description="页码（小程序前端）"),
    size: Optional[int] = Query(None, ge=1, le=100, description="每页数量（小程序前端）"),
    sort_by: Optional[str] = Query(None, description="排序方式（小程序前端）: created_at(最新发布), price(价格), views(最受欢迎)"),
    category: Optional[str] = Query(None, description="商品分类（小程序前端）"),
    search: Optional[str] = Query(None, description="搜索关键词（小程序前端）"),
    location: Optional[str] = Query(None, description="地区过滤（小程序前端）"),
    # 支持web前端的原有参数格式
    skip: Optional[int] = Query(None, ge=0, description="跳过数量（web前端）"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="限制数量（web前端）"),
    order_by: Optional[str] = Query(None, description="排序方式（web前端）: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎), dynamic_sort(动态排序)"),
    exclude_promoted: Optional[bool] = Query(None, description="是否排除推广商品"),
    status: Optional[str] = Query(None, description="商品状态: online, offline"),
    sold: Optional[bool] = Query(None, description="是否已售出"),
    user_id: Optional[int] = Query(None, description="用户ID（用于获取个人展示配置）"),
    db: Session = Depends(get_db)
):
    """获取所有商品列表，支持分页、排序和分类过滤
    
    支持两种参数格式：
    1. 小程序前端：page, size, sort_by, category, search
    2. web前端：skip, limit, order_by, exclude_promoted, status, sold
    """
    # 参数转换：优先使用web前端参数，如果没有则转换小程序前端参数
    if skip is None and page is not None:
        skip = (page - 1) * (size or 10)
    if limit is None and size is not None:
        limit = size
    
    # 设置默认值
    if skip is None:
        skip = 0
    if limit is None:
        limit = 100
    
    # 排序参数转换：优先使用web前端参数，如果没有则转换小程序前端参数
    if order_by is None and sort_by is not None:
        if sort_by == "created_at":
            order_by = "created_at_desc"
        elif sort_by == "price":
            order_by = "price_asc"
        elif sort_by == "views":
            order_by = "views_desc"
        else:
            order_by = "created_at_desc"
    
    # 设置默认排序
    if order_by is None:
        order_by = "created_at_desc"
    
    # 获取商家商品展示配置
    display_frequency = 5  # 默认展示频率
    if user_id:
        # 获取用户个人配置
        user_config = get_merchant_display_config(db, user_id)
        if user_config:
            display_frequency = user_config.display_frequency
    else:
        # 获取全局默认配置
        default_config = get_merchant_display_config(db, None)
        if default_config:
            display_frequency = default_config.display_frequency
    
    query = db.query(Item)
    
    # 状态过滤
    if status is not None:
        query = query.filter(Item.status == status)
    else:
        # 默认只显示在线商品
        query = query.filter(Item.status.in_(["online", "active"]))
    
    # 售出状态过滤
    if sold is not None:
        query = query.filter(Item.sold == sold)
    else:
        # 默认只显示未售出商品
        query = query.filter(Item.sold == False)
    
    # 分类过滤
    if category is not None and category != "":
        try:
            category_id = int(category)
            query = query.filter(Item.category == category_id)
        except ValueError:
            # 如果category不是数字，忽略此过滤条件
            pass
    
    # 搜索过滤
    if search is not None and search != "":
        query = query.filter(
            or_(
                Item.title.ilike(f"%{search}%"),
                Item.description.ilike(f"%{search}%")
            )
        )
    
    # 地区过滤
    if location is not None and location != "":
        # 使用模糊匹配，忽略大小写
        query = query.filter(Item.location.ilike(f"%{location}%"))
    
    # 排除推广商品
    if exclude_promoted:
        # 获取推广商品ID列表
        config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
        if config and config.value:
            try:
                promoted_ids = json.loads(config.value)
                if promoted_ids:
                    query = query.filter(~Item.id.in_(promoted_ids))
            except Exception as e:
                print(f"解析推广商品配置失败: {e}")
    
    # 排序
    if order_by == "dynamic_sort":
        # 使用动态排序算法
        category_id = None
        if category is not None and category != "":
            try:
                category_id = int(category)
            except ValueError:
                pass
        
        items = crud_item_sorting.get_items_with_dynamic_sorting(
            db, skip, limit, 
            category=category_id,
            search=search,
            location=location
        )
        # 处理图片路径
        for item in items:
            if item.images:
                images = item.images.split(',')
                processed_images = []
                for img in images:
                    img = img.strip()
                    if img:
                        full_url = get_full_image_url(img)
                        if full_url:
                            processed_images.append(full_url)
                item.images = ','.join(processed_images)
        return items
    elif order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        query = query.order_by(Item.created_at.desc())
    
    # 获取推广商品配置
    promoted_config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
    promoted_items = []
    
    if promoted_config and promoted_config.value and not exclude_promoted:
        try:
            promoted_ids = json.loads(promoted_config.value)
            if promoted_ids:
                # 获取推广商品详情
                promoted_items = db.query(Item).filter(
                    Item.id.in_(promoted_ids),
                    Item.status == "online",
                    Item.sold == False
                ).all()
        except Exception as e:
            print(f"解析推广商品配置失败: {e}")
    
    # 获取所有商品
    all_items = query.offset(skip).limit(limit * 2).all()  # 获取更多商品以便混合
    
    # 分离普通商品和商家商品
    normal_items = []
    merchant_items = []
    promoted_ids = [item.id for item in promoted_items] if promoted_items else []
    
    for item in all_items:
        if item.id in promoted_ids:
            continue  # 跳过推广商品，单独处理
        elif item.is_merchant_item:
            merchant_items.append(item)
        else:
            normal_items.append(item)
    
    # 处理图片路径
    for item in normal_items + merchant_items + promoted_items:
        if item.images:
            images = item.images.split(',')
            processed_images = []
            for img in images:
                img = img.strip()
                if img:
                    # 使用统一的图片URL处理函数
                    full_url = get_full_image_url(img)
                    if full_url:
                        processed_images.append(full_url)
            item.images = ','.join(processed_images)
    
    # 混合普通商品和商家商品
    mixed_items = get_items_with_merchant_display(normal_items, merchant_items, display_frequency, limit)
    
    # 插入推广商品
    result = []
    promoted_index = 0
    mixed_index = 0
    items_added = 0
    
    # 第一个位置总是推广商品（如果有的话）
    if promoted_items and promoted_index < len(promoted_items):
        promoted_item = promoted_items[promoted_index]
        promoted_item.is_promoted = True
        result.append(promoted_item)
        promoted_index += 1
        items_added += 1
    
    # 添加混合商品
    while items_added < limit and mixed_index < len(mixed_items):
        result.append(mixed_items[mixed_index])
        mixed_index += 1
        items_added += 1
    
    return result

# 公共端点 - 搜索商品（无需认证）- 必须在/{item_id}之前定义
@router.get("/search", response_model=List[ItemInDB])
def search_items(
    q: str = Query(None, min_length=1),
    skip: int = 0,
    limit: int = 100,
    order_by: str = Query("created_at_desc", description="排序方式: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎)"),
    db: Session = Depends(get_db)
):
    if not q:
        query = db.query(Item).options(joinedload(Item.owner)).filter(
            Item.status == "online",
            Item.sold == False
        )
    else:
        query = db.query(Item).options(joinedload(Item.owner)).filter(
            or_(
                Item.title.ilike(f"%{q}%"),
                Item.description.ilike(f"%{q}%")
            ),
            Item.status == "online",
            Item.sold == False
        )
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        query = query.order_by(Item.created_at.desc())
    items = query.offset(skip).limit(limit).all()
    result = []
    for item in items:
        item_dict = jsonable_encoder(item)
        
        # 处理图片路径
        if item.images:
            images = item.images.split(',')
            processed_images = []
            for img in images:
                img = img.strip()
                if img:
                    full_url = get_full_image_url(img)
                    if full_url:
                        processed_images.append(full_url)
            item_dict["images"] = ','.join(processed_images)
        
        if item.owner:
            item_dict["owner"] = {
                "id": item.owner.id,
                "username": item.owner.username,
                "avatar": item.owner.avatar
            }
        else:
            item_dict["owner"] = None
        result.append(item_dict)
    return result

# 公共端点 - 获取单个商品（无需认证）
@router.get("/{item_id}", response_model=ItemInDB)
def read_item(item_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user_optional)):
    item = db.query(Item).options(joinedload(Item.owner)).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 自动增加浏览量（不管是否登录）
    item.views = (item.views or 0) + 1
    db.commit()
    db.refresh(item)
    
    # 检查当前用户是否已点赞（只有登录用户才检查）
    liked_by_me = False
    if current_user:
        liked_by_me = db.query(ItemLike).filter_by(item_id=item_id, user_id=current_user.id).first() is not None
    
    # 处理图片路径
    processed_images = ""
    if item.images:
        images = item.images.split(',')
        processed_image_list = []
        for img in images:
            img = img.strip()
            if img:
                # 使用统一的图片URL处理函数
                full_url = get_full_image_url(img)
                if full_url:
                    processed_image_list.append(full_url)
        processed_images = ','.join(processed_image_list)
    
    # 获取卖家信息
    owner_info = None
    if item.owner:
        # 动态计算卖家的商品数量
        items_count = db.query(Item).filter(Item.owner_id == item.owner.id).count()
        
        # 处理头像URL
        avatar_url = get_full_image_url(item.owner.avatar)
        
        owner_info = {
            "id": item.owner.id,
            "username": item.owner.username,
            "avatar": avatar_url,
            "location": item.owner.location,
            "bio": item.owner.bio,
            "contact": item.owner.contact,
            "created_at": item.owner.created_at,
            "last_login": item.owner.last_login,
            "items_count": items_count,
            "followers": item.owner.followers or 0,
            "following": item.owner.following or 0
        }
    
    # 构建返回数据，包含点赞信息和卖家信息
    item_data = {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "category": item.category,
        "location": item.location,
        "condition": item.condition,
        "images": processed_images,
        "status": item.status,
        "sold": item.sold,
        "created_at": item.created_at,
        "views": item.views,
        "like_count": item.like_count or 0,
        "liked_by_me": liked_by_me,
        "owner_id": item.owner_id,
        "owner": owner_info,
        "favorited_count": item.favorited_count or 0,
        "is_merchant_item": item.is_merchant_item or False,
        "is_promoted": getattr(item, 'is_promoted', False)
    }
    
    return item_data

# 需要认证的端点
@router.post("", response_model=ItemInDB)
@router.post("/", response_model=ItemInDB)
async def create_item(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    condition: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查用户是否为待认证状态（只有管理员加入待认证名单才限制发布）
    if current_user.is_pending_verification:
        raise HTTPException(status_code=403, detail="您处于待认证状态，无法发布商品")
    
    # 创建商品基础信息
    db_item = Item(
        title=title,
        description=description,
        price=price,
        category=category,
        location=location,
        condition=condition,
        owner_id=current_user.id,
        is_merchant_item=current_user.is_merchant  # 设置是否为商家商品
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 处理图片上传
    image_paths = []
    if images:
        UPLOAD_DIR = "static/images"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        for image in images:
            # 验证文件格式
            ext = os.path.splitext(image.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext}。允许的格式: {', '.join(ALLOWED_EXTENSIONS)}")
            # 确保文件名安全
            safe_filename = f"{db_item.id}_{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
            # 使用正斜杠统一路径格式
            file_path = os.path.join(UPLOAD_DIR, safe_filename).replace(os.sep, '/')
            
            with open(file_path, "wb") as f:
                content = await image.read()
                f.write(content)
            
            image_paths.append(file_path)
    
    # 更新商品图片字段
    if image_paths:
        db_item.images = ",".join(image_paths)
        db.commit()
        db.refresh(db_item)
    
    return db_item

@router.put("/{item_id}", response_model=ItemInDB)
def update_item(
    item_id: int,
    item_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = crud_item.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud_item.update_item(db, item_id, item_update)

@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = crud_item.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    crud_item.delete_item(db, item_id)
    return {"message": "Item deleted"}

@router.post("/{item_id}/upload-image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 确保商品存在且用户有权限
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 保存图片
    UPLOAD_DIR = "static/images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{item_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 更新商品图片字段
    images = item.images.split(",") if item.images else []
    images.append(file_path)
    item.images = ",".join(images)
    db.commit()
    
    return {"message": "Image uploaded", "path": file_path}

@router.patch("/{item_id}/status")
def update_item_status(
    item_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商品状态：online(上架) 或 offline(下架)"""
    # 验证商品存在
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 验证用户权限
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此商品")
    
    # 验证状态值
    if status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="状态值无效，只能是 'online' 或 'offline'")
    
    # 更新状态
    item.status = status
    db.commit()
    db.refresh(item)
    
    return {"message": f"商品已{'上架' if status == 'online' else '下架'}", "item": item}

@router.patch("/{item_id}/views")
def update_item_views(
    item_id: int,
    db: Session = Depends(get_db)
):
    """更新商品浏览量"""
    # 验证商品存在
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 更新浏览量
    item.views += 1
    db.commit()
    db.refresh(item)
    
    return {"message": "浏览量已更新", "views": item.views}

@router.patch("/{item_id}/sold")
def mark_item_sold(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将商品标记为已售"""
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此商品")
    if item.sold:
        return {"message": "商品已售出"}
    item.sold = True
    db.commit()
    db.refresh(item)
    return {"message": "商品已标记为已售", "item": item}

# AI自动补全商品信息（图片识别）
@router.post("/upload_image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传商品图片
    """
    try:
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        # 检查文件大小（限制为5MB）
        file_size = 0
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="图片文件大小不能超过5MB")
        
        # 生成唯一文件名
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # 确保上传目录存在
        upload_dir = os.path.join("static", "uploads", "items")
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 返回图片URL
        image_url = f"/static/uploads/items/{unique_filename}"
        
        return {
            "success": True,
            "image_url": image_url,
            "filename": unique_filename,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片上传失败: {str(e)}")

@router.post("/ai-auto-complete")
async def ai_auto_complete_item_by_image(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    上传图片，AI自动补全商品信息，支持单文件和多文件
    """
    try:
        image_bytes_list = []
        if files:
            image_bytes_list = [await f.read() for f in files]
        elif file:
            image_bytes_list = [await file.read()]
        else:
            return {"success": False, "message": "未收到图片"}
        result = spark_ai_service.auto_complete_item_by_image(image_bytes_list)
        return result
    except Exception as e:
        return {"success": False, "message": f"AI自动补全失败: {str(e)}"}

@router.post("/ai-auto-complete-ws")
async def ai_auto_complete_item_by_image_ws(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    使用websockets库异步方式调用讯飞图片理解API，测试兼容性
    """
    image_bytes_list = []
    if files:
        image_bytes_list = [await f.read() for f in files]
    elif file:
        image_bytes_list = [await file.read()]
    else:
        return {"success": False, "message": "未收到图片"}
    result = await spark_ai_service.auto_complete_item_by_image_ws(image_bytes_list)
    return result

@router.post("/{item_id}/like")
def like_item_api(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    count = like_item(db, item_id, current_user.id)
    if count == -1:
        raise HTTPException(status_code=400, detail="已点赞")
    return {"like_count": count}

@router.post("/{item_id}/unlike")
def unlike_item_api(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    count = unlike_item(db, item_id, current_user.id)
    if count == -1:
        raise HTTPException(status_code=400, detail="未点赞")
    return {"like_count": count}

@router.get("/{item_id}/recommendations")
def get_item_recommendations(
    item_id: int,
    limit: int = Query(4, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """获取商品的推荐商品列表"""
    # 首先检查是否有管理员设置的推荐商品
    config_key = f"item_recommendations_{item_id}"
    config = db.query(SiteConfig).filter(SiteConfig.key == config_key).first()
    
    if config and config.value:
        try:
            recommended_ids = json.loads(config.value)
            if recommended_ids:
                # 获取管理员设置的推荐商品
                recommended_items = db.query(Item).filter(
                    Item.id.in_(recommended_ids),
                    Item.status == "online",
                    Item.sold == False
                ).limit(limit).all()
                
                if recommended_items:
                    return recommended_items
        except Exception as e:
            print(f"解析推荐商品配置失败: {e}")
    
    # 如果没有管理员设置的推荐商品，使用默认推荐逻辑
    # 获取同分类的其他商品
    current_item = db.query(Item).filter(Item.id == item_id).first()
    if not current_item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 获取同分类的其他商品，排除当前商品
    recommended_items = db.query(Item).filter(
        Item.category == current_item.category,
        Item.id != item_id,
        Item.status == "online",
        Item.sold == False
    ).order_by(Item.views.desc()).limit(limit).all()
    
    # 如果同分类商品不够，补充其他分类的商品
    if len(recommended_items) < limit:
        remaining_limit = limit - len(recommended_items)
        other_items = db.query(Item).filter(
            Item.category != current_item.category,
            Item.id != item_id,
            Item.status == "online",
            Item.sold == False
        ).order_by(Item.views.desc()).limit(remaining_limit).all()
        recommended_items.extend(other_items)
    
    return recommended_items