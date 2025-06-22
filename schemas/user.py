from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    avatar: Optional[str] = None
    bio: Optional[str] = None
    contact: Optional[str] = None
    location: Optional[str] = None
    password: Optional[str] = None  # 可选密码更新

class UserInDB(UserBase):
    id: int
    avatar: str
    bio: Optional[str]
    contact: Optional[str]
    location: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    followers: int
    following: int
    items_count: int
    class Config:
        from_attributes = True

class UserLogin(BaseModel):  # 添加登录模型
    identifier: str  # 用户名/邮箱/手机号
    password: str