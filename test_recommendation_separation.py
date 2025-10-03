#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试推荐系统分离功能
验证大数据推荐和AI增强推荐是否使用不同的数据源
"""

import requests
import json
import time

def test_recommendation_apis():
    """测试推荐API端点"""
    base_url = "http://192.168.174.128:8080"
    
    print("=== 推荐系统分离测试 ===")
    print(f"测试服务器: {base_url}")
    
    # 测试用户ID
    test_user_id = 1
    
    print(f"\n1. 测试用户 {test_user_id} 的推荐结果")
    
    # 测试大数据推荐
    print("\n--- 大数据推荐 ---")
    try:
        response = requests.get(f"{base_url}/recommendations/{test_user_id}", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"推荐数量: {len(data.get('recommendations', []))}")
            print(f"算法: {data.get('algorithm', 'unknown')}")
            print(f"类型: {data.get('type', 'unknown')}")
            print(f"推荐商品ID: {data.get('recommendations', [])[:5]}...")  # 只显示前5个
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"大数据推荐测试失败: {e}")
    
    # 测试AI增强推荐
    print("\n--- AI增强推荐 ---")
    try:
        response = requests.get(f"{base_url}/ai_recommendations/{test_user_id}", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"推荐数量: {len(data.get('recommendations', []))}")
            print(f"算法: {data.get('algorithm', 'unknown')}")
            print(f"类型: {data.get('type', 'unknown')}")
            print(f"AI模型版本: {data.get('ai_model_version', 'unknown')}")
            print(f"推荐商品ID: {data.get('recommendations', [])[:5]}...")  # 只显示前5个
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"AI增强推荐测试失败: {e}")
    
    # 测试备用AI推荐端点
    print("\n--- AI增强推荐（备用端点） ---")
    try:
        response = requests.get(f"{base_url}/recommendations/ai/{test_user_id}", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"推荐数量: {len(data.get('recommendations', []))}")
            print(f"算法: {data.get('algorithm', 'unknown')}")
            print(f"类型: {data.get('type', 'unknown')}")
            print(f"AI增强标识: {data.get('ai_enhanced', False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"AI增强推荐（备用端点）测试失败: {e}")
    
    # 测试健康检查
    print("\n--- 健康检查 ---")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"服务状态: {data.get('status', 'unknown')}")
            print(f"大数据推荐可用: {data.get('bigdata_recommendations', False)}")
            print(f"AI推荐可用: {data.get('ai_recommendations', False)}")
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"健康检查失败: {e}")

def test_data_access_script():
    """测试数据访问脚本"""
    print("\n=== 数据访问脚本测试 ===")
    
    import subprocess
    
    # 测试大数据推荐
    print("\n--- 测试大数据推荐数据访问 ---")
    try:
        result = subprocess.run([
            "/opt/scripts/data_access_api.sh", 
            "get-user", "1", "10", "bigdata"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"返回码: {result.returncode}")
        print(f"输出: {result.stdout.strip()}")
        if result.stderr:
            print(f"错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"大数据推荐数据访问测试失败: {e}")
    
    # 测试AI增强推荐
    print("\n--- 测试AI增强推荐数据访问 ---")
    try:
        result = subprocess.run([
            "/opt/scripts/data_access_api.sh", 
            "get-user", "1", "10", "ai"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"返回码: {result.returncode}")
        print(f"输出: {result.stdout.strip()}")
        if result.stderr:
            print(f"错误: {result.stderr.strip()}")
    except Exception as e:
        print(f"AI增强推荐数据访问测试失败: {e}")

def compare_recommendations():
    """比较两种推荐的结果"""
    print("\n=== 推荐结果比较 ===")
    
    base_url = "http://192.168.174.128:8080"
    test_user_id = 1
    
    try:
        # 获取大数据推荐
        bigdata_response = requests.get(f"{base_url}/recommendations/{test_user_id}", timeout=10)
        bigdata_data = bigdata_response.json() if bigdata_response.status_code == 200 else {}
        
        # 获取AI增强推荐
        ai_response = requests.get(f"{base_url}/ai_recommendations/{test_user_id}", timeout=10)
        ai_data = ai_response.json() if ai_response.status_code == 200 else {}
        
        bigdata_items = set(bigdata_data.get('recommendations', []))
        ai_items = set(ai_data.get('recommendations', []))
        
        print(f"大数据推荐商品数: {len(bigdata_items)}")
        print(f"AI增强推荐商品数: {len(ai_items)}")
        
        if bigdata_items and ai_items:
            common_items = bigdata_items.intersection(ai_items)
            bigdata_only = bigdata_items - ai_items
            ai_only = ai_items - bigdata_items
            
            print(f"共同推荐商品数: {len(common_items)}")
            print(f"仅大数据推荐: {len(bigdata_only)}")
            print(f"仅AI增强推荐: {len(ai_only)}")
            
            if len(common_items) == len(bigdata_items) == len(ai_items):
                print("⚠️  警告: 两种推荐结果完全相同！")
            elif len(common_items) > len(bigdata_items) * 0.8:
                print("⚠️  警告: 两种推荐结果高度相似！")
            else:
                print("✅ 两种推荐结果有明显差异")
        else:
            print("❌ 无法比较：至少一种推荐结果为空")
            
    except Exception as e:
        print(f"比较推荐结果失败: {e}")

if __name__ == "__main__":
    print("开始推荐系统分离测试...")
    
    # 测试API端点
    test_recommendation_apis()
    
    # 测试数据访问脚本
    test_data_access_script()
    
    # 比较推荐结果
    compare_recommendations()
    
    print("\n=== 测试完成 ===")
    print("如果看到'两种推荐结果有明显差异'，说明修改成功！")
    print("如果看到'两种推荐结果完全相同'，说明还需要进一步调试。")
