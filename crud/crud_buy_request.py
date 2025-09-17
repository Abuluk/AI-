from sqlalchemy.orm import Session
from db.models import BuyRequest, Message, BuyRequestLike, User
from sqlalchemy.orm import joinedload
from schemas.buy_request import BuyRequestCreate
from crud.crud_message import create_system_message

def create_buy_request(db: Session, buy_request: BuyRequestCreate, user_id: int):
    images = ",".join(buy_request.images) if getattr(buy_request, 'images', None) else None
    db_obj = BuyRequest(
        title=buy_request.title,
        description=buy_request.description,
        budget=buy_request.budget,
        category=buy_request.category,
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

def get_buy_requests(db: Session, skip=0, limit=10, user_id=None, category=None):
    query = db.query(BuyRequest).options(joinedload(BuyRequest.user))
    
    # 如果指定了user_id，则过滤该用户的求购信息
    if user_id is not None:
        query = query.filter(BuyRequest.user_id == user_id)
    
    # 如果指定了category，则过滤该分类的求购信息
    if category is not None:
        query = query.filter(BuyRequest.category == category)
    
    brs = query.order_by(BuyRequest.created_at.desc()).offset(skip).limit(limit).all()
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

def like_buy_request(db: Session, buy_request_id: int, user_id: int) -> int:
    exists = db.query(BuyRequestLike).filter_by(buy_request_id=buy_request_id, user_id=user_id).first()
    if exists:
        return -1
    db.add(BuyRequestLike(buy_request_id=buy_request_id, user_id=user_id))
    br = db.query(BuyRequest).filter_by(id=buy_request_id).first()
    if br:
        br.like_count += 1
        # 生成系统消息
        owner_id = br.user_id
        user = db.query(User).filter_by(id=user_id).first()
        if owner_id and user and owner_id != user_id:
            content = f"用户{user.username}点赞了你的求购《{br.title}》"
            from schemas.message import SystemMessageCreate
            msg = SystemMessageCreate(content=content, title="求购被点赞", target_users=str(owner_id), buy_request_id=buy_request_id)
            create_system_message(db, msg, admin_id=user_id)
    db.commit()
    return br.like_count if br else 0

def unlike_buy_request(db: Session, buy_request_id: int, user_id: int) -> int:
    like = db.query(BuyRequestLike).filter_by(buy_request_id=buy_request_id, user_id=user_id).first()
    if not like:
        return -1
    db.delete(like)
    br = db.query(BuyRequest).filter_by(id=buy_request_id).first()
    if br and br.like_count > 0:
        br.like_count -= 1
    db.commit()
    return br.like_count if br else 0 