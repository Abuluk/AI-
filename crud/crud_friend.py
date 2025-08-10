from sqlalchemy.orm import Session
from db.models import Friend, User
from datetime import datetime

def add_friend(db: Session, user_id: int, friend_id: int):
    if user_id == friend_id:
        return None
    exists = db.query(Friend).filter_by(user_id=user_id, friend_id=friend_id).first()
    if exists:
        return exists
    friend = Friend(user_id=user_id, friend_id=friend_id, created_at=datetime.utcnow())
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend

def remove_friend(db: Session, user_id: int, friend_id: int):
    friend = db.query(Friend).filter_by(user_id=user_id, friend_id=friend_id).first()
    if friend:
        db.delete(friend)
        db.commit()
        return True
    return False

def get_friends(db: Session, user_id: int):
    return db.query(Friend).filter_by(user_id=user_id).all() 