from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from .endpoints import (
    items, 
    users, 
    messages, 
    auth,
    profile,
    admin,
    buy_requests,  # 新增导入
    favorites,  # 新增导入
    site_config  # 新增导入site_config
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

api_router = APIRouter()

# 公共路由 - 无需认证
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])

# 公开的商品路由 - 无需认证
api_router.include_router(
    items.router, 
    prefix="/items", 
    tags=["商品"]
)

api_router.include_router(
    favorites.router,
    prefix="/favorites",
    tags=["收藏"],
    dependencies=[Depends(oauth2_scheme)]
)

# 注册site_config路由，无需认证
api_router.include_router(
    site_config.router,
    prefix="/site_config",
    tags=["站点配置"]
)

# 受保护路由 - 需要认证
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

# 管理员路由 - 需要管理员权限
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["管理员"],
    dependencies=[Depends(oauth2_scheme)]
)

# 求购信息路由
api_router.include_router(
    buy_requests.router,
    prefix="/buy_requests",
    tags=["求购信息"]
)