from sqlalchemy.orm import Session
from db.models import User
from schemas.user import UserCreate, UserUpdate
from core.pwd_util import get_password_hash
from datetime import datetime
from typing import List

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users_by_ids(db: Session, user_ids: List[int]):
    """
    根据用户ID列表批量获取用户
    """
    if not user_ids:
        return []
    return db.query(User).filter(User.id.in_(user_ids)).all()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone: str):  # 添加手机号查询方法
    return db.query(User).filter(User.phone == phone).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        phone=user.phone,  # 添加手机号
        hashed_password=hashed_password,
        avatar=getattr(user, "avatar", None) or "default_avatar.png",
        is_active=True  # 默认激活用户
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    # 特殊处理密码更新
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    # 更新所有字段
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    # 设置更新时间
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# 添加用户状态更新方法
def activate_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

# 添加更新最后登录时间的方法
def update_last_login(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user