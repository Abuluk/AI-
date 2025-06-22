#!/usr/bin/env python3
"""
修复收藏表中created_at字段的脚本
"""

import sqlite3
from datetime import datetime

def fix_favorites_created_at():
    """修复收藏表中的created_at字段"""
    
    # 连接数据库
    conn = sqlite3.connect('goofish.db')
    cursor = conn.cursor()
    
    try:
        # 检查favorites表是否存在created_at字段
        cursor.execute("PRAGMA table_info(favorites)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("favorites表的字段:", column_names)
        
        # 如果created_at字段不存在，添加它
        if 'created_at' not in column_names:
            print("添加created_at字段...")
            cursor.execute("ALTER TABLE favorites ADD COLUMN created_at DATETIME")
        
        # 更新所有created_at为NULL的记录
        print("更新created_at为NULL的记录...")
        cursor.execute("""
            UPDATE favorites 
            SET created_at = ? 
            WHERE created_at IS NULL
        """, (datetime.now(),))
        
        # 提交更改
        conn.commit()
        
        # 检查更新结果
        cursor.execute("SELECT COUNT(*) FROM favorites WHERE created_at IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"更新完成，还有 {null_count} 条记录的created_at为NULL")
        
        # 显示一些示例数据
        cursor.execute("SELECT id, user_id, item_id, created_at FROM favorites LIMIT 5")
        favorites = cursor.fetchall()
        print("示例数据:")
        for fav in favorites:
            print(f"  ID: {fav[0]}, 用户ID: {fav[1]}, 商品ID: {fav[2]}, 创建时间: {fav[3]}")
        
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_favorites_created_at() 