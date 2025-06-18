from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
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
from crud.crud_user import create_user, get_user_by_username, get_user_by_email
from schemas.user import UserCreate, UserInDB
from schemas.token import Token  # 修改为从token.py导入

router = APIRouter()

# ... 其余代码保持不变 ...

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
    
    # 创建用户
    hashed_password = get_password_hash(user_in.password)
    user_create = UserCreate(
        username=user_in.username,
        email=user_in.email,
        password=hashed_password
    )
    return create_user(db, user=user_create)

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(
    current_user: UserInDB = Depends(get_current_active_user),  # 这里使用
    db: Session = Depends(get_db)
):
    # 在实际应用中，您可能想将令牌加入黑名单
    # 这里我们只是返回成功消息
    return {"message": "成功退出登录"}