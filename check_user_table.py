import sqlite3
import os

def check_user_table():
    db_path = "goofish.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查users表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("=== users表结构 ===")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - NULL: {col[3]} - Default: {col[4]}")
        
        # 检查是否有is_admin字段
        has_is_admin = any(col[1] == 'is_admin' for col in columns)
        print(f"\nis_admin字段存在: {has_is_admin}")
        
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
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_user_table() 