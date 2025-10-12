#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强AI服务 - 真正发挥AI价值的推荐系统
版本: Enhanced AI Service v2.0
特性: 商品语义理解 + 深度用户行为分析 + 个性化特征生成
"""

import json
import asyncio
import websockets
import base64
import hmac
import hashlib
import time
import os
import sys
from email.utils import formatdate
from urllib.parse import urlparse, quote_plus
from typing import Dict, List, Any, Optional, Tuple
import traceback

class EnhancedAIService:
    """增强AI服务 - 支持商品语义理解和深度用户行为分析"""
    
    def __init__(self):
        self.app_id = os.getenv("XUNFEI_APP_ID")
        self.api_key = os.getenv("XUNFEI_API_KEY")
        self.api_secret = os.getenv("XUNFEI_API_SECRET")
        self.spark_url = os.getenv("XUNFEI_SPARK_URL", "wss://spark-api.xf-yun.com/v3.1/chat")
        
        if not all([self.app_id, self.api_key, self.api_secret]):
            print("警告: AI配置不完整，将使用模拟AI分析")
            self.ai_available = False
        else:
            self.ai_available = True
    
    async def analyze_user_behavior_deep(self, user_behaviors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """深度用户行为分析"""
        if not self.ai_available:
            return self._get_default_user_analysis()
        
        try:
            # 构建详细的用户行为分析prompt
            behavior_details = []
            for behavior in user_behaviors[:20]:  # 限制数量避免token过多
                behavior_details.append({
                    "user_id": behavior.get("user_id"),
                    "item_id": behavior.get("item_id"),
                    "rating": behavior.get("rating"),
                    "behavior_type": behavior.get("behavior_type", "view"),
                    "timestamp": behavior.get("created_at", ""),
                    "item_title": behavior.get("item_title", ""),
                    "item_category": behavior.get("item_category", ""),
                    "item_price": behavior.get("item_price", 0),
                    "item_condition": behavior.get("item_condition", ""),
                    "item_location": behavior.get("item_location", "")
                })
            
            prompt = f"""作为一位专业的用户行为分析专家，请基于以下详细的用户行为数据，进行深度分析：

用户行为数据：
{json.dumps(behavior_details, ensure_ascii=False, indent=2)}

请从以下维度进行深度分析：

1. **用户画像分析**：
   - 用户类型识别（价格敏感型、质量追求型、探索型、冲动型等）
   - 消费能力评估（基于价格偏好和购买行为）
   - 活跃度分析（基于行为频率和时间模式）

2. **行为模式分析**：
   - 浏览模式（快速浏览 vs 深度浏览）
   - 购买决策模式（理性 vs 感性）
   - 时间偏好（白天 vs 夜间用户）
   - 品类偏好和多样性

3. **个性化特征提取**：
   - 价格敏感度评分（0-1）
   - 质量偏好评分（0-1）
   - 品牌忠诚度评分（0-1）
   - 创新接受度评分（0-1）
   - 社交影响力评分（0-1）

4. **推荐策略建议**：
   - 推荐时机偏好
   - 推荐内容偏好
   - 推荐方式偏好

请以JSON格式返回分析结果：
{{
    "user_persona": "用户类型",
    "behavior_patterns": {{
        "browsing_style": "浏览风格",
        "decision_style": "决策风格",
        "time_preference": "时间偏好",
        "category_diversity": "品类多样性评分"
    }},
    "personalized_features": {{
        "price_sensitivity": 0.8,
        "quality_preference": 0.7,
        "brand_loyalty": 0.6,
        "innovation_acceptance": 0.5,
        "social_influence": 0.4
    }},
    "recommendation_strategy": {{
        "timing_preference": "推荐时机",
        "content_preference": "内容偏好",
        "method_preference": "方式偏好"
    }},
    "confidence_score": 0.85,
    "analysis_timestamp": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}}"""

            result = await self._call_ai_api(prompt)
            return self._parse_ai_result(result, "user_behavior_analysis")
            
        except Exception as e:
            print(f"深度用户行为分析失败: {e}")
            traceback.print_exc()
            return self._get_default_user_analysis()
    
    async def analyze_item_semantic(self, items_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """商品语义分析"""
        if not self.ai_available:
            return self._get_default_item_analysis()
        
        try:
            # 构建详细的商品语义分析prompt
            item_details = []
            for item in items_data[:30]:  # 限制数量避免token过多
                item_details.append({
                    "item_id": item.get("item_id"),
                    "title": item.get("item_title", ""),
                    "description": item.get("item_description", ""),
                    "category": item.get("item_category", ""),
                    "price": item.get("item_price", 0),
                    "condition": item.get("item_condition", ""),
                    "location": item.get("item_location", ""),
                    "popularity": item.get("popularity", 0),
                    "avg_rating": item.get("avg_rating", 0)
                })
            
            prompt = f"""作为一位专业的商品分析专家，请基于以下详细的商品数据，进行语义分析：

