from pydantic import BaseModel
from datetime import datetime

class FavoriteBase(BaseModel):
    user_id: int
    item_id: int

class FavoriteCreate(FavoriteBase):
    pass

class FavoriteInDB(FavoriteBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes  = True