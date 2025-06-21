from pydantic import BaseModel, Field
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
    title: str
    description: str
    price: float
    # 添加可选字段和默认值
    status: Optional[str] = "online"
    sold: Optional[bool] = False
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    images: Optional[str] = None  # 添加图片字段，多个路径用逗号分隔
    
    class Config:
        from_attributes = True