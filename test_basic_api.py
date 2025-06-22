import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_basic_connection():
    """测试基本连接"""
    print("=== 测试基本连接 ===")
    
    try:
        # 测试根路径
        response = requests.get("http://localhost:8000/")
        print(f"根路径状态码: {response.status_code}")
        
        # 测试API文档
        response = requests.get("http://localhost:8000/docs")
        print(f"API文档状态码: {response.status_code}")
        
        # 测试OpenAPI规范
        response = requests.get("http://localhost:8000/openapi.json")
        print(f"OpenAPI规范状态码: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

def test_items_endpoint():
    """测试商品端点"""
    print("\n=== 测试商品端点 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/items")
        print(f"商品列表状态码: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json()
            print(f"找到 {len(items)} 个商品")
            return True
        else:
            print(f"商品列表失败: {response.text}")
            return False
    except Exception as e:
        print(f"商品端点测试失败: {e}")
        return False

def test_register_with_error_handling():
    """测试注册（带错误处理）"""
    print("\n=== 测试注册（带错误处理） ===")
    
    user_data = {
        "username": "errortest",
        "email": "error@test.com",
        "password": "123456"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=headers)
        print(f"注册状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功!")
            return True
        elif response.status_code == 400:
            print("⚠️ 注册失败 - 客户端错误")
            return False
        elif response.status_code == 500:
            print("❌ 注册失败 - 服务器错误")
            return False
        else:
            print(f"❌ 注册失败 - 未知错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始基本API测试...")
    
    # 测试基本连接
    if not test_basic_connection():
        print("❌ 基本连接测试失败")
        return
    
    # 测试商品端点
    if not test_items_endpoint():
        print("❌ 商品端点测试失败")
        return
    
    # 测试注册
    test_register_with_error_handling()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 