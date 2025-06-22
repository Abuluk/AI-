from sqlalchemy.orm import Session
from db.session import get_db
from crud.crud_user import create_user, get_user_by_username, get_user_by_email
from schemas.user import UserCreate
from core.pwd_util import get_password_hash

def debug_register():
    """调试注册功能"""
    print("=== 调试注册功能 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        print("✅ 数据库会话获取成功")
        
        # 创建用户数据
        user_data = {
            "username": "debuguser",
            "email": "debug@test.com",
            "password": "debugpass123"
        }
        
        print(f"用户数据: {user_data}")
        
        # 创建UserCreate对象
        user_create = UserCreate(**user_data)
        print(f"✅ UserCreate对象创建成功: {user_create.username}")
        
        # 检查用户是否已存在
        existing_username = get_user_by_username(db, username=user_create.username)
        if existing_username:
            print(f"⚠️ 用户名已存在: {existing_username.username}")
            return False
        
        existing_email = get_user_by_email(db, email=user_create.email)
        if existing_email:
            print(f"⚠️ 邮箱已存在: {existing_email.email}")
            return False
        
        print("✅ 用户名和邮箱检查通过")
        
        # 创建用户
        user = create_user(db, user_create)
        print(f"✅ 用户创建成功: {user.username} (ID: {user.id})")
        
        # 清理测试用户
        db.delete(user)
        db.commit()
        print("✅ 测试用户已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 注册失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_password_hash():
    """测试密码哈希"""
    print("\n=== 测试密码哈希 ===")
    
    try:
        password = "testpass123"
        hashed = get_password_hash(password)
        print(f"✅ 密码哈希成功: {hashed[:20]}...")
        return True
    except Exception as e:
        print(f"❌ 密码哈希失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始调试注册功能...")
    
    # 测试密码哈希
    hash_ok = test_password_hash()
    
    # 调试注册
    register_ok = debug_register()
    
    if hash_ok and register_ok:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main() 