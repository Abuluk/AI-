from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db.session import get_db
from db.models import User, Item
from crud.crud_message import message_crud
from crud.crud_item import get_item
from schemas.message import MessageCreate, MessageResponse, SystemMessageCreate
from core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的消息列表"""
    messages = message_crud.get_user_messages(db, user_id=current_user.id, skip=skip, limit=limit)
    return messages

@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的对话列表"""
    conversations = message_crud.get_user_conversations(db, user_id=current_user.id)
    return conversations

@router.get("/conversation/{item_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取特定商品的对话消息"""
    messages = message_crud.get_conversation_messages(db, user_id=current_user.id, item_id=item_id)
    return messages

@router.post("/", response_model=MessageResponse)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送消息"""
    # 验证商品是否存在
    item = get_item(db, item_id=message.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 不能给自己的商品发消息
    if item.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能给自己的商品发消息")
    
    message_data = message.dict()
    message_data["user_id"] = current_user.id
    return message_crud.create(db, obj_in=message_data)

@router.post("/system", response_model=MessageResponse)
async def create_system_message(
    message: SystemMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """管理员发布系统消息"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="只有管理员可以发布系统消息")
    
    # 如果指定了item_id，验证商品是否存在
    if message.item_id:
        item = get_item(db, item_id=message.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="指定的商品不存在")
    else:
        # 如果没有指定item_id，使用第一个商品作为默认值
        first_item = db.query(Item).first()
        if not first_item:
            raise HTTPException(status_code=400, detail="系统中没有商品，无法发布系统消息")
        message.item_id = first_item.id
    
    return message_crud.create_system_message(db, message_in=message, admin_id=current_user.id)

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取未读消息数量"""
    count = message_crud.get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}

@router.put("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记消息为已读"""
    message = message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    # 只能标记自己的消息为已读
    if message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此消息")
    
    return message_crud.mark_as_read(db, message_id=message_id)

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除消息（只能删除自己的消息或管理员删除任何消息）"""
    message = message_crud.get(db, id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    
    if not current_user.is_admin and message.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此消息")
    
    message_crud.remove(db, id=message_id)
    return {"message": "消息已删除"}