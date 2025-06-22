from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, case, union_all
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
    """获取用户的所有消息（包括自己发出的和别人发给自己商品的）"""
    # 用户发出的消息
    sent = db.query(Message.id).filter(Message.user_id == user_id).all()
    # 别人发给自己商品的消息
    received = db.query(Message.id).join(Item, Message.item_id == Item.id).filter(
        Item.owner_id == user_id,
        Message.user_id != user_id
    ).all()
    all_ids = [row.id for row in sent] + [row.id for row in received]
    if not all_ids:
        return []
    # 查询所有消息并按时间排序
    return db.query(Message).filter(Message.id.in_(all_ids)).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def get_conversation_messages(db: Session, user_id: int, item_id: int, other_user_id: int) -> List[Message]:
    """获取特定商品、特定对话伙伴之间的所有消息"""
    # 验证用户是否为对话的参与者之一
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return []
        
    is_my_item = item.owner_id == user_id
    is_other_users_item = item.owner_id == other_user_id

    # 我是卖家，对方是买家 或 我是买家，对方是卖家
    valid_participants = (is_my_item and not is_other_users_item) or (not is_my_item and is_other_users_item)
    
    if not valid_participants:
        # 如果两人都不是商品的买卖方，则无权查看
        # (这也可以防止用户通过构造URL查看不相关的对话)
        return []

    # 获取此商品下，这两个用户之间的所有非系统消息
    return db.query(Message).filter(
        Message.item_id == item_id,
        Message.is_system == False,
        Message.user_id.in_([user_id, other_user_id])
    ).order_by(Message.created_at).all()

def get_user_conversations(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    获取用户的对话列表，以"对话伙伴"为中心进行聚合。
    使用更简单、更健壮的逻辑来避免SQL复杂性带来的bug。
    增加了对None值的过滤，确保other_user_id始终有效。
    """

    # 1. 获取所有与用户相关的对话对 (item_id, other_user_id)
    # 子查询1: 用户是发送者，对话伙伴是商品所有者
    sent_messages = db.query(
        Message.item_id,
        Item.owner_id.label('other_user_id')
    ).join(Item, Message.item_id == Item.id).filter(
        Message.user_id == user_id,
        Message.is_system == False,
        Item.owner_id.isnot(None),  # 确保商品所有者存在
        Item.owner_id != user_id      # 排除与自己的对话
    ).distinct()

    # 子查询2: 用户是商品所有者，对话伙伴是消息发送者
    received_messages = db.query(
        Message.item_id,
        Message.user_id.label('other_user_id')
    ).join(Item, Message.item_id == Item.id).filter(
        Item.owner_id == user_id,
        Message.is_system == False,
        Message.user_id.isnot(None), # 确保消息发送者存在
        Message.user_id != user_id   # 排除与自己的对话
    ).distinct()

    # 合并并去重所有对话对
    all_conversations_query = sent_messages.union(received_messages)
    
    # 直接从数据库获取干净的、唯一的(item_id, other_user_id)列表
    conversation_keys = all_conversations_query.all()

    if not conversation_keys:
        return []

    # 2. 为每个唯一的对话填充详细信息
    output = []
    for item_id, other_user_id in conversation_keys:
        # a. 获取对话伙伴的用户信息
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if not other_user:
            continue

        # b. 找到这个对话的最后一条消息
        last_message = db.query(Message).filter(
            Message.item_id == item_id,
            Message.user_id.in_([user_id, other_user_id])
        ).order_by(Message.created_at.desc()).first()

        if not last_message:
            continue
            
        # c. 计算当前用户在此对话中的未读消息数
        unread_count = db.query(func.count(Message.id)).filter(
            Message.item_id == item_id,
            Message.is_read == False,
            Message.user_id == other_user_id  # 未读消息是由对方发送的
        ).scalar() or 0

        # d. 组装对话摘要
        output.append({
            'item_id': item_id,
            'other_user_id': other_user.id,
            'other_user_name': other_user.username,
            'other_user_avatar': other_user.avatar,
            'last_message_content': last_message.content,
            'last_message_time': last_message.created_at,
            'unread_count': unread_count
        })

    # 3. 按最后消息时间排序
    output.sort(key=lambda x: x['last_message_time'], reverse=True)

    return output

def get_unread_count(db: Session, user_id: int) -> int:
    """获取用户所有对话的未读消息总数"""
    
    # 找出用户参与的所有对话的 item_id
    buyer_item_ids = db.query(Message.item_id).filter(Message.user_id == user_id, Message.is_system == False).distinct()
    seller_item_ids = db.query(Item.id).join(Message, Message.item_id == Item.id).filter(Item.owner_id == user_id, Message.is_system == False).distinct()
    
    involved_item_ids_query = buyer_item_ids.union(seller_item_ids)
    involved_item_ids = {row[0] for row in involved_item_ids_query.all()}
    
    if not involved_item_ids:
        return 0

    # 计算这些对话中所有未读消息的总和
    total_unread = db.query(func.count(Message.id)).filter(
        Message.item_id.in_(involved_item_ids),
        Message.is_read == False,
        Message.is_system == False,
        Message.user_id != user_id
    ).scalar() or 0
    
    return total_unread

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

def get_public_system_messages(db: Session, skip: int = 0, limit: int = 20) -> List[Message]:
    """获取所有公开的系统消息"""
    return db.query(Message).filter(Message.is_system == True).order_by(
        desc(Message.created_at)
    ).offset(skip).limit(limit).all()

def get_system_message(db: Session, message_id: int) -> Optional[Message]:
    """获取单条系统消息"""
    return db.query(Message).filter(Message.id == message_id, Message.is_system == True).first()

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
    
    def get_conversation_messages(self, db: Session, user_id: int, item_id: int, other_user_id: int):
        return get_conversation_messages(db, user_id, item_id, other_user_id)
    
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
