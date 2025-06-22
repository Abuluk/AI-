#!/usr/bin/env python3
"""
测试登录功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录功能"""
    print("🧪 测试登录功能...")
    
    # 测试数据
    login_data = {
        "identifier": "13800138000",  # 使用手机号
        "password": "test123456"
    }
    
    try:
        print(f"发送登录请求: {login_data}")
        # 使用表单格式发送数据
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功: {data}")
            return data.get('access_token')
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_user_info(token):
    """测试获取用户信息"""
    if not token:
        print("❌ 没有token，跳过用户信息测试")
        return
    
    print("\n🧪 测试获取用户信息...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户信息成功: {data}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    # 测试登录
    token = test_login()
    
    # 测试获取用户信息
    test_user_info(token) 