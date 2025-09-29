#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试大数据推荐功能
"""
import requests
import json

def test_detailed():
    """详细测试大数据推荐功能"""
    base_url = "http://localhost:8000"
    
    print("=== 详细测试大数据推荐功能 ===")
    
    # 测试大数据推荐API
    print("\n1. 测试大数据推荐API...")
    try:
        response = requests.get(f"{base_url}/api/v1/items", params={
            "order_by": "bigdata_recommendation",
            "user_id": 1,
            "limit": 3
        })
        
        print(f"状态码: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回商品数量: {len(data)}")
            
            for i, item in enumerate(data):
                print(f"\n商品 {i+1}:")
                print(f"  ID: {item.get('id')}")
                print(f"  标题: {item.get('title')}")
                print(f"  推荐标识: {item.get('is_bigdata_recommended')}")
                print(f"  推荐来源: {item.get('recommendation_source')}")
                print(f"  推荐算法: {item.get('recommendation_algorithm')}")
                print(f"  推荐原因: {item.get('recommendation_reason')}")
        else:
            print(f"错误: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")
    
    # 测试Hadoop推荐服务
    print("\n2. 测试Hadoop推荐服务...")
    try:
        response = requests.get(f"{base_url}/api/v1/ai_strategy/recommendations/1")
        print(f"Hadoop推荐状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Hadoop推荐结果: {data}")
        else:
            print(f"Hadoop推荐错误: {response.text}")
    except Exception as e:
        print(f"Hadoop推荐异常: {e}")

if __name__ == "__main__":
    test_detailed()
