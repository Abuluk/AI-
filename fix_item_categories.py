#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复商品分类脚本
根据商品标题和描述重新分配正确的分类
"""

import re
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import Item

# 分类关键词映射
CATEGORY_KEYWORDS = {
    1: ["手机", "iPhone", "iPad", "MacBook", "AirPods", "华为", "小米", "OPPO", "vivo", "三星", "苹果", "数码", "相机", "镜头", "任天堂", "Switch", "PS", "Xbox", "游戏机"],
    2: ["电脑", "笔记本", "台式机", "MacBook", "ThinkPad", "戴尔", "华硕", "联想", "办公", "打印机", "扫描仪", "键盘", "鼠标", "显示器"],
    3: ["冰箱", "洗衣机", "空调", "电视", "微波炉", "电饭煲", "吸尘器", "空气净化器", "热水器", "家电", "电器"],
    4: ["衣服", "服装", "鞋子", "包包", "Nike", "Adidas", "优衣库", "ZARA", "H&M", "羽绒服", "牛仔裤", "T恤", "连衣裙", "外套", "运动鞋", "皮鞋", "帆布鞋"],
    5: ["化妆品", "护肤品", "口红", "粉底", "面膜", "香水", "SK-II", "雅诗兰黛", "兰蔻", "资生堂", "美妆", "护肤", "防晒"],
    6: ["书", "图书", "小说", "教材", "编程", "Python", "经济学", "心理学", "历史", "文学", "教育", "文具", "笔", "本子"],
    7: ["运动", "健身", "跑步", "篮球", "足球", "羽毛球", "网球", "游泳", "瑜伽", "登山", "户外", "帐篷", "睡袋", "运动服", "运动鞋"],
    8: ["家具", "沙发", "床", "桌子", "椅子", "衣柜", "书桌", "茶几", "装修", "家装", "宜家", "收纳", "台灯", "灯具"],
    9: ["食品", "饮料", "零食", "茶叶", "咖啡", "酒", "牛奶", "奶粉", "婴儿食品"],
    10: ["婴儿", "儿童", "玩具", "童装", "婴儿车", "安全座椅", "婴儿床", "奶粉", "尿布", "绘本"],
    11: ["汽车", "车载", "行车记录仪", "脚垫", "坐垫", "充电器", "导航", "音响", "轮胎", "机油"],
    12: ["宠物", "狗", "猫", "鱼", "鸟", "宠物粮", "宠物玩具", "宠物窝", "牵引绳", "猫砂"],
    13: ["吉他", "钢琴", "小提琴", "音响", "耳机", "麦克风", "乐器", "音乐"],
    14: ["收藏", "古董", "字画", "邮票", "纪念币", "艺术品", "工艺品"],
    15: ["游戏", "动漫", "手办", "模型", "游戏卡", "游戏机"],
    16: ["珠宝", "首饰", "手表", "项链", "戒指", "耳环", "手镯"],
    17: ["箱包", "旅行", "行李箱", "背包", "手提包", "钱包"],
    18: ["园艺", "花卉", "植物", "种子", "花盆", "肥料"],
    19: ["手工", "DIY", "工具", "材料", "制作"],
    20: ["其他", "杂项", "未知"]
}

def get_category_by_keywords(title: str, description: str = "") -> int:
    """根据关键词判断商品分类"""
    text = f"{title} {description}".lower()
    
    # 计算每个分类的匹配分数
    category_scores = {}
    for category_id, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1
        if score > 0:
            category_scores[category_id] = score
    
    # 返回得分最高的分类
    if category_scores:
        return max(category_scores.items(), key=lambda x: x[1])[0]
    
    return 20  # 默认分类

def fix_item_categories():
    """修复商品分类"""
    db = SessionLocal()
    
    try:
        # 获取所有商品
        items = db.query(Item).all()
        print(f"找到 {len(items)} 个商品")
        
        fixed_count = 0
        for item in items:
            # 根据标题和描述重新判断分类
            new_category = get_category_by_keywords(item.title, item.description or "")
            
            if item.category != new_category:
                old_category = item.category
                item.category = new_category
                fixed_count += 1
                print(f"修复商品: {item.title}")
                print(f"  原分类: {old_category} -> 新分类: {new_category}")
        
        db.commit()
        print(f"\n修复完成！共修复了 {fixed_count} 个商品的分类")
        
        # 显示修复后的分类分布
        print("\n=== 修复后的分类分布 ===")
        from sqlalchemy import func
        category_counts = db.query(Item.category, func.count(Item.id)).group_by(Item.category).all()
        for category_id, count in category_counts:
            if category_id is not None:
                print(f"分类 {category_id}: {count} 个商品")
        
    except Exception as e:
        print(f"修复过程中出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_item_categories()
