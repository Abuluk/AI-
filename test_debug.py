#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调试信息
"""
import requests

def test_debug():
    """测试调试信息"""
    base_url = "http://localhost:8000"
    
    print("=== 测试调试信息 ===")
    
    # 测试大数据推荐API
    print("\n1. 测试大数据推荐API...")
    try:
        response = requests.get(f"{base_url}/api/v1/items", params={
            "order_by": "bigdata_recommendation",
            "user_id": 1,
            "limit": 1
        })
        
        print(f"状态码: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回商品数量: {len(data)}")
            
            if data:
                item = data[0]
                print(f"商品ID: {item.get('id')}")
                print(f"商品标题: {item.get('title')}")
                print(f"推荐标识: {item.get('is_bigdata_recommended')}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试其他排序方式
    print("\n2. 测试其他排序方式...")
    try:
        response = requests.get(f"{base_url}/api/v1/items", params={
            "order_by": "created_at_desc",
            "user_id": 1,
            "limit": 1
        })
        
        print(f"created_at_desc - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回商品数量: {len(data)}")
            if data:
                print(f"商品ID: {data[0].get('id')}")
                print(f"商品标题: {data[0].get('title')}")
        
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_debug()
