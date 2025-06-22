#!/usr/bin/env python3
"""
测试商品排序功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_sorting_functionality():
    """测试商品排序功能"""
    
    print("=== 测试商品排序功能 ===")
    
    # 测试首页商品排序
    print("\n1. 测试首页商品排序")
    
    # 测试最新发布排序
    print("\n   - 测试最新发布排序 (created_at_desc)")
    try:
        response = requests.get(f"{BASE_URL}/items?order_by=created_at_desc&limit=5")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取 {len(items)} 个商品")
            for i, item in enumerate(items[:3]):
                print(f"      {i+1}. {item.get('title', 'N/A')} - ¥{item.get('price', 0)} - {item.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试价格从低到高排序
    print("\n   - 测试价格从低到高排序 (price_asc)")
    try:
        response = requests.get(f"{BASE_URL}/items?order_by=price_asc&limit=5")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取 {len(items)} 个商品")
            for i, item in enumerate(items[:3]):
                print(f"      {i+1}. {item.get('title', 'N/A')} - ¥{item.get('price', 0)}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试价格从高到低排序
    print("\n   - 测试价格从高到低排序 (price_desc)")
    try:
        response = requests.get(f"{BASE_URL}/items?order_by=price_desc&limit=5")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取 {len(items)} 个商品")
            for i, item in enumerate(items[:3]):
                print(f"      {i+1}. {item.get('title', 'N/A')} - ¥{item.get('price', 0)}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试用户商品排序
    print("\n2. 测试用户商品排序")
    
    # 测试用户1的在售商品排序
    print("\n   - 测试用户1的在售商品最新发布排序")
    try:
        response = requests.get(f"{BASE_URL}/users/1/items?status=selling&order_by=created_at_desc&limit=5")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功获取用户1的 {len(items)} 个在售商品")
            for i, item in enumerate(items[:3]):
                print(f"      {i+1}. {item.get('title', 'N/A')} - ¥{item.get('price', 0)} - {item.get('created_at', 'N/A')}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 测试搜索商品排序
    print("\n3. 测试搜索商品排序")
    
    print("\n   - 测试搜索'商品'并按最新发布排序")
    try:
        response = requests.get(f"{BASE_URL}/items/search?q=商品&order_by=created_at_desc&limit=5")
        if response.status_code == 200:
            items = response.json()
            print(f"   ✅ 成功搜索到 {len(items)} 个商品")
            for i, item in enumerate(items[:3]):
                print(f"      {i+1}. {item.get('title', 'N/A')} - ¥{item.get('price', 0)}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_sorting_functionality() 