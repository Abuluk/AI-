from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.session import get_db
from db.models import Favorite, User, Item
from schemas.favorite import FavoriteCreate, FavoriteInDB, FavoriteWithItem
from core.security import get_current_user
from datetime import datetime

router = APIRouter()

def get_favorite(db: Session, favorite_id: int):
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()

def get_favorites_by_user(db: Session, user_id: int):
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()

@router.get("/user/{user_id}", response_model=list[FavoriteWithItem])
def read_user_favorites(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看其他用户的收藏")
    
    # 获取收藏记录，并关联商品信息
    favorites = db.query(Favorite).join(Item).filter(
        Favorite.user_id == user_id,
        Item.id.isnot(None)  # 确保商品存在
    ).all()
    
    # 处理created_at为None的情况
    for favorite in favorites:
        if favorite.created_at is None:
            favorite.created_at = datetime.now()
    
    return favorites

@router.delete("/by-id/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_favorite = get_favorite(db, favorite_id=favorite_id)
    if not db_favorite:
        raise HTTPException(status_code=404, detail="收藏不存在")
    if db_favorite.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此收藏")
    
    db.delete(db_favorite)
    db.commit()
    return {"message": "收藏已删除"}

@router.post("/add")
def add_favorite(
    user_id: int = Query(...),
    item_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 检查是否已收藏
    existing = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.item_id == item_id
    ).first()
    
    if existing:
        return {"message": "Already favorited"}
    
    # 创建收藏
    new_fav = Favorite(user_id=user_id, item_id=item_id)
    db.add(new_fav)
    db.commit()
    
    # 更新商品收藏计数
    item = db.query(Item).get(item_id)
    if item:
        item.favorited_count = db.query(func.count(Favorite.id)).filter(
            Favorite.item_id == item_id
        ).scalar()
        db.commit()
    
    return {"message": "Added to favorites"}

@router.delete("/remove")
def remove_favorite(
    user_id: int = Query(...),
    item_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    fav = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.item_id == item_id
    ).first()
    
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    db.delete(fav)
    db.commit()
    
    # 更新商品收藏计数
    item = db.query(Item).get(item_id)
    if item:
        item.favorited_count = db.query(func.count(Favorite.id)).filter(
            Favorite.item_id == item_id
        ).scalar()
        db.commit()
    
    return {"message": "Removed from favorites"}

@router.get("/check")
def check_favorite(
    user_id: int = Query(...),
    item_id: int = Query(...),
    db: Session = Depends(get_db)
):
    fav = db.query(Favorite).filter(
        Favorite.user_id == user_id,
        Favorite.item_id == item_id
    ).first()
    
    return {"isFavorited": fav is not None}