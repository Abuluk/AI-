#!/usr/bin/env python3
"""
检查数据库表结构和数据
"""

import sqlite3
import os

def check_database_structure():
    """检查数据库结构"""
    
    print("=== 检查数据库结构 ===")
    
    if not os.path.exists('goofish.db'):
        print("❌ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect('goofish.db')
        cursor = conn.cursor()
        
        # 1. 检查所有表
        print("\n1. 数据库中的所有表:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"   - {table[0]}")
        
        # 2. 检查items表结构
        print("\n2. items表结构:")
        cursor.execute("PRAGMA table_info(items)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - NULL: {col[3]} - Default: {col[4]}")
        
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
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_structure() 