商品数据：
{json.dumps(item_details, ensure_ascii=False, indent=2)}

请从以下维度进行深度分析：

1. **商品语义理解**：
   - 商品类型识别和分类
   - 商品特征提取（品牌、型号、规格等）
   - 商品价值评估（基于价格、成色、描述等）

2. **市场定位分析**：
   - 价格定位（高端、中端、低端）
   - 目标用户群体识别
   - 竞争优势分析
   - 市场趋势判断

3. **推荐特征提取**：
   - 推荐优先级评分（0-100）
   - 流行度潜力评分（0-1）
   - 用户匹配度评分（0-1）
   - 转化率预测评分（0-1）

4. **商品标签生成**：
   - 功能标签
   - 风格标签
   - 适用场景标签
   - 特殊属性标签

5. **推荐策略建议**：
   - 推荐时机
   - 推荐理由
   - 目标用户匹配

请以JSON格式返回分析结果：
{{
    "semantic_analysis": {{
        "item_types": ["商品类型1", "商品类型2"],
        "key_features": ["特征1", "特征2", "特征3"],
        "value_assessment": "价值评估描述"
    }},
    "market_positioning": {{
        "price_tier": "价格定位",
        "target_audience": "目标用户",
        "competitive_advantage": "竞争优势",
        "market_trend": "市场趋势"
    }},
    "recommendation_features": {{
        "priority_score": 85,
        "popularity_potential": 0.8,
        "user_match_score": 0.7,
        "conversion_potential": 0.6
    }},
    "item_tags": {{
        "functional": ["功能标签1", "功能标签2"],
        "style": ["风格标签1", "风格标签2"],
        "scenario": ["场景标签1", "场景标签2"],
        "special": ["特殊标签1", "特殊标签2"]
    }},
    "recommendation_strategy": {{
        "timing": "推荐时机",
        "reason": "推荐理由",
        "target_users": "目标用户描述"
    }},
    "confidence_score": 0.9,
    "analysis_timestamp": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}}"""

            result = await self._call_ai_api(prompt)
            return self._parse_ai_result(result, "item_semantic_analysis")
            
        except Exception as e:
            print(f"商品语义分析失败: {e}")
            traceback.print_exc()
            return self._get_default_item_analysis()
    
    async def generate_personalized_recommendations(
        self, 
        user_profile: Dict[str, Any], 
        item_features: Dict[str, Any], 
        available_items: List[Dict[str, Any]],
        limit: int = 10
    ) -> Dict[str, Any]:
        """生成个性化推荐"""
        if not self.ai_available:
            return self._get_default_recommendations(available_items, limit)
        
        try:
            prompt = f"""作为一位专业的个性化推荐专家，请基于以下用户画像和商品特征，生成个性化推荐：

用户画像：
{json.dumps(user_profile, ensure_ascii=False, indent=2)}

商品特征：
{json.dumps(item_features, ensure_ascii=False, indent=2)}

候选商品：
{json.dumps(available_items[:20], ensure_ascii=False, indent=2)}

请从以下维度进行推荐：

