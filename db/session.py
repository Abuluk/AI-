from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 使用配置文件中的数据库连接字符串
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 创建数据库引擎，无需传递 check_same_thread（MySQL 不需要）
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建 SessionLocal，用于获取数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    生成数据库会话的生成器函数，请求结束后自动关闭会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()