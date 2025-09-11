#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
为二手交易系统生成大量测试商品数据，分配到各个用户
"""

import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from db.session import SessionLocal
from db.models import User, Item
from crud.crud_user import create_user
from crud.crud_item import create_item
from schemas.user import UserCreate
from schemas.item import ItemCreate
from core.pwd_util import get_password_hash

# 商品分类定义 - 与前端分类映射保持一致
CATEGORIES = {
    1: "手机数码",
    2: "电脑办公", 
    3: "家用电器",
    4: "服装鞋包",
    5: "美妆护肤",
    6: "图书文娱",
    7: "运动户外",
    8: "家居家装",
    9: "食品饮料",
    10: "母婴用品",
    11: "汽车用品",
    12: "宠物用品",
    13: "乐器音响",
    14: "收藏品",
    15: "游戏动漫",
    16: "珠宝配饰",
    17: "箱包旅行",
    18: "园艺花卉",
    19: "手工DIY",
    20: "其他"
}

# 商品状态
CONDITIONS = ["全新", "九成新", "八成新", "七成新", "六成新", "五成新"]

# 城市列表
CITIES = [
    "北京市", "上海市", "广州市", "深圳市", "杭州市", "南京市", "武汉市", "成都市",
    "西安市", "重庆市", "天津市", "苏州市", "长沙市", "郑州市", "青岛市", "大连市",
    "宁波市", "厦门市", "福州市", "无锡市", "合肥市", "昆明市", "哈尔滨市", "济南市",
    "佛山市", "长春市", "石家庄市", "温州市", "南宁市", "贵阳市", "海口市", "兰州市"
]

# 生成更多测试用户数据
def generate_test_users_data(num_users: int = 50):
    """生成测试用户数据"""
    users = []
    for i in range(1, num_users + 1):
        username = f"test_user_{i:03d}"
        email = f"test{i:03d}@example.com"
        phone = f"1380000{i:04d}"
        users.append({
            "username": username,
            "email": email,
            "phone": phone
        })
    return users

# 商品数据模板
ITEM_TEMPLATES = {
    1: [  # 电子产品
        {"title": "iPhone 13 Pro", "description": "256GB 深空灰色，使用一年，无磕碰，功能完好", "price_range": (4000, 5500)},
        {"title": "MacBook Pro 2021", "description": "M1芯片 16GB内存 512GB存储，轻度使用", "price_range": (8000, 12000)},
        {"title": "iPad Air 4", "description": "64GB WiFi版，保护套齐全，几乎全新", "price_range": (3000, 4000)},
        {"title": "AirPods Pro", "description": "第二代降噪耳机，充电盒完好", "price_range": (1200, 1800)},
        {"title": "华为MateBook", "description": "14寸轻薄本，i5处理器，办公利器", "price_range": (3500, 5000)},
        {"title": "小米11 Ultra", "description": "12GB+256GB，陶瓷黑，拍照神器", "price_range": (2500, 3500)},
        {"title": "任天堂Switch", "description": "日版续航版，包含多款游戏", "price_range": (1800, 2500)},
        {"title": "索尼WH-1000XM4", "description": "头戴式降噪耳机，音质出色", "price_range": (1500, 2200)},
    ],
    2: [  # 服装鞋帽
        {"title": "Nike Air Max 270", "description": "42码白色运动鞋，穿过几次，鞋底干净", "price_range": (300, 500)},
        {"title": "优衣库羽绒服", "description": "L码黑色羽绒服，保暖性好，无破损", "price_range": (200, 400)},
        {"title": "ZARA风衣", "description": "M码卡其色风衣，经典款式，适合春秋", "price_range": (150, 300)},
        {"title": "Adidas运动套装", "description": "L码黑色运动服，透气舒适", "price_range": (100, 200)},
        {"title": "Levi's牛仔裤", "description": "32码蓝色直筒牛仔裤，经典款", "price_range": (80, 150)},
        {"title": "Converse帆布鞋", "description": "41码白色帆布鞋，百搭单品", "price_range": (120, 200)},
    ],
    3: [  # 家居用品
        {"title": "宜家书桌", "description": "白色简约书桌，尺寸120x60cm，无划痕", "price_range": (200, 400)},
        {"title": "小米空气净化器", "description": "Pro H型号，使用半年，滤芯可更换", "price_range": (800, 1200)},
        {"title": "戴森吸尘器", "description": "V8无线吸尘器，吸力强劲，配件齐全", "price_range": (1500, 2200)},
        {"title": "美的电饭煲", "description": "4L智能电饭煲，预约功能正常", "price_range": (150, 300)},
        {"title": "飞利浦台灯", "description": "护眼台灯，可调光调色温", "price_range": (80, 150)},
        {"title": "无印良品收纳盒", "description": "透明收纳盒套装，整理神器", "price_range": (30, 60)},
    ],
    4: [  # 图书文具
        {"title": "《百年孤独》", "description": "马尔克斯经典作品，九成新", "price_range": (15, 30)},
        {"title": "《三体》三部曲", "description": "刘慈欣科幻小说，完整套装", "price_range": (50, 80)},
        {"title": "《经济学原理》", "description": "曼昆著，经济学入门教材", "price_range": (40, 70)},
        {"title": "《Python编程》", "description": "从入门到实践，适合初学者", "price_range": (60, 100)},
        {"title": "《设计心理学》", "description": "唐纳德·诺曼著，设计必读", "price_range": (35, 60)},
        {"title": "《人类简史》", "description": "尤瓦尔·赫拉利著，历史类畅销书", "price_range": (25, 45)},
    ],
    5: [  # 运动户外
        {"title": "迪卡侬跑步鞋", "description": "42码专业跑步鞋，缓震效果好", "price_range": (200, 350)},
        {"title": "瑜伽垫", "description": "6mm厚瑜伽垫，防滑材质", "price_range": (50, 100)},
        {"title": "登山包", "description": "40L登山背包，多隔层设计", "price_range": (300, 500)},
        {"title": "哑铃套装", "description": "可调节哑铃，10-30kg", "price_range": (200, 400)},
        {"title": "篮球", "description": "斯伯丁篮球，手感好", "price_range": (80, 150)},
        {"title": "羽毛球拍", "description": "尤尼克斯羽毛球拍，专业级", "price_range": (300, 600)},
    ],
    6: [  # 美妆护肤
        {"title": "SK-II神仙水", "description": "230ml装，使用一半，正品保证", "price_range": (400, 600)},
        {"title": "雅诗兰黛小棕瓶", "description": "50ml精华液，抗衰老神器", "price_range": (500, 800)},
        {"title": "兰蔻粉水", "description": "400ml爽肤水，保湿效果好", "price_range": (200, 350)},
        {"title": "MAC口红", "description": "Chili色号，经典红棕色", "price_range": (80, 150)},
        {"title": "Dior香水", "description": "50ml真我香水，优雅花香", "price_range": (300, 500)},
        {"title": "资生堂防晒霜", "description": "50ml防晒霜，SPF50+", "price_range": (100, 180)},
    ],
    7: [  # 母婴用品
        {"title": "婴儿推车", "description": "可折叠婴儿推车，安全可靠", "price_range": (300, 600)},
        {"title": "儿童安全座椅", "description": "9个月-12岁适用，安全认证", "price_range": (400, 800)},
        {"title": "婴儿床", "description": "实木婴儿床，环保材质", "price_range": (500, 1000)},
        {"title": "儿童玩具", "description": "益智积木玩具，开发智力", "price_range": (50, 150)},
        {"title": "婴儿奶粉", "description": "进口奶粉，营养全面", "price_range": (200, 400)},
        {"title": "儿童绘本", "description": "经典儿童绘本，寓教于乐", "price_range": (20, 50)},
    ],
    8: [  # 汽车用品
        {"title": "车载充电器", "description": "双USB快充，兼容多种设备", "price_range": (30, 60)},
        {"title": "汽车脚垫", "description": "全包围脚垫，防水防污", "price_range": (100, 200)},
        {"title": "行车记录仪", "description": "高清夜视行车记录仪", "price_range": (200, 400)},
        {"title": "车载空气净化器", "description": "负离子空气净化器", "price_range": (150, 300)},
        {"title": "汽车坐垫", "description": "四季通用汽车坐垫", "price_range": (80, 150)},
        {"title": "车载冰箱", "description": "12V车载冰箱，制冷效果好", "price_range": (300, 600)},
    ],
    9: [  # 宠物用品
        {"title": "宠物笼子", "description": "大型宠物笼，适合中型犬", "price_range": (200, 400)},
        {"title": "猫砂盆", "description": "封闭式猫砂盆，防臭设计", "price_range": (80, 150)},
        {"title": "宠物玩具", "description": "互动宠物玩具，增进感情", "price_range": (30, 80)},
        {"title": "宠物食盆", "description": "不锈钢宠物食盆，易清洗", "price_range": (20, 50)},
        {"title": "宠物牵引绳", "description": "可调节牵引绳，安全可靠", "price_range": (40, 80)},
        {"title": "宠物窝", "description": "保暖宠物窝，舒适温暖", "price_range": (60, 120)},
    ],
    10: [  # 其他
        {"title": "二手自行车", "description": "山地自行车，变速正常", "price_range": (300, 600)},
        {"title": "吉他", "description": "民谣吉他，音色优美", "price_range": (400, 800)},
        {"title": "相机镜头", "description": "50mm定焦镜头，成像锐利", "price_range": (800, 1500)},
        {"title": "手表", "description": "机械手表，走时准确", "price_range": (500, 1200)},
        {"title": "茶具套装", "description": "紫砂茶具，品茶必备", "price_range": (200, 500)},
        {"title": "艺术品", "description": "手工艺品，装饰性强", "price_range": (100, 300)},
    ]
}

def get_users(db: Session):
    """获取所有用户"""
    return db.query(User).all()

def create_test_users(db: Session, num_users: int = 50) -> List[User]:
    """创建测试用户"""
    users = []
    test_users_data = generate_test_users_data(num_users)
    
    for user_data in test_users_data:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            users.append(existing_user)
            continue
            
        # 创建新用户
        user_create = UserCreate(
            username=user_data["username"],
            email=user_data["email"],
            phone=user_data["phone"],
            password="test123456"  # 默认密码
        )
        new_user = create_user(db, user_create)
        users.append(new_user)
        print(f"创建用户: {new_user.username}")
    
    return users

def generate_random_item(category_id: int, owner_id: int) -> ItemCreate:
    """生成随机商品"""
    templates = ITEM_TEMPLATES.get(category_id, ITEM_TEMPLATES[10])
    template = random.choice(templates)
    
    # 随机价格
    price_min, price_max = template["price_range"]
    price = round(random.uniform(price_min, price_max), 2)
    
    # 随机条件
    condition = random.choice(CONDITIONS)
    
    # 随机城市
    location = random.choice(CITIES)
    
    # 生成商品
    item = ItemCreate(
        title=template["title"],
        description=template["description"],
        price=price,
        category=category_id,
        condition=condition,
        location=location
    )
    
    return item

def generate_items_for_user(db: Session, user: User, num_items: int = 10):
    """为用户生成指定数量的商品"""
    items = []
    
    for _ in range(num_items):
        # 随机选择分类
        category_id = random.choice(list(CATEGORIES.keys()))
        
        # 生成商品
        item_data = generate_random_item(category_id, user.id)
        
        # 创建商品
        item = create_item(db, item_data, user.id)
        items.append(item)
        
        print(f"为用户 {user.username} 创建商品: {item.title} - ¥{item.price}")
    
    return items

def assign_items_to_users(db: Session, users: List[User], total_items: int = 200):
    """为部分用户分配商品，不是所有用户都有商品"""
    # 随机选择30-50%的用户来发布商品
    seller_ratio = random.uniform(0.3, 0.5)
    num_sellers = int(len(users) * seller_ratio)
    seller_users = random.sample(users, num_sellers)
    
    print(f"从 {len(users)} 个用户中选择 {len(seller_users)} 个用户作为卖家")
    
    total_items_created = 0
    for user in seller_users:
        # 每个卖家用户生成1-8个商品
        num_items = random.randint(1, 8)
        items = generate_items_for_user(db, user, num_items)
        total_items_created += len(items)
        
        # 更新用户的商品计数
        user.items_count = len(items)
        
        print(f"用户 {user.username} 发布了 {len(items)} 个商品")
    
    db.commit()
    return total_items_created

def main():
    """主函数"""
    print("开始生成测试数据...")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 1. 创建或获取测试用户
        print("\n=== 创建测试用户 ===")
        users = create_test_users(db, num_users=50)  # 创建50个用户
        print(f"共有 {len(users)} 个用户")
        
        # 2. 为部分用户生成商品
        print("\n=== 生成商品数据 ===")
        total_items = assign_items_to_users(db, users, total_items=200)
        
        print(f"\n=== 数据生成完成 ===")
        print(f"用户总数: {len(users)}")
        print(f"商品总数: {total_items}")
        
        # 统计有商品的用户数量
        users_with_items = db.query(User).filter(User.items_count > 0).count()
        print(f"有商品的用户数: {users_with_items}")
        print(f"无商品的用户数: {len(users) - users_with_items}")
        
        # 3. 显示统计信息
        print("\n=== 分类统计 ===")
        for category_id, category_name in CATEGORIES.items():
            count = db.query(Item).filter(Item.category == category_id).count()
            print(f"{category_name}: {count} 个商品")
        
        print("\n=== 价格统计 ===")
        items = db.query(Item).all()
        if items:
            prices = [item.price for item in items]
            print(f"最低价格: ¥{min(prices):.2f}")
            print(f"最高价格: ¥{max(prices):.2f}")
            print(f"平均价格: ¥{sum(prices)/len(prices):.2f}")
        
        print("\n=== 城市分布 ===")
        city_counts = {}
        for item in items:
            city = item.location
            city_counts[city] = city_counts.get(city, 0) + 1
        
        # 显示前10个城市
        sorted_cities = sorted(city_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for city, count in sorted_cities:
            print(f"{city}: {count} 个商品")
        
        print("\n=== 用户商品分布 ===")
        # 统计用户商品数量分布
        item_counts = {}
        for user in users:
            count = user.items_count
            item_counts[count] = item_counts.get(count, 0) + 1
        
        sorted_counts = sorted(item_counts.items())
        for count, user_num in sorted_counts:
            if count == 0:
                print(f"无商品用户: {user_num} 人")
            else:
                print(f"{count} 个商品: {user_num} 人")
            
    except Exception as e:
        print(f"生成数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
