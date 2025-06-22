#!/usr/bin/env python3
"""
测试卖家信息获取修复
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_seller_info_fix():
    """测试卖家信息获取修复"""
    
    print("开始测试卖家信息获取修复...")
    
    try:
        # 1. 登录获取token
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if login_response.status_code != 200:
            print("❌ 登录失败，请确保测试用户存在")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 获取用户信息
        user_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if user_response.status_code != 200:
            print("❌ 获取用户信息失败")
            return
            
        user_data = user_response.json()
        user_id = user_data["id"]
        print(f"✅ 当前用户ID: {user_id}")
        
        # 3. 获取用户的商品
        items_response = requests.get(
            f"{BASE_URL}/users/{user_id}/items", 
            params={"status": "selling", "limit": 1},
            headers=headers
        )
        
        if items_response.status_code != 200:
            print("❌ 获取用户商品失败")
            return
            
        items = items_response.json()
        if not items:
            print("❌ 用户没有在售商品，无法测试卖家信息")
            return
            
        item = items[0]
        item_id = item["id"]
        owner_id = item["owner_id"]
        print(f"✅ 找到商品: {item['title']} (ID: {item_id}, 卖家ID: {owner_id})")
        
        # 4. 测试获取卖家信息
        seller_response = requests.get(f"{BASE_URL}/users/{owner_id}")
        if seller_response.status_code == 200:
            seller_data = seller_response.json()
            print("✅ 卖家信息获取成功!")
            print(f"   卖家ID: {seller_data.get('id')}")
            print(f"   用户名: {seller_data.get('username')}")
            print(f"   头像: {seller_data.get('avatar')}")
            print(f"   个人简介: {seller_data.get('bio', 'N/A')}")
            print(f"   所在地: {seller_data.get('location', 'N/A')}")
            print(f"   联系方式: {seller_data.get('contact', 'N/A')}")
            print(f"   手机: {seller_data.get('phone', 'N/A')}")
            print(f"   商品数量: {seller_data.get('items_count', 0)}")
            print(f"   注册时间: {seller_data.get('created_at', 'N/A')}")
            print(f"   最近登录: {seller_data.get('last_login', 'N/A')}")
        else:
            print(f"❌ 获取卖家信息失败: {seller_response.status_code}")
            print(seller_response.text)
        
        # 5. 测试商品详情页API
        item_detail_response = requests.get(f"{BASE_URL}/items/{item_id}")
        if item_detail_response.status_code == 200:
            item_detail = item_detail_response.json()
            print(f"✅ 商品详情获取成功，owner_id: {item_detail.get('owner_id')}")
        else:
            print(f"❌ 获取商品详情失败: {item_detail_response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_seller_info_fix()
    print("\n测试完成") 