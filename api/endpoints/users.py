from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from db.models import User
from db.models import Item
from schemas.user import UserInDB, UserUpdate
from db.models import Favorite
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