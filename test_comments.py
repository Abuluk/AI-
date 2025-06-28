from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.models import Comment, User
from core.config import settings

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_comments():
    """测试评论查询"""
    db = SessionLocal()
    try:
        # 测试查询评论
        print("测试查询评论...")
        comments = db.query(Comment).filter(Comment.item_id == 32).all()
        print(f"找到 {len(comments)} 条评论")
        
        for i, comment in enumerate(comments):
            print(f"评论 {i+1}:")
            print(f"  ID: {comment.id}")
            print(f"  内容: {comment.content}")
            print(f"  用户ID: {comment.user_id}")
            
            # 测试用户查询
            try:
                user = db.query(User).filter(User.id == comment.user_id).first()
                if user:
                    print(f"  用户名: {user.username}")
                else:
                    print(f"  用户名: 用户不存在 (ID: {comment.user_id})")
            except Exception as e:
                print(f"  查询用户时出错: {e}")
            
            print()
            
    except Exception as e:
        print(f"查询评论时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_comments() 