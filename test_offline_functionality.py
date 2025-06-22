#!/usr/bin/env python3
"""
测试已下架商品功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_offline_functionality():
    """测试已下架商品功能"""
    
    print("=== 测试已下架商品功能 ===")
    
    # 1. 测试获取所有商品（应该只显示在售商品）
    print("\n1. 测试获取所有商品（首页显示）")
    try:
        response = requests.get(f"{BASE_URL}/items/")
        if response.status_code == 200:
            items = response.json()
            print(f"✅ 成功获取商品列表，共 {len(items)} 个商品")
            for item in items[:3]:  # 显示前3个商品
                print(f"   - {item['title']} (状态: {item.get('status', 'unknown')})")
        else:
            print(f"❌ 获取商品列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 2. 测试搜索商品（应该只显示在售商品）
    print("\n2. 测试搜索商品")
    try:
        response = requests.get(f"{BASE_URL}/items/search?q=商品")
        if response.status_code == 200:
            items = response.json()
            print(f"✅ 成功搜索商品，共 {len(items)} 个结果")
            for item in items[:3]:  # 显示前3个商品
                print(f"   - {item['title']} (状态: {item.get('status', 'unknown')})")
        else:
            print(f"❌ 搜索商品失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试获取用户商品（需要先登录）
    print("\n3. 测试获取用户商品（需要登录）")
    print("   注意：这个测试需要先登录获取token")
    
    # 4. 测试商品状态更新API
    print("\n4. 测试商品状态更新API")
    print("   注意：这个测试需要先登录获取token")
    
    print("\n=== 测试完成 ===")
    print("\n说明：")
    print("- 首页和搜索结果应该只显示状态为 'online' 的商品")
    print("- 个人主页的'在售商品'标签页应该只显示状态为 'online' 的商品")
    print("- 个人主页的'已下架商品'按钮可以查看状态为 'offline' 的商品")
    print("- 下架的商品在首页不显示，但在个人主页仍然可以管理")

if __name__ == "__main__":
    test_offline_functionality() 