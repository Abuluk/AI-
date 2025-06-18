from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    avatar: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    avatar: Optional[str] = None
    location: Optional[str] = None

class UserInDB(UserBase):
    id: int
    avatar: str
    location: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    disabled: bool = False

    class Config:
        from_attributes = True