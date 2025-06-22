#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

def check_admin_user():
    connection = None
    try:
        # 连接MySQL数据库 - 使用正确的配置
        connection = mysql.connector.connect(
            host='localhost',
            database='ershou',
            user='root',
            password='20030208..'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # 查询指定手机号的用户信息
            phone = '17877629971'
            query = "SELECT id, username, email, phone, is_admin, is_active FROM users WHERE phone = %s"
            cursor.execute(query, (phone,))
            users = cursor.fetchall()
            
            print(f"手机号为 {phone} 的用户信息：")
            print("ID | 用户名 | 邮箱 | 手机 | 管理员 | 激活状态")
            print("-" * 60)
            
            if not users:
                print("❌ 没有找到该手机号的用户")
            else:
                for user in users:
                    user_id, username, email, phone, is_admin, is_active = user
                    admin_status = "是" if is_admin else "否"
                    active_status = "是" if is_active else "否"
                    username_display = username if username else "(空)"
                    print(f"{user_id} | {username_display} | {email} | {phone} | {admin_status} | {active_status}")
                    
                    # 特别提示username为空的问题
                    if not username:
                        print(f"⚠️  警告：用户ID {user_id} 的username字段为空！")
                        print(f"   这会导致登录时token的sub字段为空，无法正常认证。")
    except Error as e:
        print(f"数据库连接错误: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    check_admin_user() 