#!/usr/bin/env python3
"""
测试商品详情页功能的脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_item_detail_functionality():
    """测试商品详情页功能"""
    
    print("=== 测试商品详情页功能 ===")
    
    # 1. 测试获取商品列表
    print("\n1. 测试获取商品列表")
    try:
        response = requests.get(f"{BASE_URL}/items/")
        if response.status_code == 200:
            items = response.json()
            print(f"✅ 成功获取商品列表，共 {len(items)} 个商品")
            if items:
                test_item_id = items[0]['id']
                print(f"   使用第一个商品进行测试，ID: {test_item_id}")
            else:
                print("❌ 没有商品数据，无法测试")
                return
        else:
            print(f"❌ 获取商品列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 测试获取单个商品详情
    print(f"\n2. 测试获取商品详情 (ID: {test_item_id})")
    try:
        response = requests.get(f"{BASE_URL}/items/{test_item_id}")
        if response.status_code == 200:
            item = response.json()
            print(f"✅ 成功获取商品详情")
            print(f"   标题: {item['title']}")
            print(f"   价格: ¥{item['price']}")
            print(f"   状态: {item.get('status', 'unknown')}")
            print(f"   浏览量: {item.get('views', 0)}")
            print(f"   收藏数: {item.get('favorited_count', 0)}")
            print(f"   图片字段: {item.get('images', 'none')}")
            print(f"   图片字段类型: {type(item.get('images', 'none'))}")
            if item.get('images'):
                images = item['images'].split(',')
                print(f"   图片数量: {len(images)}")
                for i, img in enumerate(images):
                    print(f"   图片{i+1}: {img.strip()}")
        else:
            print(f"❌ 获取商品详情失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 3. 测试更新商品浏览量
    print(f"\n3. 测试更新商品浏览量")
    try:
        response = requests.patch(f"{BASE_URL}/items/{test_item_id}/views")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功更新浏览量: {result.get('views', 'unknown')}")
        else:
            print(f"❌ 更新浏览量失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    # 4. 测试获取用户信息
    print(f"\n4. 测试获取用户信息")
    try:
        # 先获取商品详情来获取owner_id
        item_response = requests.get(f"{BASE_URL}/items/{test_item_id}")
        if item_response.status_code == 200:
            item = item_response.json()
            owner_id = item.get('owner_id')
            if owner_id:
                user_response = requests.get(f"{BASE_URL}/users/{owner_id}")
                if user_response.status_code == 200:
                    user = user_response.json()
                    print(f"✅ 成功获取用户信息")
                    print(f"   用户名: {user.get('username', 'unknown')}")
                    print(f"   头像: {user.get('avatar', 'none')}")
                else:
                    print(f"❌ 获取用户信息失败: {user_response.status_code}")
            else:
                print("❌ 商品没有owner_id")
        else:
            print(f"❌ 获取商品详情失败: {item_response.status_code}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("现在可以在前端测试商品跳转功能了！")

if __name__ == "__main__":
    test_item_detail_functionality() 