from fastapi import APIRouter, Depends, HTTPException, Query, Form, Body
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from db.session import get_db
from core.security import get_current_user, create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from db.models import User, Item, Favorite, SiteConfig, Message, BuyRequest, Merchant
from schemas.user import UserInDB
from schemas.item import ItemInDB, SiteConfigSchema
from schemas.buy_request import BuyRequest as BuyRequestSchema
from typing import List, Optional
from datetime import datetime, timedelta
from crud import crud_message, crud_buy_request
import schemas.message
from schemas.token import Token
import json
from config import get_full_image_url

router = APIRouter()

@router.post("/login", response_model=Token, tags=["管理员认证"])
def admin_login(
    identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    管理员登录接口。
    这个接口是公开的，但会验证用户是否为管理员。
    """
    # 1. 验证用户名和密码
    user = authenticate_user(db, identifier, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="管理员账号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 验证是否是管理员
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="该账号没有管理员权限",
        )
        
    # 3. 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="管理员账号未激活",
        )
    
    # 4. 创建Token
    token_subject = user.username if user.username else user.email
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_subject}, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_admin(current_user: User = Depends(get_current_user)):
    """验证当前用户是否为管理员"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

# 管理员统计信息
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取管理员统计信息"""
    total_users = db.query(func.count(User.id)).scalar()
    total_items = db.query(func.count(Item.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    online_items = db.query(func.count(Item.id)).filter(Item.status == "online").scalar()
    sold_items = db.query(func.count(Item.id)).filter(Item.sold == True).scalar()
    total_favorites = db.query(func.count(Favorite.id)).scalar()
    
    return {
        "total_users": total_users,
        "total_items": total_items,
        "active_users": active_users,
        "online_items": online_items,
        "sold_items": sold_items,
        "total_favorites": total_favorites
    }

# 用户管理
@router.get("/users", response_model=List[UserInDB])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_admin: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取所有用户列表"""
    query = db.query(User)
    # 搜索过滤
    if search:
        # 构建搜索条件：ID精确匹配 OR 用户名/邮箱/手机号模糊匹配
        search_conditions = []
        
        # 添加文本字段模糊搜索
        text_search = (
            User.username.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.phone.ilike(f"%{search}%")
        )
        search_conditions.append(text_search)
        
        # 如果搜索词是数字，也添加ID精确搜索
        try:
            user_id = int(search)
            id_search = User.id == user_id
            search_conditions.append(id_search)
        except ValueError:
            pass  # 不是数字，跳过ID搜索
        
        # 使用OR连接所有搜索条件
        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))
    # 状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    # 管理员过滤
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    # 按创建时间倒序
    query = query.order_by(User.created_at.desc())
    users = query.offset(skip).limit(limit).all()
    result = []
    for user in users:
        items_count = db.query(func.count(Item.id)).filter(Item.owner_id == user.id).scalar()
        avatar = get_full_image_url(user.avatar)
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": avatar,
            "bio": user.bio,
            "location": user.location,
            "contact": user.contact,
            "phone": user.phone,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "followers": user.followers,
            "following": user.following,
            "items_count": items_count
        })
    return result

@router.get("/search-users")
def search_users_for_merchant_management(
    search: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """搜索用户（用于商家管理）"""
    # 构建搜索条件：ID精确匹配 OR 用户名/邮箱/手机号模糊匹配
    search_conditions = []
    
    # 添加文本字段模糊搜索
    text_search = (
        User.username.ilike(f"%{search}%") |
        User.email.ilike(f"%{search}%") |
        User.phone.ilike(f"%{search}%")
    )
    search_conditions.append(text_search)
    
    # 如果搜索词是数字，也添加ID精确搜索
    try:
        user_id = int(search)
        id_search = User.id == user_id
        search_conditions.append(id_search)
    except ValueError:
        pass  # 不是数字，跳过ID搜索
    
    # 使用OR连接所有搜索条件
    if search_conditions:
        from sqlalchemy import or_
        query = db.query(User).filter(or_(*search_conditions))
    else:
        query = db.query(User)
    
    # 按创建时间倒序，限制数量
    users = query.order_by(User.created_at.desc()).limit(limit).all()
    
    result = []
    for user in users:
        # 获取用户的商家信息
        merchant = db.query(Merchant).filter(Merchant.user_id == user.id).first()
        
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": get_full_image_url(user.avatar),
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "is_merchant": user.is_merchant,
            "is_pending_merchant": user.is_pending_merchant,
            "is_pending_verification": user.is_pending_verification,
            "created_at": user.created_at,
            "merchant": {
                "id": merchant.id,
                "business_name": merchant.business_name,
                "status": merchant.status,
                "created_at": merchant.created_at
            } if merchant else None
        })
    
    return result

