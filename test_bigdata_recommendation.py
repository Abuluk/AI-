#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试大数据推荐功能
"""
import requests

def test_bigdata_recommendation():
    """测试大数据推荐API"""
    print("=" * 80)
    print("测试大数据推荐功能")
    print("=" * 80)
    
    # 测试API
    url = "http://127.0.0.1:8000/api/v1/items"
    params = {
        "order_by": "bigdata_recommendation",
        "user_id": 1,
        "limit": 5
    }
    
    print(f"\n1. 请求URL: {url}")
    print(f"2. 请求参数: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"3. 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"4. 返回商品数量: {len(data)}")
            
            if data:
                print(f"\n5. 第一个商品信息:")
                first_item = data[0]
                print(f"   - 商品ID: {first_item.get('id')}")
                print(f"   - 商品标题: {first_item.get('title')}")
                print(f"   - 商品价格: {first_item.get('price')}")
                
                # 检查大数据推荐标识
                print(f"\n6. 大数据推荐标识:")
                print(f"   - is_bigdata_recommended: {first_item.get('is_bigdata_recommended')}")
                print(f"   - recommendation_source: {first_item.get('recommendation_source')}")
                print(f"   - recommendation_algorithm: {first_item.get('recommendation_algorithm')}")
                print(f"   - recommendation_reason: {first_item.get('recommendation_reason')}")
                
                # 验证结果
                if first_item.get('is_bigdata_recommended'):
                    print(f"\n[SUCCESS] 测试通过！大数据推荐功能正常工作")
                    print(f"[SUCCESS] 推荐来源: {first_item.get('recommendation_source')}")
                    print(f"[SUCCESS] 推荐算法: {first_item.get('recommendation_algorithm')}")
                else:
                    print(f"\n[FAILED] 测试失败！缺少大数据推荐标识")
                    print(f"[FAILED] 可能原因：服务器需要重启才能加载新代码")
            else:
                print(f"\n[FAILED] 测试失败！返回商品列表为空")
        else:
            print(f"[FAILED] 测试失败！响应状态码异常: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print(f"[FAILED] 测试失败！无法连接到服务器")
        print(f"请确保后端服务器正在运行")
    except Exception as e:
        print(f"[FAILED] 测试失败！发生异常: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_bigdata_recommendation()


