from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User

def set_user_as_admin():
    """将用户设置为管理员"""
    print("=== 设置用户为管理员 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        
        # 查找用户
        user = db.query(User).filter(User.username == "directuser2").first()
        if not user:
            print("❌ 用户不存在")
            return False
        
        print(f"找到用户: {user.username}")
        
        # 设置为管理员
        user.is_admin = True
        db.commit()
        db.refresh(user)
        
        print(f"✅ 用户 {user.username} 已设置为管理员")
        return True
        
    except Exception as e:
        print(f"❌ 设置管理员失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始设置管理员...")
    
    if set_user_as_admin():
        print("✅ 管理员设置完成")
    else:
        print("❌ 管理员设置失败")

if __name__ == "__main__":
    main() 