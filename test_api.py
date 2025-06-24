#!/usr/bin/env python3
"""
测试AI API端点
"""

import requests
import json

def test_ai_api():
    """测试AI推荐API"""
    print("=== 测试AI推荐API ===")
    
    try:
        # 测试API端点
        url = "http://localhost:8000/api/v1/items/ai-cheap-deals"
        params = {"limit": 5}
        
        print(f"请求URL: {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功!")
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行 (python main.py)")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_ai_api() 