@router.get("/users/{user_id}", response_model=UserInDB)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取用户详细信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算用户的商品数量
    items_count = db.query(func.count(Item.id)).filter(Item.owner_id == user_id).scalar()
    
    # 处理用户头像URL
    avatar = get_full_image_url(user.avatar)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": avatar,
        "bio": user.bio,
        "location": user.location,
        "contact": user.contact,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "followers": user.followers,
        "following": user.following,
        "items_count": items_count
    }

@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新用户状态（激活/禁用）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能禁用自己
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    
    # 处理用户头像URL
    avatar = get_full_image_url(user.avatar)
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": avatar,
        "bio": user.bio,
        "location": user.location,
        "contact": user.contact,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "followers": user.followers,
        "following": user.following
    }
    
    return {"message": f"用户已{'激活' if is_active else '禁用'}", "user": user_dict}

@router.patch("/users/{user_id}/admin")
def update_user_admin_status(
    user_id: int,
    is_admin: bool,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新用户管理员状态"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能取消自己的管理员权限
    if user_id == current_admin.id and not is_admin:
        raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")
    
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    
    # 处理用户头像URL
    avatar = get_full_image_url(user.avatar)
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": avatar,
        "bio": user.bio,
        "location": user.location,
        "contact": user.contact,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "followers": user.followers,
        "following": user.following
    }
    
    return {"message": f"用户已{'设为管理员' if is_admin else '取消管理员权限'}", "user": user_dict}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不能删除自己
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    
    # 删除用户的所有商品
    db.query(Item).filter(Item.owner_id == user_id).delete()
    
    # 删除用户的所有收藏
    db.query(Favorite).filter(Favorite.user_id == user_id).delete()
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {"message": "用户已删除"}

# 商品管理
@router.get("/items", response_model=List[ItemInDB])
def get_all_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    sold: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取所有商品列表"""
    query = db.query(Item)
    
    # 搜索过滤
    if search:
        query = query.filter(
            Item.title.ilike(f"%{search}%") |
            Item.description.ilike(f"%{search}%")
        )
    
    # 状态过滤
    if status:
        query = query.filter(Item.status == status)
    
    # 售出状态过滤
    if sold is not None:
        query = query.filter(Item.sold == sold)
    
    # 分类过滤
    if category:
        query = query.filter(Item.category == category)
    
    # 按创建时间倒序
    query = query.order_by(Item.created_at.desc())
    
    items = query.offset(skip).limit(limit).all()
    for item in items:
        if item.images:
            images = item.images.split(',')
            processed_images = []
            for img in images:
                if img.strip():
                    if not img.startswith('/'):
                        img = '/' + img
                    processed_images.append(img)
            item.images = ','.join(processed_images)
    return items

@router.get("/items/{item_id}", response_model=ItemInDB)
def get_item_detail(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取商品详细信息"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    return item

@router.patch("/items/{item_id}/status")
def update_item_status(
    item_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新商品状态"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    if status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="状态值无效")
    
    # 如果是要下架商品，发送系统消息给商品所有者
    if status == "offline" and item.status == "online":
        # 创建系统消息
        system_message = schemas.message.SystemMessageCreate(
            title="商品下架通知",
            content=f"您的商品《{item.title}》因不合规内容已被管理员下架。如有疑问，请联系客服。",
            target_users=str(item.owner_id),  # 发送给商品所有者
            item_id=item_id  # 关联到具体商品
        )
        
        # 发送系统消息
        try:
            crud_message.create_system_message(db=db, message_in=system_message, admin_id=current_admin.id)
        except Exception as e:
            # 记录错误但不影响商品状态更新
            print(f"发送系统消息失败: {e}")
    
    item.status = status
    db.commit()
    db.refresh(item)
    
    return {"message": f"商品已{'上架' if status == 'online' else '下架'}", "item": item}

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除商品"""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 删除相关的收藏记录
    db.query(Favorite).filter(Favorite.item_id == item_id).delete()
    
    # 删除商品
    db.delete(item)
    db.commit()
    
    return {"message": "商品已删除"}

