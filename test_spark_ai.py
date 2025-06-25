import time
from core.spark_ai import spark_ai_service

# 测试 analyze_price_competition

def test_analyze_price_competition():
    test_items = [
        {"title": "iPhone 13", "price": 3500, "condition": "like_new"},
        {"title": "小米手环7", "price": 120, "condition": "new"},
        {"title": "戴尔笔记本", "price": 2200, "condition": "good"},
    ]
    print("\n===== 测试 analyze_price_competition =====")
    start = time.time()
    result = spark_ai_service.analyze_price_competition(test_items)
    end = time.time()
    print("AI接口返回：", result)
    print(f"总耗时：{end - start:.2f} 秒")

if __name__ == "__main__":
    test_analyze_price_competition() 