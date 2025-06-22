#!/usr/bin/env python3
"""
测试API端点
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"

def test_api_endpoints():
    """测试API端点"""
    print("🧪 测试API端点...")
    
    # 测试登录获取token
    login_data = {
        "identifier": "13800138000",
        "password": "test123456"
    }
    
    try:
        print("1. 测试登录...")
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   登录成功，token: {token[:20]}...")
            
            # 测试获取用户信息
            print("\n2. 测试获取用户信息...")
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"   用户ID: {user_data.get('id')}")
                print(f"   用户名: {user_data.get('username')}")
                print(f"   是否管理员: {user_data.get('is_admin')}")
            
            # 测试获取商品信息
            print("\n3. 测试获取商品信息...")
            response = requests.get(f"{BASE_URL}/items/13", headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                item_data = response.json()
                print(f"   商品标题: {item_data.get('title')}")
                print(f"   商品状态: {item_data.get('status')}")
                print(f"   商品所有者: {item_data.get('owner_id')}")
            
            # 测试获取消息对话
            print("\n4. 测试获取消息对话...")
            response = requests.get(f"{BASE_URL}/messages/conversations", headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                conversations = response.json()
                print(f"   对话数量: {len(conversations)}")
            
            # 测试获取未读消息数量
            print("\n5. 测试获取未读消息数量...")
            response = requests.get(f"{BASE_URL}/messages/unread-count", headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                unread_data = response.json()
                print(f"   未读消息数: {unread_data.get('unread_count')}")
            
            # 测试获取特定商品对话
            print("\n6. 测试获取特定商品对话...")
            response = requests.get(f"{BASE_URL}/messages/conversation/13", headers=headers)
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                messages = response.json()
                print(f"   消息数量: {len(messages)}")
            
        else:
            print(f"   登录失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_api_endpoints() 