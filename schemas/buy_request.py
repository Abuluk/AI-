from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from schemas.user import UserPublic

class BuyRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    budget: Optional[float] = None

class BuyRequestCreate(BuyRequestBase):
    pass

class BuyRequest(BuyRequestBase):
    id: int
    user_id: int
    created_at: datetime
    user: Optional[UserPublic] = None
    class Config:
        from_attributes = True 