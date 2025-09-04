from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from db.session import get_db
from db.models import User, Message, Blacklist, Item, BuyRequest
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
    get_user_messages,
    get_message,
    mark_all_as_read
)
from pydantic import BaseModel
import os
from datetime import datetime

# 消息列表响应模型
class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    unread_count: int
    page: int
    size: int
    total: int
    
    class Config:
        from_attributes = True

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取系统消息列表，包括发送给所有用户的和发送给当前用户的。
    """
    messages = get_public_system_messages(db, skip=skip, limit=limit, user_id=current_user.id)
    return messages

@router.get("/system/public/guest", response_model=List[MessageResponse])
def read_public_system_messages_for_guest(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取发送给所有用户的公开系统消息（无需登录）
    """
    # 只获取发送给所有用户的系统消息
    messages = db.query(Message).filter(
        Message.is_system == True,
        Message.target_users == "all"
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
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
    if type == "user":
        # 用户私聊：直接查询双方的消息
        messages = db.query(Message).filter(
            Message.is_system == False,
            Message.target_user.isnot(None),
            or_(
                and_(Message.user_id == current_user.id, Message.target_user == str(other_user_id)),
                and_(Message.user_id == other_user_id, Message.target_user == str(current_user.id))
            ),
            or_(
                and_(Message.user_id == current_user.id, Message.deleted_by_sender == False),
                and_(Message.user_id == other_user_id, Message.deleted_by_receiver == False)
            )
        ).order_by(Message.created_at).all()
    else:
        # 商品或求购消息：使用原有逻辑
        messages = get_conversation_messages(
            db, user_id=current_user.id, other_user_id=other_user_id, type=type, id=id
        )
    
    # 标记消息为已读
    for msg in messages:
        if msg.user_id != current_user.id and not msg.is_read:
            mark_as_read(db, message_id=msg.id)
    return messages

@router.get("/", response_model=MessageListResponse)
def get_user_messages_list(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的消息列表（支持分页）"""
    try:
        skip = (page - 1) * size
        
        # 获取用户的所有消息（包括系统消息和私聊消息）
        messages_query = db.query(Message).filter(
            or_(
                Message.user_id == current_user.id,  # 用户发送的消息
                Message.target_user == str(current_user.id),  # 用户接收的消息
                and_(Message.is_system == True, Message.target_users == "all"),  # 系统广播消息
                and_(Message.is_system == True, Message.target_users == str(current_user.id))  # 发送给特定用户的系统消息
            )
        ).order_by(Message.created_at.desc())
        
        # 获取总数
        total = messages_query.count()
        
        # 分页查询
        messages = messages_query.offset(skip).limit(size).all()
        
        # 获取未读消息数量
        unread_count = get_unread_count(db, user_id=current_user.id)
        
        # 返回符合小程序期望的格式
        return MessageListResponse(
            messages=messages,
            unread_count=unread_count,
            page=page,
            size=size,
            total=total
        )
    except Exception as e:
        print(f"获取消息列表时发生错误: {e}")
        # 返回空结果而不是抛出异常
        return MessageListResponse(
            messages=[],
            unread_count=0,
            page=page,
            size=size,
            total=0
        )

@router.post("/", response_model=MessageResponse)
def create_new_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建新消息"""
    # 支持三种消息类型：
    # 1. 商品消息：item_id有值，buy_request_id为空
    # 2. 求购消息：buy_request_id有值，item_id为空  
    # 3. 用户私聊：target_user有值，item_id和buy_request_id都为空
    if not message.item_id and not message.buy_request_id and not message.target_user:
        raise HTTPException(status_code=400, detail="item_id、buy_request_id 和 target_user 必须至少有一个")
    
    # 黑名单校验：检查接收方是否拉黑了发送方
    target_user_id = None
    if message.item_id:
        # 商品消息：检查商品所有者是否拉黑了发送方
        item = db.query(Item).filter(Item.id == message.item_id).first()
        if item:
            target_user_id = item.owner_id
    elif message.buy_request_id:
        # 求购消息：检查求购发布者是否拉黑了发送方
        buy_request = db.query(BuyRequest).filter(BuyRequest.id == message.buy_request_id).first()
        if buy_request:
            target_user_id = buy_request.user_id
    elif message.target_user:
        # 用户私聊：直接使用target_user
        target_user_id = int(message.target_user)
    
    if target_user_id and target_user_id != current_user.id:
        # 检查是否被拉黑
        blacklist_entry = db.query(Blacklist).filter(
            Blacklist.user_id == target_user_id,
            Blacklist.blocked_user_id == current_user.id
        ).first()
        
        if blacklist_entry:
            raise HTTPException(status_code=403, detail="无法发送消息，您已被对方拉黑")
    
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

@router.patch("/system/{message_id}/read", response_model=MessageResponse)
def mark_system_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """标记系统消息为已读"""
    message = get_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="系统消息不存在")
    
    # 检查是否是系统消息
    if not message.is_system:
        raise HTTPException(status_code=400, detail="只能标记系统消息为已读")
    
    # 检查用户是否有权限标记此系统消息为已读
    # 系统消息可以是发送给所有用户的，也可以是发送给特定用户的
    if message.target_users == "all" or message.target_users == str(current_user.id):
        return mark_as_read(db, message_id=message_id)
    else:
        raise HTTPException(status_code=403, detail="无权限操作此系统消息")

@router.patch("/batch/like-messages/read")
def mark_like_messages_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """批量标记点赞消息为已读"""
    # 查找所有发送给当前用户的未读点赞消息
    like_messages = db.query(Message).filter(
        Message.is_system == True,
        Message.target_users == str(current_user.id),
        Message.title.in_(["商品被点赞", "求购被点赞", "评论被点赞"]),
        Message.is_read == False
    ).all()
    
    # 标记所有点赞消息为已读
    for message in like_messages:
        message.is_read = True
    
    db.commit()
    
    return {"message": f"已标记 {len(like_messages)} 条点赞消息为已读"}

@router.delete("/{message_id}")
def remove_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除消息（只能删除自己的消息或管理员删除任何消息）"""
    message = get_system_message(db, message_id=message_id)
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    # 管理员可直接物理删除
    is_admin = current_user.is_admin
    # 发送方或接收方可软删除
    is_sender = message.user_id == current_user.id
    is_receiver = False
    if message.item_id:
        item = db.query(Message).get(message.id).item
        if item and item.owner_id == current_user.id:
            is_receiver = True
    elif message.buy_request_id:
        br = db.query(Message).get(message.id).buy_request
        if br and br.user_id == current_user.id:
            is_receiver = True
    if not (is_sender or is_receiver or is_admin):
        raise HTTPException(status_code=403, detail="无权限删除此消息")

    delete_message(db, message_id=message_id, current_user_id=current_user.id, is_admin=is_admin)
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
    删除某商品下与某用户的所有消息（仅限当前用户与对方的消息），采用软删除
    """
    if type == "user":
        # 用户私聊：删除双方的所有私聊消息
        messages = db.query(Message).filter(
            Message.is_system == False,
            Message.target_user.isnot(None),
            or_(
                and_(Message.user_id == current_user.id, Message.target_user == str(other_user_id)),
                and_(Message.user_id == other_user_id, Message.target_user == str(current_user.id))
            )
        ).all()
    else:
        # 商品或求购消息：使用原有逻辑
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
        messages = q.all()
    
    for msg in messages:
        delete_message(db, message_id=msg.id, current_user_id=current_user.id, is_admin=False)
    return {"message": "对话已删除"}

@router.get("/likes")
def get_like_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # 查询所有与我相关的点赞系统消息
    messages = db.query(Message).filter(
        Message.is_system == True,
        Message.target_users == str(current_user.id),
        Message.title.in_(["商品被点赞", "求购被点赞", "评论被点赞"])
    ).order_by(Message.created_at.desc()).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "created_at": m.created_at
        } for m in messages
    ]

@router.post("/upload-image")
async def upload_chat_image(file: UploadFile = File(...)):
    save_dir = os.path.join(os.getcwd(), "static", "images")
    os.makedirs(save_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[-1]
    save_name = f"chat_{int(datetime.now().timestamp())}{file_ext}"
    save_path = os.path.join(save_dir, save_name)
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/images/{save_name}"}

@router.post("/all-read")
def mark_all_messages_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """一键全部已读"""
    mark_all_as_read(db, user_id=current_user.id)
    return {"message": "全部消息已标记为已读"}