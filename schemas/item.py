from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    id: int
    username: str
    avatar: Optional[str] = None
    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: Optional[int] = None
    condition: Optional[str] = "unknown"
    location: str
    like_count: Optional[int] = 0  # 改为可选字段，允许 None 值

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    id: int
    title: str
    description: str
    price: float
    category: Optional[int] = None
    condition: Optional[str] = "unknown"
    location: str
    like_count: Optional[int] = 0  # 改为可选字段，允许 None 值
    # 添加可选字段和默认值
    status: Optional[str] = "online"
    sold: Optional[bool] = False
    created_at: Optional[datetime] = None
    images: Optional[str] = None  # 添加图片字段，多个路径用逗号分隔
    owner_id: Optional[int] = None  # 添加所有者ID字段
    views: Optional[int] = 0  # 添加浏览量字段
    favorited_count: Optional[int] = 0  # 添加收藏计数字段
    liked_by_me: Optional[bool] = False  # 添加当前用户是否已点赞字段
    owner: Optional[UserBase] = None  # 新增：嵌套用户信息
    
    class Config:
        from_attributes = True

class SiteConfigSchema(BaseModel):
    key: str
    value: Optional[List[dict]] = None  # [{img:..., link:...}]
    class Config:
        from_attributes = True