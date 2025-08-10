from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, case, union_all
from typing import List, Optional, Dict, Any
from datetime import datetime

from db.models import Message, User, Item, BuyRequest
from schemas.message import MessageCreate, MessageUpdate, SystemMessageCreate

def get_message(db: Session, message_id: int):
    return db.query(Message).filter(Message.id == message_id).first()

def create_message(db: Session, message: MessageCreate, user_id: int):
    db_message = Message(
        content=message.content,
        user_id=user_id,
        item_id=message.item_id,
        buy_request_id=message.buy_request_id,
        target_user=message.target_user,
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

def delete_message(db: Session, message_id: int, current_user_id: int, is_admin: bool = False):
    db_message = get_message(db, message_id)
    if not db_message:
        return None
    # 管理员直接物理删除
    if is_admin:
        db.delete(db_message)
        db.commit()
        print(f"[物理删除] 管理员直接删除 message_id={message_id}")
        return db_message
    # 判断当前用户是发送方还是接收方
    is_sender = db_message.user_id == current_user_id
    is_receiver = False
    item_owner_id = None
    br_owner_id = None
    if db_message.item_id:
        item = db.query(Item).filter(Item.id == db_message.item_id).first()
        if item:
            item_owner_id = item.owner_id
            if item.owner_id == current_user_id:
                is_receiver = True
    elif db_message.buy_request_id:
        br = db.query(BuyRequest).filter(BuyRequest.id == db_message.buy_request_id).first()
        if br:
            br_owner_id = br.user_id
            if br.user_id == current_user_id:
                is_receiver = True
    print(f"[调试] 当前用户:{current_user_id}, 消息发送方:{db_message.user_id}, 商品owner:{item_owner_id}, 求购owner:{br_owner_id}, is_sender:{is_sender}, is_receiver:{is_receiver}")
    # 只允许发送方或接收方删除
    if not (is_sender or is_receiver):
        print(f"[调试] 当前用户无权删除 message_id={message_id}")
        return None
    # 只允许一方设置软删除标记，优先发送方
    if is_sender and not is_receiver:
        db_message.deleted_by_sender = True
        print(f"[软删除] 设置 deleted_by_sender=True, message_id={message_id}")
    elif is_receiver and not is_sender:
        db_message.deleted_by_receiver = True
        print(f"[软删除] 设置 deleted_by_receiver=True, message_id={message_id}")
    elif is_sender and is_receiver:
        # 极端情况，理论上不应出现
        db_message.deleted_by_sender = True
        print(f"[警告] 当前用户既是发送方又是接收方，只设置 deleted_by_sender=True, message_id={message_id}")
    # 如果双方都已删除，物理删除
    if db_message.deleted_by_sender and db_message.deleted_by_receiver:
        db.delete(db_message)
        print(f"[物理删除] 双方都已删除，物理删除 message_id={message_id}")
    db.commit()
    return db_message

def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Message]:
    """获取用户的所有消息（包括自己发出的和别人发给自己商品的），过滤掉已删除的"""
    # 用户发出的消息
    sent = db.query(Message.id).filter(Message.user_id == user_id, Message.deleted_by_sender == False).all()
    # 别人发给自己商品的消息
    received = db.query(Message.id).join(Item, Message.item_id == Item.id).filter(
        Item.owner_id == user_id,
        Message.user_id != user_id,
        Message.deleted_by_receiver == False
    ).all()
    all_ids = [row.id for row in sent] + [row.id for row in received]
    if not all_ids:
        return []
    # 查询所有消息并按时间排序
    return db.query(Message).filter(Message.id.in_(all_ids)).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def get_conversation_messages(db: Session, user_id: int, other_user_id: int, type: str = "item", id: int = None) -> List[Message]:
    if type == "item":
        # 我发出的消息（未被我删除）
        sent_messages = db.query(Message).filter(
            Message.item_id == id,
            Message.is_system == False,
            Message.user_id == user_id,
            Message.target_users == str(other_user_id),
            Message.deleted_by_sender == False
        )
        # 别人发给我的消息（未被我删除）
        received_messages = db.query(Message).filter(
            Message.item_id == id,
            Message.is_system == False,
            Message.user_id == other_user_id,
            Message.target_users == str(user_id),
            Message.deleted_by_receiver == False
        )
        # 群聊消息（未被我删除）
        group_messages = db.query(Message).filter(
            Message.item_id == id,
            Message.is_system == False,
            Message.user_id.in_([user_id, other_user_id]),
            Message.target_users == None,
            or_(
                and_(Message.user_id == user_id, Message.deleted_by_sender == False),
                and_(Message.user_id == other_user_id, Message.deleted_by_receiver == False)
            )
        )
        # 获取与该商品相关的系统消息（发送给当前用户或所有用户的）
        system_messages = db.query(Message).filter(
            Message.item_id == id,
            Message.is_system == True,
            or_(
                Message.target_users == str(user_id),  # 发送给当前用户的系统消息
                Message.target_users == "all"  # 发送给所有用户的系统消息
            ),
            ~Message.title.in_(["商品被点赞", "求购被点赞", "评论被点赞"])  # 过滤掉点赞类系统消息
        )
        # 合并并排序
        all_messages = sent_messages.union(received_messages, group_messages, system_messages).order_by(Message.created_at).all()
        return all_messages
    elif type == "buy_request":
        # 我发出的消息（未被我删除）
        sent_messages = db.query(Message).filter(
            Message.buy_request_id == id,
            Message.is_system == False,
            Message.user_id == user_id,
            Message.target_users == str(other_user_id),
            Message.deleted_by_sender == False
        )
        # 别人发给我的消息（未被我删除）
        received_messages = db.query(Message).filter(
            Message.buy_request_id == id,
            Message.is_system == False,
            Message.user_id == other_user_id,
            Message.target_users == str(user_id),
            Message.deleted_by_receiver == False
        )
        # 群聊消息（未被我删除）
        group_messages = db.query(Message).filter(
            Message.buy_request_id == id,
            Message.is_system == False,
            Message.user_id.in_([user_id, other_user_id]),
            Message.target_users == None,
            or_(
                and_(Message.user_id == user_id, Message.deleted_by_sender == False),
                and_(Message.user_id == other_user_id, Message.deleted_by_receiver == False)
            )
        )
        # 获取与该求购相关的系统消息（发送给当前用户或所有用户的）
        system_messages = db.query(Message).filter(
            Message.buy_request_id == id,
            Message.is_system == True,
            or_(
                Message.target_users == str(user_id),  # 发送给当前用户的系统消息
                Message.target_users == "all"  # 发送给所有用户的系统消息
            ),
            ~Message.title.in_(["商品被点赞", "求购被点赞", "评论被点赞"])  # 过滤掉点赞类系统消息
        )
        # 合并并排序
        all_messages = sent_messages.union(received_messages, group_messages, system_messages).order_by(Message.created_at).all()
        return all_messages
    else:
        return []

