from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from core.pwd_util import verify_password
from schemas.token import TokenData
from crud.crud_user import get_user_by_username, get_user_by_email, get_user_by_phone  # 导入CRUD方法

# JWT配置
SECRET_KEY = "196ca263383b2fd21dfae2eda445f30b25d14806a861ababf10a408beb5e2117"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def authenticate_user(db: Session, identifier: str, password: str):
    """验证用户凭据，支持用户名/邮箱/手机号"""
    user = None
    
    # 尝试通过用户名查找
    if not user:
        user = get_user_by_username(db, identifier)
    
    # 尝试通过邮箱查找
    if not user:
        user = get_user_by_email(db, identifier)
    
    # 尝试通过手机号查找
    if not user:
        user = get_user_by_phone(db, identifier)
    
    if not user:
        return False
    if not user.is_active:  # 检查用户是否激活
        return None  # 返回None表示用户存在但未激活
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str = payload.get("sub")
        if not subject:
            raise credentials_exception
        token_data = TokenData(username=subject)
    except JWTError:
        raise credentials_exception
    
    # 尝试通过用户名查找用户
    user = get_user_by_username(db, token_data.username)
    
    # 如果用户名查找失败，尝试通过邮箱查找
    if user is None:
        user = get_user_by_email(db, token_data.username)
    
    # 如果邮箱查找也失败，尝试通过手机号查找
    if user is None:
        user = get_user_by_phone(db, token_data.username)
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:  # 使用is_active字段检查用户状态
        raise HTTPException(status_code=400, detail="用户已停用")
    return current_user