#!/usr/bin/env python3
"""
创建测试用户
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def create_test_user():
    """创建测试用户"""
    print("=== 创建测试用户 ===")
    
    # 创建普通测试用户
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "testpass123",
        "phone": "13800138001"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"创建测试用户状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("测试用户创建成功")
        return True
    else:
        print(f"创建测试用户失败: {response.text}")
        return False

def create_admin_user():
    """创建管理员用户"""
    print("\n=== 创建管理员用户 ===")
    
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "phone": "13800138002"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
    print(f"创建管理员用户状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("管理员用户创建成功")
        return True
    else:
        print(f"创建管理员用户失败: {response.text}")
        return False

def set_user_as_admin():
    """将用户设置为管理员"""
    print("\n=== 设置用户为管理员 ===")
    
    # 先登录管理员账户
    login_data = {
        "identifier": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        admin_token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # 获取所有用户
        users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
        if users_response.status_code == 200:
            users = users_response.json()
            admin_user = None
            for user in users:
                if user['email'] == 'admin@example.com':
                    admin_user = user
                    break
            
            if admin_user:
                # 设置为管理员
                update_response = requests.patch(
                    f"{BASE_URL}/admin/users/{admin_user['id']}/admin?is_admin=true",
                    headers=headers
                )
                if update_response.status_code == 200:
                    print("用户已设置为管理员")
                    return True
                else:
                    print(f"设置管理员失败: {update_response.text}")
            else:
                print("未找到管理员用户")
        else:
            print(f"获取用户列表失败: {users_response.text}")
    else:
        print("管理员登录失败")
    
    return False

def main():
    """主函数"""
    print("开始创建测试用户...")
    
    # 创建测试用户
    create_test_user()
    
    # 创建管理员用户
    create_admin_user()
    
    # 设置管理员权限
    set_user_as_admin()
    
    print("\n=== 用户创建完成 ===")
    print("测试用户: testuser@example.com / testpass123")
    print("管理员用户: admin@example.com / admin123")

if __name__ == "__main__":
    main() 