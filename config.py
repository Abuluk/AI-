# config.py
# 配置文件

import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

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
    构建完整的图片URL，处理各种路径格式
    """
    if not image_path:
        return None
        
    # 如果已经是完整URL，检查是否需要修正域名
    if image_path.startswith('http'):
        # 修正错误的localhost和协议
        if 'localhost:8000' in image_path or '127.0.0.1:8000' in image_path:
            # 提取文件名部分
            if '/static/images/' in image_path:
                filename = image_path.split('/static/images/')[-1]
                base_url = get_image_base_url()
                return f"{base_url}/{filename}"
        return image_path
    
    # 清理路径，移除多余的前缀和斜杠
    clean_path = image_path.strip()
    if clean_path.startswith('/'):
        clean_path = clean_path[1:]
    if clean_path.startswith('static/images/'):
        clean_path = clean_path[13:]
    
    # 构建完整URL，确保没有双斜杠
    base_url = get_image_base_url()
    if base_url.endswith('/') and clean_path.startswith('/'):
        return f"{base_url}{clean_path[1:]}"
    elif not base_url.endswith('/') and not clean_path.startswith('/'):
        return f"{base_url}/{clean_path}"
    else:
        return f"{base_url}{clean_path}"

