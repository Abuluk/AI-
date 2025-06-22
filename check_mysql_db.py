#!/usr/bin/env python3
"""
检查MySQL数据库状态
"""

import pymysql
from datetime import datetime

def check_mysql_database():
    """检查MySQL数据库"""
    
    print("=== 检查MySQL数据库 ===")
    
    try:
        # 连接MySQL数据库
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='20030208..',
            database='ershou',
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 1. 检查所有表
        print("\n1. 数据库中的所有表:")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # 2. 检查items表结构
        print("\n2. items表结构:")
        cursor.execute("DESCRIBE items")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[0]} ({col[1]}) - NULL: {col[2]} - Default: {col[4]}")
        
        # 3. 检查items表数据
        print("\n3. items表数据:")
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        print(f"   总商品数: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, title, created_at FROM items LIMIT 5")
            items = cursor.fetchall()
            for item in items:
                print(f"   ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 4. 检查users表数据
        print("\n4. users表数据:")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   总用户数: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username FROM users LIMIT 3")
            users = cursor.fetchall()
            for user in users:
                print(f"   ID: {user[0]}, 用户名: {user[1]}")
        
        # 5. 检查需要修复的商品
        print("\n5. 检查需要修复的商品:")
        cursor.execute("SELECT COUNT(*) FROM items WHERE created_at IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"   created_at为NULL的商品数: {null_count}")
        
        if null_count > 0:
            print("   开始修复...")
            # 为每个商品设置不同的时间
            import random
            base_time = datetime.now()
            
            cursor.execute("SELECT id FROM items WHERE created_at IS NULL")
            null_items = cursor.fetchall()
            
            for i, (item_id,) in enumerate(null_items):
                # 为每个商品设置一个随机的时间（最近30天内）
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                
                item_time = base_time.replace(
                    day=base_time.day - days_ago,
                    hour=base_time.hour - hours_ago,
                    minute=base_time.minute - minutes_ago
                )
                
                cursor.execute(
                    "UPDATE items SET created_at = %s WHERE id = %s",
                    (item_time, item_id)
                )
                
                if (i + 1) % 10 == 0:
                    print(f"   已修复 {i + 1}/{null_count} 个商品")
            
            # 提交更改
            conn.commit()
            print(f"   ✅ 成功修复 {null_count} 个商品")
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("请确保MySQL服务正在运行，并且连接信息正确")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_mysql_database() 