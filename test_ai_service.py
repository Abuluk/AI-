#!/usr/bin/env python3
"""
直接测试AI服务
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_ai_service():
    print("=== 直接测试AI服务 ===")
    
    # 1. 检查环境变量
    app_id = os.getenv("XUNFEI_APP_ID")
    api_key = os.getenv("XUNFEI_API_KEY")
    api_secret = os.getenv("XUNFEI_API_SECRET")
    spark_url = os.getenv("XUNFEI_SPARK_URL")
    
    print(f"APP_ID: {app_id}")
    print(f"API_KEY: {api_key}")
    print(f"API_SECRET: {api_secret}")
    print(f"SPARK_URL: {spark_url}")
    
    # 2. 检查配置完整性
    if not all([app_id, api_key, api_secret]):
        print("❌ 配置不完整")
        return
    
    # 3. 测试导入AI服务
    try:
        from core.spark_ai import spark_ai_service
        print("✅ AI服务导入成功")
        
        # 4. 测试AI服务实例
        print(f"AI服务实例: {spark_ai_service}")
        
        # 5. 测试配置获取
        config = spark_ai_service._get_config()
        print(f"动态配置: {config}")
        
        # 6. 测试配置检查
        if all([config['app_id'], config['api_key'], config['api_secret']]):
            print("✅ AI服务配置完整")
            
            # 7. 测试AI分析功能
            test_items = [
                {
                    "title": "二手 iPhone 13",
                    "price": 3500,
                    "condition": "good"
                },
                {
                    "title": "全新 AirPods Pro",
                    "price": 1200,
                    "condition": "new"
                }
            ]
            
            print("\n=== 测试AI分析功能 ===")
            result = spark_ai_service.analyze_price_competition(test_items)
            print(f"AI分析结果: {result}")
            
        else:
            print("❌ AI服务配置不完整")
            
    except ImportError as e:
        print(f"❌ 导入AI服务失败: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

if __name__ == "__main__":
    test_ai_service() 