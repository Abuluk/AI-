from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, case
from typing import List, Optional, Dict, Any
from datetime import datetime

from db.models import Message, User, Item
from schemas.message import MessageCreate, MessageUpdate, SystemMessageCreate

def get_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()

def create_message(db: Session, message: MessageCreate, user_id: int):
    db_message = Message(
        content=message.content,
        user_id=user_id,
        item_id=message.item_id,
        created_at=datetime.utcnow(),
        is_read=False,
        is_system=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def update_message(db: Session, message_id: int, message_update: MessageUpdate):
    db_message = get_message(db, message_id)
    if not db_message:
        return None
    
    update_data = message_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_message, field, value)
    
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int):
    db_message = get_message(db, message_id)
    if not db_message:
        return None
    db.delete(db_message)
    db.commit()
    return db_message

def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
    """获取用户的所有消息"""
    return db.query(Message).filter(
        Message.user_id == user_id
    ).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def get_conversation_messages(db: Session, user_id: int, item_id: int) -> List[Message]:
    """获取特定商品的对话消息"""
    # 获取用户作为买家或卖家的消息
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return []
    
    # 如果用户是商品所有者，获取所有关于这个商品的消息
    if item.owner_id == user_id:
        return db.query(Message).filter(
            Message.item_id == item_id
        ).order_by(Message.created_at).all()
    else:
        # 如果用户是买家，只获取自己发送的消息
        return db.query(Message).filter(
            and_(
                Message.item_id == item_id,
                Message.user_id == user_id
            )
        ).order_by(Message.created_at).all()

def get_user_conversations(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """获取用户的对话列表"""
    # 获取用户作为买家的对话
    buyer_conversations = db.query(
        Message.item_id,
        func.count(Message.id).label('message_count'),
        func.max(Message.created_at).label('last_message_time'),
        func.sum(case((Message.is_read == False, 1), else_=0)).label('unread_count')
    ).filter(
        Message.user_id == user_id
    ).group_by(Message.item_id).all()
    
    # 获取用户作为卖家的对话（用户发布的商品收到的消息）
    seller_conversations = db.query(
        Message.item_id,
        func.count(Message.id).label('message_count'),
        func.max(Message.created_at).label('last_message_time'),
        func.sum(case((Message.is_read == False, 1), else_=0)).label('unread_count')
    ).join(Item, Message.item_id == Item.id).filter(
        Item.owner_id == user_id
    ).group_by(Message.item_id).all()
    
    # 合并对话列表
    all_conversations = {}
    
    for conv in buyer_conversations:
        item = db.query(Item).filter(Item.id == conv.item_id).first()
        if item:
            all_conversations[conv.item_id] = {
                'item_id': conv.item_id,
                'item_title': item.title,
                'item_price': item.price,
                'item_images': item.images,
                'message_count': conv.message_count,
                'last_message_time': conv.last_message_time,
                'unread_count': conv.unread_count or 0,
                'is_seller': False
            }
    
    for conv in seller_conversations:
        item = db.query(Item).filter(Item.id == conv.item_id).first()
        if item:
            if conv.item_id in all_conversations:
                all_conversations[conv.item_id]['message_count'] += conv.message_count
                all_conversations[conv.item_id]['unread_count'] += conv.unread_count or 0
                if conv.last_message_time > all_conversations[conv.item_id]['last_message_time']:
                    all_conversations[conv.item_id]['last_message_time'] = conv.last_message_time
            else:
                all_conversations[conv.item_id] = {
                    'item_id': conv.item_id,
                    'item_title': item.title,
                    'item_price': item.price,
                    'item_images': item.images,
                    'message_count': conv.message_count,
                    'last_message_time': conv.last_message_time,
                    'unread_count': conv.unread_count or 0,
                    'is_seller': True
                }
    
    # 按最后消息时间排序
    return sorted(all_conversations.values(), key=lambda x: x['last_message_time'], reverse=True)

def get_unread_count(db: Session, user_id: int) -> int:
    """获取用户未读消息数量"""
    # 用户作为买家的未读消息
    buyer_unread = db.query(func.count(Message.id)).filter(
        and_(
            Message.user_id == user_id,
            Message.is_read == False
        )
    ).scalar() or 0
    
    # 用户作为卖家的未读消息（其他用户发给用户商品的消息）
    seller_unread = db.query(func.count(Message.id)).join(Item, Message.item_id == Item.id).filter(
        and_(
            Item.owner_id == user_id,
            Message.is_read == False
        )
    ).scalar() or 0
    
    return buyer_unread + seller_unread

def mark_as_read(db: Session, message_id: int) -> Message:
    """标记消息为已读"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message:
        message.is_read = True
        db.commit()
        db.refresh(message)
    return message

def create_system_message(db: Session, message_in: SystemMessageCreate, admin_id: int) -> Message:
    """由管理员创建系统消息"""
    db_message = Message(
        title=message_in.title,
        content=message_in.content,
        user_id=admin_id,  # 发送者是管理员
        item_id=message_in.item_id,  # 可以为None
        created_at=datetime.utcnow(),
        is_read=False,  # 对接收者来说是未读的
        is_system=True,
        target_users=message_in.target_users
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_system_messages(db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
    """获取所有系统消息"""
    return db.query(Message).filter(Message.is_system == True).order_by(
        desc(Message.created_at)
    ).offset(skip).limit(limit).all()

# 创建CRUD实例（为了保持API兼容性）
class MessageCRUD:
    def get(self, db: Session, id: int):
        return get_message(db, id)
    
    def create(self, db: Session, obj_in: dict):
        # 如果obj_in已经是MessageCreate对象，直接使用
        if isinstance(obj_in, dict):
            user_id = obj_in.pop('user_id', None)
            if user_id is None:
                raise ValueError("user_id is required")
            return create_message(db, MessageCreate(**obj_in), user_id)
        else:
            # 如果是MessageCreate对象，需要从其他地方获取user_id
            raise ValueError("user_id must be provided in obj_in dict")
    
    def update(self, db: Session, id: int, obj_in: dict):
        if isinstance(obj_in, dict):
            return update_message(db, id, MessageUpdate(**obj_in))
        else:
            return update_message(db, id, obj_in)
    
    def remove(self, db: Session, id: int):
        return delete_message(db, id)
    
    def get_user_messages(self, db: Session, user_id: int, skip: int = 0, limit: int = 50):
        return get_user_messages(db, user_id, skip, limit)
    
    def get_conversation_messages(self, db: Session, user_id: int, item_id: int):
        return get_conversation_messages(db, user_id, item_id)
    
    def get_user_conversations(self, db: Session, user_id: int):
        return get_user_conversations(db, user_id)
    
    def get_unread_count(self, db: Session, user_id: int):
        return get_unread_count(db, user_id)
    
    def mark_as_read(self, db: Session, message_id: int):
        return mark_as_read(db, message_id)
    
    def create_system_message(self, db: Session, message_in: SystemMessageCreate, admin_id: int):
        return create_system_message(db, message_in, admin_id)
    
    def get_system_messages(self, db: Session, skip: int = 0, limit: int = 20):
        return get_system_messages(db, skip=skip, limit=limit)

# 创建CRUD实例
message_crud = MessageCRUD()
