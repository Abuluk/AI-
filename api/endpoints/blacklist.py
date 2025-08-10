from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from db.models import User
from crud.crud_blacklist import add_to_blacklist, remove_from_blacklist, get_blacklist
from core.security import get_current_active_user

router = APIRouter()

@router.post("/add")
def add_blacklist_api(blocked_user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if blocked_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能拉黑自己")
    bl = add_to_blacklist(db, current_user.id, blocked_user_id)
    if not bl:
        raise HTTPException(status_code=400, detail="拉黑失败")
    return {"message": "已拉黑"}

@router.post("/remove")
def remove_blacklist_api(blocked_user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    ok = remove_from_blacklist(db, current_user.id, blocked_user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="黑名单不存在")
    return {"message": "已移除黑名单"}

@router.get("/list")
def list_blacklist_api(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    bls = get_blacklist(db, current_user.id)
    blocked_ids = [b.blocked_user_id for b in bls]
    users = db.query(User).filter(User.id.in_(blocked_ids)).all()
    return [{"id": u.id, "username": u.username, "avatar": u.avatar, "bio": u.bio} for u in users] 