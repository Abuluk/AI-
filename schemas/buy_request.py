from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from schemas.user import UserPublic

class BuyRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    budget: Optional[float] = None
    category: Optional[int] = 7  # 新增分类字段，默认为"其他"
    images: Optional[List[str]] = None
    like_count: Optional[int] = 0

class BuyRequestCreate(BuyRequestBase):
    pass

class BuyRequest(BuyRequestBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserPublic] = None
    class Config:
        orm_mode = True 