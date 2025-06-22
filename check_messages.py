#!/usr/bin/env python3
"""
检查数据库中的消息数据
"""

import mysql.connector
from mysql.connector import Error

def check_messages():
    """检查数据库中的消息数据"""
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
        
        print("=== 检查数据库中的消息数据 ===")
        
        # 查询所有消息
        query = "SELECT * FROM messages ORDER BY created_at DESC LIMIT 10"
        cursor.execute(query)
        messages = cursor.fetchall()
        
        if messages:
            print(f"✅ 找到了 {len(messages)} 条消息：")
            for msg in messages:
                print(f"  - ID: {msg['id']}, 用户ID: {msg['user_id']}, 商品ID: {msg['item_id']}, 内容: {msg['content'][:50]}..., 是否系统消息: {msg['is_system']}")
        else:
            print("❌ 没有找到任何消息")
        
        # 查询用户信息
        print("\n=== 检查用户信息 ===")
        cursor.execute("SELECT id, username, email FROM users LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            print("用户列表：")
            for user in users:
                print(f"  - ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email']}")
        
        # 查询商品信息
        print("\n=== 检查商品信息 ===")
        cursor.execute("SELECT id, title, owner_id FROM items LIMIT 5")
        items = cursor.fetchall()
        
        if items:
            print("商品列表：")
            for item in items:
                print(f"  - ID: {item['id']}, 标题: {item['title']}, 所有者ID: {item['owner_id']}")
        
        # 检查特定用户的消息
        print("\n=== 检查用户ID为3的消息 ===")
        cursor.execute("SELECT * FROM messages WHERE user_id = 3")
        user_messages = cursor.fetchall()
        
        if user_messages:
            print(f"用户ID为3的消息：{len(user_messages)}条")
            for msg in user_messages:
                print(f"  - ID: {msg['id']}, 商品ID: {msg['item_id']}, 内容: {msg['content'][:50]}...")
        else:
            print("用户ID为3没有发送任何消息")
        
        # 检查发给用户ID为3的消息（通过商品所有者）
        print("\n=== 检查发给用户ID为3的消息（作为商品所有者） ===")
        cursor.execute("""
            SELECT m.* FROM messages m 
            JOIN items i ON m.item_id = i.id 
            WHERE i.owner_id = 3 AND m.user_id != 3
        """)
        received_messages = cursor.fetchall()
        
        if received_messages:
            print(f"发给用户ID为3的消息：{len(received_messages)}条")
            for msg in received_messages:
                print(f"  - ID: {msg['id']}, 发送者ID: {msg['user_id']}, 商品ID: {msg['item_id']}, 内容: {msg['content'][:50]}...")
        else:
            print("用户ID为3没有收到任何消息")
            
    except Error as e:
        print(f"❌ 数据库操作出错: {e}")

    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭。")

if __name__ == "__main__":
    check_messages() 