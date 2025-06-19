from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)  # 增加长度限制
    email = Column(String(200), unique=True, nullable=False)     # 增加长度限制
    phone = Column(String(20), unique=True, index=True, nullable=True)  # 添加手机号字段
    hashed_password = Column(String(200), nullable=False)
    avatar = Column(String(200), default="default_avatar.png")
    location = Column(String(100))
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())  # 使用数据库函数
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # 添加更新时间
    is_active = Column(Boolean, default=True)  # 添加激活状态字段
    last_login = Column(DateTime, nullable=True)
    # 其他字段保持不变...
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    items_count = Column(Integer, default=0)
    
    items = relationship("Item", back_populates="owner")
    messages = relationship("Message", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    condition = Column(String(20), default="unknown")
    location = Column(String(100))
    images = Column(String(500))  # 存储图片路径，多个用逗号分隔
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    sold = Column(Boolean, default=False)
    
    favorited_by = relationship("Favorite", back_populates="item")
    owner = relationship("User", back_populates="items")
    messages = relationship("Message", back_populates="item")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)  # 假设消息关联到某个物品
    created_at = Column(DateTime, default=datetime.utcnow)  # 添加消息创建时间
    
    user = relationship("User", back_populates="messages")
    item = relationship("Item", back_populates="messages")

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 定义关系
    user = relationship("User", back_populates="favorites")
    item = relationship("Item", back_populates="favorited_by")