1. **用户-商品匹配度分析**：
   - 基于用户偏好和商品特征的匹配度
   - 价格敏感度与商品价格的匹配
   - 质量偏好与商品成色的匹配
   - 品类偏好与商品分类的匹配

2. **推荐理由生成**：
   - 为每个推荐商品生成个性化推荐理由
   - 基于用户行为模式解释推荐原因
   - 突出商品与用户偏好的契合点

3. **推荐策略优化**：
   - 平衡多样性和相关性
   - 考虑用户的新颖性需求
   - 优化推荐时机和方式

请以JSON格式返回推荐结果：
{{
    "recommendations": [
        {{
            "item_id": 商品ID,
            "match_score": 0.95,
            "recommendation_reason": "个性化推荐理由",
            "user_benefit": "用户收益描述",
            "confidence": 0.9
        }}
    ],
    "recommendation_strategy": {{
        "diversity_balance": 0.7,
        "novelty_factor": 0.3,
        "explanation_style": "推荐解释风格"
    }},
    "user_insights": {{
        "preference_summary": "偏好总结",
        "recommendation_rationale": "推荐逻辑"
    }},
    "generated_at": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
}}"""

            result = await self._call_ai_api(prompt)
            return self._parse_ai_result(result, "personalized_recommendations")
            
        except Exception as e:
            print(f"个性化推荐生成失败: {e}")
            traceback.print_exc()
            return self._get_default_recommendations(available_items, limit)
    
    async def _call_ai_api(self, prompt: str) -> str:
        """调用AI API"""
        try:
            # 生成鉴权URL
            date = formatdate(timeval=None, localtime=False, usegmt=True)
            parsed_url = urlparse(self.spark_url)
            host = parsed_url.netloc
            path = parsed_url.path
            
            signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
            signature_sha = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            
            signature_sha_base64 = base64.b64encode(signature_sha).decode()
            authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
            
            v = {
                "authorization": authorization,
                "date": date,
                "host": host
            }
            
            # 构建WebSocket URL
            ws_url = f"{self.spark_url}?authorization={quote_plus(v['authorization'])}&date={quote_plus(v['date'])}&host={quote_plus(v['host'])}"
            
            # 构建请求数据
            data = {
                "header": {
                    "app_id": self.app_id,
                    "uid": "enhanced_ai_service"
                },
                "parameter": {
                    "chat": {
                        "domain": "x1",
                        "temperature": 0.7,
                        "max_tokens": 8192
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
            
            result = ""
            
            # 异步WebSocket连接
            async with websockets.connect(ws_url, ping_interval=None, ping_timeout=None) as websocket:
                # 发送数据
                await websocket.send(json.dumps(data))
                
                # 接收响应
                try:
                    async with asyncio.timeout(600):  # 10分钟超时
                        while True:
                            response = await websocket.recv()
                            response_data = json.loads(response)
                            
                            # 检查响应状态
                            if response_data.get("header", {}).get("code") != 0:
                                error_msg = response_data.get('header', {}).get('message', '未知错误')
                                raise Exception(f"API错误: {error_msg}")
                            
                            # 提取文本内容
                            if "payload" in response_data and "choices" in response_data["payload"]:
                                choices = response_data["payload"]["choices"]
                                if "text" in choices and len(choices["text"]) > 0:
                                    text_item = choices["text"][0]
                                    content = text_item.get("content", "") or text_item.get("reasoning_content", "")
                                    result += content
                            
                            # 检查是否结束
                            if response_data.get("header", {}).get("status") == 2:
                                break
                                
                except asyncio.TimeoutError:
                    raise Exception("AI响应超时（10分钟）")
            
            return result
            
        except Exception as e:
            print(f"AI API调用失败: {e}")
            raise e
    
    def _parse_ai_result(self, result: str, analysis_type: str) -> Dict[str, Any]:
        """解析AI返回结果"""
        try:
            # 尝试从AI返回的文本中提取JSON
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
                return ai_data
            else:
                raise Exception("无法解析AI返回的JSON")
        except Exception as e:
            print(f"解析AI结果失败: {e}")
            if analysis_type == "user_behavior_analysis":
                return self._get_default_user_analysis()
            elif analysis_type == "item_semantic_analysis":
                return self._get_default_item_analysis()
            else:
                return self._get_default_recommendations([], 10)
    
    def _get_default_user_analysis(self) -> Dict[str, Any]:
        """默认用户分析结果"""
        return {
            "user_persona": "balanced_user",
            "behavior_patterns": {
                "browsing_style": "balanced",
                "decision_style": "rational",
                "time_preference": "daytime",
                "category_diversity": 0.5
            },
            "personalized_features": {
                "price_sensitivity": 0.5,
                "quality_preference": 0.5,
                "brand_loyalty": 0.5,
                "innovation_acceptance": 0.5,
                "social_influence": 0.5
            },
            "recommendation_strategy": {
                "timing_preference": "anytime",
                "content_preference": "balanced",
                "method_preference": "standard"
            },
            "confidence_score": 0.3,
            "analysis_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ai_enhanced": False
        }
    
    def _get_default_item_analysis(self) -> Dict[str, Any]:
        """默认商品分析结果"""
        return {
            "semantic_analysis": {
                "item_types": ["通用商品"],
                "key_features": ["基础功能"],
                "value_assessment": "标准价值"
            },
            "market_positioning": {
                "price_tier": "medium",
                "target_audience": "通用用户",
                "competitive_advantage": "标准优势",
                "market_trend": "稳定"
            },
            "recommendation_features": {
                "priority_score": 50,
                "popularity_potential": 0.5,
                "user_match_score": 0.5,
                "conversion_potential": 0.5
            },
            "item_tags": {
                "functional": ["基础功能"],
                "style": ["通用风格"],
                "scenario": ["日常使用"],
                "special": ["标准属性"]
            },
            "recommendation_strategy": {
                "timing": "anytime",
                "reason": "基础推荐",
                "target_users": "通用用户"
            },
            "confidence_score": 0.3,
            "analysis_timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ai_enhanced": False
        }
    
    def _get_default_recommendations(self, available_items: List[Dict[str, Any]], limit: int) -> Dict[str, Any]:
        """默认推荐结果"""
        recommendations = []
        for i, item in enumerate(available_items[:limit]):
            recommendations.append({
                "item_id": item.get("item_id", i),
                "match_score": 0.5,
                "recommendation_reason": "基础推荐",
                "user_benefit": "通用商品",
                "confidence": 0.3
            })
        
        return {
            "recommendations": recommendations,
            "recommendation_strategy": {
                "diversity_balance": 0.5,
                "novelty_factor": 0.5,
                "explanation_style": "基础"
            },
            "user_insights": {
                "preference_summary": "通用偏好",
                "recommendation_rationale": "基础推荐逻辑"
            },
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
            "ai_enhanced": False
        }

async def main():
    """主函数 - 处理命令行参数"""
    if len(sys.argv) < 2:
        print("用法: python EnhancedAIService.py <analysis_type> [data_json]")
        print("分析类型: user_behavior, item_semantic, personalized_recommendation")
        sys.exit(1)
    
    analysis_type = sys.argv[1]
    data_json = sys.argv[2] if len(sys.argv) > 2 else "{}"
    
    try:
        data = json.loads(data_json)
        ai_service = EnhancedAIService()
        
        if analysis_type == "user_behavior":
            user_behaviors = data.get("user_behaviors", [])
            result = await ai_service.analyze_user_behavior_deep(user_behaviors)
        elif analysis_type == "item_semantic":
            items_data = data.get("items_data", [])
            result = await ai_service.analyze_item_semantic(items_data)
        elif analysis_type == "personalized_recommendation":
            user_profile = data.get("user_profile", {})
            item_features = data.get("item_features", {})
            available_items = data.get("available_items", [])
            limit = data.get("limit", 10)
            result = await ai_service.generate_personalized_recommendations(
                user_profile, item_features, available_items, limit
            )
        else:
            raise ValueError(f"不支持的分析类型: {analysis_type}")
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"处理失败: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())



