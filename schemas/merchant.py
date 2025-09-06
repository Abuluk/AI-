from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MerchantBase(BaseModel):
    business_name: str = Field(..., description="商家名称")
    business_license: Optional[str] = Field(None, description="营业执照号")
    contact_person: str = Field(..., description="联系人")
    contact_phone: str = Field(..., description="联系电话")
    business_address: str = Field(..., description="营业地址")
    business_description: Optional[str] = Field(None, description="商家描述")

class MerchantCreate(MerchantBase):
    pass

class MerchantUpdate(MerchantBase):
    business_name: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    business_address: Optional[str] = None

class MerchantInDB(MerchantBase):
    id: int
    user_id: int
    business_name: str
    business_license: Optional[str]
    contact_person: str
    contact_phone: str
    business_address: str
    business_description: Optional[str]
    status: str  # pending, approved, rejected
    is_pending: bool
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    rejected_at: Optional[datetime]
    reject_reason: Optional[str]
    
    class Config:
        from_attributes = True

class MerchantDisplayConfigBase(BaseModel):
    display_frequency: int = Field(5, ge=1, le=100, description="展示频率，每几个商品展示一个商家商品")

class MerchantDisplayConfigCreate(MerchantDisplayConfigBase):
    pass

class MerchantDisplayConfigUpdate(MerchantDisplayConfigBase):
    display_frequency: Optional[int] = None

class MerchantDisplayConfigInDB(MerchantDisplayConfigBase):
    id: int
    user_id: Optional[int]  # 为None表示全局默认配置
    display_frequency: int
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MerchantStatusUpdate(BaseModel):
    status: str = Field(..., description="状态: approved, rejected")
    reject_reason: Optional[str] = Field(None, description="拒绝原因（当状态为rejected时必填）")

class PendingMerchantCreate(BaseModel):
    user_id: int = Field(..., description="用户ID")
    business_name: str = Field(..., description="商家名称")
    contact_person: str = Field(..., description="联系人")
    contact_phone: str = Field(..., description="联系电话")
    business_address: str = Field(..., description="营业地址")
    business_description: Optional[str] = Field(None, description="商家描述")

class SetPendingVerificationRequest(BaseModel):
    user_id: int = Field(..., description="用户ID")

