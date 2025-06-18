from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user
from db.models import User
from schemas.user import UserInDB, UserUpdate
from crud.crud_user import update_user
import os

router = APIRouter()

@router.put("/avatar", response_model=UserInDB)
async def update_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_active_user)
):
    # 确保上传的是图片
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只能上传图片文件"
        )
    
    # 保存图片
    UPLOAD_DIR = "static/avatars"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"user_{current_user.id}_{file.filename}"
    file_path = f"{UPLOAD_DIR}/{filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 更新用户头像
    user_update = UserUpdate(avatar=file_path)
    return update_user(db, user_id=current_user.id, user_update=user_update)