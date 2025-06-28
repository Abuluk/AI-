from sqlalchemy.orm import Session, joinedload
from db.models import Comment, User, Item, BuyRequest, CommentLike
from schemas.message import CommentCreate, SystemMessageCreate
from datetime import datetime
from typing import List, Optional
from crud.crud_message import create_system_message

def create_comment(db: Session, comment_in: CommentCreate, user_id: int) -> Comment:
    db_comment = Comment(
        content=comment_in.content,
        user_id=user_id,
        item_id=comment_in.item_id,
        buy_request_id=comment_in.buy_request_id,
        parent_id=comment_in.parent_id,
        reply_to_user_id=comment_in.reply_to_user_id,
        created_at=datetime.utcnow()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments(db: Session, item_id: Optional[int] = None, buy_request_id: Optional[int] = None) -> List[Comment]:
    q = db.query(Comment).options(joinedload(Comment.user))  # 预加载用户信息
    if item_id:
        q = q.filter(Comment.item_id == item_id)
    if buy_request_id:
        q = q.filter(Comment.buy_request_id == buy_request_id)
    comments = q.order_by(Comment.created_at).all()
    return comments

def delete_comment(db: Session, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return False
    if not is_admin and comment.user_id != user_id:
        return False
    db.delete(comment)
    db.commit()
    return True

def get_user_related_comments(db: Session, user_id: int) -> List[Comment]:
    # 我发出的评论
    my_comments = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.user_id == user_id).all()
    # 别人回复我的评论（reply_to_user_id = 当前用户，且不是自己回复自己）
    replies_to_me = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.reply_to_user_id == user_id, Comment.user_id != user_id).all()
    # 别人对我商品的一级评论
    item_comments = db.query(Comment).options(joinedload(Comment.user)).join(Item, Comment.item_id == Item.id).filter(
        Comment.parent_id == None,
        Item.owner_id == user_id,
        Comment.user_id != user_id
    ).all()
    # 别人对我求购的一级评论
    br_comments = db.query(Comment).options(joinedload(Comment.user)).join(BuyRequest, Comment.buy_request_id == BuyRequest.id).filter(
        Comment.parent_id == None,
        BuyRequest.user_id == user_id,
        Comment.user_id != user_id
    ).all()
    return my_comments + replies_to_me + item_comments + br_comments

def like_comment(db: Session, comment_id: int, user_id: int) -> int:
    # 检查是否已点赞
    exists = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=user_id).first()
    if exists:
        return -1  # 已点赞
    db.add(CommentLike(comment_id=comment_id, user_id=user_id))
    comment = db.query(Comment).filter_by(id=comment_id).first()
    if comment:
        comment.like_count += 1
        # 新增：生成点赞消息
        if comment.user_id != user_id:
            user = db.query(User).filter_by(id=user_id).first()
            content = f"用户{user.username}点赞了你的评论：'{comment.content[:20]}'"
            msg = SystemMessageCreate(
                content=content,
                title="评论被点赞",
                target_users=str(comment.user_id),
                item_id=comment.item_id
            )
            create_system_message(db, msg, admin_id=user_id)
    db.commit()
    return comment.like_count if comment else 0

def unlike_comment(db: Session, comment_id: int, user_id: int) -> int:
    like = db.query(CommentLike).filter_by(comment_id=comment_id, user_id=user_id).first()
    if not like:
        return -1  # 未点赞
    db.delete(like)
    comment = db.query(Comment).filter_by(id=comment_id).first()
    if comment and comment.like_count > 0:
        comment.like_count -= 1
    db.commit()
    return comment.like_count if comment else 0 