from sqlalchemy.orm import Session
from db.models import Merchant, MerchantDisplayConfig, User, Item
from schemas.merchant import MerchantCreate, MerchantUpdate, MerchantDisplayConfigCreate, MerchantDisplayConfigUpdate
from datetime import datetime
from typing import Optional, List

def create_merchant(db: Session, merchant: MerchantCreate, user_id: int) -> Merchant:
    """创建商家认证申请"""
    from db.models import User
    
    # 创建商家记录
    db_merchant = Merchant(
        user_id=user_id,
        business_name=merchant.business_name,
        business_license=merchant.business_license,
        contact_person=merchant.contact_person,
        contact_phone=merchant.contact_phone,
        business_address=merchant.business_address,
        business_description=merchant.business_description,
        status="pending"
    )
    db.add(db_merchant)
    
    # 更新用户状态为待定商家
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_pending_merchant = True
        db.add(user)
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

def get_merchant_by_user_id(db: Session, user_id: int) -> Optional[Merchant]:
    """根据用户ID获取商家信息"""
    return db.query(Merchant).filter(Merchant.user_id == user_id).first()

def get_merchant_by_id(db: Session, merchant_id: int) -> Optional[Merchant]:
    """根据商家ID获取商家信息"""
    return db.query(Merchant).filter(Merchant.id == merchant_id).first()

def update_merchant(db: Session, merchant_id: int, merchant_update: MerchantUpdate) -> Optional[Merchant]:
    """更新商家信息"""
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not db_merchant:
        return None
    
    update_data = merchant_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_merchant, field, value)
    
    db_merchant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

def update_merchant_status(db: Session, merchant_id: int, status: str, reject_reason: Optional[str] = None) -> Optional[Merchant]:
    """更新商家状态"""
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not db_merchant:
        return None
    
    db_merchant.status = status
    db_merchant.updated_at = datetime.utcnow()
    
    if status == "approved":
        db_merchant.approved_at = datetime.utcnow()
        # 更新用户为商家
        user = db.query(User).filter(User.id == db_merchant.user_id).first()
        if user:
            user.is_merchant = True
            user.is_pending_merchant = False
            user.is_pending_verification = False
    elif status == "rejected":
        db_merchant.rejected_at = datetime.utcnow()
        db_merchant.reject_reason = reject_reason
        # 如果用户是待定商家，取消待定状态
        user = db.query(User).filter(User.id == db_merchant.user_id).first()
        if user and user.is_pending_merchant:
            user.is_pending_merchant = False
    elif status == "pending_verification":
        # 设置为待认证状态
        user = db.query(User).filter(User.id == db_merchant.user_id).first()
        if user:
            user.is_pending_verification = True
            user.is_pending_merchant = False
            # 下架用户所有商品
            items = db.query(Item).filter(Item.owner_id == user.id).all()
            for item in items:
                item.status = "offline"
                db.add(item)
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

def cancel_merchant_application(db: Session, user_id: int) -> bool:
    """用户取消商家认证申请"""
    merchant = db.query(Merchant).filter(Merchant.user_id == user_id, Merchant.status == "pending").first()
    if not merchant:
        return False
    
    # 删除商家记录
    db.delete(merchant)
    
    # 更新用户状态
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_pending_merchant = False
        db.add(user)
    
    db.commit()
    return True

