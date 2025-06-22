#!/usr/bin/env python3
"""
检查管理员用户信息
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User
from core.pwd_util import verify_password

# 创建数据库连接
engine = create_engine("sqlite:///goofish.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_admin_user():
    db = SessionLocal()
    try:
        # 查找所有管理员用户
        admin_users = db.query(User).filter(User.is_admin == True).all()
        
        print("=== 管理员用户列表 ===")
        if not admin_users:
            print("没有找到管理员用户")
            return
        
        for user in admin_users:
            print(f"ID: {user.id}")
            print(f"用户名: {user.username}")
            print(f"邮箱: {user.email}")
            print(f"手机: {user.phone}")
            print(f"是否激活: {user.is_active}")
            print(f"是否管理员: {user.is_admin}")
            print(f"创建时间: {user.created_at}")
            print("---")
        
        # 测试密码验证
        print("\n=== 测试密码验证 ===")
        test_user = admin_users[0]
        test_passwords = ["password123", "directpass123", "admin123", "123456"]
        
        for password in test_passwords:
            is_valid = verify_password(password, test_user.hashed_password)
            print(f"密码 '{password}': {'✅ 正确' if is_valid else '❌ 错误'}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user() 