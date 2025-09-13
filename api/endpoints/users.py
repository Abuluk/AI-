from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user, get_current_user
from db.models import User
from db.models import Item
from schemas.user import UserInDB, UserUpdate, UserPublic, UserIds
from config import get_full_image_url
from db.models import Favorite
from schemas.item import ItemInDB
from schemas.favorite import FavoriteInDB
from typing import List, Optional
from crud.crud_user import (
    get_user,
    update_user,
    delete_user,
    get_users_by_ids
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import random, string, time
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

# 简单内存验证码存储，生产建议用redis
reset_codes = {}

class RequestPasswordReset(BaseModel):
    account: EmailStr

class DoResetPassword(BaseModel):
    account: EmailStr
    code: str
    new_password: str

def send_email_code(to_email, code):
    # 这里请替换为你自己的邮箱配置
    smtp_server = 'smtp.qq.com'
    smtp_port = 465
    smtp_user = '2720691438@qq.com'
    smtp_pass = 'zzpvejnmtsvbdghi'
    msg = MIMEText(f'您的验证码是：{code}，5分钟内有效。', 'plain', 'utf-8')
    msg['Subject'] = '找回密码验证码'
    msg['From'] = smtp_user
    msg['To'] = to_email
    s = smtplib.SMTP_SSL(smtp_server, smtp_port)
    s.login(smtp_user, smtp_pass)
    s.sendmail(smtp_user, [to_email], msg.as_string())
    s.quit()

@router.get("/me", response_model=UserInDB)
def read_user_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 计算用户的商品数量
    items_count = db.query(Item).filter(Item.owner_id == current_user.id).count()
    
    # 返回完整的用户信息，包括is_admin字段
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone,
        "avatar": get_full_image_url(current_user.avatar),
        "bio": current_user.bio,
        "location": current_user.location,
        "contact": current_user.contact,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "last_login": current_user.last_login,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "followers": current_user.followers,
        "following": current_user.following,
        "items_count": items_count,
        "is_merchant": current_user.is_merchant or False,
        "is_pending_merchant": current_user.is_pending_merchant or False,
        "is_pending_verification": current_user.is_pending_verification or False
    }

@router.put("/me", response_model=UserInDB)
def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    return update_user(db, user_id=current_user.id, user_update=user_update)

@router.delete("/me")
def delete_user_me(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    delete_user(db, user_id=current_user.id)
    return {"message": "用户已删除"}

@router.get("/{user_id}/stats")
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    # 获取用户商品统计
    selling_count = db.query(Item).filter(
        Item.owner_id == user_id,
        Item.sold == False,
        Item.status.in_(["online", "active"])
    ).count()
    
    sold_count = db.query(Item).filter(
        Item.owner_id == user_id,
        Item.sold == True
    ).count()
    
    # 获取用户收藏统计
    favorites_count = db.query(Favorite).filter(
        Favorite.user_id == user_id
    ).count()
    
    return {
        "selling": selling_count,
        "sold": sold_count,
        "favorites": favorites_count
    }

# 添加用户商品查询路由
@router.get("/{user_id}/items")
def get_user_items(
    user_id: int,
    status: Optional[str] = Query("selling", description="商品状态: selling(在售), sold(已售), offline(下架)"),
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(10, description="每页记录数"),
    order_by: str = Query("created_at_desc", description="排序方式: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎)"),
    db: Session = Depends(get_db)
):
    """
    获取指定用户的商品列表，可按状态筛选和排序，返回分页数据和总数
    """
    # 验证用户存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 根据状态筛选商品
    query = db.query(Item).filter(Item.owner_id == user_id)
    if status == "selling":
        query = query.filter(Item.sold == False, Item.status.in_(["online", "active"]))
    elif status == "sold":
        query = query.filter(Item.sold == True)
    elif status == "offline":
        query = query.filter(Item.status == "offline")
    else:
        return JSONResponse(content={"data": [], "total": 0})
    # 总数
    total = query.count()
    # 排序
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "created_at_asc":
        query = query.order_by(Item.created_at.asc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        query = query.order_by(Item.created_at.desc())
    # 分页
    items = query.offset(skip).limit(limit).all()
    
    # 处理图片路径
    for item in items:
        if item.images:
            images = item.images.split(',')
            processed_images = []
            for img in images:
                img = img.strip()
                if img:
                    full_url = get_full_image_url(img)
                    if full_url:
                        processed_images.append(full_url)
            item.images = ','.join(processed_images)
    
    return {"data": items, "total": total}

@router.get("/pending-verification")
def get_pending_verification_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(""),
    db: Session = Depends(get_db)
):
    """获取待认证用户列表"""
    query = db.query(User).filter(User.is_pending_verification == True)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.phone.contains(search))
        )
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    # 计算每个用户的商品数量
    user_data = []
    for user in users:
        items_count = db.query(Item).filter(Item.owner_id == user.id).count()
        user_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": get_full_image_url(user.avatar),
            "bio": user.bio,
            "location": user.location,
            "contact": user.contact,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "followers": user.followers,
            "following": user.following,
            "items_count": items_count,
            "is_merchant": user.is_merchant or False,
            "is_pending_merchant": user.is_pending_merchant or False,
            "is_pending_verification": user.is_pending_verification or False
        })
    
    return {
        "data": user_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{user_id}", response_model=UserInDB)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算用户的商品数量
    items_count = db.query(Item).filter(Item.owner_id == user_id).count()
    
    # 返回用户信息，包含商品数量
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar,
        "bio": user.bio,
        "location": user.location,
        "contact": user.contact,
        "phone": user.phone,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "followers": user.followers,
        "following": user.following,
        "items_count": items_count,
        "is_merchant": user.is_merchant or False,
        "is_pending_merchant": user.is_pending_merchant or False
    }

