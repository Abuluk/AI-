#!/usr/bin/env python3
"""
数据库迁移脚本：为用户表添加is_admin字段
"""

import sqlite3
import os

def add_admin_field():
    """为用户表添加is_admin字段"""
    
    db_path = "goofish.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件 {db_path} 不存在")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' in columns:
            print("✅ is_admin字段已存在")
        else:
            # 添加is_admin字段
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("✅ 成功添加is_admin字段")
        
        # 设置第一个用户为管理员（可选）
        cursor.execute("SELECT id, username, email FROM users ORDER BY id LIMIT 1")
        first_user = cursor.fetchone()
        
        if first_user:
            user_id, username, email = first_user
            cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user_id,))
            print(f"✅ 已将用户 {username or email} (ID: {user_id}) 设为管理员")
        
        # 提交更改
        conn.commit()
        
        # 验证更改
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE is_admin = 1")
        admins = cursor.fetchall()
        
        print(f"\n📊 当前管理员列表:")
        for admin in admins:
            user_id, username, email, is_admin = admin
            print(f"   - {username or email} (ID: {user_id}) - 管理员: {'是' if is_admin else '否'}")
        
        print(f"\n🎉 数据库迁移完成！")
        
    except sqlite3.Error as e:
        print(f"❌ 数据库操作失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("开始数据库迁移...")
    add_admin_field()
    print("迁移完成") 