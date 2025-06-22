import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_simple_register():
    """测试简单注册"""
    print("=== 测试简单注册 ===")
    
    # 最简单的用户数据
    user_data = {
        "username": "simpleuser2",
        "email": "simple2@test.com",
        "password": "123456"
    }
    
    # 添加正确的请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("注册成功!")
            return True
        else:
            print("注册失败")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_login():
    """测试登录"""
    print("\n=== 测试登录 ===")
    
    login_data = {
        "identifier": "simpleuser2",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.text}")
        
        if response.status_code == 200:
            print("登录成功!")
            return response.json().get("access_token")
        else:
            print("登录失败")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        return None

def main():
    """主函数"""
    print("开始简单测试...")
    
    # 测试注册
    if test_simple_register():
        # 测试登录
        token = test_login()
        if token:
            print(f"获取到token: {token[:20]}...")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 