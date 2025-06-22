#!/usr/bin/env python3
"""
MySQL数据库迁移脚本：为用户表添加is_admin字段
"""

import mysql.connector
import os
from mysql.connector import Error

def add_admin_field_mysql():
    """为MySQL数据库的users表添加is_admin字段"""
    
    # MySQL连接配置
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '20030208..',
        'database': 'ershou'
    }
    
    try:
        # 连接MySQL数据库
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("✅ 成功连接到MySQL数据库")
        
        # 检查字段是否已存在
        cursor.execute("DESCRIBE users")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("✅ is_admin字段已存在")
        else:
            # 添加is_admin字段
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            print("✅ 成功添加is_admin字段")
        
        # 设置第一个用户为管理员
        cursor.execute("SELECT id, username, email FROM users ORDER BY id LIMIT 1")
        first_user = cursor.fetchone()
        
        if first_user:
            user_id, username, email = first_user
            cursor.execute("UPDATE users SET is_admin = TRUE WHERE id = %s", (user_id,))
            print(f"✅ 已将用户 {username or email} (ID: {user_id}) 设为管理员")
        
        # 提交更改
        connection.commit()
        
        # 验证更改
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE is_admin = TRUE")
        admins = cursor.fetchall()
        
        print(f"\n📊 当前管理员列表:")
        for admin in admins:
            user_id, username, email, is_admin = admin
            print(f"   - {username or email} (ID: {user_id}) - 管理员: {'是' if is_admin else '否'}")
        
        print(f"\n🎉 MySQL数据库迁移完成！")
        
    except Error as e:
        print(f"❌ MySQL数据库操作失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ 数据库连接已关闭")

if __name__ == "__main__":
    print("开始MySQL数据库迁移...")
    add_admin_field_mysql()
    print("迁移完成") 