def set_pending_verification(db: Session, user_id: int, business_name: str, contact_person: str, 
                           contact_phone: str, business_address: str, business_description: Optional[str] = None) -> Optional[Merchant]:
    """管理员设置用户为待认证状态"""
    # 检查是否已有商家记录
    existing_merchant = db.query(Merchant).filter(Merchant.user_id == user_id).first()
    if existing_merchant:
        # 更新现有记录
        existing_merchant.business_name = business_name
        existing_merchant.contact_person = contact_person
        existing_merchant.contact_phone = contact_phone
        existing_merchant.business_address = business_address
        existing_merchant.business_description = business_description
        existing_merchant.status = "pending_verification"
        existing_merchant.updated_at = datetime.utcnow()
        db_merchant = existing_merchant
    else:
        # 创建新记录
        db_merchant = Merchant(
            user_id=user_id,
            business_name=business_name,
            business_license=None,
            contact_person=contact_person,
            contact_phone=contact_phone,
            business_address=business_address,
            business_description=business_description,
            status="pending_verification",
            is_pending=True
        )
        db.add(db_merchant)
    
    # 更新用户状态
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_pending_verification = True
        user.is_pending_merchant = False
        db.add(user)
        
        # 下架用户所有商品
        items = db.query(Item).filter(Item.owner_id == user.id).all()
        for item in items:
            item.status = "offline"
            db.add(item)
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

def get_pending_merchants(db: Session, skip: int = 0, limit: int = 100) -> List[Merchant]:
    """获取待审核的商家列表"""
    return db.query(Merchant).filter(Merchant.status == "pending").offset(skip).limit(limit).all()

def get_all_merchants(db: Session, skip: int = 0, limit: int = 100) -> List[Merchant]:
    """获取所有商家列表"""
    return db.query(Merchant).offset(skip).limit(limit).all()

def create_pending_merchant(db: Session, user_id: int, business_name: str, contact_person: str, 
                          contact_phone: str, business_address: str, business_description: Optional[str] = None) -> Merchant:
    """管理员创建待定商家"""
    # 创建商家记录
    db_merchant = Merchant(
        user_id=user_id,
        business_name=business_name,
        business_license=None,
        contact_person=contact_person,
        contact_phone=contact_phone,
        business_address=business_address,
        business_description=business_description,
        status="pending",
        is_pending=True
    )
    db.add(db_merchant)
    
    # 更新用户为待定商家
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_pending_merchant = True
        # 下架用户的所有商品
        db.query(Item).filter(Item.owner_id == user_id).update({"status": "offline"})
    
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

def delete_merchant(db: Session, merchant_id: int) -> bool:
    """删除商家"""
    db_merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not db_merchant:
        return False
    
    # 更新用户状态
    user = db.query(User).filter(User.id == db_merchant.user_id).first()
    if user:
        user.is_merchant = False
        user.is_pending_merchant = False
    
    db.delete(db_merchant)
    db.commit()
    return True

# 商家展示配置相关操作
def create_merchant_display_config(db: Session, config: MerchantDisplayConfigCreate, user_id: Optional[int] = None) -> MerchantDisplayConfig:
    """创建商家展示配置"""
    db_config = MerchantDisplayConfig(
        user_id=user_id,
        display_frequency=config.display_frequency,
        is_default=(user_id is None)
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def get_merchant_display_config(db: Session, user_id: Optional[int] = None) -> Optional[MerchantDisplayConfig]:
    """获取商家展示配置"""
    if user_id:
        # 获取用户特定配置
        return db.query(MerchantDisplayConfig).filter(MerchantDisplayConfig.user_id == user_id).first()
    else:
        # 获取全局默认配置
        return db.query(MerchantDisplayConfig).filter(MerchantDisplayConfig.is_default == True).first()

def update_merchant_display_config(db: Session, config_id: int, config_update: MerchantDisplayConfigUpdate) -> Optional[MerchantDisplayConfig]:
    """更新商家展示配置"""
    db_config = db.query(MerchantDisplayConfig).filter(MerchantDisplayConfig.id == config_id).first()
    if not db_config:
        return None
    
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db_config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    return db_config

def get_or_create_user_display_config(db: Session, user_id: int) -> MerchantDisplayConfig:
    """获取或创建用户展示配置"""
    config = get_merchant_display_config(db, user_id)
    if not config:
        # 获取全局默认配置
        default_config = get_merchant_display_config(db, None)
        default_frequency = default_config.display_frequency if default_config else 5
        
        # 创建用户配置
        config = create_merchant_display_config(
            db, 
            MerchantDisplayConfigCreate(display_frequency=default_frequency), 
            user_id
        )
    return config

