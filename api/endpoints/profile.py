from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from db.models import User, BuyRequest
from schemas.user import UserInDB, UserUpdate
from crud.crud_user import update_user
import os
from fastapi import Request
from schemas.buy_request import BuyRequest as BuyRequestSchema
from typing import List

router = APIRouter()

# 添加POST路由路径（文件上传通常使用POST方法）
@router.post("/avatar")
async def update_avatar(
    request: Request,
    # 将 file 改为 avatar，与前端发送的字段名一致
    avatar: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    # 验证文件类型
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只能上传图片文件"
        )
    
    # 验证文件大小
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    contents = await avatar.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件大小超过5MB限制"
        )
    
    # 重置文件指针
    await avatar.seek(0)
    
    # 生成唯一文件名
    import uuid
    ext = avatar.filename.split('.')[-1]
    filename = f"user_{current_user.id}_{uuid.uuid4().hex}.{ext}"
    
    # 保存文件
    UPLOAD_DIR = "static/images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # 构建正确的头像URL，使用统一的图片URL处理函数
    from config import get_full_image_url
    avatar_url = get_full_image_url(f"static/images/{filename}")
    
    # 更新用户头像
    user_update = UserUpdate(avatar=avatar_url)
    updated_user = update_user(db, user_id=current_user.id, user_update=user_update)
    
    # 返回包含头像URL的响应
    return {"avatar": avatar_url}

@router.put("/", response_model=UserInDB)
def update_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 更新用户资料
    updated_user = update_user(db, user_id=current_user.id, user_update=user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return updated_user

@router.get("/my_buy_requests", response_model=List[BuyRequestSchema])
def my_buy_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(BuyRequest).filter(BuyRequest.user_id == current_user.id).order_by(BuyRequest.created_at.desc()).all()