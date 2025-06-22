from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from schemas.user import UserCreate
from core.pwd_util import get_password_hash

def test_db_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        print("✅ 数据库连接成功")
        
        # 测试查询
        users = db.query(User).all()
        print(f"✅ 查询成功，当前用户数量: {len(users)}")
        
        # 测试创建用户
        print("\n=== 测试创建用户 ===")
        test_user = User(
            username="testuser_db",
            email="testdb@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ 用户创建成功: {test_user.username}")
        
        # 清理测试用户
        db.delete(test_user)
        db.commit()
        print("✅ 测试用户已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_schema():
    """测试用户schema"""
    print("\n=== 测试用户Schema ===")
    
    try:
        user_data = {
            "username": "testschema",
            "email": "testschema@example.com",
            "password": "testpass123"
        }
        
        user_create = UserCreate(**user_data)
        print(f"✅ Schema验证成功: {user_create.username}")
        return True
        
    except Exception as e:
        print(f"❌ Schema验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始数据库连接测试...")
    
    # 测试数据库连接
    db_ok = test_db_connection()
    
    # 测试用户schema
    schema_ok = test_user_schema()
    
    if db_ok and schema_ok:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main() 