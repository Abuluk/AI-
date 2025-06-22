#!/usr/bin/env python3
"""
测试系统消息发布功能
"""

import requests
import json

# API 基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_system_message():
    print("=== 测试系统消息发布功能 ===")
    
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
    
    # 2. 发布系统消息
    print("\n2. 发布系统消息...")
    message_data = {
        "title": "测试系统消息",
        "content": "这是一条测试系统消息，用于验证管理员消息管理功能。",
        "target_users": "all"
    }
    
    response = requests.post(f"{BASE_URL}/admin/messages", 
                           json=message_data, 
                           headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    
    if response.status_code == 200:
        print("✅ 系统消息发布成功")
        new_message = response.json()
        print(f"新消息ID: {new_message.get('id')}")
    else:
        print("❌ 发布系统消息失败")
        return
    
    # 3. 获取系统消息列表
    print("\n3. 获取系统消息列表...")
    response = requests.get(f"{BASE_URL}/admin/messages", headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"获取到 {len(messages)} 条系统消息")
        for msg in messages:
            print(f"  - ID: {msg.get('id')}, 标题: {msg.get('title', '无标题')}, 内容: {msg.get('content')[:50]}...")
    else:
        print(f"获取系统消息失败: {response.status_code}")
        print(response.text)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_system_message() 