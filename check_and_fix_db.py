#!/usr/bin/env python3
"""
检查和强制修复数据库中的时间字段
"""

import sqlite3
from datetime import datetime
import os

def check_and_fix_database():
    """检查并修复数据库"""
    
    print("=== 检查并修复数据库 ===")
    
    # 检查数据库文件是否存在
    if not os.path.exists('goofish.db'):
        print("❌ 数据库文件不存在: goofish.db")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect('goofish.db')
        cursor = conn.cursor()
        
        # 1. 检查当前状态
        print("\n1. 检查当前商品状态")
        cursor.execute("SELECT id, title, created_at FROM items LIMIT 10")
        items = cursor.fetchall()
        
        print(f"   找到 {len(items)} 个商品:")
        for item in items:
            print(f"     ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 2. 统计需要修复的商品数量
        cursor.execute("SELECT COUNT(*) FROM items WHERE created_at IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"\n2. 需要修复的商品数量: {null_count}")
        
        if null_count == 0:
            print("   ✅ 所有商品都有created_at字段")
        else:
            # 3. 强制修复所有商品
            print(f"\n3. 开始修复 {null_count} 个商品...")
            
            # 为每个商品设置不同的时间（模拟真实发布时间）
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
                
                # 格式化为ISO格式
                iso_time = item_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                cursor.execute(
                    "UPDATE items SET created_at = ? WHERE id = ?",
                    (iso_time, item_id)
                )
                
                if (i + 1) % 10 == 0:
                    print(f"   已修复 {i + 1}/{null_count} 个商品")
            
            # 提交更改
            conn.commit()
            print(f"   ✅ 成功修复 {null_count} 个商品")
        
        # 4. 验证修复结果
        print("\n4. 验证修复结果")
        cursor.execute("SELECT id, title, created_at FROM items ORDER BY created_at DESC LIMIT 5")
        items = cursor.fetchall()
        
        print("   最新的5个商品:")
        for item in items:
            print(f"     ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 5. 检查是否还有NULL值
        cursor.execute("SELECT COUNT(*) FROM items WHERE created_at IS NULL")
        remaining_null = cursor.fetchone()[0]
        print(f"\n5. 剩余NULL值: {remaining_null}")
        
        if remaining_null == 0:
            print("   ✅ 所有商品都已修复完成！")
        else:
            print(f"   ⚠️ 还有 {remaining_null} 个商品需要修复")
        
    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
    finally:
        conn.close()
    
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_and_fix_database() 