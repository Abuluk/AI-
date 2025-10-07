#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能排序对抗算法演示
展示预测曲线、真实曲线和最终曲线的收敛过程
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import math

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class SortingAlgorithmDemo:
    """智能排序对抗算法演示类"""
    
    def __init__(self):
        self.time_steps = 100
        self.items_count = 20
        
        # 初始化数据
        self.setup_data()
        
    def setup_data(self):
        """初始化演示数据"""
        # 时间步长
        self.t = np.linspace(0, 10, self.time_steps)
        
        # 真实曲线：基于商品真实表现（浏览量、点赞数等）
        # 使用正弦波 + 噪声模拟真实的市场波动
        self.true_curve = 50 + 30 * np.sin(0.5 * self.t) + 10 * np.sin(2 * self.t) + np.random.normal(0, 5, self.time_steps)
        
        # 预测曲线：基于历史数据的预测
        # 使用指数平滑 + 趋势预测
        self.predicted_curve = np.zeros_like(self.true_curve)
        self.predicted_curve[0] = self.true_curve[0]
        
        # 计算预测值（使用指数平滑）
        alpha = 0.3  # 平滑参数
        for i in range(1, len(self.predicted_curve)):
            # 指数平滑预测
            self.predicted_curve[i] = alpha * self.true_curve[i-1] + (1 - alpha) * self.predicted_curve[i-1]
            
            # 添加趋势预测
            if i > 1:
                trend = self.predicted_curve[i-1] - self.predicted_curve[i-2]
                self.predicted_curve[i] += 0.1 * trend
        
        # 最终曲线：预测值和真实值的加权平均
        # 使用自适应权重，随着时间收敛
        self.final_curve = np.zeros_like(self.true_curve)
        
        for i in range(len(self.final_curve)):
            # 自适应权重：随着时间增加，更信任真实值
            weight_true = min(0.8, 0.3 + 0.5 * i / len(self.final_curve))
            weight_pred = 1 - weight_true
            
            # 最终曲线 = 权重真实值 + 权重预测值
            self.final_curve[i] = weight_true * self.true_curve[i] + weight_pred * self.predicted_curve[i]
    
    def calculate_convergence_metrics(self):
        """计算收敛指标"""
        # 计算预测误差
        prediction_error = np.abs(self.predicted_curve - self.true_curve)
        
        # 计算最终曲线误差
        final_error = np.abs(self.final_curve - self.true_curve)
        
        # 计算收敛速度（误差减少率）
        convergence_rate = []
        for i in range(1, len(prediction_error)):
            if prediction_error[i-1] > 0:
                rate = (prediction_error[i-1] - final_error[i]) / prediction_error[i-1]
                convergence_rate.append(rate)
            else:
                convergence_rate.append(0)
        
        return prediction_error, final_error, convergence_rate
    
    def plot_static_demo(self):
        """绘制静态演示图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('智能排序对抗算法演示', fontsize=16, fontweight='bold')
        
        # 1. 三条曲线对比
        ax1.plot(self.t, self.true_curve, 'b-', linewidth=2, label='真实曲线', alpha=0.8)
        ax1.plot(self.t, self.predicted_curve, 'r--', linewidth=2, label='预测曲线', alpha=0.8)
        ax1.plot(self.t, self.final_curve, 'g-', linewidth=3, label='最终曲线', alpha=0.9)
        ax1.set_title('对抗算法收敛过程', fontsize=14, fontweight='bold')
        ax1.set_xlabel('时间步长')
        ax1.set_ylabel('商品权重分数')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 添加收敛区域标注
        ax1.axvspan(6, 10, alpha=0.2, color='green', label='收敛区域')
        
        # 2. 误差分析
        prediction_error, final_error, convergence_rate = self.calculate_convergence_metrics()
        
        ax2.plot(self.t, prediction_error, 'r-', linewidth=2, label='预测误差')
        ax2.plot(self.t, final_error, 'g-', linewidth=2, label='最终误差')
        ax2.set_title('误差收敛分析', fontsize=14, fontweight='bold')
        ax2.set_xlabel('时间步长')
        ax2.set_ylabel('绝对误差')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 收敛速度
        ax3.plot(self.t[1:], convergence_rate, 'purple', linewidth=2, label='收敛速度')
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('收敛速度分析', fontsize=14, fontweight='bold')
        ax3.set_xlabel('时间步长')
        ax3.set_ylabel('收敛速度')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 权重变化
        weights_true = [min(0.8, 0.3 + 0.5 * i / len(self.final_curve)) for i in range(len(self.final_curve))]
        weights_pred = [1 - w for w in weights_true]
        
        ax4.plot(self.t, weights_true, 'b-', linewidth=2, label='真实值权重')
        ax4.plot(self.t, weights_pred, 'r-', linewidth=2, label='预测值权重')
        ax4.set_title('自适应权重变化', fontsize=14, fontweight='bold')
        ax4.set_xlabel('时间步长')
        ax4.set_ylabel('权重系数')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('sorting_algorithm_demo.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_animated_demo(self):
        """绘制动画演示"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 初始化线条
        line_true, = ax.plot([], [], 'b-', linewidth=2, label='真实曲线', alpha=0.8)
        line_pred, = ax.plot([], [], 'r--', linewidth=2, label='预测曲线', alpha=0.8)
        line_final, = ax.plot([], [], 'g-', linewidth=3, label='最终曲线', alpha=0.9)
        
        # 设置坐标轴
        ax.set_xlim(0, 10)
        ax.set_ylim(20, 100)
        ax.set_xlabel('时间步长')
        ax.set_ylabel('商品权重分数')
        ax.set_title('智能排序对抗算法动态演示', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        def animate(frame):
            """动画函数"""
            if frame < len(self.t):
                # 更新线条数据
                line_true.set_data(self.t[:frame+1], self.true_curve[:frame+1])
                line_pred.set_data(self.t[:frame+1], self.predicted_curve[:frame+1])
                line_final.set_data(self.t[:frame+1], self.final_curve[:frame+1])
                
                # 添加当前点标记
                if frame > 0:
                    ax.scatter(self.t[frame], self.true_curve[frame], color='blue', s=50, zorder=5)
                    ax.scatter(self.t[frame], self.predicted_curve[frame], color='red', s=50, zorder=5)
                    ax.scatter(self.t[frame], self.final_curve[frame], color='green', s=50, zorder=5)
            
            return line_true, line_pred, line_final
        
        # 创建动画
        anim = FuncAnimation(fig, animate, frames=len(self.t), interval=100, blit=False)
        
        # 保存动画
        anim.save('sorting_algorithm_animation.gif', writer='pillow', fps=10)
        plt.show()
        
        return anim
    
    def analyze_convergence_speed(self):
        """分析收敛速度"""
        prediction_error, final_error, convergence_rate = self.calculate_convergence_metrics()
        
        # 计算收敛指标
        initial_error = prediction_error[0]
        final_error_value = final_error[-1]
        convergence_ratio = final_error_value / initial_error if initial_error > 0 else 0
        
        # 计算平均收敛速度
        avg_convergence_rate = np.mean(convergence_rate) if convergence_rate else 0
        
        # 计算收敛时间（误差减少到初始误差的10%）
        convergence_threshold = initial_error * 0.1
        convergence_time = None
        for i, error in enumerate(final_error):
            if error <= convergence_threshold:
                convergence_time = i
                break
        
        print("=== 收敛速度分析 ===")
        print(f"初始预测误差: {initial_error:.2f}")
        print(f"最终误差: {final_error_value:.2f}")
        print(f"收敛比例: {convergence_ratio:.2%}")
        print(f"平均收敛速度: {avg_convergence_rate:.2%}")
        if convergence_time:
            print(f"收敛时间: {convergence_time} 步")
        else:
            print("未完全收敛")
        
        return {
            'initial_error': initial_error,
            'final_error': final_error_value,
            'convergence_ratio': convergence_ratio,
            'avg_convergence_rate': avg_convergence_rate,
            'convergence_time': convergence_time
        }
    
    def plot_convergence_analysis(self):
        """绘制收敛分析图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        prediction_error, final_error, convergence_rate = self.calculate_convergence_metrics()
        
        # 1. 误差对比
        ax1.plot(self.t, prediction_error, 'r-', linewidth=2, label='预测误差')
        ax1.plot(self.t, final_error, 'g-', linewidth=2, label='最终误差')
        ax1.fill_between(self.t, prediction_error, final_error, alpha=0.3, color='yellow', label='误差改善区域')
        ax1.set_title('误差收敛对比', fontsize=14, fontweight='bold')
        ax1.set_xlabel('时间步长')
        ax1.set_ylabel('绝对误差')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 收敛速度分析
        ax2.plot(self.t[1:], convergence_rate, 'purple', linewidth=2, label='收敛速度')
        ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5, label='零收敛线')
        ax2.fill_between(self.t[1:], convergence_rate, 0, alpha=0.3, color='purple', label='收敛区域')
        ax2.set_title('收敛速度分析', fontsize=14, fontweight='bold')
        ax2.set_xlabel('时间步长')
        ax2.set_ylabel('收敛速度')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('convergence_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """主函数"""
    print("智能排序对抗算法演示")
    print("=" * 50)
    
    # 创建演示实例
    demo = SortingAlgorithmDemo()
    
    # 绘制静态演示图
    print("生成静态演示图...")
    demo.plot_static_demo()
    
    # 绘制收敛分析图
    print("生成收敛分析图...")
    demo.plot_convergence_analysis()
    
    # 分析收敛速度
    print("分析收敛速度...")
    convergence_metrics = demo.analyze_convergence_speed()
    
    # 生成动画（可选）
    print("生成动画演示...")
    try:
        demo.plot_animated_demo()
    except Exception as e:
        print(f"动画生成失败: {e}")
    
    print("\n演示完成！")
    print("生成的文件:")
    print("- sorting_algorithm_demo.png: 静态演示图")
    print("- convergence_analysis.png: 收敛分析图")
    print("- sorting_algorithm_animation.gif: 动画演示")

if __name__ == "__main__":
    main()