def get_user_conversations(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """
    获取用户的对话列表，支持商品(item)、求购(buy_request)、用户私聊(user)三种类型。
    过滤掉当前用户已删除的消息。
    """
    output = []
    # ----------- 商品对话 -----------
    # 1. 我发起的（我不是 owner）
    sent_items = db.query(
        Message.item_id,
        Item.owner_id.label('other_user_id')
    ).join(Item, Message.item_id == Item.id).filter(
        Message.user_id == user_id,
        Message.is_system == False,
        Item.owner_id.isnot(None),
        Item.owner_id != user_id,
        Message.item_id.isnot(None),
        Message.deleted_by_sender == False
    ).distinct()
    # 2. 别人发给自己的（我是 owner）
    received_items = db.query(
        Message.item_id,
        Message.user_id.label('other_user_id')
    ).join(Item, Message.item_id == Item.id).filter(
        Item.owner_id == user_id,
        Message.is_system == False,
        Message.user_id.isnot(None),
        Message.user_id != user_id,
        Message.item_id.isnot(None),
        Message.deleted_by_receiver == False
    ).distinct()
    all_item_convs = sent_items.union(received_items).all()
    for item_id, other_user_id in all_item_convs:
        if not item_id or not other_user_id:
            continue
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if not other_user:
            continue
        item = db.query(Item).filter(Item.id == item_id).first()
        item_title = item.title if item else ''
        last_message = db.query(Message).filter(
            Message.item_id == item_id,
            Message.user_id.in_([user_id, other_user_id]),
            # 过滤掉当前用户已删除的消息
            or_(
                and_(Message.user_id == user_id, Message.deleted_by_sender == False),
                and_(Message.user_id != user_id, Message.deleted_by_receiver == False)
            )
        ).order_by(Message.created_at.desc()).first()
        if not last_message:
            continue
        unread_count = db.query(func.count(Message.id)).filter(
            Message.item_id == item_id,
            Message.is_read == False,
            Message.user_id == other_user_id
        ).scalar() or 0
        output.append({
            'type': 'item',
            'item_id': item_id,
            'buy_request_id': None,
            'other_user_id': other_user.id,
            'other_user_name': other_user.username,
            'other_user_avatar': other_user.avatar,
            'item_title': item_title,
            'buy_request_title': None,
            'last_message_content': last_message.content,
            'last_message_time': last_message.created_at,
            'unread_count': unread_count
        })
    # ----------- 求购对话 -----------
    # 1. 我发起的（我不是发布者）
    sent_brs = db.query(
        Message.buy_request_id,
        BuyRequest.user_id.label('other_user_id')
    ).join(BuyRequest, Message.buy_request_id == BuyRequest.id).filter(
        Message.user_id == user_id,
        Message.is_system == False,
        BuyRequest.user_id.isnot(None),
        BuyRequest.user_id != user_id,
        Message.buy_request_id.isnot(None),
        Message.deleted_by_sender == False
    ).distinct()
    # 2. 别人发给自己的（我是发布者）
    received_brs = db.query(
        Message.buy_request_id,
        Message.user_id.label('other_user_id')
    ).join(BuyRequest, Message.buy_request_id == BuyRequest.id).filter(
        BuyRequest.user_id == user_id,
        Message.is_system == False,
        Message.user_id.isnot(None),
        Message.user_id != user_id,
        Message.buy_request_id.isnot(None),
        Message.deleted_by_receiver == False
    ).distinct()
    all_br_convs = sent_brs.union(received_brs).all()
    for buy_request_id, other_user_id in all_br_convs:
        if not buy_request_id or not other_user_id:
            continue
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if not other_user:
            continue
        br = db.query(BuyRequest).filter(BuyRequest.id == buy_request_id).first()
        br_title = br.title if br else ''
        last_message = db.query(Message).filter(
            Message.buy_request_id == buy_request_id,
            Message.user_id.in_([user_id, other_user_id]),
            # 过滤掉当前用户已删除的消息
            or_(
                and_(Message.user_id == user_id, Message.deleted_by_sender == False),
                and_(Message.user_id != user_id, Message.deleted_by_receiver == False)
            )
        ).order_by(Message.created_at.desc()).first()
        if not last_message:
            continue
        unread_count = db.query(func.count(Message.id)).filter(
            Message.buy_request_id == buy_request_id,
            Message.is_read == False,
            Message.user_id == other_user_id
        ).scalar() or 0
        output.append({
            'type': 'buy_request',
            'item_id': None,
            'buy_request_id': buy_request_id,
            'other_user_id': other_user.id,
            'other_user_name': other_user.username,
            'other_user_avatar': other_user.avatar,
            'item_title': None,
            'buy_request_title': br_title,
            'last_message_content': last_message.content,
            'last_message_time': last_message.created_at,
            'unread_count': unread_count
        })
    # ----------- 用户私聊对话 -----------
    # 查询所有与当前用户相关的私聊消息
    user_chat_msgs = db.query(Message).filter(
        Message.is_system == False,
        Message.target_user.isnot(None),
        or_(Message.user_id == user_id, Message.target_user == str(user_id))
    ).all()
    # 用frozenset({user_id, target_user})去重，分组
    chat_pairs = {}
    for msg in user_chat_msgs:
        uid1 = msg.user_id
        uid2 = int(msg.target_user)
        if uid1 == uid2:
            continue  # 跳过自己给自己发的
        pair = frozenset([uid1, uid2])
        if pair not in chat_pairs or msg.created_at > chat_pairs[pair].created_at:
            chat_pairs[pair] = msg
    for pair, last_message in chat_pairs.items():
        # 取对方id
        other_user_id = [uid for uid in pair if uid != user_id][0]
        other_user = db.query(User).filter(User.id == other_user_id).first()
        if not other_user:
            continue
        # 统计未读数（对方发给我且未读）
        unread_count = db.query(func.count(Message.id)).filter(
            Message.is_system == False,
            Message.target_user == str(user_id),
            Message.user_id == other_user_id,
            Message.is_read == False
        ).scalar() or 0
        output.append({
            'type': 'user',
            'item_id': None,
            'buy_request_id': None,
            'other_user_id': other_user.id,
            'other_user_name': other_user.username,
            'other_user_avatar': other_user.avatar,
            'item_title': None,
            'buy_request_title': None,
            'last_message_content': last_message.content,
            'last_message_time': last_message.created_at,
            'unread_count': unread_count
        })
    # 按最后消息时间排序
    output.sort(key=lambda x: x['last_message_time'], reverse=True)
    return output

def get_unread_count(db: Session, user_id: int) -> int:
    """获取用户所有对话的未读消息总数"""
    
    total_unread = 0
    
    # 1. 计算商品相关对话的未读消息
    buyer_item_ids = db.query(Message.item_id).filter(Message.user_id == user_id, Message.is_system == False).distinct()
    seller_item_ids = db.query(Item.id).join(Message, Message.item_id == Item.id).filter(Item.owner_id == user_id, Message.is_system == False).distinct()
    
    involved_item_ids_query = buyer_item_ids.union(seller_item_ids)
    involved_item_ids = {row[0] for row in involved_item_ids_query.all()}
    
    if involved_item_ids:
        item_unread = db.query(func.count(Message.id)).filter(
            Message.item_id.in_(involved_item_ids),
            Message.is_read == False,
            Message.is_system == False,
            Message.user_id != user_id
        ).scalar() or 0
        total_unread += item_unread
    
    # 2. 计算求购相关对话的未读消息
    buyer_br_ids = db.query(Message.buy_request_id).filter(Message.user_id == user_id, Message.is_system == False).distinct()
    seller_br_ids = db.query(BuyRequest.id).join(Message, Message.buy_request_id == BuyRequest.id).filter(BuyRequest.user_id == user_id, Message.is_system == False).distinct()
    
    involved_br_ids_query = buyer_br_ids.union(seller_br_ids)
    involved_br_ids = {row[0] for row in involved_br_ids_query.all() if row[0] is not None}
    
    if involved_br_ids:
        br_unread = db.query(func.count(Message.id)).filter(
            Message.buy_request_id.in_(involved_br_ids),
            Message.is_read == False,
            Message.is_system == False,
            Message.user_id != user_id
        ).scalar() or 0
        total_unread += br_unread
    
    # 3. 计算用户私聊的未读消息
    user_chat_unread = db.query(func.count(Message.id)).filter(
        Message.is_system == False,
        Message.target_user == str(user_id),
        Message.user_id != user_id,
        Message.is_read == False
    ).scalar() or 0
    total_unread += user_chat_unread
    
    # 4. 计算系统消息的未读数量
    system_unread = db.query(func.count(Message.id)).filter(
        Message.is_system == True,
        Message.is_read == False,
        or_(
            Message.target_users == "all",
            Message.target_users == str(user_id)
        )
    ).scalar() or 0
    total_unread += system_unread
    
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
        buy_request_id=message_in.buy_request_id,  # 可以为None
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

def get_public_system_messages(db: Session, skip: int = 0, limit: int = 20, user_id: int = None) -> List[Message]:
    """获取系统消息，包括发送给所有用户的和发送给特定用户的"""
    query = db.query(Message).filter(Message.is_system == True)
    
    if user_id:
        # 获取发送给所有用户的和发送给特定用户的系统消息
        query = query.filter(
            or_(
                Message.target_users == "all",
                Message.target_users == str(user_id)
            )
        )
    
    return query.order_by(desc(Message.created_at)).offset(skip).limit(limit).all()

def get_system_message(db: Session, message_id: int) -> Optional[Message]:
    """获取单条系统消息"""
    return db.query(Message).filter(Message.id == message_id, Message.is_system == True).first()

def mark_all_as_read(db: Session, user_id: int):
    """将当前用户所有未读消息全部标记为已读（包括商品、求购、私聊、系统消息）"""
    # 商品相关
    db.query(Message).filter(
        Message.is_system == False,
        Message.is_read == False,
        Message.user_id != user_id,
        (
            (Message.item_id.in_([row[0] for row in db.query(Message.item_id).filter(Message.user_id == user_id, Message.is_system == False).distinct()])) |
            (Message.item_id.in_([row[0] for row in db.query(Item.id).join(Message, Message.item_id == Item.id).filter(Item.owner_id == user_id, Message.is_system == False).distinct()]))
        )
    ).update({Message.is_read: True}, synchronize_session=False)
    # 求购相关
    db.query(Message).filter(
        Message.is_system == False,
        Message.is_read == False,
        Message.user_id != user_id,
        (
            (Message.buy_request_id.in_([row[0] for row in db.query(Message.buy_request_id).filter(Message.user_id == user_id, Message.is_system == False).distinct() if row[0] is not None])) |
            (Message.buy_request_id.in_([row[0] for row in db.query(BuyRequest.id).join(Message, Message.buy_request_id == BuyRequest.id).filter(BuyRequest.user_id == user_id, Message.is_system == False).distinct() if row[0] is not None]))
        )
    ).update({Message.is_read: True}, synchronize_session=False)
    # 私聊
    db.query(Message).filter(
        Message.is_system == False,
        Message.is_read == False,
        Message.target_user == str(user_id),
        Message.user_id != user_id
    ).update({Message.is_read: True}, synchronize_session=False)
    # 系统消息
    db.query(Message).filter(
        Message.is_system == True,
        Message.is_read == False,
        or_(Message.target_users == "all", Message.target_users == str(user_id))
    ).update({Message.is_read: True}, synchronize_session=False)
    db.commit()
    return True

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
        return delete_message(db, id, 0, False)
    
    def get_user_messages(self, db: Session, user_id: int, skip: int = 0, limit: int = 50):
        return get_user_messages(db, user_id, skip, limit)
    
    def get_conversation_messages(self, db: Session, user_id: int, other_user_id: int, type: str = "item", id: int = None):
        return get_conversation_messages(db, user_id, other_user_id, type, id)
    
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
