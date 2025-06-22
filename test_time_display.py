#!/usr/bin/env python3
"""
测试商品时间字段显示的脚本
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_time_display():
    """测试商品时间字段显示"""
    
    print("=== 测试商品时间字段显示 ===")
    
    # 测试获取商品列表
    print("\n1. 测试获取商品列表")
    try:
        response = requests.get(f"{BASE_URL}/items?limit=3")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取 {len(items)} 个商品")
            for i, item in enumerate(items):
                print(f"   商品 {i+1}:")
                print(f"     ID: {item.get('id')}")
                print(f"     标题: {item.get('title')}")
                print(f"     created_at: {item.get('created_at')}")
                print(f"     createdAt: {item.get('createdAt')}")
                print(f"     时间类型: {type(item.get('created_at'))}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试获取单个商品详情
    print("\n2. 测试获取单个商品详情")
    try:
        response = requests.get(f"{BASE_URL}/items/1")
        if response.status_code == 200:
            item = response.json()
            print(f"   ✅ 成功获取商品详情")
            print(f"     ID: {item.get('id')}")
            print(f"     标题: {item.get('title')}")
            print(f"     created_at: {item.get('created_at')}")
            print(f"     createdAt: {item.get('createdAt')}")
            print(f"     时间类型: {type(item.get('created_at'))}")
            
            # 测试时间格式化
            if item.get('created_at'):
                try:
                    dt = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                    print(f"     格式化时间: {dt.strftime('%Y年%m月%d日 %H:%M')}")
                except Exception as e:
                    print(f"     时间格式化失败: {e}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试用户商品列表
    print("\n3. 测试用户商品列表")
    try:
        response = requests.get(f"{BASE_URL}/users/1/items?status=selling&limit=3")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取用户 {len(items)} 个商品")
            for i, item in enumerate(items):
                print(f"   商品 {i+1}:")
                print(f"     ID: {item.get('id')}")
                print(f"     标题: {item.get('title')}")
                print(f"     created_at: {item.get('created_at')}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_time_display() 