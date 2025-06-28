import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

class Settings:
    PROJECT_NAME: str = "校园二手交易平台"
    PROJECT_VERSION: str = "1.0.0"
    
    # 数据库配置 - MySQL
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "20030208..")
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "ershou")
    DATABASE_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "196ca263383b2fd21dfae2eda445f30b25d14806a861ababf10a408beb5e2117")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
    
    # 文件存储
    AVATAR_UPLOAD_DIR: str = "static/images"  # 使用正斜杠避免转义问题
    MAX_AVATAR_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # 云存储配置 (可选)
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    USE_CLOUD_STORAGE: bool = os.getenv("USE_CLOUD_STORAGE", "false").lower() == "true"
    
    # 科大讯飞星火大模型配置
    XUNFEI_APP_ID: str = os.getenv("XUNFEI_APP_ID", "")
    XUNFEI_API_KEY: str = os.getenv("XUNFEI_API_KEY", "")
    XUNFEI_API_SECRET: str = os.getenv("XUNFEI_API_SECRET", "")
    XUNFEI_SPARK_URL: str = os.getenv("XUNFEI_SPARK_URL", "wss://spark-api.xf-yun.com/v1/x1")

settings = Settings()