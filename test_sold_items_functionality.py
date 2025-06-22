#!/usr/bin/env python3
"""
测试已售商品功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的认证token
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIiLCJleHAiOjE3NTMxNDg1MTl9.7SdtjqCSWQeJwZmeYmUBkua0WqvTXwKEKxEApV65B14"

# 请求头
headers = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def test_sold_items_functionality():
    """测试已售商品功能"""
    
    print("=== 测试已售商品功能 ===")
    
    test_user_id = 1
    
    # 1. 测试获取用户已售商品列表
    print(f"\n1. 测试获取用户已售商品列表 (用户ID: {test_user_id})")
    try:
        response = requests.get(f"{BASE_URL}/users/{test_user_id}/items?status=sold", headers=headers)
        if response.status_code == 200:
            sold_items = response.json()
            print(f"✅ 成功获取已售商品列表，共 {len(sold_items)} 个已售商品")
            for item in sold_items[:3]:  # 显示前3个已售商品
                print(f"   - ID: {item.get('id')}, 标题: {item.get('title')}, 价格: ¥{item.get('price')}")
        else:
            print(f"❌ 获取已售商品列表失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 2. 测试获取用户所有商品（包括已售）
    print(f"\n2. 测试获取用户所有商品")
    try:
        response = requests.get(f"{BASE_URL}/users/{test_user_id}/items", headers=headers)
        if response.status_code == 200:
            all_items = response.json()
            print(f"✅ 成功获取所有商品，共 {len(all_items)} 个商品")
            
            # 统计不同状态的商品
            sold_count = sum(1 for item in all_items if item.get('sold'))
            online_count = sum(1 for item in all_items if not item.get('sold') and item.get('status') == 'online')
            offline_count = sum(1 for item in all_items if item.get('status') == 'offline')
            
            print(f"   已售商品: {sold_count} 个")
            print(f"   在售商品: {online_count} 个")
            print(f"   下架商品: {offline_count} 个")
        else:
            print(f"❌ 获取所有商品失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试标记商品为已售（如果有在售商品的话）
    print(f"\n3. 测试标记商品为已售")
    try:
        # 先获取一个在售商品
        response = requests.get(f"{BASE_URL}/users/{test_user_id}/items?status=selling", headers=headers)
        if response.status_code == 200:
            selling_items = response.json()
            if selling_items:
                test_item_id = selling_items[0]['id']
                print(f"   使用商品ID {test_item_id} 进行测试")
                
                # 标记为已售
                sold_response = requests.patch(f"{BASE_URL}/items/{test_item_id}/sold", headers=headers)
                if sold_response.status_code == 200:
                    result = sold_response.json()
                    print(f"✅ 成功标记商品为已售: {result}")
                else:
                    print(f"❌ 标记为已售失败: {sold_response.status_code}")
                    print(f"   响应内容: {sold_response.text}")
            else:
                print("   没有在售商品可供测试")
        else:
            print(f"❌ 获取在售商品失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_sold_items_functionality() 