from sqlalchemy.orm import Session
from db.session import get_db
from crud.crud_message import message_crud
from crud.crud_item import get_item
from schemas.message import MessageCreate
from db.models import User

def debug_message_creation():
    """调试消息创建"""
    print("=== 调试消息创建 ===")
    
    try:
        # 获取数据库会话
        db = next(get_db())
        print("✅ 数据库会话获取成功")
        
        # 获取商品
        item = get_item(db, item_id=13)
        if not item:
            print("❌ 商品不存在")
            return False
        print(f"✅ 找到商品: {item.title}")
        
        # 获取用户
        user = db.query(User).filter(User.username == "directuser").first()
        if not user:
            print("❌ 用户不存在")
            return False
        print(f"✅ 找到用户: {user.username}")
        
        # 创建消息数据
        message_data = {
            "content": "这是一条测试消息",
            "item_id": 13,
            "user_id": user.id
        }
        
        print(f"消息数据: {message_data}")
        
        # 创建消息
        message = message_crud.create(db, obj_in=message_data)
        print(f"✅ 消息创建成功: {message.content}")
        
        # 清理测试消息
        db.delete(message)
        db.commit()
        print("✅ 测试消息已清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_schema():
    """测试消息schema"""
    print("\n=== 测试消息Schema ===")
    
    try:
        message_data = {
            "content": "测试消息内容",
            "item_id": 13
        }
        
        message_create = MessageCreate(**message_data)
        print(f"✅ Schema验证成功: {message_create.content}")
        return True
        
    except Exception as e:
        print(f"❌ Schema验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始调试消息功能...")
    
    # 测试消息schema
    schema_ok = test_message_schema()
    
    # 调试消息创建
    message_ok = debug_message_creation()
    
    if schema_ok and message_ok:
        print("\n✅ 所有测试通过")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main() 