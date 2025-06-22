from fastapi.testclient import TestClient
from main import app
import json

# 创建测试客户端
client = TestClient(app)

def test_register_direct():
    """直接测试注册API"""
    print("=== 直接测试注册API ===")
    
    # 测试数据
    user_data = {
        "username": "directuser2",
        "email": "direct2@test.com",
        "password": "directpass123"
    }
    
    try:
        # 发送POST请求
        response = client.post("/api/v1/auth/register", json=user_data)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功!")
            return True
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_and_message():
    """测试登录和消息功能"""
    print("\n=== 测试登录和消息功能 ===")
    
    # 登录
    login_data = {
        "identifier": "directuser",
        "password": "directpass123"
    }
    
    try:
        response = client.post("/api/v1/auth/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ 登录成功!")
            
            # 测试发送消息
            headers = {"Authorization": f"Bearer {token}"}
            message_data = {
                "content": "这是一条测试消息",
                "item_id": 13
            }
            
            response = client.post("/api/v1/messages", json=message_data, headers=headers)
            print(f"发送消息状态码: {response.status_code}")
            print(f"发送消息响应: {response.text}")
            
            if response.status_code == 200:
                print("✅ 消息发送成功!")
                return True
            else:
                print("❌ 消息发送失败")
                return False
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始直接API测试...")
    
    # 测试注册
    test_register_direct()
    
    # 测试登录和消息
    test_login_and_message()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 