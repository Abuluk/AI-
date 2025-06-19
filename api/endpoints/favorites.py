from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import Favorite, User
from schemas.favorite import FavoriteCreate, FavoriteInDB
from core.security import get_current_user

def get_favorite(db: Session, favorite_id: int):
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()

def get_favorites_by_user(db: Session, user_id: int):
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()

router = APIRouter()

@router.post("/", response_model=FavoriteInDB)
def create_favorite(
    favorite: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 验证用户只能为自己创建收藏
    if favorite.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="不能为其他用户创建收藏")
    
    return create_favorite(db, favorite)

@router.get("/user/{user_id}", response_model=list[FavoriteInDB])
def read_user_favorites(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看其他用户的收藏")
    
    return get_favorites_by_user(db, user_id=user_id)

@router.delete("/{favorite_id}")
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
    
    delete_favorite(db, favorite_id=favorite_id)
    return {"message": "收藏已删除"}