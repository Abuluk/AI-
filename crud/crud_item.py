from sqlalchemy.orm import Session
from sqlalchemy import or_
from db.models import Item, ItemLike, User
from schemas.item import ItemCreate
from datetime import datetime
from crud.crud_message import create_system_message

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def get_items_by_owner(db: Session, owner_id: int):
    return db.query(Item).filter(Item.owner_id == owner_id).all()

# 搜索函数
def get_items_by_search(db: Session, query: str, skip: int = 0, limit: int = 100):
    return db.query(Item).filter(
        or_(
            Item.title.ilike(f"%{query}%"),
            Item.description.ilike(f"%{query}%")
        )
    ).offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemCreate, owner_id: int):
    data = item.dict()
    data.pop('created_at', None)  # 确保不传递 created_at
    db_item = Item(**data, owner_id=owner_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item_update: dict):
    db_item = get_item(db, item_id)
    if db_item:
        for key, value in item_update.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item

def like_item(db: Session, item_id: int, user_id: int) -> int:
    exists = db.query(ItemLike).filter_by(item_id=item_id, user_id=user_id).first()
    if exists:
        return -1
    db.add(ItemLike(item_id=item_id, user_id=user_id))
    item = db.query(Item).filter_by(id=item_id).first()
    if item:
        item.like_count += 1
        # 生成系统消息
        owner_id = item.owner_id
        user = db.query(User).filter_by(id=user_id).first()
        if owner_id and user and owner_id != user_id:  # 不能给自己点赞的商品发消息
            content = f"用户{user.username}点赞了你的商品《{item.title}》"
            from schemas.message import SystemMessageCreate
            msg = SystemMessageCreate(content=content, title="商品被点赞", target_users=str(owner_id), item_id=item_id)
            create_system_message(db, msg, admin_id=user_id)  # 使用点赞用户的ID作为发送者
    db.commit()
    return item.like_count if item else 0

def unlike_item(db: Session, item_id: int, user_id: int) -> int:
    like = db.query(ItemLike).filter_by(item_id=item_id, user_id=user_id).first()
    if not like:
        return -1
    db.delete(like)
    item = db.query(Item).filter_by(id=item_id).first()
    if item and item.like_count > 0:
        item.like_count -= 1
    db.commit()
    return item.like_count if item else 0