#!/usr/bin/env python3
"""
初始化商品排序配置
"""

from sqlalchemy.orm import Session
from db.session import SessionLocal
from crud import crud_item_sorting

def init_sorting_configs():
    """初始化排序配置"""
    db = SessionLocal()
    try:
        # 时间窗口配置
        crud_item_sorting.update_sorting_config(
            db, 
            "time_window_minutes", 
            {"default": 30, "min": 5, "max": 1440},
            "排序算法的时间窗口配置（分钟）"
        )
        
        # 权重因子配置
        crud_item_sorting.update_sorting_config(
            db,
            "weight_factors",
            {
                "base_weight": 0.4,      # 基础权重占比40%
                "trend_weight": 0.35,    # 趋势权重占比35%
                "position_weight": 0.25  # 位置权重占比25%
            },
            "各项权重的占比配置"
        )
        
        # 趋势计算配置
        crud_item_sorting.update_sorting_config(
            db,
            "trend_calculation",
            {
                "views_weight": 0.3,        # 浏览量权重30%
                "likes_weight": 0.25,       # 点赞权重25%
                "favorites_weight": 0.2,   # 收藏权重20%
                "messages_weight": 0.15,    # 消息权重15%
                "activity_weight": 0.1,     # 活跃度权重10%
                "max_trend_weight": 1.5,    # 最大趋势权重
                "min_trend_weight": 0.5     # 最小趋势权重
            },
            "趋势计算的权重配置"
        )
        
        # 对抗曲线算法配置
        crud_item_sorting.update_sorting_config(
            db,
            "position_algorithm",
            {
                "log_base": 1.0,           # 对数基数
                "position_adjustment": 0.2, # 位置调整系数
                "decline_adjustment": 0.15, # 下降调整系数
                "position_factor_max": 0.3, # 位置因子最大值
                "max_position_weight": 1.3, # 最大位置权重
                "min_position_weight": 0.7  # 最小位置权重
            },
            "对抗曲线算法的参数配置"
        )
        
        # 卖家活跃度计算配置
        crud_item_sorting.update_sorting_config(
            db,
            "seller_activity",
            {
                "items_published_weight": 0.4,  # 发布商品权重40%
                "messages_replied_weight": 0.3, # 回复消息权重30%
                "login_activity_weight": 0.3,   # 登录活跃度权重30%
                "max_activity_score": 10.0,     # 最大活跃度分数
                "login_score_days": {           # 登录分数天数配置
                    "1": 1.0,    # 1天内登录
                    "7": 0.7,    # 7天内登录
                    "30": 0.3,   # 30天内登录
                    "default": 0.1  # 超过30天
                }
            },
            "卖家活跃度计算配置"
        )
        
        print("商品排序配置初始化完成！")
        
    except Exception as e:
        print(f"初始化配置失败: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_sorting_configs()

