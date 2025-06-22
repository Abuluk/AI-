#!/usr/bin/env python3
"""
测试删除商品功能
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_delete_item():
    """测试删除商品功能"""
    
    # 1. 首先登录获取token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print("登录失败，请确保测试用户存在")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 获取用户信息
        user_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if user_response.status_code != 200:
            print("获取用户信息失败")
            return
            
        user_id = user_response.json()["id"]
        print(f"用户ID: {user_id}")
        
        # 3. 获取用户的在售商品
        items_response = requests.get(
            f"{BASE_URL}/users/{user_id}/items", 
            params={"status": "selling", "limit": 1},
            headers=headers
        )
        
        if items_response.status_code != 200:
            print("获取用户商品失败")
            return
            
        items = items_response.json()
        if not items:
            print("用户没有在售商品，无法测试删除功能")
            return
            
        item_to_delete = items[0]
        item_id = item_to_delete["id"]
        print(f"准备删除商品: {item_to_delete['title']} (ID: {item_id})")
        
        # 4. 删除商品
        delete_response = requests.delete(
            f"{BASE_URL}/items/{item_id}",
            headers=headers
        )
        
        if delete_response.status_code == 200:
            print("✅ 商品删除成功!")
            
            # 5. 验证商品已被删除
            verify_response = requests.get(f"{BASE_URL}/items/{item_id}")
            if verify_response.status_code == 404:
                print("✅ 商品已从数据库中删除")
            else:
                print("❌ 商品仍然存在于数据库中")
        else:
            print(f"❌ 删除商品失败: {delete_response.status_code}")
            print(delete_response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    print("开始测试删除商品功能...")
    test_delete_item()
    print("测试完成") 