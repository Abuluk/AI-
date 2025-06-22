#!/usr/bin/env python3
"""
测试管理员消息管理功能
"""

import requests
import json

# API 基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_admin_messages():
    print("=== 测试管理员消息管理功能 ===")
    
    # 1. 管理员登录
    print("\n1. 管理员登录...")
    login_data = {
        "identifier": "directuser2",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        print(response.text)
        return
    
    token = response.json().get("access_token")
    if not token:
        print("未获取到访问令牌")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("登录成功")
    
    # 2. 获取系统消息列表
    print("\n2. 获取系统消息列表...")
    response = requests.get(f"{BASE_URL}/admin/messages", headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"获取到 {len(messages)} 条系统消息")
        for msg in messages:
            print(f"  - ID: {msg.get('id')}, 标题: {msg.get('title', '无标题')}")
    else:
        print(f"获取系统消息失败: {response.status_code}")
        print(response.text)
    
    # 3. 发布系统消息
    print("\n3. 发布系统消息...")
    message_data = {
        "title": "测试系统消息",
        "content": "这是一条测试系统消息，用于验证管理员消息管理功能。",
        "target_users": "all"
    }
    
    response = requests.post(f"{BASE_URL}/admin/messages", 
                           json=message_data, 
                           headers=headers)
    if response.status_code == 200:
        print("系统消息发布成功")
        new_message = response.json()
        print(f"新消息ID: {new_message.get('id')}")
    else:
        print(f"发布系统消息失败: {response.status_code}")
        print(response.text)
    
    # 4. 再次获取系统消息列表
    print("\n4. 再次获取系统消息列表...")
    response = requests.get(f"{BASE_URL}/admin/messages", headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"现在有 {len(messages)} 条系统消息")
        for msg in messages:
            print(f"  - ID: {msg.get('id')}, 标题: {msg.get('title', '无标题')}")
    else:
        print(f"获取系统消息失败: {response.status_code}")
        print(response.text)
    
    # 5. 获取管理员统计信息
    print("\n5. 获取管理员统计信息...")
    response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("统计信息:")
        print(f"  - 总用户数: {stats.get('total_users', 0)}")
        print(f"  - 总商品数: {stats.get('total_items', 0)}")
        print(f"  - 活跃用户: {stats.get('active_users', 0)}")
        print(f"  - 在售商品: {stats.get('online_items', 0)}")
        print(f"  - 已售商品: {stats.get('sold_items', 0)}")
        print(f"  - 总收藏数: {stats.get('total_favorites', 0)}")
    else:
        print(f"获取统计信息失败: {response.status_code}")
        print(response.text)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_admin_messages() 