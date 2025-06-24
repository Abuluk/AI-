#!/usr/bin/env python3
"""
检查环境变量配置
"""

import os
from dotenv import load_dotenv

def check_env():
    print("=== 环境变量检查 ===")
    
    # 1. 检查.env文件是否存在
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env 文件存在: {env_file}")
    else:
        print(f"❌ .env 文件不存在: {env_file}")
        print("请创建 .env 文件并配置科大讯飞API密钥")
        return False
    
    # 2. 加载环境变量
    print("\n=== 加载环境变量 ===")
    load_dotenv()
    
    # 3. 检查科大讯飞配置
    print("\n=== 科大讯飞配置检查 ===")
    app_id = os.getenv("XUNFEI_APP_ID")
    api_key = os.getenv("XUNFEI_API_KEY")
    api_secret = os.getenv("XUNFEI_API_SECRET")
    spark_url = os.getenv("XUNFEI_SPARK_URL")
    
    print(f"XUNFEI_APP_ID: {'✅ 已配置' if app_id else '❌ 未配置'}")
    print(f"XUNFEI_API_KEY: {'✅ 已配置' if api_key else '❌ 未配置'}")
    print(f"XUNFEI_API_SECRET: {'✅ 已配置' if api_secret else '❌ 未配置'}")
    print(f"XUNFEI_SPARK_URL: {'✅ 已配置' if spark_url else '❌ 未配置'}")
    
    # 4. 检查配置完整性
    if all([app_id, api_key, api_secret]):
        print("\n✅ 科大讯飞配置完整")
        return True
    else:
        print("\n❌ 科大讯飞配置不完整")
        print("\n请确保 .env 文件包含以下内容：")
        print("XUNFEI_APP_ID=你的app_id")
        print("XUNFEI_API_KEY=你的api_key")
        print("XUNFEI_API_SECRET=你的api_secret")
        print("XUNFEI_SPARK_URL=wss://spark-api.xf-yun.com/v1/x1")
        return False

if __name__ == "__main__":
    check_env() 