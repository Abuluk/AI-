from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_active_user, get_current_user
from db.models import User
from schemas.feedback import FeedbackCreate, FeedbackInDB, FeedbackUpdate
from crud import crud_feedback

router = APIRouter()

@router.post("/", response_model=FeedbackInDB)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return crud_feedback.create_feedback(db, user_id=current_user.id, content=feedback_in.content)

@router.get("/", response_model=list[FeedbackInDB])
def list_feedbacks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")
    return crud_feedback.get_all_feedbacks(db)

@router.patch("/{feedback_id}", response_model=FeedbackInDB)
def solve_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")
    feedback = crud_feedback.solve_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="留言不存在")
    return feedback

@router.delete("/{feedback_id}")
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")
    feedback = crud_feedback.delete_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="留言不存在")
    return {"msg": "删除成功"} 