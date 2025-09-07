from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_user, get_current_user_optional
from db.models import User, Item, Feedback
from crud import crud_user_behavior, crud_ai_recommendation
from typing import Any, Dict, List, Optional
import os
import json
import base64
import hmac
import hashlib
import time
import asyncio
import websockets
import traceback
import sys
from urllib.parse import urlparse, quote_plus
from email.utils import formatdate
from datetime import datetime, timedelta
from sqlalchemy import desc, asc

router = APIRouter()

def get_available_items_for_ai(db: Session, settings: Dict[str, Any]) -> List[Item]:
    """根据配置获取AI推荐可用的商品"""
    try:
        item_selection = settings.get("item_selection", {})
        if not item_selection.get("enable_sort_filter", True) and not item_selection.get("enable_category_filter", True):
            # 如果都不启用，返回所有在售商品
            return db.query(Item).filter(
                Item.status == "online",
                Item.sold == False
            ).limit(item_selection.get("max_total_items", 100)).all()
        
        all_items = []
        used_item_ids = set()
        
        # 按排序方式获取商品
        if item_selection.get("enable_sort_filter", True):
            sort_orders = item_selection.get("sort_orders", [])
            for sort_config in sort_orders:
                if not sort_config.get("enabled", True):
                    continue
                
                field = sort_config.get("field", "price")
                order = sort_config.get("order", "asc")
                limit = sort_config.get("limit", 20)
                
                # 构建排序查询
                if order == "desc":
                    order_func = desc(getattr(Item, field))
                else:
                    order_func = asc(getattr(Item, field))
                
                items = db.query(Item).filter(
                    Item.status == "online",
                    Item.sold == False
                ).order_by(order_func).limit(limit).all()
                
                # 添加未重复的商品
                for item in items:
                    if item.id not in used_item_ids:
                        all_items.append(item)
                        used_item_ids.add(item.id)
        
        # 按分类获取商品
        if item_selection.get("enable_category_filter", True):
            category_limits = item_selection.get("category_limits", {})
            for category_id, category_config in category_limits.items():
                if not category_config.get("enabled", True):
                    continue
                
                limit = category_config.get("limit", 10)
                items = db.query(Item).filter(
                    Item.status == "online",
                    Item.sold == False,
                    Item.category == int(category_id)
                ).order_by(desc(Item.created_at)).limit(limit).all()
                
                # 添加未重复的商品
                for item in items:
                    if item.id not in used_item_ids:
                        all_items.append(item)
                        used_item_ids.add(item.id)
        
        # 限制总数量
        max_total = item_selection.get("max_total_items", 100)
        return all_items[:max_total]
        
    except Exception as e:
        print(f"获取商品选择范围失败: {e}")
        # 出错时返回默认商品
        return db.query(Item).filter(
            Item.status == "online",
            Item.sold == False
        ).limit(100).all()

async def call_xunfei_v3_chat_async(app_id, api_key, api_secret, spark_url, prompt):
    """异步调用讯飞v3.1/chat API"""
    try:
        print(f"开始调用讯飞AI，app_id: {app_id}, api_key: {api_key[:10]}..., spark_url: {spark_url}")
        
        # 生成鉴权URL
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        parsed_url = urlparse(spark_url)
        host = parsed_url.netloc
        path = parsed_url.path
        
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        
        # 构建WebSocket URL
        ws_url = f"{spark_url}?authorization={quote_plus(v['authorization'])}&date={quote_plus(v['date'])}&host={quote_plus(v['host'])}"
        print(f"WebSocket URL: {ws_url}")
        
        # 构建请求数据
        data = {
            "header": {
                "app_id": app_id,
                "uid": "12345"
            },
            "parameter": {
                "chat": {
                    "domain": "x1",
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": prompt}
                    ]
                }
            }
        }
        
        print(f"发送给AI的prompt: {prompt[:100]}...")
        result = ""
        
        # 异步WebSocket连接，设置10分钟超时
        async with websockets.connect(ws_url, ping_interval=None, ping_timeout=None) as websocket:
            print("WebSocket连接成功，开始发送数据...")
            # 发送数据
            await websocket.send(json.dumps(data))
            
            # 接收响应，设置10分钟超时
            try:
                async with asyncio.timeout(600):  # 10分钟超时
                    while True:
                        response = await websocket.recv()
                        response_data = json.loads(response)
                        print(f"收到AI响应: {response_data}")
                        
                        # 检查响应状态
                        if response_data.get("header", {}).get("code") != 0:
                            raise Exception(f"API错误: {response_data.get('header', {}).get('message', '未知错误')}")
                        
                        # 提取文本内容
                        if "payload" in response_data and "choices" in response_data["payload"]:
                            choices = response_data["payload"]["choices"]
                            if "text" in choices and len(choices["text"]) > 0:
                                text_item = choices["text"][0]
                                # 尝试获取content或reasoning_content
                                content = text_item.get("content", "") or text_item.get("reasoning_content", "")
                                result += content
                        
                        # 检查是否结束
                        if response_data.get("header", {}).get("status") == 2:
                            break
                            
            except asyncio.TimeoutError:
                raise Exception("AI响应超时（10分钟）")
        
        print(f"AI调用成功，结果长度: {len(result)}")
        return result
        
    except Exception as e:
        print(f"AI调用异常: {e}")
        traceback.print_exc(file=sys.stdout)
        raise Exception(f"AI调用失败: {str(e)}")

