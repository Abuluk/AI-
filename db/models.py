from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(200), nullable=False)
    avatar = Column(String(200), default="default_avatar.png")
    location = Column(String(100))
    bio = Column(Text, nullable=True)
    contact = Column(String(100), nullable=True)  # 添加联系方式字段
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # 添加管理员字段
    last_login = Column(DateTime, nullable=True)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    items_count = Column(Integer, default=0)
    
    items = relationship("Item", back_populates="owner")
    messages = relationship("Message", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    buy_requests = relationship("BuyRequest", back_populates="user")  # 新增

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    condition = Column(String(20), default="unknown")
    status = Column(String(20), default="online", nullable=False)  # online, offline, sold
    location = Column(String(100))
    images = Column(String(500))  # 存储图片路径，多个用逗号分隔
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    sold = Column(Boolean, default=False)
    views = Column(Integer, default=0)  # 添加浏览量字段
    favorited_count = Column(Integer, default=0)  # 添加收藏计数
    
    favorited_by = relationship("Favorite", back_populates="item")
    owner = relationship("User", back_populates="items")
    messages = relationship("Message", back_populates="item")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())  # 使用数据库函数
    is_read = Column(Boolean, default=False)  # 添加已读状态
    is_system = Column(Boolean, default=False)  # 添加系统消息标识
    title = Column(String(200), nullable=True)  # 系统消息标题
    target_users = Column(String(500), nullable=True)  # 目标用户（系统消息）
    
    user = relationship("User", back_populates="messages")
    item = relationship("Item", back_populates="messages")

# 在Favorite模型中添加唯一约束
class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),
    )
    
    user = relationship("User", back_populates="favorites")
    item = relationship("Item", back_populates="favorited_by")

class BuyRequest(Base):
    __tablename__ = 'buy_requests'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    budget = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='buy_requests')