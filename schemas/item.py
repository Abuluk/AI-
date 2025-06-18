from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    condition: Optional[str] = "unknown"
    location: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    id: int
    owner_id: int
    images: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True