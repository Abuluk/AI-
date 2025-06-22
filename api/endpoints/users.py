from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user, get_current_user
from db.models import User
from db.models import Item
from schemas.user import UserInDB, UserUpdate
from db.models import Favorite
from schemas.item import ItemInDB
from schemas.favorite import FavoriteInDB
from typing import List, Optional
from crud.crud_user import (
    get_user,
    update_user,
    delete_user
)

router = APIRouter()

@router.get("/me", response_model=UserInDB)
def read_user_me(
    current_user: UserInDB = Depends(get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserInDB)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    return update_user(db, user_id=current_user.id, user_update=user_update)

@router.delete("/me")
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    delete_user(db, user_id=current_user.id)
    return {"message": "用户已删除"}

@router.get("/{user_id}/stats")
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    # 获取用户商品统计
    selling_count = db.query(Item).filter(
        Item.owner_id == user_id,
        Item.sold == False
    ).count()
    
    sold_count = db.query(Item).filter(
        Item.owner_id == user_id,
        Item.sold == True
    ).count()
    
    # 获取用户收藏统计
    favorites_count = db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).count()
    
    return {
        "selling": selling_count,
        "sold": sold_count,
        "favorites": favorites_count
    }

# 添加用户商品查询路由
# users.py
@router.get("/{user_id}/items", response_model=List[ItemInDB])
def get_user_items(
    user_id: int,
    status: Optional[str] = Query("selling", description="商品状态: selling(在售), sold(已售), offline(下架)"),
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(10, description="每页记录数"),
    order_by: str = Query("created_at_desc", description="排序方式: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎)"),
    db: Session = Depends(get_db)
):
    """
    获取指定用户的商品列表，可按状态筛选和排序
    """
    # 验证用户存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 根据状态筛选商品
    query = db.query(Item).filter(Item.owner_id == user_id)
    
    if status == "selling":
        # 在售商品：未售出且状态为 online
        query = query.filter(Item.sold == False, Item.status == "online")
    elif status == "sold":
        # 已售商品：已售出
        query = query.filter(Item.sold == True)
    elif status == "offline":
        # 已下架商品：状态为 offline
        query = query.filter(Item.status == "offline")
    else:
        # 如果是不支持的状态，返回空列表
        return []
    
    # 根据排序参数进行排序
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        # 默认按最新发布排序
        query = query.order_by(Item.created_at.desc())
    
    # 添加分页
    items = query.offset(skip).limit(limit).all()
    return items

@router.get("/{user_id}", response_model=UserInDB)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.get("/me", response_model=UserInDB)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user