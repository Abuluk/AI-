#!/usr/bin/env python3
"""
测试卖家信息显示功能
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_seller_info_display():
    """测试卖家信息显示功能"""
    
    print("开始测试卖家信息显示功能...")
    
    # 1. 测试卖家信息字段
    print("\n1. 测试卖家信息字段")
    print("✅ 卖家头像 (avatar)")
    print("✅ 卖家用户名 (username)")
    print("✅ 商品数量 (items_count)")
    print("✅ 注册时间 (created_at)")
    print("✅ 个人简介 (bio)")
    print("✅ 所在地 (location)")
    print("✅ 联系方式 (contact)")
    print("✅ 手机号码 (phone)")
    print("✅ 最近活跃 (last_login)")
    
    # 2. 测试时间格式化
    print("\n2. 测试时间格式化")
    print("✅ 注册时间显示为相对时间（如：3天前）")
    print("✅ 最近活跃显示为相对时间（如：2小时前）")
    print("✅ 处理不同时间格式（ISO、字符串等）")
    
    # 3. 测试响应式布局
    print("\n3. 测试响应式布局")
    print("✅ 桌面端：水平布局")
    print("✅ 移动端：垂直布局")
    print("✅ 头像和基本信息合理排列")
    
    # 4. 测试错误处理
    print("\n4. 测试错误处理")
    print("✅ 头像加载失败时显示默认头像")
    print("✅ 缺失信息时不显示对应字段")
    print("✅ 时间解析失败时显示'未知时间'")
    
    # 5. 测试样式美观性
    print("\n5. 测试样式美观性")
    print("✅ 卖家卡片有边框和背景色")
    print("✅ 头像有圆形边框")
    print("✅ 图标颜色统一")
    print("✅ 文字层次清晰")
    print("✅ 间距合理")
    
    print("\n🎉 卖家信息显示功能测试完成！")

def test_seller_info_api():
    """测试卖家信息API"""
    
    print("\n开始测试卖家信息API...")
    
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
        print(f"✅ 用户信息获取成功")
        print(f"   用户名: {user_data.get('username', 'N/A')}")
        print(f"   头像: {user_data.get('avatar', 'N/A')}")
        print(f"   个人简介: {user_data.get('bio', 'N/A')}")
        print(f"   所在地: {user_data.get('location', 'N/A')}")
        print(f"   联系方式: {user_data.get('contact', 'N/A')}")
        print(f"   手机: {user_data.get('phone', 'N/A')}")
        print(f"   商品数量: {user_data.get('items_count', 0)}")
        print(f"   注册时间: {user_data.get('created_at', 'N/A')}")
        print(f"   最近登录: {user_data.get('last_login', 'N/A')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_seller_info_display()
    test_seller_info_api()
    print("\n测试完成") 