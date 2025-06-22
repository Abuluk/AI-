from sqlalchemy.orm import Session
from db.session import get_db
from crud.crud_message import message_crud
from schemas.message import SystemMessageCreate
from db.models import User

def debug_system_message():
    """调试系统消息创建"""
    print("=== 调试系统消息创建 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        print("✅ 数据库会话获取成功")
        
        # 获取管理员用户
        admin = db.query(User).filter(User.username == "directuser2").first()
        if not admin:
            print("❌ 管理员用户不存在")
            return False
        print(f"✅ 找到管理员: {admin.username}")
        
        # 创建系统消息数据
        message_data = {
            "content": "这是一条系统测试消息",
            "title": "系统通知",
            "target_users": "all",
            "item_id": 13
        }
        
        print(f"系统消息数据: {message_data}")
        
        # 创建SystemMessageCreate对象
        system_message = SystemMessageCreate(**message_data)
        print(f"✅ SystemMessageCreate对象创建成功: {system_message.content}")
        
        # 创建系统消息
        message = message_crud.create_system_message(db, message_in=system_message, admin_id=admin.id)
        print(f"✅ 系统消息创建成功: {message.content}")
        
        # 清理测试消息
        db.delete(message)
        db.commit()
        print("✅ 测试系统消息已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统消息创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始调试系统消息功能...")
    
    if debug_system_message():
        print("\n✅ 系统消息测试通过")
    else:
        print("\n❌ 系统消息测试失败")

if __name__ == "__main__":
    main() 