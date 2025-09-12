from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user, get_current_user
from db.models import User, Merchant
from config import get_full_image_url
from schemas.merchant import (
    MerchantCreate, MerchantUpdate, MerchantInDB, 
    MerchantDisplayConfigCreate, MerchantDisplayConfigUpdate, MerchantDisplayConfigInDB,
    MerchantStatusUpdate, PendingMerchantCreate, SetPendingVerificationRequest
)
from crud.crud_merchant import (
    create_merchant, get_merchant_by_user_id, get_merchant_by_id, update_merchant,
    update_merchant_status, get_pending_merchants, get_all_merchants,
    create_pending_merchant, delete_merchant,
    create_merchant_display_config, get_merchant_display_config, 
    update_merchant_display_config, get_or_create_user_display_config
)
from typing import List, Optional

router = APIRouter()

# 用户商家认证相关端点
@router.post("/apply", response_model=MerchantInDB)
def apply_merchant_verification(
    merchant: MerchantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """用户申请商家认证"""
    # 检查是否已经是商家
    if current_user.is_merchant:
        raise HTTPException(status_code=400, detail="您已经是认证商家")
    
    # 检查是否已有商家记录
    existing_merchant = get_merchant_by_user_id(db, current_user.id)
    if existing_merchant:
        if existing_merchant.status == "pending":
            raise HTTPException(status_code=400, detail="您已有待审核的商家认证申请")
        elif existing_merchant.status == "approved":
            raise HTTPException(status_code=400, detail="您已经是认证商家")
        elif existing_merchant.status == "rejected":
            # 如果之前被拒绝，更新现有记录
            updated_merchant = update_merchant(db, existing_merchant.id, merchant)
            # 更新状态为待审核
            updated_merchant = update_merchant_status(db, existing_merchant.id, "pending")
            # 更新用户状态
            user = db.query(User).filter(User.id == current_user.id).first()
            if user:
                user.is_pending_merchant = True
                user.is_merchant = False
                user.is_pending_verification = False
                db.commit()
            return updated_merchant
    
    return create_merchant(db, merchant, current_user.id)

@router.get("/my", response_model=Optional[MerchantInDB])
def get_my_merchant_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的商家信息"""
    return get_merchant_by_user_id(db, current_user.id)

@router.delete("/cancel-application")
def cancel_merchant_application(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """取消商家认证申请"""
    from crud.crud_merchant import cancel_merchant_application
    
    success = cancel_merchant_application(db, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="没有可取消的申请")
    
    return {"message": "申请已取消"}

@router.put("/my", response_model=MerchantInDB)
def update_my_merchant_info(
    merchant_update: MerchantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新我的商家信息"""
    merchant = get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(status_code=404, detail="未找到商家信息")
    
    # 更新商家信息
    updated_merchant = update_merchant(db, merchant.id, merchant_update)
    
    # 如果商家已认证，修改后重新进入申请状态
    if merchant.status == "approved":
        # 更新商家状态为待审核
        updated_merchant = update_merchant_status(db, merchant.id, "pending")
        
        # 更新用户状态
        user = db.query(User).filter(User.id == current_user.id).first()
        if user:
            user.is_merchant = False
            user.is_pending_merchant = True
            db.commit()
    
    return updated_merchant

@router.get("/display-config", response_model=MerchantDisplayConfigInDB)
def get_my_display_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取我的商家商品展示配置"""
    return get_or_create_user_display_config(db, current_user.id)

@router.put("/display-config", response_model=MerchantDisplayConfigInDB)
def update_my_display_config(
    config_update: MerchantDisplayConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新我的商家商品展示配置"""
    config = get_or_create_user_display_config(db, current_user.id)
    return update_merchant_display_config(db, config.id, config_update)

# 管理员商家管理端点
@router.get("/admin/pending", response_model=List[MerchantInDB])
def get_pending_merchants_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取待审核商家列表（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    return get_pending_merchants(db, skip, limit)

@router.get("/admin/all")
def get_all_merchants_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(""),
    status: str = Query(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有商家列表（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 构建查询
    query = db.query(Merchant).join(User, Merchant.user_id == User.id)
    
    # 搜索过滤
    if search:
        query = query.filter(
            (Merchant.business_name.contains(search)) |
            (Merchant.contact_person.contains(search)) |
            (User.username.contains(search))
        )
    
    # 状态过滤
    if status and status.strip():
        query = query.filter(Merchant.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页查询
    merchants = query.offset(skip).limit(limit).all()
    
    # 构建返回数据
    result = []
    for merchant in merchants:
        user = db.query(User).filter(User.id == merchant.user_id).first()
        result.append({
            "id": merchant.id,
            "user_id": merchant.user_id,
            "business_name": merchant.business_name,
            "business_license": merchant.business_license,
            "contact_person": merchant.contact_person,
            "contact_phone": merchant.contact_phone,
            "business_address": merchant.business_address,
            "business_description": merchant.business_description,
            "status": merchant.status,
            "is_pending": merchant.is_pending,
            "approved_at": merchant.approved_at,
            "rejected_at": merchant.rejected_at,
            "reject_reason": merchant.reject_reason,
            "created_at": merchant.created_at,
            "updated_at": merchant.updated_at,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "avatar": get_full_image_url(user.avatar),
                "is_merchant": user.is_merchant,
                "is_pending_merchant": user.is_pending_merchant,
                "is_pending_verification": user.is_pending_verification
            } if user else None
        })
    
    return {
        "data": result,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": len(result) == limit
    }

@router.put("/admin/{merchant_id}/status", response_model=MerchantInDB)
def update_merchant_status_admin(
    merchant_id: int,
    status_update: MerchantStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商家状态（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    
    if status_update.status == "rejected" and not status_update.reject_reason:
        raise HTTPException(status_code=400, detail="拒绝时必须提供拒绝原因")
    
    return update_merchant_status(db, merchant_id, status_update.status, status_update.reject_reason)

@router.post("/{merchant_id}/approve", response_model=MerchantInDB)
def approve_merchant(
    merchant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """通过商家认证（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    
    if merchant.status != "pending":
        raise HTTPException(status_code=400, detail="只能审核待审核状态的商家")
    
    # 更新商家状态为已通过
    updated_merchant = update_merchant_status(db, merchant_id, "approved")
    
    # 更新用户为商家
    user = db.query(User).filter(User.id == merchant.user_id).first()
    if user:
        user.is_merchant = True
        user.is_pending_merchant = False
        db.commit()
    
    return updated_merchant

@router.post("/{merchant_id}/reject", response_model=MerchantInDB)
def reject_merchant(
    merchant_id: int,
    reject_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拒绝商家认证（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    
    if merchant.status != "pending":
        raise HTTPException(status_code=400, detail="只能审核待审核状态的商家")
    
    reject_reason = reject_data.get("reason", "")
    if not reject_reason:
        raise HTTPException(status_code=400, detail="拒绝时必须提供拒绝原因")
    
    # 更新商家状态为已拒绝
    updated_merchant = update_merchant_status(db, merchant_id, "rejected", reject_reason)
    
    # 更新用户状态
    user = db.query(User).filter(User.id == merchant.user_id).first()
    if user:
        user.is_merchant = False
        user.is_pending_merchant = False
        db.commit()
        
        # 发送系统消息给被拒绝的用户
        try:
            from crud.crud_message import create_system_message
            from schemas.message import SystemMessageCreate
            
            system_message = SystemMessageCreate(
                title="商家认证申请被拒绝",
                content=f"很抱歉，您的商家认证申请《{merchant.business_name}》已被拒绝。\n\n拒绝原因：{reject_reason}\n\n如有疑问，请联系客服或重新提交申请。",
                target_users=str(merchant.user_id)  # 发送给被拒绝的用户
            )
            
            create_system_message(db=db, message_in=system_message, admin_id=current_user.id)
        except Exception as e:
            # 记录错误但不影响主要流程
            print(f"发送系统消息失败: {e}")
    
    return updated_merchant

@router.post("/admin/pending", response_model=MerchantInDB)
def create_pending_merchant_admin(
    pending_merchant: PendingMerchantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建待定商家（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == pending_merchant.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查用户是否已经是商家或待定商家
    if user.is_merchant or user.is_pending_merchant:
        raise HTTPException(status_code=400, detail="用户已经是商家或待定商家")
    
    return create_pending_merchant(
        db, 
        pending_merchant.user_id,
        pending_merchant.business_name,
        pending_merchant.contact_person,
        pending_merchant.contact_phone,
        pending_merchant.business_address,
        pending_merchant.business_description
    )

@router.delete("/admin/{merchant_id}")
def delete_merchant_admin(
    merchant_id: int,
    delete_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除商家（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取商家信息
    merchant = get_merchant_by_id(db, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")
    
    delete_reason = delete_data.get("reason", "")
    if not delete_reason:
        raise HTTPException(status_code=400, detail="删除时必须提供删除原因")
    
    # 获取用户信息
    user = db.query(User).filter(User.id == merchant.user_id).first()
    if user:
        # 取消用户的商家资格
        user.is_merchant = False
        user.is_pending_merchant = False
        user.is_pending_verification = False
        db.commit()
        
        # 发送系统消息给用户
        try:
            from crud.crud_message import create_system_message
            from schemas.message import SystemMessageCreate
            
            system_message = SystemMessageCreate(
                title="商家认证已被取消",
                content=f"您的商家认证《{merchant.business_name}》已被管理员取消。\n\n取消原因：{delete_reason}\n\n您可以重新提交商家认证申请。",
                target_users=str(merchant.user_id)  # 发送给被取消商家的用户
            )
            
            create_system_message(db=db, message_in=system_message, admin_id=current_user.id)
        except Exception as e:
            # 记录错误但不影响主要流程
            print(f"发送系统消息失败: {e}")
    
    # 删除商家记录
    success = delete_merchant(db, merchant_id)
    if not success:
        raise HTTPException(status_code=404, detail="商家不存在")
    
    return {"message": "商家已删除"}

@router.post("/cancel-application")
def cancel_merchant_application(
    cancel_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """用户申请取消商家认证"""
    if not current_user.is_merchant:
        raise HTTPException(status_code=400, detail="您当前不是商家")
    
    cancel_reason = cancel_data.get("reason", "")
    if not cancel_reason:
        raise HTTPException(status_code=400, detail="请提供取消原因")
    
    # 获取用户的商家信息
    merchant = get_merchant_by_user_id(db, current_user.id)
    if not merchant:
        raise HTTPException(status_code=404, detail="未找到商家信息")
    
    # 更新商家状态为已取消
    updated_merchant = update_merchant_status(db, merchant.id, "cancelled", cancel_reason)
    
    # 更新用户状态
    current_user.is_merchant = False
    current_user.is_pending_merchant = False
    current_user.is_pending_verification = False
    db.commit()
    
    # 发送系统消息给管理员
    try:
        from crud.crud_message import create_system_message
        from schemas.message import SystemMessageCreate
        
        # 获取所有管理员
        admins = db.query(User).filter(User.is_admin == True).all()
        for admin in admins:
            system_message = SystemMessageCreate(
                title="用户申请取消商家认证",
                content=f"用户 {current_user.username} 申请取消商家认证《{merchant.business_name}》。\n\n取消原因：{cancel_reason}",
                target_users=str(admin.id)  # 发送给管理员
            )
            create_system_message(db=db, message_in=system_message, admin_id=current_user.id)
    except Exception as e:
        print(f"发送系统消息失败: {e}")
    
    return {"message": "取消申请已提交，等待管理员处理"}

@router.get("/admin/user/{user_id}", response_model=MerchantInDB)
def get_user_merchant_info_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户的商家信息（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    merchant = get_merchant_by_user_id(db, user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="该用户没有商家信息")
    
    return merchant

@router.post("/admin/user/{user_id}/approve")
def approve_pending_verification_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """通过待认证用户（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_pending_verification:
        raise HTTPException(status_code=400, detail="该用户不是待认证状态")
    
    # 获取商家信息
    merchant = get_merchant_by_user_id(db, user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="该用户没有商家信息")
    
    # 更新商家状态为已通过
    updated_merchant = update_merchant_status(db, merchant.id, "approved")
    
    # 更新用户状态
    user.is_merchant = True
    user.is_pending_verification = False
    user.is_pending_merchant = False
    db.commit()
    
    return {"message": "用户已通过认证"}

@router.post("/admin/user/{user_id}/reject")
def reject_pending_verification_user(
    user_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """拒绝待认证用户（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 获取用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if not user.is_pending_verification:
        raise HTTPException(status_code=400, detail="该用户不是待认证状态")
    
    # 获取商家信息
    merchant = get_merchant_by_user_id(db, user_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="该用户没有商家信息")
    
    # 更新商家状态为已拒绝
    updated_merchant = update_merchant_status(db, merchant.id, "rejected", reason)
    
    # 更新用户状态
    user.is_merchant = False
    user.is_pending_verification = False
    user.is_pending_merchant = False
    db.commit()
    
    # 发送系统消息给被拒绝的用户
    try:
        from crud.crud_message import create_system_message
        from schemas.message import SystemMessageCreate
        
        reject_reason = reason or "未提供具体原因"
        system_message = SystemMessageCreate(
            title="商家认证申请被拒绝",
            content=f"很抱歉，您的商家认证申请《{merchant.business_name}》已被拒绝。\n\n拒绝原因：{reject_reason}\n\n如有疑问，请联系客服或重新提交申请。",
            target_users=str(user_id)  # 发送给被拒绝的用户
        )
        
        create_system_message(db=db, message_in=system_message, admin_id=current_user.id)
    except Exception as e:
        # 记录错误但不影响主要流程
        print(f"发送系统消息失败: {e}")
    
    return {"message": "用户已被拒绝"}

@router.post("/admin/set-pending-verification", response_model=MerchantInDB)
def set_pending_verification_admin(
    user_id: int,
    business_name: str,
    contact_person: str,
    contact_phone: str,
    business_address: str,
    business_description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """设置用户为待认证状态（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    from crud.crud_merchant import set_pending_verification
    
    merchant = set_pending_verification(
        db, user_id, business_name, contact_person, 
        contact_phone, business_address, business_description
    )
    
    if not merchant:
        raise HTTPException(status_code=400, detail="设置失败")
    
    return merchant

# 管理员展示配置管理端点
@router.get("/admin/display-config/default", response_model=MerchantDisplayConfigInDB)
def get_default_display_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取默认展示配置（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    config = get_merchant_display_config(db, None)
    if not config:
        # 创建默认配置
        config = create_merchant_display_config(
            db, 
            MerchantDisplayConfigCreate(display_frequency=5), 
            None
        )
    return config

@router.put("/admin/display-config/default", response_model=MerchantDisplayConfigInDB)
def update_default_display_config(
    config_update: MerchantDisplayConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新默认展示配置（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    config = get_merchant_display_config(db, None)
    if not config:
        # 创建默认配置
        config = create_merchant_display_config(
            db, 
            MerchantDisplayConfigCreate(display_frequency=config_update.display_frequency or 5), 
            None
        )
    else:
        config = update_merchant_display_config(db, config.id, config_update)
    
    return config

@router.post("/remove-pending-verification")
def remove_pending_verification(
    request: SetPendingVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """解除用户待认证状态（管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 解除待认证状态
    user.is_pending_verification = False
    db.commit()
    
    return {"message": "已解除待认证状态"}
