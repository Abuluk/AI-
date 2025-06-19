from sqlalchemy.orm import Session
from db.models import Favorite

def create_favorite(db: Session, favorite):
    db_favorite = Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def get_favorite(db: Session, favorite_id: int):
    return db.query(Favorite).filter(Favorite.id == favorite_id).first()

def get_favorites_by_user(db: Session, user_id: int):
    return db.query(Favorite).filter(Favorite.user_id == user_id).all()

def delete_favorite(db: Session, favorite_id: int):
    db_favorite = get_favorite(db, favorite_id)
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return db_favorite