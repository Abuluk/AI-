import mysql.connector
from mysql.connector import Error
import os

def fix_mysql_is_admin():
    # 数据库配置 - 使用与session.py相同的配置
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '20030208..',
        'database': 'ershou',
        'charset': 'utf8mb4'
    }
    
    connection = None
    try:
        # 连接数据库
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("=== 检查users表结构 ===")
        
        # 检查表结构
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        print("当前users表结构:")
        for col in columns:
            print(f"  {col[0]} ({col[1]}) - NULL: {col[2]} - Key: {col[3]} - Default: {col[4]}")
        
        # 检查是否有is_admin字段
        has_is_admin = any(col[0] == 'is_admin' for col in columns)
        print(f"\nis_admin字段存在: {has_is_admin}")
        
        if not has_is_admin:
            print("\n正在添加is_admin字段...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
            connection.commit()
            print("is_admin字段添加成功！")
            
            # 重新检查表结构
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            print("\n更新后的users表结构:")
            for col in columns:
                print(f"  {col[0]} ({col[1]}) - NULL: {col[2]} - Key: {col[3]} - Default: {col[4]}")
        else:
            print("is_admin字段已存在")
        
        # 检查用户数据
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n用户总数: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username, email, is_admin FROM users LIMIT 5")
            users = cursor.fetchall()
            print("\n前5个用户:")
            for user in users:
                print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 管理员: {user[3]}")
        
        # 为第一个用户设置管理员权限（可选）
        if user_count > 0:
            print("\n是否要为第一个用户设置管理员权限？(y/n): ", end="")
            choice = input().strip().lower()
            if choice == 'y':
                cursor.execute("UPDATE users SET is_admin = TRUE WHERE id = 1")
                connection.commit()
                print("已为用户ID=1设置管理员权限")
        
    except Error as e:
        print(f"数据库操作出错: {e}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n数据库连接已关闭")

if __name__ == "__main__":
    fix_mysql_is_admin() 