from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
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

class UserPublic(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = Field(None, alias='avatar')

    class Config:
        from_attributes = True
        populate_by_name = True

class UserIds(BaseModel):
    user_ids: List[int]

class RequestPasswordReset(BaseModel):
    account: EmailStr

class DoResetPassword(BaseModel):
    account: EmailStr
    code: str
    new_password: str