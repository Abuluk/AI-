from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Form, BackgroundTasks
from typing import List, Optional
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
from core.spark_ai import spark_ai_service

router = APIRouter()

# 公共端点 - 获取所有商品（无需认证）
@router.get("", response_model=List[ItemInDB])
def get_all_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    order_by: str = Query("created_at_desc", description="排序方式: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎)"),
    category: Optional[int] = Query(None, description="商品分类ID"),
    db: Session = Depends(get_db)
):
    """获取所有在售商品列表，支持分页和排序（只显示状态为online的商品）"""
    query = db.query(Item).filter(
        Item.status == "online",  # 只显示上架的商品
        Item.sold == False        # 不显示已售出的商品
    )
    if category is not None:
        query = query.filter(Item.category == category)
    # 根据排序参数进行排序
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        # 默认按最新发布排序
        query = query.order_by(Item.created_at.desc())
    return query.offset(skip).limit(limit).all()

# 公共端点 - 搜索商品（无需认证）- 必须在/{item_id}之前定义
@router.get("/search", response_model=List[ItemInDB])
def search_items(
    q: str = Query(None, min_length=1),
    skip: int = 0,
    limit: int = 100,
    order_by: str = Query("created_at_desc", description="排序方式: created_at_desc(最新发布), price_asc(价格从低到高), price_desc(价格从高到低), views_desc(最受欢迎)"),
    db: Session = Depends(get_db)
):
    if not q:
        # 如果没有搜索关键词，返回所有在售商品
        query = db.query(Item).filter(
            Item.status == "online",  # 只显示上架的商品
            Item.sold == False        # 不显示已售出的商品
        )
    else:
        # 搜索在售商品
        query = db.query(Item).filter(
            or_(
                Item.title.ilike(f"%{q}%"),
                Item.description.ilike(f"%{q}%")
            ),
            Item.status == "online",  # 只显示上架的商品
            Item.sold == False        # 不显示已售出的商品
        )
    
    # 根据排序参数进行排序
    if order_by == "created_at_desc":
        query = query.order_by(Item.created_at.desc())
    elif order_by == "price_asc":
        query = query.order_by(Item.price.asc())
    elif order_by == "price_desc":
        query = query.order_by(Item.price.desc())
    elif order_by == "views_desc":
        query = query.order_by(Item.views.desc())
    else:
        # 默认按最新发布排序
        query = query.order_by(Item.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

# 公共端点 - 获取AI分析的低价好物推荐
@router.get("/ai-cheap-deals")
def get_ai_cheap_deals(
    limit: int = Query(10, ge=1, le=20, description="获取商品数量"),
    db: Session = Depends(get_db)
):
    """获取AI分析的低价好物推荐"""
    try:
        # 获取当前在售的商品
        items = db.query(Item).filter(
            Item.status == "online",
            Item.sold == False
        ).order_by(Item.price.asc()).limit(limit).all()
        
        # 转换为字典格式
        items_data = []
        for item in items:
            items_data.append({
                "id": item.id,
                "title": item.title,
                "price": float(item.price),
                "condition": item.condition,
                "description": item.description,
                "category": item.category,
                "location": item.location,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "user": {
                    "id": item.owner_id,
                    "username": item.owner.username if item.owner else "未知用户"
                } if item.owner else None
            })
        
        # 调用AI服务进行分析
        ai_result = spark_ai_service.analyze_price_competition(items_data)
        
        if ai_result.get("success"):
            # 将AI推荐的商品与数据库中的商品信息合并
            recommendations = ai_result.get("recommendations", [])
            enhanced_recommendations = []
            
            for rec in recommendations:
                # 在数据库中找到对应的商品
                matching_item = next(
                    (item for item in items_data if item["title"] == rec["title"]), 
                    None
                )
                
                if matching_item:
                    enhanced_recommendations.append({
                        **matching_item,
                        "ai_reason": rec.get("reason", ""),
                        "ai_price": rec.get("price", matching_item["price"])
                    })
            
            return {
                "success": True,
                "analysis": ai_result.get("analysis", ""),
                "market_insights": ai_result.get("market_insights", ""),
                "recommendations": enhanced_recommendations,
                "total_items_analyzed": len(items_data)
            }
        else:
            # 如果AI服务失败，返回简单的低价商品列表
            return {
                "success": False,
                "message": ai_result.get("message", "AI分析服务暂时不可用"),
                "fallback_recommendations": items_data[:5],  # 返回前5个最低价的商品
                "total_items_analyzed": len(items_data)
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取AI推荐失败: {str(e)}"
        )

# 公共端点 - 获取单个商品（无需认证）
@router.get("/{item_id}", response_model=ItemInDB)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# 需要认证的端点
@router.post("", response_model=ItemInDB)
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

@router.patch("/{item_id}/status")
def update_item_status(
    item_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商品状态：online(上架) 或 offline(下架)"""
    # 验证商品存在
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 验证用户权限
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此商品")
    
    # 验证状态值
    if status not in ["online", "offline"]:
        raise HTTPException(status_code=400, detail="状态值无效，只能是 'online' 或 'offline'")
    
    # 更新状态
    item.status = status
    db.commit()
    db.refresh(item)
    
    return {"message": f"商品已{'上架' if status == 'online' else '下架'}", "item": item}

@router.patch("/{item_id}/views")
def update_item_views(
    item_id: int,
    db: Session = Depends(get_db)
):
    """更新商品浏览量"""
    # 验证商品存在
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    
    # 更新浏览量
    item.views += 1
    db.commit()
    db.refresh(item)
    
    return {"message": "浏览量已更新", "views": item.views}

@router.patch("/{item_id}/sold")
def mark_item_sold(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """将商品标记为已售"""
    item = crud_item.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")
    if item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此商品")
    if item.sold:
        return {"message": "商品已售出"}
    item.sold = True
    db.commit()
    db.refresh(item)
    return {"message": "商品已标记为已售", "item": item}

# AI自动补全商品信息（图片识别）
@router.post("/ai-auto-complete")
async def ai_auto_complete_item_by_image(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    上传图片，AI自动补全商品信息，支持单文件和多文件
    """
    try:
        image_bytes_list = []
        if files:
            image_bytes_list = [await f.read() for f in files]
        elif file:
            image_bytes_list = [await file.read()]
        else:
            return {"success": False, "message": "未收到图片"}
        result = spark_ai_service.auto_complete_item_by_image(image_bytes_list)
        return result
    except Exception as e:
        return {"success": False, "message": f"AI自动补全失败: {str(e)}"}

@router.post("/ai-auto-complete-ws")
async def ai_auto_complete_item_by_image_ws(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    使用websockets库异步方式调用讯飞图片理解API，测试兼容性
    """
    image_bytes_list = []
    if files:
        image_bytes_list = [await f.read() for f in files]
    elif file:
        image_bytes_list = [await file.read()]
    else:
        return {"success": False, "message": "未收到图片"}
    result = await spark_ai_service.auto_complete_item_by_image_ws(image_bytes_list)
    return result