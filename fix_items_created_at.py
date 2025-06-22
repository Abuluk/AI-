import pymysql
from datetime import datetime, timedelta

# 数据库连接配置
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='20030208..',
    database='ershou',
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        # 查询所有 created_at 为当前时间的数据
        cursor.execute("SELECT id FROM items WHERE created_at IS NOT NULL ORDER BY id")
        rows = cursor.fetchall()
        base_time = datetime.now().replace(second=0, microsecond=0)
        for idx, row in enumerate(rows):
            item_id = row[0]
            new_time = base_time + timedelta(minutes=74 * idx)
            # 格式化为 'YYYY-MM-DD HH:MM:00'
            new_time_str = new_time.strftime('%Y-%m-%d %H:%M:00')
            cursor.execute("UPDATE items SET created_at = %s WHERE id = %s", (new_time_str, item_id))
    conn.commit()
    print('已批量精细修复所有商品 created_at 字段，依次相差74分钟')
finally:
    conn.close() 