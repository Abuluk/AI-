#!/usr/bin/env python3
"""
修复MySQL数据库中商品的created_at字段
"""

import pymysql
from datetime import datetime
import random

def fix_mysql_created_at():
    """修复MySQL数据库中商品的created_at字段"""
    
    print("=== 修复MySQL数据库中的created_at字段 ===")
    
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
        
        # 1. 检查需要修复的商品
        print("\n1. 检查需要修复的商品:")
        cursor.execute("SELECT COUNT(*) FROM items WHERE created_at IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"   created_at为NULL的商品数: {null_count}")
        
        if null_count == 0:
            print("   ✅ 所有商品都有created_at字段")
            return
        
        # 2. 显示需要修复的商品
        print("\n2. 需要修复的商品列表:")
        cursor.execute("SELECT id, title FROM items WHERE created_at IS NULL")
        null_items = cursor.fetchall()
        for item in null_items:
            print(f"   ID: {item[0]}, 标题: {item[1]}")
        
        # 3. 开始修复
        print(f"\n3. 开始修复 {null_count} 个商品...")
        
        base_time = datetime.now()
        
        for i, (item_id, title) in enumerate(null_items):
            # 为每个商品设置一个随机的时间（最近30天内）
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            # 创建随机时间
            item_time = base_time.replace(
                day=base_time.day - days_ago,
                hour=base_time.hour - hours_ago,
                minute=base_time.minute - minutes_ago
            )
            
            # 更新数据库
            cursor.execute(
                "UPDATE items SET created_at = %s WHERE id = %s",
                (item_time, item_id)
            )
            
            print(f"   已修复 {i + 1}/{null_count}: ID {item_id} ({title}) -> {item_time}")
        
        # 4. 提交更改
        conn.commit()
        print(f"\n4. ✅ 成功修复 {null_count} 个商品")
        
        # 5. 验证修复结果
        print("\n5. 验证修复结果:")
        cursor.execute("SELECT id, title, created_at FROM items ORDER BY created_at DESC LIMIT 5")
        items = cursor.fetchall()
        for item in items:
            print(f"   ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 6. 检查是否还有NULL值
        cursor.execute("SELECT COUNT(*) FROM items WHERE created_at IS NULL")
        remaining_null = cursor.fetchone()[0]
        print(f"\n6. 剩余NULL值: {remaining_null}")
        
        if remaining_null == 0:
            print("   ✅ 所有商品都已修复完成！")
        else:
            print(f"   ⚠️ 还有 {remaining_null} 个商品需要修复")
        
    except Exception as e:
        print(f"❌ MySQL操作失败: {e}")
        print("请确保MySQL服务正在运行，并且连接信息正确")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_mysql_created_at() 