@router.post("/by_ids", response_model=List[UserPublic])
def get_users_info_by_ids(
    payload: UserIds,
    db: Session = Depends(get_db)
):
    """
    根据用户ID列表批量获取用户信息
    """
    users = get_users_by_ids(db, user_ids=payload.user_ids)
    return users

@router.post('/request-password-reset')
def request_password_reset(data: RequestPasswordReset, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.account).first()
    if not user:
        raise HTTPException(status_code=404, detail='用户不存在')
    code = ''.join(random.choices(string.digits, k=6))
    reset_codes[data.account] = (code, time.time())
    background_tasks.add_task(send_email_code, data.account, code)
    return {'msg': '验证码已发送'}

@router.post('/reset-password')
def reset_password(data: DoResetPassword, db: Session = Depends(get_db)):
    code_tuple = reset_codes.get(data.account)
    if not code_tuple or code_tuple[0] != data.code or time.time() - code_tuple[1] > 300:
        raise HTTPException(status_code=400, detail='验证码错误或已过期')
    user = db.query(User).filter(User.email == data.account).first()
    if not user:
        raise HTTPException(status_code=404, detail='用户不存在')
    from core.pwd_util import get_password_hash
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    reset_codes.pop(data.account, None)
    return {'msg': '密码重置成功'}

@router.get("/search", response_model=UserInDB)
def search_user(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """搜索用户（通过用户名、邮箱或手机号）"""
    # 尝试通过用户名查找
    user = db.query(User).filter(User.username == keyword).first()
    
    # 尝试通过邮箱查找
    if not user:
        user = db.query(User).filter(User.email == keyword).first()
    
    # 尝试通过手机号查找
    if not user:
        user = db.query(User).filter(User.phone == keyword).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算用户的商品数量
    items_count = db.query(Item).filter(Item.owner_id == user.id).count()
    
    # 返回用户信息，包含商品数量
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "avatar": user.avatar,
        "bio": user.bio,
        "location": user.location,
        "contact": user.contact,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login,
        "followers": user.followers,
        "following": user.following,
        "items_count": items_count,
        "is_merchant": user.is_merchant or False,
        "is_pending_merchant": user.is_pending_merchant or False,
        "is_pending_verification": user.is_pending_verification or False
    }

@router.get("/{user_id}/avatar")
def get_user_avatar(user_id: int, db: Session = Depends(get_db)):
    """获取用户头像URL"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 返回用户头像URL，如果没有头像则返回默认头像
    if user.avatar:
        return {"avatar_url": get_full_image_url(user.avatar)}
    else:
        return {"avatar_url": "http://127.0.0.1:8000/static/images/default_avatar.png"}
