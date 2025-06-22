#!/usr/bin/env python3
"""
测试消息功能
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录功能"""
    print("=== 测试登录功能 ===")
    
    # 测试用户登录
    login_data = {
        "identifier": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"用户登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        user_token = response.json().get("access_token")
        print("用户登录成功")
        return user_token
    else:
        print(f"用户登录失败: {response.text}")
        return None

def test_admin_login():
    """测试管理员登录"""
    print("\n=== 测试管理员登录 ===")
    
    admin_data = {
        "identifier": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=admin_data)
    print(f"管理员登录状态码: {response.status_code}")
    
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        print("管理员登录成功")
        return admin_token
    else:
        print(f"管理员登录失败: {response.text}")
        return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print(f"获取用户信息状态码: {response.status_code}")
    
    if response.status_code == 200:
        user_info = response.json()
        print(f"用户信息: {json.dumps(user_info, indent=2, ensure_ascii=False)}")
        return user_info
    else:
        print(f"获取用户信息失败: {response.text}")
        return None

def test_get_items(token):
    """测试获取商品列表"""
    print("\n=== 测试获取商品列表 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/items", headers=headers)
    print(f"获取商品列表状态码: {response.status_code}")
    
    if response.status_code == 200:
        items = response.json()
        print(f"找到 {len(items)} 个商品")
        if items:
            print(f"第一个商品: {items[0]['title']}")
            return items[0]['id']  # 返回第一个商品的ID用于测试消息
        return None
    else:
        print(f"获取商品列表失败: {response.text}")
        return None

def test_send_message(token, item_id):
    """测试发送消息"""
    print(f"\n=== 测试发送消息 (商品ID: {item_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    message_data = {
        "content": f"这是一条测试消息，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "item_id": item_id
    }
    
    response = requests.post(f"{BASE_URL}/messages", json=message_data, headers=headers)
    print(f"发送消息状态码: {response.status_code}")
    
    if response.status_code == 200:
        message = response.json()
        print(f"消息发送成功: {message['content']}")
        return message['id']
    else:
        print(f"发送消息失败: {response.text}")
        return None

def test_get_conversations(token):
    """测试获取对话列表"""
    print("\n=== 测试获取对话列表 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages/conversations", headers=headers)
    print(f"获取对话列表状态码: {response.status_code}")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"找到 {len(conversations)} 个对话")
        for conv in conversations:
            print(f"对话: {conv.get('item_title', 'Unknown')} - 消息数: {conv.get('message_count', 0)}")
        return conversations
    else:
        print(f"获取对话列表失败: {response.text}")
        return None

def test_get_unread_count(token):
    """测试获取未读消息数量"""
    print("\n=== 测试获取未读消息数量 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages/unread-count", headers=headers)
    print(f"获取未读消息数量状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"未读消息数量: {result.get('unread_count', 0)}")
        return result.get('unread_count', 0)
    else:
        print(f"获取未读消息数量失败: {response.text}")
        return 0

def test_admin_send_system_message(admin_token):
    """测试管理员发送系统消息"""
    print("\n=== 测试管理员发送系统消息 ===")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    message_data = {
        "content": f"这是一条系统消息，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "title": "系统通知",
        "target_users": "all"
    }
    
    response = requests.post(f"{BASE_URL}/admin/messages", json=message_data, headers=headers)
    print(f"发送系统消息状态码: {response.status_code}")
    
    if response.status_code == 200:
        message = response.json()
        print(f"系统消息发送成功: {message['content']}")
        return message['id']
    else:
        print(f"发送系统消息失败: {response.text}")
        return None

def test_admin_get_system_messages(admin_token):
    """测试管理员获取系统消息列表"""
    print("\n=== 测试管理员获取系统消息列表 ===")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/admin/messages", headers=headers)
    print(f"获取系统消息列表状态码: {response.status_code}")
    
    if response.status_code == 200:
        messages = response.json()
        print(f"找到 {len(messages)} 条系统消息")
        for msg in messages:
            print(f"系统消息: {msg.get('title', 'No title')} - {msg.get('content', 'No content')}")
        return messages
    else:
        print(f"获取系统消息列表失败: {response.text}")
        return None

def main():
    """主测试函数"""
    print("开始测试消息功能...")
    
    # 测试用户登录
    user_token = test_login()
    if not user_token:
        print("用户登录失败，无法继续测试")
        return
    
    # 测试管理员登录
    admin_token = test_admin_login()
    if not admin_token:
        print("管理员登录失败，无法测试管理员功能")
    
    # 获取用户信息
    user_info = test_get_user_info(user_token)
    
    # 获取商品列表
    item_id = test_get_items(user_token)
    
    # 如果有商品，测试发送消息
    if item_id:
        test_send_message(user_token, item_id)
    
    # 测试获取对话列表
    test_get_conversations(user_token)
    
    # 测试获取未读消息数量
    test_get_unread_count(user_token)
    
    # 测试管理员功能
    if admin_token:
        test_admin_send_system_message(admin_token)
        test_admin_get_system_messages(admin_token)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 