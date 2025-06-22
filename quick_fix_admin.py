import mysql.connector
from mysql.connector import Error

def quick_fix():
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': '20030208..',
        'database': 'ershou',
        'charset': 'utf8mb4'
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        print("正在添加is_admin字段...")
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
        connection.commit()
        print("is_admin字段添加成功！")
        
        # 为第一个用户设置管理员权限
        cursor.execute("UPDATE users SET is_admin = TRUE WHERE id = 1")
        connection.commit()
        print("已为用户ID=1设置管理员权限")
        
        cursor.close()
        connection.close()
        print("完成！")
        
    except Error as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    quick_fix() 