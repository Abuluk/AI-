from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form
from typing import List
from sqlalchemy.orm import Session
from db.session import get_db
from crud import crud_item
from schemas.item import ItemCreate, ItemInDB
from core.security import get_current_user
from db.models import User
import os
import uuid
from db.models import Item
from sqlalchemy import or_

router = APIRouter()

@router.post("/", response_model=ItemInDB)
async def create_item(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    location: str = Form(...),
    condition: str = Form(...),
    images: List[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 创建商品基础信息
    db_item = Item(
        title=title,
        description=description,
        price=price,
        category=category,
        location=location,
        condition=condition,
        owner_id=current_user.id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 处理图片上传
    image_paths = []
    if images:
        UPLOAD_DIR = "static/images"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        for image in images:
            # 验证文件格式
            ext = os.path.splitext(image.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext}。允许的格式: {', '.join(ALLOWED_EXTENSIONS)}")
            # 确保文件名安全
            safe_filename = f"{db_item.id}_{uuid.uuid4().hex}{os.path.splitext(image.filename)[1]}"
            # 使用正斜杠统一路径格式
            file_path = os.path.join(UPLOAD_DIR, safe_filename).replace(os.sep, '/')
            
            with open(file_path, "wb") as f:
                content = await image.read()
                f.write(content)
            
            image_paths.append(file_path)
    
    # 更新商品图片字段
    if image_paths:
        db_item.images = ",".join(image_paths)
        db.commit()
        db.refresh(db_item)
    
    return db_item

@router.get("/{item_id}", response_model=ItemInDB)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/{item_id}", response_model=ItemInDB)
def update_item(
    item_id: int,
    item_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = crud_item.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud_item.update_item(db, item_id, item_update)

@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = crud_item.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    crud_item.delete_item(db, item_id)
    return {"message": "Item deleted"}

@router.post("/{item_id}/upload-image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 确保商品存在且用户有权限
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # 保存图片
    UPLOAD_DIR = "static/images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = f"{UPLOAD_DIR}/{item_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 更新商品图片字段
    images = item.images.split(",") if item.images else []
    images.append(file_path)
    item.images = ",".join(images)
    db.commit()
    
    return {"message": "Image uploaded", "path": file_path}

# 添加搜索路由
@router.get("/search/", response_model=List[ItemInDB])
def search_items(
    q: str = Query(None, min_length=1),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if not q:
        return crud_item.get_items(db, skip, limit)
    
    return db.query(Item).filter(
        or_(
            Item.title.ilike(f"%{q}%"),
            Item.description.ilike(f"%{q}%")
        )
    ).offset(skip).limit(limit).all()