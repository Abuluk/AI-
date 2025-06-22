#!/usr/bin/env python3
"""
测试图片上传功能的脚本
"""

import requests
import os
import tempfile
from PIL import Image

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试用的认证token（你需要用真实的token替换）
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIiLCJleHAiOjE3NTMxNDgzMjB9.yKlFKK3A2bi7do4wzge8X6w2l6YnIoQ-GP3VkSMBV7c"

# 请求头
headers = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "multipart/form-data"
}

def create_test_image(width=300, height=300, color=(255, 0, 0)):
    """创建一个测试图片"""
    img = Image.new('RGB', (width, height), color)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    img.save(temp_file.name, 'JPEG')
    return temp_file.name

def test_image_upload():
    """测试图片上传功能"""
    
    print("=== 测试图片上传功能 ===")
    
    # 创建测试图片
    print("\n1. 创建测试图片")
    test_image_path = create_test_image()
    print(f"   ✅ 测试图片已创建: {test_image_path}")
    
    # 测试上传商品（包含图片）
    print("\n2. 测试上传商品（包含图片）")
    try:
        with open(test_image_path, 'rb') as f:
            files = {'images': ('test_image.jpg', f, 'image/jpeg')}
            data = {
                'title': '测试商品（带图片）',
                'description': '这是一个测试商品，包含上传的图片',
                'price': '99.99',
                'category': '1',
                'location': '北京',
                'condition': 'new'
            }
            
            response = requests.post(f"{BASE_URL}/items/", files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ 商品上传成功")
                print(f"      商品ID: {result.get('id')}")
                print(f"      商品标题: {result.get('title')}")
                print(f"      图片路径: {result.get('images')}")
            else:
                print(f"   ❌ 商品上传失败: {response.status_code}")
                print(f"      响应内容: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
    
    # 清理测试文件
    try:
        os.unlink(test_image_path)
        print(f"\n3. 清理测试文件")
        print(f"   ✅ 测试图片已删除: {test_image_path}")
    except Exception as e:
        print(f"   ❌ 删除测试文件失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_image_upload() 