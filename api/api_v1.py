from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from .endpoints import (
    items, 
    users, 
    messages, 
    auth,
    profile
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

api_router = APIRouter()

# 公共路由 - 无需认证
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])

from .endpoints import favorites  # 新增导入

api_router.include_router(
    favorites.router,
    prefix="/favorites",
    tags=["收藏"],
    dependencies=[Depends(oauth2_scheme)]
)

# 受保护路由 - 需要认证
api_router.include_router(
    items.router, 
    prefix="/items", 
    tags=["商品"],
    dependencies=[Depends(oauth2_scheme)]
)
api_router.include_router(
    messages.router, 
    prefix="/messages", 
    tags=["消息"],
    dependencies=[Depends(oauth2_scheme)]
)
api_router.include_router(
    profile.router,
    prefix="/profile",
    tags=["个人中心"],
    dependencies=[Depends(oauth2_scheme)]
)