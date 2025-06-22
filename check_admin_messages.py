import mysql.connector
from mysql.connector import Error

def check_admin_messages():
    """连接到数据库并检查系统消息。"""
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '20030208..',
        'database': 'ershou',
        'charset': 'utf8mb4'
    }
    
    connection = None
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        print("=== 正在检查数据库中的系统消息... ===")
        
        # 查询 is_system 为 true 的消息
        query = "SELECT * FROM messages WHERE is_system = 1"
        cursor.execute(query)
        admin_messages = cursor.fetchall()
        
        if admin_messages:
            print(f"✅ 找到了 {len(admin_messages)} 条系统消息：")
            for msg in admin_messages:
                print(f"  - ID: {msg['id']}, 标题: {msg['title']}, 内容: {msg['content']}")
        else:
            print("❌ 在 `messages` 表中没有找到任何系统消息（即 is_system = 1 的记录）。")
            print("这可能是你没有在管理员后台发布过消息，或者发布时出错了。")
            
    except Error as e:
        print(f"❌ 数据库操作出错: {e}")
        if '1054' in str(e):
             print("提示：你的 `messages` 表可能仍然缺少 `is_system` 等字段。")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭。")

if __name__ == "__main__":
    check_admin_messages() 