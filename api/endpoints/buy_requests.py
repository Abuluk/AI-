from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.buy_request import BuyRequest, BuyRequestCreate
from crud import crud_buy_request
from core.security import get_current_user
from typing import List

router = APIRouter()

@router.post("/", response_model=BuyRequest)
def create_buy_request_api(
    buy_request: BuyRequestCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return crud_buy_request.create_buy_request(db, buy_request, user_id=current_user.id)

@router.get("/", response_model=List[BuyRequest])
def list_buy_requests(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_buy_request.get_buy_requests(db, skip=skip, limit=limit)

@router.get("/{id}", response_model=BuyRequest)
def get_buy_request(id: int, db: Session = Depends(get_db)):
    buy_request = crud_buy_request.get_buy_request(db, id)
    if not buy_request:
        raise HTTPException(status_code=404, detail="Buy request not found")
    return buy_request 