from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form, Body
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import (
    create_access_token,
    authenticate_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from core.pwd_util import get_password_hash
from db.models import User
from crud.crud_user import create_user, get_user_by_username, get_user_by_email, get_user_by_phone  # 导入get_user_by_phone
from schemas.user import UserCreate, UserInDB, UserLogin  # 导入UserLogin
from schemas.token import Token
from pydantic import BaseModel

# 登录请求模型
class LoginRequest(BaseModel):
    identifier: str
    password: str

router = APIRouter()

@router.post("/register", response_model=UserInDB)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )
    
    # 检查手机号是否已存在
    if user_in.phone:
        db_user = get_user_by_phone(db, phone=user_in.phone)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已注册"
            )
    
    # 使用create_user函数创建用户
    db_user = create_user(db, user_in)
    return db_user

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest = Body(...),  # 使用Body接收JSON数据
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, login_data.identifier, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户未激活",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 确定token的sub字段：优先使用username，如果为空则使用邮箱
    token_subject = user.username if user.username else user.email
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_subject}, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_active_user),  # 这里直接使用User模型，因为get_current_active_user返回的是User对象
    db: Session = Depends(get_db)
):
    # 在实际应用中，您可能想将令牌加入黑名单
    # 这里我们只是返回成功消息
    return {"message": "成功退出登录"}

@router.get("/me", response_model=UserInDB)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前登录用户信息"""
    return current_user