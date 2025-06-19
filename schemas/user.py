from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=8, max_length=20)  # 添加手机号字段

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=20)  # 添加手机号
    password: Optional[str] = Field(None, min_length=6)
    avatar: Optional[str] = None
    location: Optional[str] = None

class UserInDB(UserBase):
    id: int
    avatar: str
    location: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool = True  # 将disabled改为is_active，并默认True
    # 注意：我们不再使用disabled，而是使用is_active

    class Config:
        from_attributes = True

class UserLogin(BaseModel):  # 添加登录模型
    identifier: str  # 用户名/邮箱/手机号
    password: str