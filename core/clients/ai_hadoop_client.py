#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI增强推荐系统的Hadoop客户端
用于调用基于阿里云百炼大模型的AI增强推荐结果
"""

import requests
import json
from datetime import datetime, timedelta

class AIHadoopClient:
    """AI增强推荐系统的Hadoop客户端"""
    
    def __init__(self, vm_ip="192.168.174.128", api_port=8080):
        self.base_url = f"http://{vm_ip}:{api_port}"
        self.ai_model_version = "bailian-ai-enhanced-v2.0"
        self.data_source = "ershou_mysql_with_bailian_ai"
    
    def test_connection(self):
        """测试AI推荐API连接"""
        health_endpoints = [
            "/",
            "/health", 
            "/api/v1/ai_recommendations/",
            "/api/v1/ai_strategy/",
            "/docs"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                print(f"测试AI推荐端点 {endpoint}: 状态码 {response.status_code}")
                if response.status_code == 200:
                    print(f"成功连接到AI推荐API: {self.base_url}{endpoint}")
                    return True
            except Exception as e:
                print(f"连接失败 {endpoint}: {e}")
                continue
        
        print("所有AI推荐健康检查端点都失败")
        return False
    
    def get_ai_recommendations(self, user_id, limit=10):
        """获取AI增强的推荐结果
        
        基于我们分析的数据格式：
        - recommendations表：user_id, recommended_items, algorithm, generated_at, expires_at
        - user_item_scores表：user_id, item_id, score, algorithm, generated_at
        - ai_features表：user_id, item_id, rating, user_ai_profile, item_ai_features, ai_processing_timestamp, ai_model_version, data_source
        """
        try:
            # 尝试多个可能的AI推荐API端点
            endpoints_to_test = [
                f"/api/v1/ai_recommendations/{user_id}",
                f"/api/v1/ai_strategy/recommendations/{user_id}",
                f"/ai_recommendations/{user_id}",
                f"/recommendations/ai/{user_id}",
                f"/api/v1/ai_recommendations?user_id={user_id}&limit={limit}",
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    print(f"尝试AI推荐端点: {url}")
                    
                    response = requests.get(url, timeout=10)
                    print(f"AI推荐响应状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            # 添加AI增强标识
                            result["ai_enhanced"] = True
                            result["ai_model_version"] = self.ai_model_version
                            result["data_source"] = self.data_source
                            result["request_timestamp"] = datetime.now().isoformat()
                            
                            print(f"成功获取AI增强推荐: {json.dumps(result, indent=2, ensure_ascii=False)}")
                            return result
                        except ValueError as e:
                            print(f"AI推荐JSON解析错误: {e}")
                            continue
                    else:
                        print(f"AI推荐HTTP错误: {response.status_code}, 响应: {response.text[:200]}")
                        continue
                        
                except Exception as e:
                    print(f"AI推荐端点异常 {endpoint}: {e}")
                    continue
            
            # 如果所有端点都失败，返回错误而不是模拟数据（生产环境）
            print("所有AI推荐端点都失败！")
            print(f"尝试连接的服务器: {self.base_url}")
            print("请检查：")
            print("   1. Hadoop AI推荐服务是否正在运行")
            print("   2. 服务器IP和端口是否正确")
            print("   3. 网络连接是否正常")
            print("   4. API端点路径是否正确")
            
            # 强制使用真实数据，不提供模拟数据
            return {
                "error": "AI推荐服务不可用",
                "message": "无法连接到Hadoop AI推荐服务，请检查服务状态",
                "server": self.base_url,
                "user_id": str(user_id),
                "require_real_data": True
            }
            
        except Exception as e:
            print(f"获取AI推荐失败: {e}")
            return {"error": f"获取AI推荐失败: {str(e)}"}
    
    
    def get_user_ai_profile(self, user_id):
        """获取用户的AI画像"""
        try:
            endpoints_to_test = [
                f"/api/v1/ai_profile/{user_id}",
                f"/api/v1/users/{user_id}/ai_profile",
                f"/ai_profile/{user_id}",
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        return response.json()
                except Exception:
                    continue
            
            # 无法获取真实数据，返回错误
            return {
                "error": "用户AI画像服务不可用",
                "message": "无法连接到Hadoop AI画像服务，请检查服务状态",
                "server": self.base_url,
                "user_id": str(user_id),
                "require_real_data": True
            }
            
        except Exception as e:
            return {"error": f"获取用户AI画像失败: {str(e)}"}
    
    def get_item_ai_features(self, item_id):
        """获取商品的AI特征"""
        try:
            # 尝试从真实API获取商品AI特征
            endpoints_to_test = [
                f"/api/v1/ai_features/item/{item_id}",
                f"/api/v1/items/{item_id}/ai_features",
                f"/ai_features/item/{item_id}",
            ]
            
            for endpoint in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint}"
                    response = requests.get(url, timeout=5)
                    
                    if response.status_code == 200:
                        return response.json()
                except Exception:
                    continue
            
            # 无法获取真实数据，返回错误
            return {
                "error": "商品AI特征服务不可用",
                "message": "无法连接到Hadoop商品AI特征服务，请检查服务状态",
                "server": self.base_url,
                "item_id": str(item_id),
                "require_real_data": True
            }
            
        except Exception as e:
            return {"error": f"获取商品AI特征失败: {str(e)}"}
    
    def compare_with_traditional_recommendations(self, user_id, traditional_client):
        """对比AI增强推荐与传统推荐的结果"""
        try:
            print(f"\n=== 对比用户 {user_id} 的推荐结果 ===")
            
            # 获取AI增强推荐
            ai_recommendations = self.get_ai_recommendations(user_id)
            print(f"\nAI增强推荐结果:")
            print(json.dumps(ai_recommendations, indent=2, ensure_ascii=False))
            
            # 获取传统推荐
            traditional_recommendations = traditional_client.get_recommendations(user_id)
            print(f"\n传统推荐结果:")
            print(json.dumps(traditional_recommendations, indent=2, ensure_ascii=False))
            
            # 分析对比
            comparison = {
                "user_id": str(user_id),
                "ai_enhanced": {
                    "algorithm": ai_recommendations.get("metadata", {}).get("algorithm", "AI增强ALS"),
                    "total_items": ai_recommendations.get("metadata", {}).get("total_recommendations", 0),
                    "has_ai_profile": "ai_features" in ai_recommendations,
                    "model_version": ai_recommendations.get("ai_model_version", "unknown")
                },
                "traditional": {
                    "algorithm": "传统ALS",
                    "total_items": len(traditional_recommendations.get("recommended_items", [])) if isinstance(traditional_recommendations.get("recommended_items"), list) else 0,
                    "has_ai_profile": False,
                    "model_version": "traditional"
                },
                "comparison_timestamp": datetime.now().isoformat()
            }
            
            print(f"\n=== 推荐对比分析 ===")
            print(json.dumps(comparison, indent=2, ensure_ascii=False))
            
            return comparison
            
        except Exception as e:
            return {"error": f"推荐对比失败: {str(e)}"}

# 使用示例
if __name__ == "__main__":
    print("=== AI增强推荐系统客户端测试 ===")
    
    # 创建AI Hadoop客户端
    ai_client = AIHadoopClient("192.168.174.128", 8080)
    
    # 测试连接
    print("\n1. 测试AI推荐API连接...")
    if ai_client.test_connection():
        print("AI推荐API连接成功！")
    else:
        print("AI推荐API连接失败，将使用模拟数据")
    
    # 测试AI增强推荐
    print("\n2. 测试AI增强推荐功能...")
    test_user_ids = ["1", "12", "6"]
    
    for user_id in test_user_ids:
        print(f"\n--- 测试用户 {user_id} 的AI增强推荐 ---")
        
        # 获取AI增强推荐
        ai_recommendations = ai_client.get_ai_recommendations(user_id)
        print("AI增强推荐结果:")
        print(json.dumps(ai_recommendations, indent=2, ensure_ascii=False))
        
        # 获取用户AI画像
        user_profile = ai_client.get_user_ai_profile(user_id)
        print(f"\n用户 {user_id} 的AI画像:")
        print(json.dumps(user_profile, indent=2, ensure_ascii=False))
        
        # 如果有推荐商品，获取商品AI特征
        if "detailed_scores" in ai_recommendations:
            first_item = ai_recommendations["detailed_scores"][0]["item_id"]
            item_features = ai_client.get_item_ai_features(first_item)
            print(f"\n商品 {first_item} 的AI特征:")
            print(json.dumps(item_features, indent=2, ensure_ascii=False))
        
        print("\n" + "="*50)
    
    print("\n=== AI增强推荐系统测试完成 ===")
