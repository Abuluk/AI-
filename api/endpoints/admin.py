from fastapi import APIRouter, Depends, HTTPException, Query, Form, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from core.security import get_current_user, create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from db.models import User, Item, Favorite, SiteConfig
from schemas.user import UserInDB
from schemas.item import ItemInDB, SiteConfigSchema
from typing import List, Optional
from datetime import datetime, timedelta
from crud import crud_message
import schemas.message
from schemas.token import Token
import json

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
        query = query.filter(
            User.username.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.phone.ilike(f"%{search}%")
        )
    
    # 状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 管理员过滤
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    # 按创建时间倒序
    query = query.order_by(User.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

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
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
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
    
    return {"message": f"用户已{'激活' if is_active else '禁用'}", "user": user}

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
    
    return {"message": f"用户已{'设为管理员' if is_admin else '取消管理员权限'}", "user": user}

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
    
    return query.offset(skip).limit(limit).all()

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