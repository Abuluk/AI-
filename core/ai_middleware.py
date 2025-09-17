# core/ai_middleware.py
# AI推荐中间件 - 请求监控和限流

import time
from typing import Dict, Any
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json

class AIRecommendationMiddleware:
    """AI推荐中间件"""
    
    def __init__(self):
        # 请求统计
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'timeout_requests': 0,
            'rate_limited_requests': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }
        
        # IP级别限流（防止恶意请求）
        self.ip_rate_limiter = defaultdict(list)
        self.max_requests_per_ip_per_minute = 10
        
        # 全局请求限流
        self.global_requests = []
        self.max_global_requests_per_minute = 30
    
    def _check_ip_rate_limit(self, client_ip: str) -> bool:
        """检查IP级别限流"""
        current_time = time.time()
        ip_requests = self.ip_rate_limiter[client_ip]
        
        # 清除1分钟前的请求记录
        ip_requests[:] = [
            req_time for req_time in ip_requests 
            if current_time - req_time < 60
        ]
        
        if len(ip_requests) >= self.max_requests_per_ip_per_minute:
            return False
        
        ip_requests.append(current_time)
        return True
    
    def _check_global_rate_limit(self) -> bool:
        """检查全局限流"""
        current_time = time.time()
        
        # 清除1分钟前的请求记录
        self.global_requests[:] = [
            req_time for req_time in self.global_requests 
            if current_time - req_time < 60
        ]
        
        if len(self.global_requests) >= self.max_global_requests_per_minute:
            return False
        
        self.global_requests.append(current_time)
        return True
    
    def _update_response_time_stats(self, response_time: float):
        """更新响应时间统计"""
        self.request_stats['response_times'].append(response_time)
        
        # 只保留最近100个响应时间
        if len(self.request_stats['response_times']) > 100:
            self.request_stats['response_times'] = self.request_stats['response_times'][-100:]
        
        # 计算平均响应时间
        if self.request_stats['response_times']:
            self.request_stats['avg_response_time'] = sum(self.request_stats['response_times']) / len(self.request_stats['response_times'])
    
    async def __call__(self, request: Request, call_next):
        """中间件处理函数"""
        # 只处理AI推荐相关请求
        if "/api/v1/ai_strategy/recommendations" not in str(request.url):
            return await call_next(request)
        
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        
        # 更新总请求数
        self.request_stats['total_requests'] += 1
        
        # 检查IP限流
        if not self._check_ip_rate_limit(client_ip):
            self.request_stats['rate_limited_requests'] += 1
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": f"IP {client_ip} 请求过于频繁，请稍后再试",
                    "error_code": "IP_RATE_LIMITED"
                }
            )
        
        # 检查全局限流
        if not self._check_global_rate_limit():
            self.request_stats['rate_limited_requests'] += 1
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": "AI推荐服务繁忙，请稍后再试",
                    "error_code": "SERVICE_BUSY"
                }
            )
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算响应时间
            response_time = time.time() - start_time
            self._update_response_time_stats(response_time)
            
            # 检查响应状态
            if response.status_code == 200:
                self.request_stats['successful_requests'] += 1
            elif response.status_code == 408:
                self.request_stats['timeout_requests'] += 1
            else:
                self.request_stats['failed_requests'] += 1
            
            # 添加响应头
            response.headers["X-AI-Response-Time"] = f"{response_time:.3f}s"
            response.headers["X-AI-Request-ID"] = f"ai_{int(start_time * 1000)}"
            
            return response
            
        except Exception as e:
            # 处理异常
            response_time = time.time() - start_time
            self._update_response_time_stats(response_time)
            self.request_stats['failed_requests'] += 1
            
            print(f"AI推荐中间件捕获异常: {e}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "AI推荐服务异常",
                    "error_code": "INTERNAL_ERROR"
                }
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            **self.request_stats,
            "current_ip_connections": len(self.ip_rate_limiter),
            "current_global_requests_per_minute": len(self.global_requests)
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.request_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'timeout_requests': 0,
            'rate_limited_requests': 0,
            'avg_response_time': 0.0,
            'response_times': []
        }
        self.ip_rate_limiter.clear()
        self.global_requests.clear()

# 全局中间件实例
ai_middleware = AIRecommendationMiddleware()
