from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from db.session import get_db
from db.models import User, Message
from schemas.message import MessageCreate, MessageResponse, Conversation
from core.security import get_current_active_user
from crud.crud_message import (
    create_message,
    get_user_conversations,
    get_conversation_messages,
    get_unread_count,
    get_public_system_messages,
    get_system_message,
    mark_as_read,
    delete_message,
    get_user_messages
)

router = APIRouter()

@router.get("/conversations", response_model=List[Conversation])
def read_user_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的对话列表"""
    conversations = get_user_conversations(db, user_id=current_user.id)
    if not conversations:
        return []
    return conversations

@router.get("/system/public", response_model=List[MessageResponse])
def read_public_system_messages(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取公开的系统消息列表。
    """
    messages = get_public_system_messages(db, skip=skip, limit=limit)
    return messages

@router.get("/system/{message_id}", response_model=MessageResponse)
def read_system_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单条系统消息。
    """
    message = get_system_message(db, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="消息不存在")
    return message

@router.get("/unread-count")
def read_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取未读消息数量"""
    count = get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}

@router.get("/conversation/{type}/{id}/{other_user_id}", response_model=List[MessageResponse])
def read_conversation_messages(
    type: str,
    id: int,
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    messages = get_conversation_messages(
        db, user_id=current_user.id, other_user_id=other_user_id, type=type, id=id
    )
    for msg in messages:
        if msg.user_id != current_user.id and not msg.is_read:
            mark_as_read(db, message_id=msg.id)
    return messages

@router.post("/", response_model=MessageResponse)
def create_new_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新消息"""
    if not message.item_id and not message.buy_request_id:
        raise HTTPException(status_code=400, detail="item_id 和 buy_request_id 必须至少有一个")
    return create_message(db, message=message, user_id=current_user.id)

@router.patch("/{message_id}/read", response_model=MessageResponse)
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记消息为已读"""
    message = get_system_message(db, message_id=message_id) # Reuse get_system_message to get any message
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    # 只能标记发给自己的消息
    item = message.item
    if not (message.user_id != current_user.id and (item and item.owner_id == current_user.id)):
         raise HTTPException(status_code=403, detail="无权限操作此消息")
            
    return mark_as_read(db, message_id=message_id)

@router.delete("/{message_id}")
def remove_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除消息（只能删除自己的消息或管理员删除任何消息）"""
    message = get_system_message(db, message_id=message_id) # Reuse get_system_message
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    if message.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限删除此消息")
        
    delete_message(db, message_id=message_id)
    return {"message": "消息已删除"}

@router.delete("/conversation/{type}/{id}/{other_user_id}")
def delete_conversation(
    type: str,
    id: int,
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除某商品下与某用户的所有消息（仅限当前用户与对方的消息）
    """
    q = db.query(Message).filter(
        Message.is_system == False,
        or_(
            and_(Message.user_id == current_user.id, Message.target_users == str(other_user_id)),
            and_(Message.user_id == other_user_id, Message.target_users == str(current_user.id)),
            and_(Message.user_id.in_([current_user.id, other_user_id]), Message.target_users == None)
        )
    )
    if type == "item":
        q = q.filter(Message.item_id == id)
    elif type == "buy_request":
        q = q.filter(Message.buy_request_id == id)
    else:
        raise HTTPException(status_code=400, detail="type参数错误")
    q.delete(synchronize_session=False)
    db.commit()
    return {"message": "对话已删除"}