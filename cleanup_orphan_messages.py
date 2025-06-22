import sqlite3
import os

# --- 配置 ---
DB_FILE = "goofish.db"

def cleanup_orphan_messages():
    """
    清理 messages 表中 item_id 指向不存在的 items 的记录。
    """
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_FILE)
    if not os.path.exists(db_path):
        print(f"错误：数据库文件 '{DB_FILE}' 不存在。")
        return

    try:
        conn = sqlite3.connect(db_path)
        # 允许外键约束 (虽然默认ALTER TABLE不支持，但DELETE时会检查)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        # 1. 找出所有在 messages 表中但不在 items 表中的 item_id
        # 使用 LEFT JOIN，如果 items.id is NULL，说明 item 不存在
        orphan_query = """
        SELECT DISTINCT m.item_id
        FROM messages AS m
        LEFT JOIN items AS i ON m.item_id = i.id
        WHERE i.id IS NULL
        """
        cursor.execute(orphan_query)
        orphan_item_ids = [row[0] for row in cursor.fetchall()]

        if not orphan_item_ids:
            print("数据库中没有发现孤儿消息，数据很干净！")
            return

        print(f"发现了 {len(orphan_item_ids)} 个商品ID存在孤儿消息: {orphan_item_ids}")
        
        # 2. 删除所有与这些孤儿 item_id 相关的消息
        # 使用元组来传递参数，即使只有一个元素也要用 (id,) 的形式
        for item_id in orphan_item_ids:
            delete_query = "DELETE FROM messages WHERE item_id = ?"
            print(f"正在删除 item_id = {item_id} 的所有消息...")
            cursor.execute(delete_query, (item_id,))
            print(f" > 成功删除了 {cursor.rowcount} 条消息。")

        conn.commit()
        print("\n所有孤儿消息已清理完毕。")

    except sqlite3.Error as e:
        print(f"数据库操作时发生错误: {e}")
        # 如果出错，回滚所有操作
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    cleanup_orphan_messages() 