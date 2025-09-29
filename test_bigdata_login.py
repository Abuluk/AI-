#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试大数据推荐登录要求
"""
import requests

def test_bigdata_without_login():
    """测试未登录用户的大数据推荐"""
    print("=" * 60)
    print("测试未登录用户的大数据推荐")
    print("=" * 60)
    
    url = "http://127.0.0.1:8000/api/v1/items"
    params = {
        "order_by": "bigdata_recommendation",
        "limit": 5
    }
    
    print(f"请求URL: {url}")
    print(f"请求参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应类型: {type(data)}")
            
            if isinstance(data, dict) and 'error' in data:
                print(f"[SUCCESS] 正确返回错误信息:")
                print(f"  - 错误: {data.get('error')}")
                print(f"  - 消息: {data.get('message')}")
                print(f"  - 商品数量: {len(data.get('items', []))}")
            else:
                print(f"[FAILED] 应该返回错误信息，但返回了: {data}")
        else:
            print(f"[FAILED] 响应状态码异常: {response.status_code}")
            
    except Exception as e:
        print(f"[FAILED] 请求失败: {e}")

def test_bigdata_with_login():
    """测试已登录用户的大数据推荐"""
    print("\n" + "=" * 60)
    print("测试已登录用户的大数据推荐")
    print("=" * 60)
    
    url = "http://127.0.0.1:8000/api/v1/items"
    params = {
        "order_by": "bigdata_recommendation",
        "user_id": 1,
        "limit": 5
    }
    
    print(f"请求URL: {url}")
    print(f"请求参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应类型: {type(data)}")
            
            if isinstance(data, list) and len(data) > 0:
                print(f"[SUCCESS] 正确返回推荐商品:")
                print(f"  - 商品数量: {len(data)}")
                print(f"  - 第一个商品ID: {data[0].get('id')}")
                print(f"  - 是否大数据推荐: {data[0].get('is_bigdata_recommended')}")
            else:
                print(f"[FAILED] 应该返回推荐商品列表，但返回了: {data}")
        else:
            print(f"[FAILED] 响应状态码异常: {response.status_code}")
            
    except Exception as e:
        print(f"[FAILED] 请求失败: {e}")

if __name__ == "__main__":
    test_bigdata_without_login()
    test_bigdata_with_login()
