from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    item_id: Optional[int] = None

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None

class SystemMessageCreate(BaseModel):
    content: str
    title: Optional[str] = None
    target_users: Optional[str] = None  # "all", "buyers", "sellers", 或用户ID列表
    item_id: Optional[int] = None  # 系统消息可以关联到特定商品，也可以为空

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
    item_id: int
    other_user_id: int
    other_user_name: str
    other_user_avatar: Optional[str] = None
    last_message_content: str
    last_message_time: datetime
    unread_count: int
    
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
