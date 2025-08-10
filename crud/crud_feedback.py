from sqlalchemy.orm import Session
from db.models import Feedback
from datetime import datetime

def create_feedback(db: Session, user_id: int, content: str):
    feedback = Feedback(user_id=user_id, content=content)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_all_feedbacks(db: Session):
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()

def solve_feedback(db: Session, feedback_id: int):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        feedback.status = 'solved'
        feedback.solved_at = datetime.utcnow()
        db.commit()
        db.refresh(feedback)
    return feedback

def delete_feedback(db: Session, feedback_id: int):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        db.delete(feedback)
        db.commit()
    return feedback 