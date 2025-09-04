from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from schemas.item import ItemInDB

class FavoriteBase(BaseModel):
    user_id: int
    item_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteInDB(FavoriteBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FavoriteWithItem(FavoriteInDB):
    item: ItemInDB
    
    class Config:
        from_attributes = True

class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteWithItem]
    total: int
    page: int
    size: int
    
    class Config:
        from_attributes = True