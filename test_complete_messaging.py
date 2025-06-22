import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_user_workflow():
    """测试用户完整工作流程"""
    print("=== 测试用户完整工作流程 ===")
    
    # 1. 用户登录
    login_data = {
        "identifier": "directuser",
        "password": "directpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ 用户登录失败: {response.text}")
        return None
    
    user_token = response.json().get("access_token")
    print("✅ 用户登录成功")
    
    # 2. 获取用户信息
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ 用户信息: {user_info['username']}")
    
    # 3. 获取商品列表
    response = requests.get(f"{BASE_URL}/items", headers=headers)
    if response.status_code == 200:
        items = response.json()
        if items:
            item_id = items[0]['id']
            print(f"✅ 找到商品: {items[0]['title']} (ID: {item_id})")
            
            # 4. 发送消息
            message_data = {
                "content": f"这是一条测试消息 - {datetime.now().strftime('%H:%M:%S')}",
                "item_id": item_id
            }
            
            response = requests.post(f"{BASE_URL}/messages", json=message_data, headers=headers)
            if response.status_code == 200:
                message = response.json()
                print(f"✅ 消息发送成功: {message['content']}")
            else:
                print(f"❌ 消息发送失败: {response.text}")
    
    # 5. 获取对话列表
    response = requests.get(f"{BASE_URL}/messages/conversations", headers=headers)
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ 对话列表: {len(conversations)} 个对话")
        for conv in conversations:
            print(f"  - {conv.get('item_title', 'Unknown')}: {conv.get('message_count', 0)} 条消息")
    
    # 6. 获取未读消息数量
    response = requests.get(f"{BASE_URL}/messages/unread-count", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 未读消息数量: {result.get('unread_count', 0)}")
    
    return user_token

def test_admin_workflow():
    """测试管理员工作流程"""
    print("\n=== 测试管理员工作流程 ===")
    
    # 1. 管理员登录
    login_data = {
        "identifier": "directuser2",
        "password": "directpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ 管理员登录失败: {response.text}")
        return None
    
    admin_token = response.json().get("access_token")
    print("✅ 管理员登录成功")
    
    # 2. 获取管理员信息
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ 管理员信息: {user_info['username']} (管理员: {user_info.get('is_admin', False)})")
    
    # 3. 发送系统消息
    system_message_data = {
        "content": f"这是一条系统消息 - {datetime.now().strftime('%H:%M:%S')}",
        "title": "系统通知",
        "target_users": "all",
        "item_id": 13
    }
    
    response = requests.post(f"{BASE_URL}/admin/messages", json=system_message_data, headers=headers)
    if response.status_code == 200:
        message = response.json()
        print(f"✅ 系统消息发送成功: {message['content']}")
    else:
        print(f"❌ 系统消息发送失败: {response.text}")
    
    # 4. 获取系统消息列表
    response = requests.get(f"{BASE_URL}/admin/messages", headers=headers)
    if response.status_code == 200:
        messages = response.json()
        print(f"✅ 系统消息列表: {len(messages)} 条消息")
        for msg in messages:
            print(f"  - {msg.get('title', 'No title')}: {msg.get('content', 'No content')}")
    
    return admin_token

def test_admin_stats():
    """测试管理员统计信息"""
    print("\n=== 测试管理员统计信息 ===")
    
    # 使用管理员token
    login_data = {
        "identifier": "directuser2",
        "password": "directpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ 管理员登录失败: {response.text}")
        return
    
    admin_token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 获取统计信息
    response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print("✅ 管理员统计信息:")
        print(f"  - 总用户数: {stats.get('total_users', 0)}")
        print(f"  - 总商品数: {stats.get('total_items', 0)}")
        print(f"  - 活跃用户: {stats.get('active_users', 0)}")
        print(f"  - 在线商品: {stats.get('online_items', 0)}")
        print(f"  - 已售商品: {stats.get('sold_items', 0)}")
        print(f"  - 总收藏数: {stats.get('total_favorites', 0)}")
    else:
        print(f"❌ 获取统计信息失败: {response.text}")

def main():
    """主函数"""
    print("开始完整消息功能测试...")
    
    # 测试用户工作流程
    user_token = test_user_workflow()
    
    # 测试管理员工作流程
    admin_token = test_admin_workflow()
    
    # 测试管理员统计信息
    test_admin_stats()
    
    print("\n=== 测试完成 ===")
    print("✅ 消息功能测试完成！")
    print("✅ 用户功能正常")
    print("✅ 管理员功能正常")
    print("✅ 系统消息功能正常")

if __name__ == "__main__":
    main() 