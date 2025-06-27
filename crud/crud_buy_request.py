from sqlalchemy.orm import Session
from db.models import BuyRequest, Message
from sqlalchemy.orm import joinedload
from schemas.buy_request import BuyRequestCreate

def create_buy_request(db: Session, buy_request: BuyRequestCreate, user_id: int):
    images = ",".join(buy_request.images) if getattr(buy_request, 'images', None) else None
    db_obj = BuyRequest(
        title=buy_request.title,
        description=buy_request.description,
        budget=buy_request.budget,
        user_id=user_id,
        images=images
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    if db_obj.images:
        db_obj.images = db_obj.images.split(",")
    else:
        db_obj.images = []
    return db_obj

def get_buy_requests(db: Session, skip=0, limit=10):
    brs = db.query(BuyRequest).options(joinedload(BuyRequest.user)).order_by(BuyRequest.created_at.desc()).offset(skip).limit(limit).all()
    for br in brs:
        if br.images:
            br.images = br.images.split(",")
        else:
            br.images = []
    return brs

def get_buy_request(db: Session, id: int):
    br = db.query(BuyRequest).options(joinedload(BuyRequest.user)).filter(BuyRequest.id == id).first()
    if br and br.images:
        br.images = br.images.split(",")
    elif br:
        br.images = []
    return br

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