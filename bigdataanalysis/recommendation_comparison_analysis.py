#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐系统对比分析工具
比较大数据推荐、AI增强推荐和AI智能推荐三种方法的性能和准确性
"""

import asyncio
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入推荐服务
from core.bigdata_recommendation_service import bigdata_recommendation_service
from core.ai_enhanced_recommendation_service import ai_enhanced_recommendation_service
from core.ai_recommendation_service import ai_recommendation_service
from core.spark_ai import spark_ai_service

# 导入数据库相关
from db.session import get_db
from db.models import User, Item, UserBehavior, Feedback
from sqlalchemy.orm import Session

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class RecommendationComparisonAnalyzer:
    """推荐系统对比分析器"""
    
    def __init__(self):
        self.results = {
            'bigdata': [],
            'ai_enhanced': [],
            'ai_smart': []
        }
        self.performance_metrics = {}
        self.user_id = 79  # 使用用户ID 1进行测试
        
    def test_bigdata_recommendation(self, db: Session, limit: int = 10) -> Dict[str, Any]:
        """测试大数据推荐服务"""
        print("测试大数据推荐服务...")
        start_time = time.time()
        
        try:
            # 获取推荐结果
            result = bigdata_recommendation_service.get_recommendations(self.user_id, limit)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 获取推荐的商品详情
            recommended_items = bigdata_recommendation_service.get_recommended_items(db, self.user_id, limit)
            
            return {
                'service': 'bigdata',
                'success': 'error' not in result,
                'response_time': response_time,
                'recommendation_count': len(recommended_items),
                'recommended_items': [item.id for item in recommended_items],
                'raw_result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'service': 'bigdata',
                'success': False,
                'response_time': end_time - start_time,
                'recommendation_count': 0,
                'recommended_items': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_ai_enhanced_recommendation(self, db: Session, limit: int = 10) -> Dict[str, Any]:
        """测试AI增强推荐服务"""
        print("测试AI增强推荐服务...")
        start_time = time.time()
        
        try:
            # 获取推荐结果
            result = ai_enhanced_recommendation_service.get_ai_recommendations(self.user_id, limit)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # 获取推荐的商品详情
            recommended_items = ai_enhanced_recommendation_service.get_recommended_items(db, self.user_id, limit)
            
            return {
                'service': 'ai_enhanced',
                'success': 'error' not in result,
                'response_time': response_time,
                'recommendation_count': len(recommended_items),
                'recommended_items': [item.id for item in recommended_items],
                'raw_result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'service': 'ai_enhanced',
                'success': False,
                'response_time': end_time - start_time,
                'recommendation_count': 0,
                'recommended_items': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def test_ai_smart_recommendation(self, db: Session, limit: int = 10) -> Dict[str, Any]:
        """测试AI智能推荐服务"""
        print("测试AI智能推荐服务...")
        start_time = time.time()
        
        try:
            # 获取推荐结果
            result = await ai_recommendation_service.get_ai_recommendations(db, self.user_id, limit)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            return {
                'service': 'ai_smart',
                'success': result.get('success', False),
                'response_time': response_time,
                'recommendation_count': len(result.get('recommendations', [])),
                'recommended_items': [item['id'] for item in result.get('recommendations', [])],
                'raw_result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'service': 'ai_smart',
                'success': False,
                'response_time': end_time - start_time,
                'recommendation_count': 0,
                'recommended_items': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def test_price_competition_analysis(self, db: Session) -> Dict[str, Any]:
        """测试价格竞争力分析（使用Spark AI）"""
        print("测试价格竞争力分析...")
        start_time = time.time()
        
        try:
            # 获取一些商品数据用于分析
            items = db.query(Item).filter(
                Item.status == "online",
                Item.sold == False
            ).limit(10).all()
            
            # 构建商品信息
            current_items = []
            for item in items:
                current_items.append({
                    'title': item.title,
                    'price': item.price,
                    'condition': item.condition,
                    'category': item.category
                })
            
            # 调用价格竞争力分析
            result = spark_ai_service.analyze_price_competition(current_items)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            return {
                'service': 'price_analysis',
                'success': result.get('success', False),
                'response_time': response_time,
                'analysis': result.get('analysis', ''),
                'recommendations': result.get('recommendations', []),
                'market_insights': result.get('market_insights', ''),
                'raw_result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'service': 'price_analysis',
                'success': False,
                'response_time': end_time - start_time,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_comprehensive_test(self, db: Session, test_rounds: int = 5) -> Dict[str, Any]:
        """运行综合测试"""
        print(f"开始运行 {test_rounds} 轮综合测试...")
        
        all_results = {
            'bigdata': [],
            'ai_enhanced': [],
            'ai_smart': [],
            'price_analysis': []
        }
        
        for round_num in range(test_rounds):
            print(f"\n=== 第 {round_num + 1} 轮测试 ===")
            
            # 测试大数据推荐
            bigdata_result = self.test_bigdata_recommendation(db)
            all_results['bigdata'].append(bigdata_result)
            
            # 测试AI增强推荐
            ai_enhanced_result = self.test_ai_enhanced_recommendation(db)
            all_results['ai_enhanced'].append(ai_enhanced_result)
            
            # 测试AI智能推荐
            ai_smart_result = await self.test_ai_smart_recommendation(db)
            all_results['ai_smart'].append(ai_smart_result)
            
            # 测试价格分析（每轮只测试一次）
            if round_num == 0:
                price_analysis_result = self.test_price_competition_analysis(db)
                all_results['price_analysis'].append(price_analysis_result)
            
            # 等待一段时间避免过于频繁的请求
            await asyncio.sleep(2)
        
        return all_results
    
    def calculate_metrics(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {}
        
        for service_name, service_results in results.items():
            if not service_results:
                continue
                
            # 过滤成功的测试
            successful_results = [r for r in service_results if r.get('success', False)]
            
            if not successful_results:
                metrics[service_name] = {
                    'success_rate': 0,
                    'avg_response_time': 0,
                    'avg_recommendation_count': 0,
                    'total_tests': len(service_results)
                }
                continue
            
            # 计算指标
            success_rate = len(successful_results) / len(service_results)
            avg_response_time = np.mean([r['response_time'] for r in successful_results])
            avg_recommendation_count = np.mean([r['recommendation_count'] for r in successful_results])
            
            # 计算响应时间标准差
            response_times = [r['response_time'] for r in successful_results]
            response_time_std = np.std(response_times) if len(response_times) > 1 else 0
            
            metrics[service_name] = {
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'response_time_std': response_time_std,
                'avg_recommendation_count': avg_recommendation_count,
                'total_tests': len(service_results),
                'successful_tests': len(successful_results)
            }
        
        return metrics
    
    def create_performance_charts(self, metrics: Dict[str, Any], save_path: str = "recommendation_performance_analysis.png"):
        """创建性能对比图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('推荐系统性能对比分析 (用户ID: 1)', fontsize=16, fontweight='bold')
        
        # 准备数据
        services = list(metrics.keys())
        success_rates = [metrics[s]['success_rate'] for s in services]
        avg_response_times = [metrics[s]['avg_response_time'] for s in services]
        avg_recommendation_counts = [metrics[s]['avg_recommendation_count'] for s in services]
        response_time_stds = [metrics[s].get('response_time_std', 0) for s in services]
        
        # 1. 成功率对比
        axes[0, 0].bar(services, success_rates, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[0, 0].set_title('成功率对比', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('成功率')
        axes[0, 0].set_ylim(0, 1.1)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(success_rates):
            axes[0, 0].text(i, v + 0.02, f'{v:.2f}', ha='center', va='bottom')
        
        # 2. 平均响应时间对比
        bars = axes[0, 1].bar(services, avg_response_times, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[0, 1].set_title('平均响应时间对比', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('响应时间 (秒)')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 添加误差线
        axes[0, 1].errorbar(services, avg_response_times, yerr=response_time_stds, 
                           fmt='none', color='black', capsize=5)
        
        # 添加数值标签
        for i, v in enumerate(avg_response_times):
            axes[0, 1].text(i, v + max(response_time_stds) * 0.1, f'{v:.2f}s', ha='center', va='bottom')
        
        # 3. 平均推荐数量对比
        axes[1, 0].bar(services, avg_recommendation_counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
        axes[1, 0].set_title('平均推荐数量对比', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('推荐数量')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(avg_recommendation_counts):
            axes[1, 0].text(i, v + 0.1, f'{v:.1f}', ha='center', va='bottom')
        
        # 4. 综合性能雷达图
        # 标准化数据用于雷达图
        normalized_success = [s for s in success_rates]
        normalized_speed = [1 - (rt / max(avg_response_times)) for rt in avg_response_times]  # 响应时间越短越好
        normalized_count = [rc / max(avg_recommendation_counts) for rc in avg_recommendation_counts]
        
        # 创建雷达图数据
        categories = ['成功率', '响应速度', '推荐数量']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形
        
        ax_radar = plt.subplot(2, 2, 4, projection='polar')
        
        for i, service in enumerate(services):
            values = [normalized_success[i], normalized_speed[i], normalized_count[i]]
            values += values[:1]  # 闭合图形
            
            ax_radar.plot(angles, values, 'o-', linewidth=2, label=service)
            ax_radar.fill(angles, values, alpha=0.25)
        
        ax_radar.set_xticks(angles[:-1])
        ax_radar.set_xticklabels(categories)
        ax_radar.set_ylim(0, 1)
        ax_radar.set_title('综合性能雷达图', fontsize=14, fontweight='bold', pad=20)
        ax_radar.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"性能对比图表已保存到: {save_path}")
        
        return fig
    
    def create_accuracy_analysis(self, results: Dict[str, List[Dict[str, Any]]], save_path: str = "recommendation_accuracy_analysis.png"):
        """创建准确性分析图表"""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('推荐系统准确性分析 (用户ID: 1)', fontsize=16, fontweight='bold')
        
        # 分析推荐商品的重叠情况
        services = ['bigdata', 'ai_enhanced', 'ai_smart']
        overlap_matrix = np.zeros((len(services), len(services)))
        
        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services):
                if i == j:
                    overlap_matrix[i][j] = 1.0
                    continue
                
                # 计算两个服务的推荐商品重叠度
                items1 = set()
                items2 = set()
                
                for result in results.get(service1, []):
                    if result.get('success', False):
                        items1.update(result.get('recommended_items', []))
                
                for result in results.get(service2, []):
                    if result.get('success', False):
                        items2.update(result.get('recommended_items', []))
                
                if items1 and items2:
                    overlap = len(items1.intersection(items2)) / len(items1.union(items2))
                    overlap_matrix[i][j] = overlap
                else:
                    overlap_matrix[i][j] = 0.0
        
        # 1. 推荐重叠度热力图
        im = axes[0].imshow(overlap_matrix, cmap='YlOrRd', aspect='auto')
        axes[0].set_xticks(range(len(services)))
        axes[0].set_yticks(range(len(services)))
        axes[0].set_xticklabels(services)
        axes[0].set_yticklabels(services)
        axes[0].set_title('推荐商品重叠度热力图', fontsize=14, fontweight='bold')
        
        # 添加数值标签
        for i in range(len(services)):
            for j in range(len(services)):
                text = axes[0].text(j, i, f'{overlap_matrix[i, j]:.2f}',
                                  ha="center", va="center", color="black", fontweight='bold')
        
        # 添加颜色条
        plt.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04)
        
        # 2. 推荐多样性分析
        diversity_scores = []
        for service in services:
            all_items = set()
            for result in results.get(service, []):
                if result.get('success', False):
                    all_items.update(result.get('recommended_items', []))
            
            # 计算多样性：推荐商品的总数
            diversity_scores.append(len(all_items))
        
        bars = axes[1].bar(services, diversity_scores, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        axes[1].set_title('推荐多样性分析', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('唯一推荐商品数量')
        axes[1].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(diversity_scores):
            axes[1].text(i, v + 0.1, f'{v}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"准确性分析图表已保存到: {save_path}")
        
        return fig
    
    def create_trend_analysis(self, results: Dict[str, List[Dict[str, Any]]], save_path: str = "recommendation_trend_analysis.png"):
        """创建趋势分析图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('推荐系统趋势分析 (用户ID: 1)', fontsize=16, fontweight='bold')
        
        services = ['bigdata', 'ai_enhanced', 'ai_smart']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # 1. 响应时间趋势
        for i, service in enumerate(services):
            service_results = results.get(service, [])
            if service_results:
                response_times = [r['response_time'] for r in service_results if r.get('success', False)]
                if response_times:
                    axes[0, 0].plot(range(1, len(response_times) + 1), response_times, 
                                   marker='o', label=service, color=colors[i], linewidth=2)
        
        axes[0, 0].set_title('响应时间趋势', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('测试轮次')
        axes[0, 0].set_ylabel('响应时间 (秒)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 推荐数量趋势
        for i, service in enumerate(services):
            service_results = results.get(service, [])
            if service_results:
                recommendation_counts = [r['recommendation_count'] for r in service_results if r.get('success', False)]
                if recommendation_counts:
                    axes[0, 1].plot(range(1, len(recommendation_counts) + 1), recommendation_counts, 
                                   marker='s', label=service, color=colors[i], linewidth=2)
        
        axes[0, 1].set_title('推荐数量趋势', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('测试轮次')
        axes[0, 1].set_ylabel('推荐数量')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 成功率趋势
        for i, service in enumerate(services):
            service_results = results.get(service, [])
            if service_results:
                success_rates = []
                for j in range(1, len(service_results) + 1):
                    successful = sum(1 for r in service_results[:j] if r.get('success', False))
                    success_rates.append(successful / j)
                
                axes[1, 0].plot(range(1, len(success_rates) + 1), success_rates, 
                               marker='^', label=service, color=colors[i], linewidth=2)
        
        axes[1, 0].set_title('累计成功率趋势', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('测试轮次')
        axes[1, 0].set_ylabel('累计成功率')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim(0, 1.1)
        
        # 4. 性能稳定性分析（响应时间标准差）
        stability_scores = []
        for service in services:
            service_results = results.get(service, [])
            if service_results:
                response_times = [r['response_time'] for r in service_results if r.get('success', False)]
                if len(response_times) > 1:
                    stability = 1 / (1 + np.std(response_times))  # 标准差越小，稳定性越高
                    stability_scores.append(stability)
                else:
                    stability_scores.append(0)
            else:
                stability_scores.append(0)
        
        bars = axes[1, 1].bar(services, stability_scores, color=colors)
        axes[1, 1].set_title('性能稳定性分析', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('稳定性得分 (越高越稳定)')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(stability_scores):
            axes[1, 1].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"趋势分析图表已保存到: {save_path}")
        
        return fig
    
    def generate_report(self, results: Dict[str, List[Dict[str, Any]]], metrics: Dict[str, Any]) -> str:
        """生成分析报告"""
        report = f"""
# 推荐系统对比分析报告

## 测试概况
- 测试用户ID: {self.user_id}
- 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 测试轮次: {len(next(iter(results.values()))) if results else 0}

## 服务性能对比

### 1. 大数据推荐服务
- 成功率: {metrics.get('bigdata', {}).get('success_rate', 0):.2%}
- 平均响应时间: {metrics.get('bigdata', {}).get('avg_response_time', 0):.3f}秒
- 平均推荐数量: {metrics.get('bigdata', {}).get('avg_recommendation_count', 0):.1f}个
- 成功测试次数: {metrics.get('bigdata', {}).get('successful_tests', 0)}/{metrics.get('bigdata', {}).get('total_tests', 0)}

### 2. AI增强推荐服务
- 成功率: {metrics.get('ai_enhanced', {}).get('success_rate', 0):.2%}
- 平均响应时间: {metrics.get('ai_enhanced', {}).get('avg_response_time', 0):.3f}秒
- 平均推荐数量: {metrics.get('ai_enhanced', {}).get('avg_recommendation_count', 0):.1f}个
- 成功测试次数: {metrics.get('ai_enhanced', {}).get('successful_tests', 0)}/{metrics.get('ai_enhanced', {}).get('total_tests', 0)}

### 3. AI智能推荐服务
- 成功率: {metrics.get('ai_smart', {}).get('success_rate', 0):.2%}
- 平均响应时间: {metrics.get('ai_smart', {}).get('avg_response_time', 0):.3f}秒
- 平均推荐数量: {metrics.get('ai_smart', {}).get('avg_recommendation_count', 0):.1f}个
- 成功测试次数: {metrics.get('ai_smart', {}).get('successful_tests', 0)}/{metrics.get('ai_smart', {}).get('total_tests', 0)}

## 详细分析

### 性能排名
"""
        
        # 按成功率排序
        sorted_services = sorted(metrics.items(), key=lambda x: x[1].get('success_rate', 0), reverse=True)
        for i, (service, data) in enumerate(sorted_services, 1):
            report += f"{i}. {service}: {data.get('success_rate', 0):.2%} 成功率\n"
        
        report += f"""
### 响应时间排名
"""
        # 按响应时间排序（越短越好）
        sorted_services = sorted(metrics.items(), key=lambda x: x[1].get('avg_response_time', float('inf')))
        for i, (service, data) in enumerate(sorted_services, 1):
            report += f"{i}. {service}: {data.get('avg_response_time', 0):.3f}秒\n"
        
        report += f"""
### 推荐数量排名
"""
        # 按推荐数量排序
        sorted_services = sorted(metrics.items(), key=lambda x: x[1].get('avg_recommendation_count', 0), reverse=True)
        for i, (service, data) in enumerate(sorted_services, 1):
            report += f"{i}. {service}: {data.get('avg_recommendation_count', 0):.1f}个\n"
        
        report += f"""
## 结论与建议

1. **最佳性能服务**: {max(metrics.items(), key=lambda x: x[1].get('success_rate', 0))[0]}
2. **最快响应服务**: {min(metrics.items(), key=lambda x: x[1].get('avg_response_time', float('inf')))[0]}
3. **最多推荐服务**: {max(metrics.items(), key=lambda x: x[1].get('avg_recommendation_count', 0))[0]}

## 技术建议

- 对于高并发场景，建议使用响应时间最短的服务
- 对于准确性要求高的场景，建议使用成功率最高的服务
- 可以考虑混合使用多种推荐策略，提高整体推荐效果
"""
        
        return report

async def main():
    """主函数"""
    print("开始推荐系统对比分析...")
    
    # 创建分析器
    analyzer = RecommendationComparisonAnalyzer()
    
    # 获取数据库连接
    db = next(get_db())
    
    try:
        # 运行综合测试
        results = await analyzer.run_comprehensive_test(db, test_rounds=3)
        
        # 计算性能指标
        metrics = analyzer.calculate_metrics(results)
        
        # 生成图表
        print("\n生成性能对比图表...")
        analyzer.create_performance_charts(metrics, "recommendation_performance_analysis.png")
        
        print("生成准确性分析图表...")
        analyzer.create_accuracy_analysis(results, "recommendation_accuracy_analysis.png")
        
        print("生成趋势分析图表...")
        analyzer.create_trend_analysis(results, "recommendation_trend_analysis.png")
        
        # 生成报告
        print("生成分析报告...")
        report = analyzer.generate_report(results, metrics)
        
        # 保存报告
        with open("recommendation_analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("\n分析完成！生成的文件：")
        print("- recommendation_performance_analysis.png")
        print("- recommendation_accuracy_analysis.png") 
        print("- recommendation_trend_analysis.png")
        print("- recommendation_analysis_report.md")
        
        # 打印简要结果
        print("\n=== 简要结果 ===")
        for service, data in metrics.items():
            print(f"{service}: 成功率={data.get('success_rate', 0):.2%}, "
                  f"响应时间={data.get('avg_response_time', 0):.3f}s, "
                  f"推荐数量={data.get('avg_recommendation_count', 0):.1f}")
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
