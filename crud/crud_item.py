from sqlalchemy.orm import Session
from sqlalchemy import or_
from db.models import Item
from schemas.item import ItemCreate
from datetime import datetime

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