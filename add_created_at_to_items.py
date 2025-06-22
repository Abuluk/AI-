import pymysql

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
        sql = """
        ALTER TABLE items ADD COLUMN created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
        """
        cursor.execute(sql)
    conn.commit()
    print('items 表已成功添加 created_at 字段')
finally:
    conn.close() 