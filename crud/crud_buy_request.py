from sqlalchemy.orm import Session
from db.models import BuyRequest, Message
from sqlalchemy.orm import joinedload
from schemas.buy_request import BuyRequestCreate

def create_buy_request(db: Session, buy_request: BuyRequestCreate, user_id: int):
    db_obj = BuyRequest(**buy_request.dict(), user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_buy_requests(db: Session, skip=0, limit=10):
    return db.query(BuyRequest).options(joinedload(BuyRequest.user)).order_by(BuyRequest.created_at.desc()).offset(skip).limit(limit).all()

def get_buy_request(db: Session, id: int):
    return db.query(BuyRequest).options(joinedload(BuyRequest.user)).filter(BuyRequest.id == id).first()

def get_all_buy_requests_admin(db: Session, skip=0, limit=20, search=None):
    """管理员获取所有求购信息"""
    query = db.query(BuyRequest).options(joinedload(BuyRequest.user))
    
    if search:
        query = query.filter(
            BuyRequest.title.ilike(f"%{search}%") |
            BuyRequest.description.ilike(f"%{search}%")
        )
    
    return query.order_by(BuyRequest.created_at.desc()).offset(skip).limit(limit).all()

def delete_buy_request_admin(db: Session, buy_request_id: int):
    """管理员删除求购信息"""
    try:
        # 直接删除求购信息，相关的消息会通过级联删除自动删除
        buy_request = db.query(BuyRequest).filter(BuyRequest.id == buy_request_id).first()
        if buy_request:
            db.delete(buy_request)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"删除求购信息失败: {e}")
        return False 