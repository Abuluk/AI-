#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI自动补全功能
"""

import requests
import json
import os
from pathlib import Path

def test_ai_auto_complete():
    """测试AI自动补全功能"""
    
    # API端点
    url = "http://localhost:8000/api/v1/items/ai-auto-complete"
    
    # 查找测试图片
    test_images = []
    static_dir = Path("static/images")
    
    if static_dir.exists():
        # 查找前4张图片用于测试
        for img_file in static_dir.glob("*.jpg"):
            if len(test_images) < 4:
                test_images.append(img_file)
            else:
                break
        
        for img_file in static_dir.glob("*.png"):
            if len(test_images) < 4:
                test_images.append(img_file)
            else:
                break
    
    if not test_images:
        print("❌ 未找到测试图片，请确保static/images目录中有图片文件")
        return
    
    print(f"📸 找到 {len(test_images)} 张测试图片")
    
    # 准备文件数据
    files = []
    for i, img_path in enumerate(test_images):
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))
        print(f"  图片 {i+1}: {img_path.name}")
    
    try:
        print("\n🚀 发送AI自动补全请求...")
        
        # 发送请求
        response = requests.post(url, files=files, timeout=60)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功!")
            print(f"📋 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                data = result.get('data', {})
                print("\n🎯 AI识别结果:")
                print(f"  标题: {data.get('title', 'N/A')}")
                print(f"  描述: {data.get('description', 'N/A')}")
                print(f"  分类: {data.get('category', 'N/A')}")
                print(f"  状态: {data.get('condition', 'N/A')}")
                print(f"  价格建议: {data.get('price_suggestion', 'N/A')}")
            else:
                print(f"❌ AI识别失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    finally:
        # 关闭文件
        for _, (_, file_obj, _) in files:
            file_obj.close()

def test_ai_auto_complete_ws():
    """测试websockets版本的AI自动补全功能"""
    
    # API端点
    url = "http://localhost:8000/api/v1/items/ai-auto-complete-ws"
    
    # 查找测试图片
    test_images = []
    static_dir = Path("static/images")
    
    if static_dir.exists():
        # 查找前4张图片用于测试
        for img_file in static_dir.glob("*.jpg"):
            if len(test_images) < 4:
                test_images.append(img_file)
            else:
                break
        
        for img_file in static_dir.glob("*.png"):
            if len(test_images) < 4:
                test_images.append(img_file)
            else:
                break
    
    if not test_images:
        print("❌ 未找到测试图片，请确保static/images目录中有图片文件")
        return
    
    print(f"📸 找到 {len(test_images)} 张测试图片")
    
    # 准备文件数据
    files = []
    for i, img_path in enumerate(test_images):
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))
        print(f"  图片 {i+1}: {img_path.name}")
    
    try:
        print("\n🚀 发送websockets版本AI自动补全请求...")
        
        # 发送请求
        response = requests.post(url, files=files, timeout=60)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 请求成功!")
            print(f"📋 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get('success'):
                data = result.get('data', {})
                print("\n🎯 AI识别结果:")
                print(f"  标题: {data.get('title', 'N/A')}")
                print(f"  描述: {data.get('description', 'N/A')}")
                print(f"  分类: {data.get('category', 'N/A')}")
                print(f"  状态: {data.get('condition', 'N/A')}")
                print(f"  价格建议: {data.get('price_suggestion', 'N/A')}")
            else:
                print(f"❌ AI识别失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    finally:
        # 关闭文件
        for _, (_, file_obj, _) in files:
            file_obj.close()

if __name__ == "__main__":
    print("🧪 测试AI自动补全功能")
    print("=" * 50)
    
    print("\n1️⃣ 测试标准版本:")
    test_ai_auto_complete()
    
    print("\n" + "=" * 50)
    print("\n2️⃣ 测试websockets版本:")
    test_ai_auto_complete_ws()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成!") 