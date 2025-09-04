from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User, Comment, CommentLike
from schemas.message import CommentCreate, CommentResponse
from core.security import get_current_active_user, get_current_user_optional
from crud.crud_comment import create_comment, get_comments, delete_comment, get_user_related_comments, like_comment, unlike_comment
from crud.crud_message import create_system_message
from schemas.message import SystemMessageCreate
from config import get_image_base_url, get_full_image_url

router = APIRouter()

def process_avatar_url(avatar_url):
    """处理用户头像URL"""
    return get_full_image_url(avatar_url)

@router.post("/", response_model=CommentResponse)
def post_comment(
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comment = create_comment(db, comment_in, user_id=current_user.id)
    # 不再生成系统消息，仅在评论互动高亮@对象
    reply_to_user = db.query(User).filter(User.id == comment.reply_to_user_id).first() if comment.reply_to_user_id else None
    return CommentResponse(
        id=comment.id,
        content=comment.content,
        user_id=comment.user_id,
        item_id=comment.item_id,
        buy_request_id=comment.buy_request_id,
        parent_id=comment.parent_id,
        reply_to_user_id=comment.reply_to_user_id,
        created_at=comment.created_at,
        user_name=current_user.username if current_user else None,
        user_avatar=current_user.avatar if current_user else None,
        reply_to_user_name=reply_to_user.username if reply_to_user else None,
        children=[]
    )

@router.get("/", response_model=List[CommentResponse])
def get_comment_list(
    item_id: Optional[int] = None,
    buy_request_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    comments = get_comments(db, item_id=item_id, buy_request_id=buy_request_id)
    # 构建树形结构
    comment_map = {c.id: c for c in comments}
    resp_map = {}
    for c in comments:
        user = c.user if hasattr(c, 'user') else None
        user_name = user.username if user else None
        user_avatar = user.avatar if user else None
        reply_to_user = db.query(User).filter(User.id == c.reply_to_user_id).first() if c.reply_to_user_id else None
        reply_to_user_name = reply_to_user.username if reply_to_user else None
        resp = CommentResponse(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            item_id=c.item_id,
            buy_request_id=c.buy_request_id,
            parent_id=c.parent_id,
            reply_to_user_id=c.reply_to_user_id,
            created_at=c.created_at,
            user_name=user_name,
            user_avatar=user_avatar,
            reply_to_user_name=reply_to_user_name,
            children=[]
        )
        resp_map[c.id] = resp
    # 组装树
    root_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in resp_map:
            resp_map[c.parent_id].children.append(resp_map[c.id])
        else:
            root_comments.append(resp_map[c.id])
    return root_comments

@router.delete("/{comment_id}")
def remove_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    is_admin = current_user.is_admin
    success = delete_comment(db, comment_id, user_id=current_user.id, is_admin=is_admin)
    if not success:
        raise HTTPException(status_code=403, detail="无权限删除评论")
    return {"message": "评论已删除"}

@router.get("/my_related", response_model=List[CommentResponse])
def get_my_related_comments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comments = get_user_related_comments(db, current_user.id)
    # 按时间倒序
    comments = sorted(comments, key=lambda c: c.created_at, reverse=True)
    # 转为响应格式
    resp = []
    for c in comments:
        user = c.user if hasattr(c, 'user') else None
        user_name = user.username if user else None
        user_avatar = user.avatar if user else None
        reply_to_user = db.query(User).filter(User.id == c.reply_to_user_id).first() if c.reply_to_user_id else None
        reply_to_user_name = reply_to_user.username if reply_to_user else None
        resp.append(CommentResponse(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            item_id=c.item_id,
            buy_request_id=c.buy_request_id,
            parent_id=c.parent_id,
            reply_to_user_id=c.reply_to_user_id,
            created_at=c.created_at,
            user_name=user_name,
            user_avatar=user_avatar,
            reply_to_user_name=reply_to_user_name,
            children=[]
        ))
    return resp

@router.post("/{comment_id}/like")
def like_comment_api(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    count = like_comment(db, comment_id, current_user.id)
    if count == -1:
        raise HTTPException(status_code=400, detail="已点赞")
    return {"like_count": count}

@router.post("/{comment_id}/unlike")
def unlike_comment_api(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    count = unlike_comment(db, comment_id, current_user.id)
    if count == -1:
        raise HTTPException(status_code=400, detail="未点赞")
    return {"like_count": count}

@router.get("/{item_id}", response_model=List[CommentResponse])
def get_comments_by_item_id(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """根据商品ID获取评论列表（公共接口，支持可选认证）"""
    
    comments = get_comments(db, item_id=item_id)
    comment_map = {c.id: c for c in comments}
    
    # 查询当前用户点赞过的评论id（如果有用户登录的话）
    liked_ids = set()
    if current_user:
        liked_ids = set([r.comment_id for r in db.query(CommentLike).filter(CommentLike.user_id == current_user.id).all()])
    
    resp_map = {}
    for c in comments:
        user = c.user if hasattr(c, 'user') else None
        user_name = user.username if user else None
        user_avatar = process_avatar_url(user.avatar) if user else None
        reply_to_user = db.query(User).filter(User.id == c.reply_to_user_id).first() if c.reply_to_user_id else None
        reply_to_user_name = reply_to_user.username if reply_to_user else None
        resp = CommentResponse(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            item_id=c.item_id,
            buy_request_id=c.buy_request_id,
            parent_id=c.parent_id,
            reply_to_user_id=c.reply_to_user_id,
            created_at=c.created_at,
            user_name=user_name,
            user_avatar=user_avatar,
            reply_to_user_name=reply_to_user_name,
            children=[],
            like_count=c.like_count or 0,
            liked_by_me=(c.id in liked_ids)
        )
        resp_map[c.id] = resp
    # 组装树
    root_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in resp_map:
            resp_map[c.parent_id].children.append(resp_map[c.id])
        else:
            root_comments.append(resp_map[c.id])
    # 按点赞数和时间排序
    root_comments.sort(key=lambda x: (-x.like_count, -x.created_at.timestamp()))
    return root_comments

@router.get("/tree", response_model=List[CommentResponse])
def get_comment_tree(
    item_id: Optional[int] = None,
    buy_request_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    comments = get_comments(db, item_id=item_id, buy_request_id=buy_request_id)
    comment_map = {c.id: c for c in comments}
    # 查询当前用户点赞过的评论id
    liked_ids = set()
    if current_user:
        liked_ids = set([r.comment_id for r in db.query(CommentLike).filter(CommentLike.user_id == current_user.id).all()])
    resp_map = {}
    for c in comments:
        user = c.user if hasattr(c, 'user') else None
        user_name = user.username if user else None
        user_avatar = user.avatar if user else None
        reply_to_user = db.query(User).filter(User.id == c.reply_to_user_id).first() if c.reply_to_user_id else None
        reply_to_user_name = reply_to_user.username if reply_to_user else None
        resp = CommentResponse(
            id=c.id,
            content=c.content,
            user_id=c.user_id,
            item_id=c.item_id,
            buy_request_id=c.buy_request_id,
            parent_id=c.parent_id,
            reply_to_user_id=c.reply_to_user_id,
            created_at=c.created_at,
            user_name=user_name,
            user_avatar=user_avatar,
            reply_to_user_name=reply_to_user_name,
            children=[],
            like_count=c.like_count or 0,
            liked_by_me=(c.id in liked_ids)
        )
        resp_map[c.id] = resp
    root_comments = []
    for c in comments:
        if c.parent_id and c.parent_id in resp_map:
            resp_map[c.parent_id].children.append(resp_map[c.id])
        else:
            root_comments.append(resp_map[c.id])
    # 按点赞数和时间排序
    root_comments.sort(key=lambda x: (-x.like_count, -x.created_at.timestamp()))
    return root_comments 