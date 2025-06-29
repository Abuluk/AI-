from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from crud.crud_friend import add_friend, remove_friend, get_friends
from core.security import get_current_active_user
from pydantic import BaseModel

router = APIRouter()

class FriendIdBody(BaseModel):
    friend_id: int

@router.post("/add")
def add_friend_api(
    body: FriendIdBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    friend_id = body.friend_id
    if friend_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")
    friend = add_friend(db, current_user.id, friend_id)
    if not friend:
        raise HTTPException(status_code=400, detail="添加失败")
    return {"message": "添加成功"}

@router.post("/delete")
def delete_friend_api(
    body: FriendIdBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    friend_id = body.friend_id
    ok = remove_friend(db, current_user.id, friend_id)
    if not ok:
        raise HTTPException(status_code=404, detail="好友不存在")
    return {"message": "删除成功"}

@router.get("/list")
def list_friends_api(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    friends = get_friends(db, current_user.id)
    # 返回好友用户信息
    friend_ids = [f.friend_id for f in friends]
    users = db.query(User).filter(User.id.in_(friend_ids)).all()
    return [{"id": u.id, "username": u.username, "avatar": u.avatar, "bio": u.bio} for u in users]

@router.get("/search")
def search_users_api(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    users = db.query(User).filter(User.username.ilike(f"%{keyword}%"), User.id != current_user.id).limit(20).all()
    return [{"id": u.id, "username": u.username, "avatar": u.avatar, "bio": u.bio} for u in users]

@router.get("/{friend_id}")
def get_friend_detail(friend_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == friend_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"id": user.id, "username": user.username, "avatar": user.avatar, "bio": user.bio, "location": user.location} 