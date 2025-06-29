from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_db
from core.security import get_current_user
from db.models import User, Item, Feedback
from typing import Any, Dict
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

router = APIRouter()

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
                    "domain": "generalv3",
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
                            if "text" in choices:
                                result += choices["text"][0]["content"]
                        
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
        items = db.query(Item).all()
        feedbacks = db.query(Feedback).all()
        
        print(f"获取到数据: 用户{len(users)}个, 商品{len(items)}个, 反馈{len(feedbacks)}条")
        
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
- 商品总数：{item_count}个
- 用户反馈：{feedback_count}条

示例用户：{', '.join(sample_users) if sample_users else '暂无'}
示例商品：{', '.join(sample_items) if sample_items else '暂无'}
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