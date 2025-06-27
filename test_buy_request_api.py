#!/usr/bin/env python3
"""
测试求购信息API的脚本
"""
import requests
import json

# 配置
BASE_URL = "http://8.138.47.159:8000/api/v1"
ADMIN_TOKEN = None

def admin_login():
    """管理员登录"""
    global ADMIN_TOKEN
    login_data = {
        "identifier": "admin@example.com",  # 替换为实际的管理员邮箱
        "password": "admin123"  # 替换为实际的管理员密码
    }
    
    response = requests.post(f"{BASE_URL}/admin/login", data=login_data)
    if response.status_code == 200:
        ADMIN_TOKEN = response.json()["access_token"]
        print("管理员登录成功")
        return True
    else:
        print(f"管理员登录失败: {response.status_code} - {response.text}")
        return False

def get_buy_requests():
    """获取求购信息列表"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    response = requests.get(f"{BASE_URL}/admin/buy_requests", headers=headers)
    
    if response.status_code == 200:
        buy_requests = response.json()
        print(f"获取到 {len(buy_requests)} 条求购信息")
        for br in buy_requests:
            print(f"ID: {br['id']}, 标题: {br['title']}, 预算: {br['budget']}")
        return buy_requests
    else:
        print(f"获取求购信息失败: {response.status_code} - {response.text}")
        return []

def delete_buy_request(buy_request_id):
    """删除求购信息"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    response = requests.delete(f"{BASE_URL}/admin/buy_requests/{buy_request_id}", headers=headers)
    
    if response.status_code == 200:
        print(f"成功删除求购信息 ID: {buy_request_id}")
        return True
    else:
        print(f"删除求购信息失败: {response.status_code} - {response.text}")
        return False

def get_users():
    """获取用户列表"""
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"获取到 {len(users)} 个用户")
        for user in users:
            print(f"ID: {user['id']}, 用户名: {user['username']}, 邮箱: {user['email']}, 管理员: {user['is_admin']}")
        return users
    else:
        print(f"获取用户列表失败: {response.status_code} - {response.text}")
        return []

def main():
    print("开始测试求购信息API...")
    
    # 1. 管理员登录
    if not admin_login():
        print("尝试使用不同的登录信息...")
        # 尝试其他可能的登录信息
        global ADMIN_TOKEN
        login_data = {
            "identifier": "admin",  # 尝试用户名
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/admin/login", data=login_data)
        if response.status_code == 200:
            ADMIN_TOKEN = response.json()["access_token"]
            print("管理员登录成功（使用用户名）")
        else:
            print(f"管理员登录仍然失败: {response.status_code} - {response.text}")
            return
    
    # 2. 获取用户列表
    users = get_users()
    
    # 3. 获取求购信息列表
    buy_requests = get_buy_requests()
    
    if not buy_requests:
        print("没有找到求购信息，无法测试删除功能")
        return
    
    # 4. 测试删除第一条求购信息
    first_buy_request = buy_requests[0]
    print(f"\n准备删除求购信息: ID={first_buy_request['id']}, 标题={first_buy_request['title']}")
    
    if delete_buy_request(first_buy_request['id']):
        print("删除测试成功！")
    else:
        print("删除测试失败！")

if __name__ == "__main__":
    main() 