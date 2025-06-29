from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    item_id: Optional[int] = None
    buy_request_id: Optional[int] = None

class MessageCreate(MessageBase):
    target_user: Optional[str] = None

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None

class SystemMessageCreate(BaseModel):
    content: str
    title: Optional[str] = None
    target_users: Optional[str] = None  # "all", "buyers", "sellers", 或用户ID列表
    item_id: Optional[int] = None  # 系统消息可以关联到特定商品，也可以为空
    buy_request_id: Optional[int] = None  # 系统消息可以关联到特定求购信息，也可以为空

class MessageResponse(MessageBase):
    id: int
    user_id: int
    created_at: datetime
    is_read: bool = False
    is_system: bool = False
    title: Optional[str] = None
    target_users: Optional[str] = None
    
    class Config:
        from_attributes = True

class Conversation(BaseModel):
    item_id: Optional[int] = None
    buy_request_id: Optional[int] = None
    item_title: Optional[str] = None
    buy_request_title: Optional[str] = None
    other_user_id: int
    other_user_name: str
    other_user_avatar: Optional[str] = None
    last_message_content: str
    last_message_time: datetime
    unread_count: int
    type: str  # 新增，前端已用
    
    class Config:
        from_attributes = True

class ConversationSummary(BaseModel):
    item_id: int
    item_title: str
    last_message: str
    last_message_time: datetime
    unread_count: int
    other_user_id: int
    other_username: str
    other_avatar: str
    
    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str
    item_id: Optional[int] = None
    buy_request_id: Optional[int] = None
    parent_id: Optional[int] = None
    reply_to_user_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    item_id: Optional[int] = None
    buy_request_id: Optional[int] = None
    parent_id: Optional[int] = None
    reply_to_user_id: Optional[int] = None
    created_at: datetime
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    reply_to_user_name: Optional[str] = None
    children: Optional[List['CommentResponse']] = None
    like_count: Optional[int] = 0  # 改为可选字段，允许 None 值
    liked_by_me: bool = False  # 当前用户是否已点赞

    class Config:
        from_attributes = True

CommentResponse.update_forward_refs()
