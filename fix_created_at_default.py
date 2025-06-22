#!/usr/bin/env python3
"""
修复商品created_at字段的脚本
"""

import sqlite3
from datetime import datetime

def fix_created_at_fields():
    """修复商品表中的created_at字段"""
    
    print("=== 修复商品created_at字段 ===")
    
    try:
        # 连接数据库
        conn = sqlite3.connect('goofish.db')
        cursor = conn.cursor()
        
        # 检查当前状态
        print("\n1. 检查当前商品状态")
        cursor.execute("SELECT id, title, created_at FROM items LIMIT 5")
        items = cursor.fetchall()
        
        for item in items:
            print(f"   商品ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 更新所有没有created_at的商品
        print("\n2. 更新商品的created_at字段")
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # 为所有created_at为NULL或不包含'T'的商品设置当前时间
        cursor.execute("""
            UPDATE items
            SET created_at = ?
            WHERE created_at IS NULL OR instr(created_at, 'T') = 0
        """, (now,))
        
        print(f"   ✅ 已更新 {cursor.rowcount} 个商品的created_at字段")
        
        # 验证更新结果
        print("\n3. 验证更新结果")
        cursor.execute("SELECT id, title, created_at FROM items LIMIT 5")
        items = cursor.fetchall()
        
        for item in items:
            print(f"   商品ID: {item[0]}, 标题: {item[1]}, created_at: {item[2]}")
        
        # 提交更改
        conn.commit()
        print("\n4. 数据库更改已提交")
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
    finally:
        conn.close()
    
    print("\n=== 修复完成 ===")

if __name__ == "__main__":
    fix_created_at_fields() 