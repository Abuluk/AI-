# config.py
# 配置文件

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent

# 静态文件目录配置 - 支持环境变量覆盖
STATIC_DIR = Path(os.getenv("STATIC_DIR", BASE_DIR / "static"))

# 确保静态目录存在
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "images").mkdir(exist_ok=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True)
(STATIC_DIR / "uploads" / "items").mkdir(exist_ok=True)

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000

# HTTPS配置
USE_HTTPS = False
SSL_CERT_FILE = BASE_DIR / "ssl" / "cert.pem"
SSL_KEY_FILE = BASE_DIR / "ssl" / "key.pem"

# 域名配置
# 开发环境 - 使用IP地址避免localhost的HTTPS限制
DEV_DOMAIN = "127.0.0.1"
# 生产环境（需要替换为真实域名）
PROD_DOMAIN = "your-domain.com"

# 当前环境
ENV = os.getenv("ENV", "development")

# 获取当前域名
def get_domain():
    if ENV == "production":
        return PROD_DOMAIN
    else:
        return DEV_DOMAIN

# 获取图片基础URL
def get_image_base_url():
    domain = get_domain()
    if USE_HTTPS:
        return f"https://{domain}:{PORT}/static/images"
    else:
        return f"http://{domain}:{PORT}/static/images"

# 获取完整的图片URL
def get_full_image_url(image_path):
    """
    构建完整的图片URL
    """
    if not image_path:
        return None
    
    # 如果已经是完整URL，直接返回
    if image_path.startswith('http'):
        return image_path
    
    # 提取文件名
    filename = image_path.split('/')[-1]
    
    # 构建完整URL
    base_url = get_image_base_url()
    return f"{base_url}/{filename}"

