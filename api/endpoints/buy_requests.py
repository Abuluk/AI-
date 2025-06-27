from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from db.session import get_db
from db.models import BuyRequest
from schemas.buy_request import BuyRequest as BuyRequestSchema, BuyRequestCreate
from crud import crud_buy_request
from core.security import get_current_user, get_current_active_user
from typing import List
import os
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=BuyRequestSchema)
def create_buy_request_api(
    buy_request: BuyRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_buy_request.create_buy_request(db, buy_request, user_id=current_user.id)

@router.get("/", response_model=List[BuyRequestSchema])
def list_buy_requests(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    brs = crud_buy_request.get_buy_requests(db, skip=skip, limit=limit)
    for br in brs:
        if br.images and isinstance(br.images, str):
            br.images = br.images.split(",")
        elif not br.images:
            br.images = []
    return brs

@router.get("/my_own", response_model=List[BuyRequestSchema])
def my_own_buy_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    brs = db.query(BuyRequest).options(joinedload(BuyRequest.user)).filter(
        BuyRequest.user_id == current_user.id
    ).order_by(BuyRequest.created_at.desc()).all()
    for br in brs:
        if br.images and isinstance(br.images, str):
            br.images = br.images.split(",")
        elif not br.images:
            br.images = []
    return brs

@router.get("/{id}", response_model=BuyRequestSchema)
def get_buy_request(id: int, db: Session = Depends(get_db)):
    buy_request = crud_buy_request.get_buy_request(db, id)
    if not buy_request:
        raise HTTPException(status_code=404, detail="Buy request not found")
    return buy_request

@router.delete("/{id}", response_model=None)
def delete_buy_request(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    buy_request = db.query(BuyRequest).filter(BuyRequest.id == id, BuyRequest.user_id == current_user.id).first()
    if not buy_request:
        raise HTTPException(status_code=404, detail="Buy request not found")
    db.delete(buy_request)
    db.commit()
    return {"msg": "deleted"}

@router.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    save_dir = os.path.join(os.getcwd(), "static", "images")
    os.makedirs(save_dir, exist_ok=True)
    file_ext = os.path.splitext(file.filename)[-1]
    save_name = f"buyreq_{int(datetime.now().timestamp())}{file_ext}"
    save_path = os.path.join(save_dir, save_name)
    with open(save_path, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/images/{save_name}"} 