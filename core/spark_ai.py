import json
import time
import hmac
import base64
import hashlib
import websocket
import threading
from urllib.parse import urlparse, quote_plus
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config import settings
import os
from email.utils import formatdate

class SparkAIService:
    def __init__(self):
        # 初始化时不立即获取配置，而是在需要时动态获取
        pass
        
    def _get_config(self):
        """动态获取配置"""
        return {
            'app_id': os.getenv("XUNFEI_APP_ID", ""),
            'api_key': os.getenv("XUNFEI_API_KEY", ""),
            'api_secret': os.getenv("XUNFEI_API_SECRET", ""),
            'spark_url': os.getenv("XUNFEI_SPARK_URL", "wss://spark-api.xf-yun.com/v1/x1")
        }
        
    def _create_url(self) -> str:
        """生成鉴权url"""
        config = self._get_config()
        api_key = config['api_key']
        api_secret = config['api_secret']
        spark_url = config['spark_url']
        
        # 用标准库生成HTTP时间戳
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        
        # 解析URL
        parsed_url = urlparse(spark_url)
        host = parsed_url.netloc
        path = parsed_url.path
        
        # 拼接字符串
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        
        # 使用hmac-sha256进行加密
        signature_sha = hmac.new(
            api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        # URL参数必须URL编码
        url = f"{spark_url}?authorization={quote_plus(authorization)}&date={quote_plus(date)}&host={quote_plus(host)}"
        return url, date, host, authorization
    
    def _create_message(self, content: str) -> Dict[str, Any]:
        """创建消息格式"""
        config = self._get_config()
        return {
            "header": {
                "app_id": config['app_id'],
                "uid": "12345"
            },
            "parameter": {
                "chat": {
                    "domain": "x1",
                    "temperature": 0.5,
                    "max_tokens": 2048
                }
            },
            "payload": {
                "message": {
                    "text": [
                        {"role": "user", "content": content}
                    ]
                }
            }
        }
    
    def analyze_price_competition(self, current_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析当前网站商品的价格竞争力，并推荐最低价的竞品
        
        Args:
            current_items: 当前网站的商品列表
            
        Returns:
            包含分析结果的字典
        """
        if not current_items:
            return {
                "success": False,
                "message": "没有商品数据可供分析",
                "recommendations": []
            }
        
        # 构建商品信息字符串
        items_info = []
        for item in current_items:
            items_info.append(f"商品：{item.get('title', '未知')}，价格：¥{item.get('price', 0)}，状态：{item.get('condition', '未知')}")
        
        items_text = "\n".join(items_info)
        
        # 构建提示词
        prompt = f"""
        请分析以下校园二手交易平台的商品价格竞争力，并推荐当前网站价格最低的竞品：

        当前网站商品列表：
        {items_text}

        请按照以下格式返回JSON结果：
        {{
            "analysis": "价格竞争力分析",
            "lowest_price_items": [
                {{
                    "title": "商品标题",
                    "price": 价格,
                    "reason": "推荐理由"
                }}
            ],
            "market_insights": "市场洞察和建议"
        }}

        要求：
        1. 分析当前商品的价格是否具有竞争力
        2. 从当前商品中挑选出价格最低且性价比最高的商品
        3. 提供市场洞察和购买建议
        4. 只返回JSON格式，不要其他文字
        """
        
        try:
            result = self._call_spark_api(prompt)
            if result.get("success"):
                # 解析AI返回的JSON
                ai_response = result.get("response", "")
                try:
                    # 尝试从AI响应中提取JSON
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = ai_response[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        return {
                            "success": True,
                            "analysis": parsed_result.get("analysis", ""),
                            "recommendations": parsed_result.get("lowest_price_items", []),
                            "market_insights": parsed_result.get("market_insights", "")
                        }
                    else:
                        return {
                            "success": False,
                            "message": "AI响应格式错误",
                            "recommendations": []
                        }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "message": "无法解析AI响应",
                        "recommendations": []
                    }
            else:
                return result
        except Exception as e:
            return {
                "success": False,
                "message": f"调用AI服务失败: {str(e)}",
                "recommendations": []
            }
    
    def _call_spark_api(self, content: str) -> Dict[str, Any]:
        """调用星火大模型API"""
        config = self._get_config()
        app_id = config['app_id']
        api_key = config['api_key']
        api_secret = config['api_secret']
        spark_url = config['spark_url']
        if not all([app_id, api_key, api_secret]):
            return {
                "success": False,
                "message": "星火大模型配置不完整，请检查环境变量"
            }
        
        url, date, host, authorization = self._create_url()
        message = self._create_message(content)
        
        response_text = ""
        success = False
        error_message = ""
        
        headers = [
            f"Host: {host}",
            f"Date: {date}",
            f"Authorization: {authorization}"
        ]
        
        def on_message(ws, message):
            nonlocal response_text, success, error_message
            try:
                data = json.loads(message)
                code = data['header']['code']
                if code != 0:
                    error_message = f"请求错误: {data['header']['message']}"
                    ws.close()
                    return

                # 健壮解析choices/text/content
                choices = data.get('payload', {}).get('choices', {})
                text_list = choices.get('text', [])
                if text_list and isinstance(text_list, list):
                    for t in text_list:
                        if 'content' in t:
                            response_text += t['content']
                else:
                    error_message = "AI响应格式错误：未找到content"
                    ws.close()
                    return

                status = choices.get('status')
                if status == 2:
                    success = True
                    ws.close()
            except Exception as e:
                error_message = f"解析响应失败: {str(e)}"
                ws.close()
        
        def on_error(ws, error):
            nonlocal error_message
            error_message = f"WebSocket错误: {str(error)}"
        
        def on_close(ws, close_status_code, close_msg):
            pass
        
        def on_open(ws):
            ws.send(json.dumps(message))
        
        try:
            ws = websocket.WebSocketApp(
                url,
                header=headers,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            
            # 用线程+join方式实现超时控制
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.start()
            ws_thread.join(timeout=30)
            if ws_thread.is_alive():
                try:
                    ws.close()
                except Exception:
                    pass
                error_message = error_message or "请求超时"
            if success:
                return {
                    "success": True,
                    "response": response_text
                }
            else:
                return {
                    "success": False,
                    "message": error_message or "请求超时"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"连接失败: {str(e)}"
            }

# 创建全局实例
spark_ai_service = SparkAIService() 