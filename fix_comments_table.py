from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)

def fix_comments_table():
    """修复comments表，添加缺失的字段"""
    with engine.connect() as conn:
        try:
            # 检查comments表结构
            result = conn.execute(text("DESCRIBE comments"))
            columns = [row[0] for row in result.fetchall()]
            print("comments 表的列:", columns)
            
            # 检查是否缺少 like_count 字段
            if 'like_count' not in columns:
                print("comments 表缺少 like_count 字段，正在添加...")
                conn.execute(text("ALTER TABLE comments ADD COLUMN like_count INT NOT NULL DEFAULT 0"))
                conn.commit()
                print("已为 comments 表添加 like_count 字段")
            else:
                print("comments 表已有 like_count 字段")
            
            # 检查是否存在 comment_likes 表
            result = conn.execute(text("SHOW TABLES LIKE 'comment_likes'"))
            if not result.fetchone():
                print("comment_likes 表不存在，正在创建...")
                conn.execute(text("""
                    CREATE TABLE comment_likes (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        user_id INT NOT NULL,
                        comment_id INT NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY _user_comment_uc (user_id, comment_id),
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (comment_id) REFERENCES comments(id)
                    )
                """))
                conn.commit()
                print("已创建 comment_likes 表")
            else:
                print("comment_likes 表已存在")
                
        except Exception as e:
            print(f"修复comments表时出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_comments_table() 