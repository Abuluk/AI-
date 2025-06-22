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
    category: Optional[str] = None
    condition: Optional[str] = "unknown"
    location: str
    # 添加可选字段和默认值
    status: Optional[str] = "online"
    sold: Optional[bool] = False
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    images: Optional[str] = None  # 添加图片字段，多个路径用逗号分隔
    owner_id: Optional[int] = None  # 添加所有者ID字段
    views: Optional[int] = 0  # 添加浏览量字段
    favorited_count: Optional[int] = 0  # 添加收藏计数字段
    
    class Config:
        from_attributes = True