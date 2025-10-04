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
import asyncio
import websockets

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
    
    async def _call_spark_api_async(self, content: str) -> Dict[str, Any]:
        """异步调用星火大模型API"""
        config = self._get_config()
        app_id = config['app_id']
        api_key = config['api_key']
        api_secret = config['api_secret']
        spark_url = config['spark_url']
        if not all([app_id, api_key, api_secret]):
            return {
                "success": False,
                "message": "大模型配置不完整，请检查环境变量"
            }
        
        url, date, host, authorization = self._create_url()
        message = self._create_message(content)
        
        response_text = ""
        success = False
        error_message = ""
        
        headers = {
            "Host": host,
            "Date": date,
            "authorization": authorization
        }
        
        try:
            async with websockets.connect(url, extra_headers=headers, timeout=30) as websocket:
                print("WebSocket已连接，发送消息...")
                await websocket.send(json.dumps(message, ensure_ascii=False))
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        code = data['header']['code']
                        if code != 0:
                            error_message = f"请求错误: {data['header']['message']}"
                            break

                        # 健壮解析choices/text/content
                        choices = data.get('payload', {}).get('choices', {})
                        text_list = choices.get('text', [])
                        if text_list and isinstance(text_list, list):
                            for t in text_list:
                                if 'content' in t:
                                    if isinstance(t['content'], str):
                                        response_text += t['content']
                                    elif isinstance(t['content'], list):
                                        response_text += ''.join([item for item in t['content'] if isinstance(item, str)])
                        else:
                            error_message = "AI响应格式错误：未找到content"
                            break

                        status = choices.get('status')
                        if status == 2:
                            success = True
                            break
                    except Exception as e:
                        error_message = f"解析响应失败: {str(e)}"
                        break
                
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

    def _call_spark_api(self, content: str) -> Dict[str, Any]:
        """同步调用星火大模型API（保持向后兼容）"""
        import asyncio
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果当前在事件循环中，使用线程池执行异步函数
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._call_spark_api_async(content))
                    return future.result(timeout=35)
            else:
                # 如果没有事件循环，直接运行
                return asyncio.run(self._call_spark_api_async(content))
        except Exception as e:
            return {
                "success": False,
                "message": f"调用失败: {str(e)}"
            }

    def auto_complete_item_by_image(self, image_bytes_list: list) -> dict:
        """
        通过图片调用星火大模型自动补全商品信息，支持多图片
        Args:
            image_bytes_list: 图片的二进制内容列表
        Returns:
            dict: 包含AI识别的商品标题、描述、类别、状态等
        """
        config = self._get_config()
        app_id = config['app_id']
        api_key = config['api_key']
        api_secret = config['api_secret']
        spark_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"
        if not all([app_id, api_key, api_secret]):
            return {"success": False, "message": "星火大模型配置不完整，请检查环境变量"}

        def create_url():
            from email.utils import formatdate
            from urllib.parse import urlparse, quote_plus
            import base64, hmac, hashlib
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
            url = f"{spark_url}?authorization={quote_plus(authorization)}&date={quote_plus(date)}&host={quote_plus(host)}"
            return url, date, host, authorization

        url, date, host, authorization = create_url()
        import base64
        
        # 限制图片数量为1~4
        if not (1 <= len(image_bytes_list) <= 4):
            return {"success": False, "message": "图片数量必须为1~4张"}
        
        # 将图片转换为base64，确保没有换行符
        image_b64_list = []
        for img in image_bytes_list:
            b64 = base64.b64encode(img).decode('utf-8')
            # 移除所有换行符和回车符
            b64 = b64.replace('\n', '').replace('\r', '')
            image_b64_list.append(b64)
        
        print("上传图片数量：", len(image_b64_list))
        for idx, b64 in enumerate(image_b64_list):
            print(f"图片{idx+1} base64长度：", len(b64))
        
        # 构建详细的提示词，指导AI识别商品信息
        prompt = """请仔细分析这些二手商品图片，以二手卖家的身份识别商品信息，并按照以下JSON格式返回：

{
    "title": "商品标题（简洁明了，突出商品特点和二手属性）",
    "description": "二手商品描述（以卖家口吻描述：品牌、型号、购买时间、使用情况、成色、是否有瑕疵、为什么出售等）",
    "category": "商品分类ID（1:手机数码, 2:电脑办公, 3:家用电器, 4:服装鞋包, 5:美妆护肤, 6:图书文娱, 7:运动户外, 8:家居家装）",
    "condition": "商品状态（new:全新, like_new:几乎全新, good:轻微使用痕迹, fair:使用痕迹明显）",
    "price_suggestion": "建议价格范围（如：100-200元）"
}

要求：
1. 仔细观察图片中的商品外观、品牌标识、型号信息、使用痕迹
2. 根据商品的新旧程度和磨损情况判断condition
3. 根据商品类型选择合适的category
4. 标题要体现二手属性，如"二手iPhone 13"、"九成新MacBook"等
5. 描述要以二手卖家的口吻，包含：
   - 品牌型号
   - 购买时间或使用时长
   - 成色描述（几成新）
   - 是否有磕碰、划痕等瑕疵
   - 功能是否正常
   - 为什么出售（如：换新、闲置等）
   - 配件情况（原装充电器、包装盒等）
6. 只返回JSON格式，不要其他文字
7. 如果无法识别某些信息，相应字段填写"未知"
8. 描述要真实、诚恳，符合二手交易的特点
"""
        
        # 构建符合讯飞API文档的消息体
        # 首先添加图片（每个图片为一个独立元素，content_type为image）
        text_array = []
        for b64 in image_b64_list:
            text_array.append({
                "role": "user",
                "content": b64,
                "content_type": "image"
            })
        # 最后添加文本问题（content_type为text）
        text_array.append({
            "role": "user",
            "content": prompt,
            "content_type": "text"
        })
        # 日志打印最终text数组内容
        print("最终发送给讯飞的text数组：", json.dumps(text_array, ensure_ascii=False, indent=2))
        message = {
            "header": {
                "app_id": app_id,
                "uid": "12345"
            },
            "parameter": {
                "chat": {
                    "domain": "imagev3",  # 使用高级版以获得更好的效果
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2048,
                    "chat_id": "auto_complete_" + str(int(time.time()))
                }
            },
            "payload": {
                "message": {
                    "text": text_array
                }
            }
        }
        
        print("发送给讯飞的消息体结构：", json.dumps(message, ensure_ascii=False, indent=2)[:1000])
        print("准备连接讯飞WebSocket...")
        
        full_response = ""
        success = False
        error_message = ""
        
        headers = [
            f"Host: {host}",
            f"Date: {date}",
            f"authorization: {authorization}"
        ]
        
        def on_message(ws, message):
            nonlocal full_response, success, error_message
            try:
                data = json.loads(message)
                print(f"收到讯飞响应：{json.dumps(data, ensure_ascii=False, indent=2)}")
                
                # 检查响应状态
                if data.get("header", {}).get("code") != 0:
                    print(f"讯飞API返回错误：{data}")
                    error_message = f"讯飞API错误：{data.get('header', {}).get('message', '未知错误')}"
                    ws.close()
                    return
                
                # 提取文本内容
                if "payload" in data and "choices" in data["payload"]:
                    choices = data["payload"]["choices"]
                    if "text" in choices and choices["text"]:
                        for text_item in choices["text"]:
                            if "content" in text_item:
                                content = text_item["content"]
                                if isinstance(content, str):
                                    full_response += content
                                elif isinstance(content, list):
                                    full_response += ''.join([item for item in content if isinstance(item, str)])
                
                # 检查是否完成
                if data.get("header", {}).get("status") == 2:
                    print(f"讯飞响应完成，完整响应：{full_response}")
                    success = True
                    ws.close()
                    
            except json.JSONDecodeError as e:
                print(f"解析讯飞响应JSON失败：{e}")
                error_message = f"解析响应失败: {str(e)}"
                ws.close()
            except Exception as e:
                print(f"处理讯飞响应时出错：{e}")
                error_message = f"处理响应失败: {str(e)}"
                ws.close()
        
        def on_error(ws, error):
            nonlocal error_message
            error_message = f"WebSocket错误: {str(error)}"
            print("WebSocket错误：", error)
        
        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket连接关闭：{close_status_code} - {close_msg}")
        
        def on_open(ws):
            print("WebSocket已连接，发送消息...")
            ws.send(json.dumps(message, ensure_ascii=False))
        
        try:
            ws = websocket.WebSocketApp(
                url,
                header=headers,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
                on_open=on_open
            )
            print("WebSocketApp已创建，开始run_forever...")
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
                # 打印AI原始返回内容
                print("AI原始返回内容：", full_response)
                try:
                    # 尝试从AI响应中提取JSON
                    json_start = full_response.find('{')
                    json_end = full_response.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = full_response[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        return {"success": True, "data": parsed_result}
                    else:
                        return {"success": False, "message": "AI响应格式错误，未找到JSON内容"}
                except Exception as e:
                    return {"success": False, "message": f"无法解析AI响应: {str(e)}"}
            else:
                return {"success": False, "message": error_message or "请求超时"}
        except Exception as e:
            print("WebSocket连接异常：", str(e))
            return {"success": False, "message": f"连接失败: {str(e)}"}

    async def auto_complete_item_by_image_ws(self, image_bytes_list: list) -> dict:
        """
        使用websockets库异步方式调用讯飞图片理解API，测试兼容性
        """
        config = self._get_config()
        app_id = config['app_id']
        api_key = config['api_key']
        api_secret = config['api_secret']
        spark_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"
        if not all([app_id, api_key, api_secret]):
            return {"success": False, "message": "星火大模型配置不完整，请检查环境变量"}

        def create_url():
            from email.utils import formatdate
            from urllib.parse import urlparse, quote_plus
            import base64, hmac, hashlib
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
            url = f"{spark_url}?authorization={quote_plus(authorization)}&date={quote_plus(date)}&host={quote_plus(host)}"
            return url

        url = create_url()
        
        # 限制图片数量为1~4
        if not (1 <= len(image_bytes_list) <= 4):
            return {"success": False, "message": "图片数量必须为1~4张"}
        
        # 将图片转换为base64，确保没有换行符
        image_b64_list = []
        for img in image_bytes_list:
            b64 = base64.b64encode(img).decode('utf-8')
            # 移除所有换行符和回车符
            b64 = b64.replace('\n', '').replace('\r', '')
            image_b64_list.append(b64)
        
        print("[websockets] 上传图片数量：", len(image_b64_list))
        for idx, b64 in enumerate(image_b64_list):
            print(f"[websockets] 图片{idx+1} base64长度：", len(b64))
        
        # 构建详细的提示词，指导AI识别商品信息
        prompt = """请仔细分析这些二手商品图片，以二手卖家的身份识别商品信息，并按照以下JSON格式返回：

{
    "title": "商品标题（简洁明了，突出商品特点和二手属性）",
    "description": "二手商品描述（以卖家口吻描述：品牌、型号、购买时间、使用情况、成色、是否有瑕疵等）",
    "category": "商品分类ID（1:手机数码, 2:电脑办公, 3:家用电器, 4:服装鞋包, 5:美妆护肤, 6:图书文娱, 7:运动户外, 8:家居家装）",
    "condition": "商品状态（new:全新, like_new:几乎全新, good:轻微使用痕迹, fair:使用痕迹明显）",
    "price_suggestion": "建议价格范围（如：100-200元）"
}

要求：
1. 仔细观察图片中的商品外观、品牌标识、型号信息、使用痕迹
2. 根据商品的新旧程度和磨损情况判断condition
3. 根据商品类型选择合适的category
4. 标题要体现二手属性，如"二手iPhone 13"、"九成新MacBook"等
5. 描述要以二手卖家的口吻，包含：
   - 品牌型号
   - 购买时间或使用时长
   - 成色描述（几成新）
   - 是否有磕碰、划痕等瑕疵
   - 功能是否正常
   - 配件情况（原装充电器、包装盒等）
6. 只返回JSON格式，不要其他文字
7. 如果无法识别某些信息，相应字段填写"未知"
8. 描述要真实、诚恳，符合二手交易的特点
"""
        
        # 构建符合讯飞API文档的消息体
        # 首先添加图片（每个图片为一个独立元素，content_type为image）
        text_array = []
        for b64 in image_b64_list:
            text_array.append({
                "role": "user",
                "content": b64,
                "content_type": "image"
            })
        # 最后添加文本问题（content_type为text）
        text_array.append({
            "role": "user",
            "content": prompt,
            "content_type": "text"
        })
        # 日志打印最终text数组内容
        print("最终发送给讯飞的text数组：", json.dumps(text_array, ensure_ascii=False, indent=2))
        message = {
            "header": {
                "app_id": app_id,
                "uid": "12345"
            },
            "parameter": {
                "chat": {
                    "domain": "imagev3",  # 使用高级版以获得更好的效果
                    "temperature": 0.5,
                    "top_k": 4,
                    "max_tokens": 2048,
                    "chat_id": "auto_complete_" + str(int(time.time()))
                }
            },
            "payload": {
                "message": {
                    "text": text_array
                }
            }
        }
        
        print("[websockets] 发送给讯飞的消息体结构：", json.dumps(message, ensure_ascii=False, indent=2)[:1000])
        
        try:
            async with websockets.connect(url) as websocket:
                await websocket.send(json.dumps(message, ensure_ascii=False))
                print("[websockets] 消息已发送，等待响应...")
                full_response = ""
                
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        print(f"[websockets] 收到讯飞响应：{json.dumps(data, ensure_ascii=False, indent=2)}")
                        
                        # 检查响应状态
                        if data.get("header", {}).get("code") != 0:
                            print(f"[websockets] 讯飞API返回错误：{data}")
                            return {"success": False, "message": f"讯飞API错误：{data.get('header', {}).get('message', '未知错误')}"}
                        
                        # 提取文本内容
                        if "payload" in data and "choices" in data["payload"]:
                            choices = data["payload"]["choices"]
                            if "text" in choices and choices["text"]:
                                for text_item in choices["text"]:
                                    if "content" in text_item:
                                        content = text_item["content"]
                                        if isinstance(content, str):
                                            full_response += content
                                        elif isinstance(content, list):
                                            full_response += ''.join([item for item in content if isinstance(item, str)])
                        
                        # 检查是否完成
                        if data.get("header", {}).get("status") == 2:
                            print(f"[websockets] 讯飞响应完成，完整响应：{full_response}")
                            break
                            
                    except websockets.exceptions.ConnectionClosed:
                        print("[websockets] WebSocket连接已关闭")
                        break
                    except Exception as e:
                        print(f"[websockets] 处理响应时出错：{e}")
                        continue
                
                print("[websockets] AI原始返回内容：", full_response[:500])
                
                try:
                    # 尝试从AI响应中提取JSON
                    json_start = full_response.find('{')
                    json_end = full_response.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        json_str = full_response[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        return {"success": True, "data": parsed_result}
                    else:
                        return {"success": False, "message": "AI响应格式错误，未找到JSON内容"}
                except Exception as e:
                    return {"success": False, "message": f"无法解析AI响应: {str(e)}"}
                    
        except Exception as e:
            print("[websockets] 连接异常：", str(e))
            return {"success": False, "message": f"websockets连接失败: {str(e)}"}

# 创建全局实例
spark_ai_service = SparkAIService() 