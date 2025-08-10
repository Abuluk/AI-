from sqlalchemy.orm import Session
from db.models import Blacklist, User
from datetime import datetime

def add_to_blacklist(db: Session, user_id: int, blocked_user_id: int):
    if user_id == blocked_user_id:
        return None
    exists = db.query(Blacklist).filter_by(user_id=user_id, blocked_user_id=blocked_user_id).first()
    if exists:
        return exists
    bl = Blacklist(user_id=user_id, blocked_user_id=blocked_user_id, created_at=datetime.utcnow())
    db.add(bl)
    db.commit()
    db.refresh(bl)
    return bl

def remove_from_blacklist(db: Session, user_id: int, blocked_user_id: int):
    bl = db.query(Blacklist).filter_by(user_id=user_id, blocked_user_id=blocked_user_id).first()
    if bl:
        db.delete(bl)
        db.commit()
        return True
    return False

def get_blacklist(db: Session, user_id: int):
    return db.query(Blacklist).filter_by(user_id=user_id).all() 