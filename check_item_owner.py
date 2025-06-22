import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
import os
import sys

# 将项目根目录添加到Python路径中，以便能导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import Item

# --- 配置 ---
ITEM_ID_TO_CHECK = 13
# 假设数据库文件在项目根目录
DATABASE_URL = "sqlite:///goofish.db" 

def get_item_owner():
    """连接数据库，查询并打印指定ID的商品所有者"""
    try:
        engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db: Session = SessionLocal()
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print(f"请确认数据库文件路径是否正确: {DATABASE_URL}")
        return

    try:
        print(f"正在查询 Item ID: {ITEM_ID_TO_CHECK}...")
        item = db.query(Item).filter(Item.id == ITEM_ID_TO_CHECK).first()

        if item:
            print("--- 查询成功 ---")
            print(f"商品 (Item) ID: {item.id}")
            print(f"商品标题 (Title): {item.title}")
            print(f"商品主人 (Owner ID): {item.owner_id}")
            print("-----------------")
            if item.owner_id == 1:
                print("\n结论：你的账号 (user_id=1) 正是这个商品的主人。")
                print("所以，你能看到关于这件商品的所有对话是符合预期的。")
            else:
                 print(f"\n结论：商品的主人是 user_id={item.owner_id}，而不是你 (user_id=1)。")
                 print("这说明系统中可能存在一个让你看到不属于你的对话的BUG。")

        else:
            print(f"--- 查询失败 ---")
            print(f"在数据库中找不到 ID 为 {ITEM_ID_TO_CHECK} 的商品。")
            print("-----------------")

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_item_owner() 