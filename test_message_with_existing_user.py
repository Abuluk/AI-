import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_login_with_existing_user():
    """使用现有用户测试登录"""
    print("=== 使用现有用户测试登录 ===")
    
    # 尝试使用之前创建的用户
    login_data = {
        "identifier": "directuser",
        "password": "directpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ 登录成功!")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_get_user_info(token):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print(f"获取用户信息状态码: {response.status_code}")
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 用户信息: {user_info['username']} ({user_info['email']})")
            return user_info
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return None

def test_get_items(token):
    """测试获取商品列表"""
    print("\n=== 测试获取商品列表 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/items", headers=headers)
        print(f"获取商品列表状态码: {response.status_code}")
        
        if response.status_code == 200:
            items = response.json()
            print(f"✅ 找到 {len(items)} 个商品")
            if items:
                print(f"第一个商品: {items[0]['title']}")
                return items[0]['id']
            return None
        else:
            print(f"❌ 获取商品列表失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取商品列表异常: {e}")
        return None

def test_send_message(token, item_id):
    """测试发送消息"""
    print(f"\n=== 测试发送消息 (商品ID: {item_id}) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    message_data = {
        "content": f"这是一条测试消息，发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "item_id": item_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/messages", json=message_data, headers=headers)
        print(f"发送消息状态码: {response.status_code}")
        
        if response.status_code == 200:
            message = response.json()
            print(f"✅ 消息发送成功: {message['content']}")
            return message['id']
        else:
            print(f"❌ 发送消息失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 发送消息异常: {e}")
        return None

def test_get_conversations(token):
    """测试获取对话列表"""
    print("\n=== 测试获取对话列表 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/messages/conversations", headers=headers)
        print(f"获取对话列表状态码: {response.status_code}")
        
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ 找到 {len(conversations)} 个对话")
            for conv in conversations:
                print(f"对话: {conv.get('item_title', 'Unknown')} - 消息数: {conv.get('message_count', 0)}")
            return conversations
        else:
            print(f"❌ 获取对话列表失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取对话列表异常: {e}")
        return None

def test_get_unread_count(token):
    """测试获取未读消息数量"""
    print("\n=== 测试获取未读消息数量 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/messages/unread-count", headers=headers)
        print(f"获取未读消息数量状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 未读消息数量: {result.get('unread_count', 0)}")
            return result.get('unread_count', 0)
        else:
            print(f"❌ 获取未读消息数量失败: {response.text}")
            return 0
    except Exception as e:
        print(f"❌ 获取未读消息数量异常: {e}")
        return 0

def main():
    """主函数"""
    print("开始测试消息功能（使用现有用户）...")
    
    # 使用现有用户登录
    token = test_login_with_existing_user()
    if not token:
        print("❌ 登录失败，无法继续测试")
        return
    
    # 获取用户信息
    user_info = test_get_user_info(token)
    if not user_info:
        print("❌ 获取用户信息失败")
        return
    
    # 获取商品列表
    item_id = test_get_items(token)
    if not item_id:
        print("❌ 没有找到商品，无法测试消息功能")
        return
    
    # 测试发送消息
    message_id = test_send_message(token, item_id)
    if not message_id:
        print("❌ 发送消息失败")
        return
    
    # 测试获取对话列表
    conversations = test_get_conversations(token)
    if conversations is None:
        print("❌ 获取对话列表失败")
        return
    
    # 测试获取未读消息数量
    unread_count = test_get_unread_count(token)
    
    print(f"\n✅ 消息功能测试完成！")
    print(f"发送了 {1 if message_id else 0} 条消息")
    print(f"找到 {len(conversations) if conversations else 0} 个对话")
    print(f"未读消息数量: {unread_count}")

if __name__ == "__main__":
    main() 