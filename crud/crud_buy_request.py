from sqlalchemy.orm import Session
from db.models import BuyRequest
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