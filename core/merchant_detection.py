"""
商贩识别系统
通过AI分析用户行为模式，自动识别潜在的商贩用户
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from db.models import User, Item, Merchant
from core.spark_ai import SparkAIService
from core.config import settings


class MerchantDetectionSystem:
    """商贩识别系统"""
    
    def __init__(self, db: Session):
        self.db = db
        self.spark_ai = SparkAIService()
        
    async def analyze_user_behavior(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        分析用户行为模式
        
        Args:
            user_id: 用户ID
            days: 分析天数
            
        Returns:
            用户行为分析结果
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "用户不存在"}
        
        # 计算分析时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 统计用户商品数据
        total_items = self.db.query(Item).filter(
            and_(
                Item.owner_id == user_id,
                Item.created_at >= start_date
            )
        ).count()
        
        active_items = self.db.query(Item).filter(
            and_(
                Item.owner_id == user_id,
                Item.status == "online",
                Item.sold == False,
                Item.created_at >= start_date
            )
        ).count()
        
        sold_items = self.db.query(Item).filter(
            and_(
                Item.owner_id == user_id,
                Item.sold == True,
                Item.created_at >= start_date
            )
        ).count()
        
        # 统计商品分类分布
        category_stats = self.db.query(
            Item.category,
            func.count(Item.id).label('count')
        ).filter(
            and_(
                Item.owner_id == user_id,
                Item.created_at >= start_date
            )
        ).group_by(Item.category).all()
        
        # 统计价格分布
        price_stats = self.db.query(
            func.min(Item.price).label('min_price'),
            func.max(Item.price).label('max_price'),
            func.avg(Item.price).label('avg_price')
        ).filter(
            and_(
                Item.owner_id == user_id,
                Item.created_at >= start_date
            )
        ).first()
        
        # 统计发布频率（每天平均发布商品数）
        daily_publish_rate = total_items / days if days > 0 else 0
        
        # 统计商品标题和描述的关键词
        items = self.db.query(Item).filter(
            and_(
                Item.owner_id == user_id,
                Item.created_at >= start_date
            )
        ).all()
        
        titles = [item.title for item in items]
        descriptions = [item.description for item in items if item.description]
        
        return {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "analysis_period_days": days,
            "total_items": total_items,
            "active_items": active_items,
            "sold_items": sold_items,
            "daily_publish_rate": round(daily_publish_rate, 2),
            "category_distribution": dict(category_stats),
            "price_stats": {
                "min_price": float(price_stats.min_price) if price_stats.min_price else 0,
                "max_price": float(price_stats.max_price) if price_stats.max_price else 0,
                "avg_price": float(price_stats.avg_price) if price_stats.avg_price else 0
            },
            "titles": titles,
            "descriptions": descriptions,
            "is_merchant": user.is_merchant,
            "is_pending_verification": user.is_pending_verification,
            "created_at": user.created_at.isoformat()
        }
    
    async def get_ai_judgment(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用AI判断用户是否为商贩
        
        Args:
            behavior_data: 用户行为数据
            
        Returns:
            AI判断结果
        """
        # 先进行简单的规则判断，减少AI调用
        simple_judgment = self._simple_merchant_judgment(behavior_data)
        if simple_judgment["confidence"] > 0.8:
            return simple_judgment
        
        # 构建AI分析提示词
        prompt = self._build_analysis_prompt(behavior_data)
        
        try:
            # 调用星火大模型
            response = self.spark_ai._call_spark_api(prompt)
            
            if response.get("success", False):
                # 解析AI响应
                ai_result = self._parse_ai_response(response.get("response", ""))
                return ai_result
            else:
                # AI调用失败时使用简单判断
                return simple_judgment
            
        except Exception as e:
            # AI分析失败时使用简单判断
            return simple_judgment
    
    def _simple_merchant_judgment(self, behavior_data: Dict[str, Any]) -> Dict[str, Any]:
        """简单的商贩判断规则"""
        total_items = behavior_data.get("total_items", 0)
        active_items = behavior_data.get("active_items", 0)
        daily_publish_rate = behavior_data.get("daily_publish_rate", 0)
        price_stats = behavior_data.get("price_stats", {})
        avg_price = price_stats.get("avg_price", 0)
        
        # 商贩特征指标
        merchant_indicators = []
        confidence = 0.0
        
        # 1. 发布频率过高
        if daily_publish_rate > 2:  # 每天发布超过2个商品
            merchant_indicators.append(f"发布频率过高：每天{daily_publish_rate}个商品")
            confidence += 0.3
        
        # 2. 在售商品过多
        if active_items > 10:  # 在售商品超过10个
            merchant_indicators.append(f"在售商品过多：{active_items}个")
            confidence += 0.4
        
        # 3. 商品价格特征（价格相对较低，可能是批量商品）
        if avg_price > 0 and avg_price < 100:  # 平均价格低于100元
            merchant_indicators.append(f"商品价格较低：平均{avg_price}元")
            confidence += 0.2
        
        # 4. 总发布商品数过多
        if total_items > 20:  # 总发布超过20个商品
            merchant_indicators.append(f"总发布商品过多：{total_items}个")
            confidence += 0.3
        
        # 5. 商品分类过于集中
        category_distribution = behavior_data.get("category_distribution", {})
        if len(category_distribution) == 1 and total_items > 5:
            category = list(category_distribution.keys())[0]
            merchant_indicators.append(f"商品分类过于集中：全部为{category}")
            confidence += 0.2
        
        is_merchant = confidence > 0.5
        
        return {
            "is_merchant": is_merchant,
            "confidence": min(confidence, 1.0),
            "reason": "基于规则判断：" + ("；".join(merchant_indicators) if merchant_indicators else "无明显商贩特征"),
            "evidence": merchant_indicators,
            "recommendation": "需要人工审核" if is_merchant else "正常用户"
        }
    
    def _build_analysis_prompt(self, behavior_data: Dict[str, Any]) -> str:
        """构建AI分析提示词"""
        prompt = f"""
你是一个专业的二手交易平台管理员，需要分析用户行为来判断该用户是否为商贩。

用户信息：
- 用户名：{behavior_data['username']}
- 邮箱：{behavior_data['email']}
- 注册时间：{behavior_data['created_at']}
- 当前状态：{'已认证商家' if behavior_data['is_merchant'] else '普通用户'}

行为数据（最近{behavior_data['analysis_period_days']}天）：
- 总发布商品数：{behavior_data['total_items']}
- 在售商品数：{behavior_data['active_items']}
- 已售商品数：{behavior_data['sold_items']}
- 日均发布率：{behavior_data['daily_publish_rate']}件/天

商品分类分布：{json.dumps(behavior_data['category_distribution'], ensure_ascii=False)}

价格统计：
- 最低价：{behavior_data['price_stats']['min_price']}元
- 最高价：{behavior_data['price_stats']['max_price']}元
- 平均价：{behavior_data['price_stats']['avg_price']}元

商品标题示例：{behavior_data['titles'][:10]}  # 只显示前10个

商品描述示例：{behavior_data['descriptions'][:5]}  # 只显示前5个

请分析以上数据，判断该用户是否为商贩。商贩的特征通常包括：
1. 大量发布商品（日均发布率较高）
2. 商品种类多样化
3. 价格范围较广
4. 商品标题和描述可能包含商业性词汇
5. 持续活跃发布商品

请以JSON格式返回分析结果：
{{
    "is_merchant": true/false,
    "confidence": 0.0-1.0,
    "reason": "详细的分析理由",
    "evidence": ["证据1", "证据2", "证据3"],
    "recommendation": "建议采取的行动"
}}
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            # 尝试从响应中提取JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                return result
            else:
                # 如果没有找到JSON，尝试从文本中提取信息
                return {
                    "is_merchant": "是" in response or "商贩" in response or "true" in response.lower(),
                    "confidence": 0.5,
                    "reason": response,
                    "evidence": [],
                    "recommendation": "需要人工审核"
                }
        except Exception as e:
            return {
                "is_merchant": False,
                "confidence": 0.0,
                "reason": f"解析AI响应失败: {str(e)}",
                "error": str(e)
            }
    
    async def detect_merchants(self, 
                             top_n: int = 50, 
                             threshold_items: int = 10,
                             analysis_days: int = 30) -> List[Dict[str, Any]]:
        """
        检测潜在的商贩用户
        
        Args:
            top_n: 监控的商品数量（每个分类和首页）
            threshold_items: 在售商品数阈值
            analysis_days: 分析天数
            
        Returns:
            检测结果列表
        """
        results = []
        
        # 获取所有分类
        categories = self.db.query(Item.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        # 监控每个分类的前N个商品
        monitored_users = set()
        
        for category in categories:
            # 获取该分类下最近发布的商品
            items = self.db.query(Item).filter(
                and_(
                    Item.category == category,
                    Item.status == "online",
                    Item.sold == False
                )
            ).order_by(desc(Item.created_at)).limit(top_n).all()
            
            for item in items:
                monitored_users.add(item.owner_id)
        
        # 获取首页排序前N的商品（按浏览量排序）
        homepage_items = self.db.query(Item).filter(
            and_(
                Item.status == "online",
                Item.sold == False
            )
        ).order_by(desc(Item.views)).limit(top_n).all()
        
        for item in homepage_items:
            monitored_users.add(item.owner_id)
        
        # 分析每个监控用户
        for user_id in monitored_users:
            # 首先检查用户是否已经是商家，如果是则跳过检测
            user = self.db.query(User).filter(User.id == user_id).first()
            if user and (user.is_merchant or user.is_pending_merchant or user.is_pending_verification):
                print(f"用户 {user_id} 已经是商家或待认证状态，跳过检测")
                continue
            
            # 检查用户当前在售商品数
            active_items_count = self.db.query(Item).filter(
                and_(
                    Item.owner_id == user_id,
                    Item.status == "online",
                    Item.sold == False
                )
            ).count()
            
            # 如果超过阈值，进行详细分析
            if active_items_count >= threshold_items:
                behavior_data = await self.analyze_user_behavior(user_id, analysis_days)
                ai_result = await self.get_ai_judgment(behavior_data)
                
                # 判断是否为商贩
                is_merchant = ai_result.get("is_merchant", False)
                confidence = ai_result.get("confidence", 0.0)
                
                # 普通用户直接通过，疑似商贩需要管理员确认
                processed = not is_merchant  # 普通用户直接处理，商贩需要确认
                
                result = {
                    "user_id": user_id,
                    "active_items_count": active_items_count,
                    "behavior_data": behavior_data,
                    "ai_analysis": ai_result,
                    "detected_at": datetime.now().isoformat()
                }
                
                # 保存检测历史到数据库
                from crud.crud_detection_history import create_detection_history
                create_detection_history(
                    db=self.db,
                    user_id=user_id,
                    detection_type="manual",
                    behavior_data=result["behavior_data"],
                    ai_analysis=ai_result,
                    active_items_count=active_items_count,
                    is_merchant=is_merchant,
                    confidence=confidence,
                    ai_reason=ai_result.get("reason", ""),
                    processed=processed
                )
                
                results.append(result)
        
        return results
    
    async def auto_set_pending_verification(self, detection_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        自动将识别出的商贩设为待认证状态
        
        Args:
            detection_results: 检测结果列表
            
        Returns:
            处理结果
        """
        processed_count = 0
        success_count = 0
        errors = []
        
        for result in detection_results:
            user_id = result["user_id"]
            ai_analysis = result["ai_analysis"]
            
            # 如果AI判断为商贩且置信度较高
            if (ai_analysis.get("is_merchant", False) and 
                ai_analysis.get("confidence", 0) > 0.7):
                
                try:
                    # 检查用户是否已经是商家或待认证状态
                    user = self.db.query(User).filter(User.id == user_id).first()
                    if not user:
                        errors.append(f"用户 {user_id} 不存在")
                        continue
                    
                    if user.is_merchant or user.is_pending_verification:
                        continue  # 已经是商家或待认证，跳过
                    
                    # 设为待认证状态
                    user.is_pending_verification = True
                    self.db.commit()
                    
                    # 记录操作日志
                    self._log_auto_detection(user_id, ai_analysis)
                    
                    success_count += 1
                    processed_count += 1
                    
                except Exception as e:
                    errors.append(f"处理用户 {user_id} 时出错: {str(e)}")
                    processed_count += 1
        
        return {
            "processed_count": processed_count,
            "success_count": success_count,
            "error_count": len(errors),
            "errors": errors
        }
    
    def _log_auto_detection(self, user_id: int, ai_analysis: Dict[str, Any]):
        """记录自动检测日志"""
        # 这里可以添加日志记录逻辑
        # 比如记录到数据库或日志文件
        pass


# 全局检测系统实例
detection_system = None

def get_detection_system(db: Session) -> MerchantDetectionSystem:
    """获取检测系统实例"""
    global detection_system
    if detection_system is None:
        detection_system = MerchantDetectionSystem(db)
    return detection_system
