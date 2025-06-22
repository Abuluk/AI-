#!/usr/bin/env python3
"""
测试收藏功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的认证token（你需要用真实的token替换）
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIiLCJleHAiOjE3NTMxNDgzMjB9.yKlFKK3A2bi7do4wzge8X6w2l6YnIoQ-GP3VkSMBV7c"

# 请求头
headers = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def test_favorite_functionality():
    """测试收藏功能"""
    
    print("=== 测试收藏功能 ===")
    
    # 测试数据
    test_user_id = 1
    test_item_id = 3
    
    # 1. 测试检查收藏状态
    print(f"\n1. 测试检查收藏状态 (用户ID: {test_user_id}, 商品ID: {test_item_id})")
    try:
        response = requests.get(f"{BASE_URL}/favorites/check?user_id={test_user_id}&item_id={test_item_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功检查收藏状态: {result}")
        else:
            print(f"❌ 检查收藏状态失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 2. 测试添加收藏
    print(f"\n2. 测试添加收藏")
    try:
        response = requests.post(f"{BASE_URL}/favorites/add?user_id={test_user_id}&item_id={test_item_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功添加收藏: {result}")
        else:
            print(f"❌ 添加收藏失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 再次检查收藏状态
    print(f"\n3. 再次检查收藏状态")
    try:
        response = requests.get(f"{BASE_URL}/favorites/check?user_id={test_user_id}&item_id={test_item_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 收藏状态: {result}")
        else:
            print(f"❌ 检查收藏状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 4. 测试获取用户收藏列表
    print(f"\n4. 测试获取用户收藏列表")
    try:
        response = requests.get(f"{BASE_URL}/favorites/user/{test_user_id}", headers=headers)
        if response.status_code == 200:
            favorites = response.json()
            print(f"✅ 成功获取收藏列表，共 {len(favorites)} 个收藏")
            for fav in favorites[:3]:  # 显示前3个收藏
                print(f"   - 收藏ID: {fav.get('id')}, 商品ID: {fav.get('item_id')}")
        else:
            print(f"❌ 获取收藏列表失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 5. 测试移除收藏
    print(f"\n5. 测试移除收藏")
    try:
        response = requests.delete(f"{BASE_URL}/favorites/remove?user_id={test_user_id}&item_id={test_item_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功移除收藏: {result}")
        else:
            print(f"❌ 移除收藏失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 6. 最终检查收藏状态
    print(f"\n6. 最终检查收藏状态")
    try:
        response = requests.get(f"{BASE_URL}/favorites/check?user_id={test_user_id}&item_id={test_item_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 最终收藏状态: {result}")
        else:
            print(f"❌ 检查收藏状态失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_favorite_functionality() 