@router.get("/recommendations", response_model=Dict[str, Any])
def get_ai_recommendations(
    limit: int = Query(10, ge=1, le=20, description="推荐商品数量"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """获取AI智能推荐商品列表 - 基于用户浏览行为序列"""
    try:
        # 获取AI推荐配置
        settings = crud_ai_recommendation.get_ai_recommendation_settings(db)
        
        if not settings.get("enable_ai_analysis", True):
            # 如果AI分析被禁用，返回基础推荐
            return get_basic_recommendations(db, limit)
        
        # 如果用户未登录，返回热门商品推荐
        if not current_user:
            return get_basic_recommendations(db, limit)
        
        # 获取用户行为序列
        behavior_sequence = crud_user_behavior.get_user_behavior_sequence(
            db, current_user.id, 
            limit=settings.get("sequence_length", 10),
            days=settings.get("behavior_days", 30)
        )
        
        # 如果用户行为数据不足，返回基础推荐
        if len(behavior_sequence) < settings.get("min_behavior_count", 3):
            return get_basic_recommendations(db, limit)
        
        # 基于用户行为序列进行AI分析推荐
        import asyncio
        ai_recommendations = asyncio.run(analyze_user_behavior_and_recommend(
            db, behavior_sequence, settings, limit
        ))
        
        return ai_recommendations
        
    except Exception as e:
        print(f"获取AI推荐失败: {e}")
        traceback.print_exc()
        # 返回基础推荐作为备用
        return get_basic_recommendations(db, limit)

def get_basic_recommendations(db: Session, limit: int) -> Dict[str, Any]:
    """获取基础推荐商品（热门商品）"""
    try:
        # 获取热门商品作为推荐
        recommended_items = db.query(Item).filter(
            Item.status == "online",
            Item.sold == False
        ).order_by(Item.views.desc(), Item.like_count.desc()).limit(limit).all()
        
        # 转换为字典格式
        result = []
        for item in recommended_items:
            # 处理图片路径
            processed_images = []
            if item.images:
                images = item.images.split(',')
                for img in images:
                    img = img.strip()
                    if img:
                        from config import get_full_image_url
                        full_url = get_full_image_url(img)
                        if full_url:
                            processed_images.append(full_url)
            
            result.append({
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "category": item.category,
                "condition": item.condition,
                "location": item.location,
                "like_count": item.like_count,
                "views": item.views,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "image_urls": processed_images,
                "ai_reason": "热门商品推荐"
            })
        
        return {
            "success": True,
            "recommendations": result,
            "analysis": "基于热门商品的基础推荐",
            "market_insights": "为您推荐当前最受欢迎的商品",
            "recommendation_type": "basic"
        }
        
    except Exception as e:
        print(f"获取基础推荐失败: {e}")
        return {
            "success": False,
            "recommendations": [],
            "analysis": None,
            "market_insights": None,
            "message": "推荐服务暂时不可用",
            "recommendation_type": "fallback"
        }

async def analyze_user_behavior_and_recommend(
    db: Session, 
    behavior_sequence: List[Dict[str, Any]], 
    settings: Dict[str, Any],
    limit: int
) -> Dict[str, Any]:
    """基于用户行为序列进行AI分析推荐"""
    try:
        # 构建AI分析prompt
        sequence_text = "\n".join([
            f"- {item['title']} (分类: {item['category']}, 价格: ¥{item['price']}, 行为: {item['behavior_type']})"
            for item in behavior_sequence[:10]  # 只取前10个
        ])
        
        # 根据配置获取商品选择范围
        available_items = get_available_items_for_ai(db, settings)
        
        items_text = "\n".join([
            f"- {item.title} (分类: {item.category}, 价格: ¥{item.price}, 成色: {item.condition})"
            for item in available_items
        ])
        
        prompt = f"""作为一位专业的商品推荐专家，请基于用户的浏览行为序列，从当前在售商品中推荐最合适的商品。

用户浏览行为序列（按时间倒序）：
{sequence_text}

当前在售商品（部分）：
{items_text}

请分析用户的兴趣偏好，包括：
1. 偏好的商品分类
2. 价格区间偏好
3. 商品成色偏好
4. 浏览模式分析

然后从在售商品中选择{limit}个最符合用户偏好的商品进行推荐。

请以JSON格式返回结果：
{{
    "analysis": "用户偏好分析（100字以内）",
    "market_insights": "市场洞察和建议（50字以内）",
    "recommendations": [
        {{
            "item_id": 商品ID,
            "reason": "推荐理由（20字以内）"
        }}
    ]
}}

请确保推荐的商品ID在提供的在售商品列表中。"""

        # 调用AI分析
        app_id = os.getenv("XUNFEI_APP_ID")
        api_key = os.getenv("XUNFEI_API_KEY")
        api_secret = os.getenv("XUNFEI_API_SECRET")
        spark_url = os.getenv("XUNFEI_SPARK_URL")
        
        if not all([app_id, api_key, api_secret, spark_url]):
            raise Exception("AI配置不完整")
        
        ai_result = await call_xunfei_v3_chat_async(app_id, api_key, api_secret, spark_url, prompt)
        
        # 解析AI返回结果
        try:
            # 尝试从AI返回的文本中提取JSON
            import re
            json_match = re.search(r'\{.*\}', ai_result, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
            else:
                raise Exception("无法解析AI返回的JSON")
        except:
            # 如果解析失败，使用基础推荐
            return get_basic_recommendations(db, limit)
        
        # 获取推荐的商品详情
        recommended_items = []
        for rec in ai_data.get("recommendations", []):
            item_id = rec.get("item_id")
            if item_id:
                # 尝试将字符串ID转换为整数
                try:
                    item_id = int(item_id)
                except (ValueError, TypeError):
                    # 如果转换失败，尝试通过商品名称查找
                    item_name = str(item_id)
                    item = db.query(Item).filter(Item.title == item_name).first()
                    if not item:
                        continue
                else:
                    item = db.query(Item).filter(Item.id == item_id).first()
                
                if item:
                    # 处理图片路径
                    processed_images = []
                    if item.images:
                        images = item.images.split(',')
                        for img in images:
                            img = img.strip()
                            if img:
                                from config import get_full_image_url
                                full_url = get_full_image_url(img)
                                if full_url:
                                    processed_images.append(full_url)
                    
                    recommended_items.append({
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "price": item.price,
                        "category": item.category,
                        "condition": item.condition,
                        "location": item.location,
                        "like_count": item.like_count,
                        "views": item.views,
                        "created_at": item.created_at.isoformat() if item.created_at else None,
                        "image_urls": processed_images,
                        "ai_reason": rec.get("reason", "AI智能推荐")
                    })
        
        return {
            "success": True,
            "recommendations": recommended_items,
            "analysis": ai_data.get("analysis", "基于您的浏览行为进行智能推荐"),
            "market_insights": ai_data.get("market_insights", "为您推荐最符合偏好的商品"),
            "recommendation_type": "ai_behavior_based"
        }
        
    except Exception as e:
        print(f"AI行为分析推荐失败: {e}")
        traceback.print_exc()
        return get_basic_recommendations(db, limit)

@router.post("/record-behavior")
def record_user_behavior(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """记录用户行为"""
    try:
        behavior_type = request.get("behavior_type")
        item_id = request.get("item_id")
        behavior_data = request.get("behavior_data")
        
        if not behavior_type:
            raise HTTPException(status_code=422, detail="behavior_type is required")
        
        behavior = crud_user_behavior.create_user_behavior(
            db=db,
            user_id=current_user.id,
            behavior_type=behavior_type,
            item_id=item_id,
            behavior_data=behavior_data
        )
        
        return {
            "success": True,
            "behavior_id": behavior.id,
            "message": "行为记录成功"
        }
    except Exception as e:
        print(f"记录用户行为失败: {e}")
        raise HTTPException(status_code=500, detail="记录行为失败")

@router.get("/behavior-stats")
def get_user_behavior_stats(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户行为统计"""
    try:
        stats = crud_user_behavior.get_user_behavior_stats(db, current_user.id, days)
        return {
            "success": True,
            "stats": stats,
            "period_days": days
        }
    except Exception as e:
        print(f"获取行为统计失败: {e}")
        raise HTTPException(status_code=500, detail="获取统计失败")

@router.post("/", response_model=Dict[str, Any])
def ai_strategy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="无权限")
    
    try:
        print("开始AI策略分析...")
        
        # 获取数据
        users = db.query(User).all()
        items = db.query(Item).filter(Item.status == 'online').all()
        feedbacks = db.query(Feedback).all()
        
        print(f"获取到数据: 用户{len(users)}个, 在售商品{len(items)}个, 反馈{len(feedbacks)}条")
        
        # 组装prompt
        user_count = len(users)
        item_count = len(items)
        feedback_count = len(feedbacks)
        
        # 获取一些示例数据
        sample_users = [u.username for u in users[:5]]
        sample_items = [i.title for i in items[:5]]
        sample_feedbacks = [f.content for f in feedbacks[:5]]
        
        prompt = f"""作为一位电商平台运营专家，请基于以下数据生成一份详细的运营分析报告：

平台数据概览：
- 用户总数：{user_count}人
- 在售商品数：{item_count}个
- 用户反馈：{feedback_count}条

示例用户：{', '.join(sample_users) if sample_users else '暂无'}
示例在售商品：{', '.join(sample_items) if sample_items else '暂无'}
示例反馈：{', '.join(sample_feedbacks) if sample_feedbacks else '暂无'}

请从以下角度进行分析：
1. 平台现状分析
2. 用户行为分析
3. 商品结构分析
4. 用户满意度分析
5. 运营建议和改进方向
6. 未来发展规划

请提供具体、可操作的建议，报告要详细且专业。"""

        # 获取环境变量
        app_id = os.getenv("XUNFEI_V3_APP_ID")
        api_key = os.getenv("XUNFEI_V3_API_KEY")
        api_secret = os.getenv("XUNFEI_V3_API_SECRET")
        spark_url = os.getenv("XUNFEI_V3_SPARK_URL")
        
        print(f"环境变量检查: app_id={app_id}, api_key={api_key[:10] if api_key else None}..., api_secret={'已设置' if api_secret else '未设置'}, spark_url={spark_url}")
        
        if not all([app_id, api_key, api_secret, spark_url]):
            raise HTTPException(status_code=500, detail="AI配置不完整，请检查环境变量")
        
        # 使用asyncio.run调用异步AI函数
        print("开始调用AI...")
        ai_result = asyncio.run(call_xunfei_v3_chat_async(app_id, api_key, api_secret, spark_url, prompt))
        
        print("AI调用完成，返回结果")
        return {
            "report": ai_result,
            "data_summary": {
                "user_count": user_count,
                "item_count": item_count,
                "feedback_count": feedback_count
            }
        }
        
    except Exception as e:
        print(f"AI策略接口异常: {e}")
        traceback.print_exc(file=sys.stdout)
        raise HTTPException(status_code=500, detail=f"AI策略生成失败: {str(e)}") 