# 消息管理 (管理员)
@router.post("/messages", response_model=schemas.message.MessageResponse)
def post_system_message(
    message_in: schemas.message.SystemMessageCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """发布系统消息"""
    return crud_message.create_system_message(db=db, message_in=message_in, admin_id=current_admin.id)

@router.get("/messages", response_model=List[schemas.message.MessageResponse])
def get_system_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取所有系统消息"""
    return crud_message.get_system_messages(db=db, skip=skip, limit=limit)

@router.delete("/messages/{id}")
def delete_system_message(
    id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除系统消息（仅 Message 表，is_system=True）"""
    message = db.query(Message).filter(Message.id == id, Message.is_system == True).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    db.delete(message)
    db.commit()
    return {"message": "系统消息已删除"}

@router.post("/site_config/activity_banner", response_model=SiteConfigSchema)
def set_activity_banner(
    value: list = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    config = db.query(SiteConfig).filter(SiteConfig.key == "activity_banner").first()
    value_str = json.dumps(value, ensure_ascii=False)
    if not config:
        config = SiteConfig(key="activity_banner", value=value_str)
        db.add(config)
    else:
        config.value = value_str
    db.commit()
    db.refresh(config)
    return SiteConfigSchema(key="activity_banner", value=value)

@router.get("/site_config/activity_banner", response_model=SiteConfigSchema)
def get_activity_banner_admin(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    config = db.query(SiteConfig).filter(SiteConfig.key == "activity_banner").first()
    if not config or not config.value:
        return SiteConfigSchema(key="activity_banner", value=None)
    return SiteConfigSchema(key="activity_banner", value=json.loads(config.value))

@router.get("/buy_requests", response_model=List[BuyRequestSchema])
def get_all_buy_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取所有求购信息列表"""
    brs = crud_buy_request.get_all_buy_requests_admin(db, skip=skip, limit=limit, search=search)
    for br in brs:
        if br.images and isinstance(br.images, str):
            br.images = br.images.split(",")
        elif not br.images:
            br.images = []
        
        # 处理用户头像URL
        if br.user and br.user.avatar:
            br.user.avatar = get_full_image_url(br.user.avatar)
    return brs

@router.delete("/buy_requests/{buy_request_id}")
def delete_buy_request(
    buy_request_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """删除求购信息"""
    buy_request = db.query(BuyRequest).filter(BuyRequest.id == buy_request_id).first()
    if not buy_request:
        raise HTTPException(status_code=404, detail="求购信息不存在")
    
    # 删除求购信息
    db.delete(buy_request)
    db.commit()
    
    # 发送系统消息通知发布者
    try:
        message_content = f"您的求购信息「{buy_request.title}」因不合规内容已被管理员删除。如有疑问，请联系客服。"
        system_message = Message(
            title="求购信息被删除通知",
            content=message_content,
            target_users=f"{buy_request.user_id}",
            created_at=datetime.utcnow()
        )
        db.add(system_message)
        db.commit()
    except Exception as e:
        print(f"发送删除通知失败: {e}")
    
    return {"message": "求购信息已删除"}

# 推广位管理接口
@router.get("/promoted_items")
def get_promoted_items(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取推广商品列表"""
    # 从SiteConfig中获取推广商品ID列表
    config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
    if not config or not config.value:
        return []
    
    try:
        promoted_ids = json.loads(config.value)
        if not promoted_ids:
            return []
        
        # 获取推广商品详情
        promoted_items = db.query(Item).filter(Item.id.in_(promoted_ids)).all()
        
        # 按配置的顺序返回
        result = []
        for item_id in promoted_ids:
            item = next((item for item in promoted_items if item.id == item_id), None)
            if item:
                # 处理图片路径
                processed_images = item.images
                if item.images:
                    images = item.images.split(',')
                    processed_images_list = []
                    for img in images:
                        if img.strip():
                            if not img.startswith('/'):
                                img = '/' + img
                            processed_images_list.append(img)
                    processed_images = ','.join(processed_images_list)
                
                # 获取商品所有者信息
                owner = db.query(User).filter(User.id == item.owner_id).first()
                owner_info = {
                    "id": owner.id,
                    "username": owner.username,
                    "avatar": owner.avatar
                } if owner else None
                
                result.append({
                    "id": item.id,
                    "title": item.title,
                    "price": item.price,
                    "description": item.description,
                    "images": processed_images,
                    "status": item.status,
                    "sold": item.sold,
                    "category": item.category,
                    "location": item.location,
                    "views": item.views,
                    "favorited_count": item.favorited_count,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "owner": owner_info
                })
        
        return result
    except Exception as e:
        print(f"获取推广商品失败: {e}")
        return []

@router.put("/promoted_items")
def update_promoted_items(
    item_ids: List[int] = Body(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新推广商品设置"""
    # 验证商品是否存在
    if item_ids:
        existing_items = db.query(Item).filter(Item.id.in_(item_ids)).all()
        if len(existing_items) != len(item_ids):
            raise HTTPException(status_code=400, detail="部分商品不存在")
    
    # 保存到SiteConfig
    config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_items").first()
    if config:
        config.value = json.dumps(item_ids)
    else:
        config = SiteConfig(
            key="promoted_items",
            value=json.dumps(item_ids)
        )
        db.add(config)
    
    db.commit()
    return {"message": "推广商品设置已更新", "item_ids": item_ids}

@router.put("/promoted_items/interval")
def update_promoted_interval(
    interval: int = Body(..., ge=1, le=20, description="推广商品间隔，每多少个商品显示一个推广商品"),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """更新推广商品间隔设置"""
    # 保存到SiteConfig
    config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_interval").first()
    if config:
        config.value = str(interval)
    else:
        config = SiteConfig(
            key="promoted_interval",
            value=str(interval)
        )
        db.add(config)
    
    db.commit()
    return {"message": "推广商品间隔设置已更新", "interval": interval}

@router.get("/promoted_items/interval")
def get_promoted_interval(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """获取推广商品间隔设置"""
    config = db.query(SiteConfig).filter(SiteConfig.key == "promoted_interval").first()
    if not config or not config.value:
        return {"interval": 5}  # 默认间隔为5
    
    try:
        interval = int(config.value)
        return {"interval": interval}
    except ValueError:
        return {"interval": 5}

@router.put("/items/{item_id}/recommendations")
def update_item_recommendations(
    item_id: int,
    recommended_item_ids: List[int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """为特定商品设置推荐商品"""
    # 验证主商品是否存在
    main_item = db.query(Item).filter(Item.id == item_id).first()
    if not main_item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 验证推荐商品是否存在
    if recommended_item_ids:
        existing_items = db.query(Item).filter(Item.id.in_(recommended_item_ids)).all()
        if len(existing_items) != len(recommended_item_ids):
            raise HTTPException(status_code=400, detail="部分推荐商品不存在")
    
    # 保存到SiteConfig
    config_key = f"item_recommendations_{item_id}"
    config = db.query(SiteConfig).filter(SiteConfig.key == config_key).first()
    if config:
        config.value = json.dumps(recommended_item_ids)
    else:
        config = SiteConfig(
            key=config_key,
            value=json.dumps(recommended_item_ids)
        )
        db.add(config)
    
    db.commit()
    return {"message": "商品推荐设置已更新", "item_id": item_id, "recommended_item_ids": recommended_item_ids} 