from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, func, UniqueConstraint, DECIMAL, JSON
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
    is_merchant = Column(Boolean, default=False)  # 是否为商家
    is_pending_merchant = Column(Boolean, default=False)  # 是否为待定商家（申请中）
    is_pending_verification = Column(Boolean, default=False)  # 是否为待认证商家（管理员判定）
    
    items = relationship("Item", back_populates="owner")
    messages = relationship("Message", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    buy_requests = relationship("BuyRequest", back_populates="user")  # 新增
    merchant = relationship("Merchant", back_populates="user", uselist=False)  # 商家信息
    merchant_display_config = relationship("MerchantDisplayConfig", back_populates="user", uselist=False)  # 商家展示配置
    detection_histories = relationship("MerchantDetectionHistory", back_populates="user")  # 检测历史

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(Integer)  # 修改为整数类型，与前端分类ID对应
    condition = Column(String(20), default="unknown")
    status = Column(String(20), default="online", nullable=False)  # online, offline, sold
    location = Column(String(100))
    images = Column(String(500))  # 存储图片路径，多个用逗号分隔
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    sold = Column(Boolean, default=False)
    views = Column(Integer, default=0)  # 添加浏览量字段
    favorited_count = Column(Integer, default=0)  # 添加收藏计数
    like_count = Column(Integer, default=0)  # 新增点赞数
    is_merchant_item = Column(Boolean, default=False)  # 是否为商家商品
    
    favorited_by = relationship("Favorite", back_populates="item")
    owner = relationship("User", back_populates="items")
    messages = relationship("Message", back_populates="item")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    buy_request_id = Column(Integer, ForeignKey("buy_requests.id"), nullable=True)  # 新增
    target_user = Column(String(50), nullable=True)  # 新增：目标用户ID（用于用户私聊）
    created_at = Column(DateTime, server_default=func.now())  # 使用数据库函数
    is_read = Column(Boolean, default=False)  # 添加已读状态
    is_system = Column(Boolean, default=False)  # 添加系统消息标识
    title = Column(String(200), nullable=True)  # 系统消息标题
    target_users = Column(String(500), nullable=True)  # 目标用户（系统消息）
    deleted_by_sender = Column(Boolean, default=False)  # 发送方删除
    deleted_by_receiver = Column(Boolean, default=False)  # 接收方删除
    
    user = relationship("User", back_populates="messages")
    item = relationship("Item", back_populates="messages")
    buy_request = relationship("BuyRequest", back_populates="messages")

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
    images = Column(String(500))  # 新增，存储图片路径，多个用逗号分隔
    created_at = Column(DateTime, server_default=func.now())
    like_count = Column(Integer, default=0)  # 新增点赞数

    user = relationship('User', back_populates='buy_requests')
    messages = relationship("Message", back_populates="buy_request")

class SiteConfig(Base):
    __tablename__ = 'site_config'
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(500), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    buy_request_id = Column(Integer, ForeignKey('buy_requests.id'), nullable=True)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    reply_to_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    like_count = Column(Integer, default=0)  # 新增点赞数

    user = relationship('User', foreign_keys=[user_id], lazy='joined')
    item = relationship('Item', foreign_keys=[item_id])
    buy_request = relationship('BuyRequest', foreign_keys=[buy_request_id])
    parent = relationship('Comment', remote_side=[id], backref='children')
    reply_to_user = relationship('User', foreign_keys=[reply_to_user_id])

class CommentLike(Base):
    __tablename__ = 'comment_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    comment_id = Column(Integer, ForeignKey('comments.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),)

class ItemLike(Base):
    __tablename__ = 'item_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),)

class BuyRequestLike(Base):
    __tablename__ = 'buy_request_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    buy_request_id = Column(Integer, ForeignKey('buy_requests.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'buy_request_id', name='_user_buyreq_uc'),)

class Friend(Base):
    __tablename__ = 'friends'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    friend_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'friend_id', name='uq_user_friend'),)

class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint('user_id', 'blocked_user_id', name='uq_user_blocked'),)

class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String(1000), nullable=False)
    status = Column(String(20), default='pending')  # pending/solved
    created_at = Column(DateTime, default=datetime.utcnow)
    solved_at = Column(DateTime, nullable=True)

    user = relationship('User', foreign_keys=[user_id])

class Merchant(Base):
    __tablename__ = 'merchants'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    business_name = Column(String(100), nullable=False)  # 商家名称
    business_license = Column(String(200), nullable=True)  # 营业执照号
    contact_person = Column(String(50), nullable=False)  # 联系人
    contact_phone = Column(String(20), nullable=False)  # 联系电话
    business_address = Column(String(200), nullable=False)  # 营业地址
    business_description = Column(Text, nullable=True)  # 商家描述
    status = Column(String(20), default='pending')  # pending(申请中), pending_verification(待认证), approved(已认证), rejected(已拒绝)
    is_pending = Column(Boolean, default=False)  # 是否为待定商家
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime, nullable=True)  # 认证通过时间
    rejected_at = Column(DateTime, nullable=True)  # 拒绝时间
    reject_reason = Column(Text, nullable=True)  # 拒绝原因
    
    user = relationship('User', foreign_keys=[user_id])

class MerchantDisplayConfig(Base):
    __tablename__ = 'merchant_display_configs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 用户ID，为NULL表示全局默认配置
    display_frequency = Column(Integer, default=5)  # 展示频率，每几个商品展示一个商家商品
    is_default = Column(Boolean, default=False)  # 是否为默认配置
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user = relationship('User', foreign_keys=[user_id])

class MerchantDetectionConfig(Base):
    __tablename__ = 'merchant_detection_configs'
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)  # 配置键
    value = Column(Text, nullable=True)  # 配置值
    description = Column(String(500), nullable=True)  # 配置描述
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MerchantDetectionHistory(Base):
    __tablename__ = 'merchant_detection_histories'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 被检测用户ID
    detection_type = Column(String(20), nullable=False, default='manual')  # 检测类型：manual/auto
    behavior_data = Column(JSON, nullable=True)  # 用户行为数据
    ai_analysis = Column(JSON, nullable=True)  # AI分析结果
    active_items_count = Column(Integer, nullable=False, default=0)  # 在售商品数
    is_merchant = Column(Boolean, nullable=False, default=False)  # AI判断结果
    confidence = Column(Float, nullable=False, default=0.0)  # 置信度
    ai_reason = Column(Text, nullable=True)  # AI分析理由
    processed = Column(Boolean, nullable=False, default=False)  # 是否已处理
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联用户
    user = relationship("User", back_populates="detection_histories")

class UserBehavior(Base):
    """用户行为记录表 - 用于AI推荐分析"""
    __tablename__ = 'user_behaviors'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    behavior_type = Column(String(20), nullable=False)  # view, click, favorite, like, search
    behavior_data = Column(JSON, nullable=True)  # 行为相关数据，如搜索关键词、停留时间等
    created_at = Column(DateTime, server_default=func.now())
    
    # 关联用户和商品
    user = relationship("User")
    item = relationship("Item")

class AIRecommendationConfig(Base):
    """AI推荐配置表"""
    __tablename__ = 'ai_recommendation_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False)  # 配置键
    config_value = Column(JSON, nullable=True)  # 配置值
    description = Column(String(500), nullable=True)  # 配置描述
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())