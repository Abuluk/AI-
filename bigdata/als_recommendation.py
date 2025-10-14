from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql.functions import col, concat, lit, concat_ws, date_format, current_timestamp, expr, to_json

spark = SparkSession.builder \
    .appName("Ershou ALS Recommendation") \
    .config("spark.driver.memory", "512m") \
    .config("spark.executor.memory", "512m") \
    .master("local[2]") \
    .getOrCreate()

# 读取HDFS评分数据
ratings = spark.read.option("sep", "\t").csv("hdfs://localhost:9000/data/input/user_item_scores/dt=*") \
    .toDF("user_id", "item_id", "score", "updated_at") \
    .select(col("user_id").cast("int"), col("item_id").cast("int"), col("score").cast("double")) \
    .filter(col("user_id").isNotNull() & col("item_id").isNotNull())

print(f"读取 {ratings.count()} 条评分")

# ALS训练
als = ALS(maxIter=5, regParam=0.01, rank=10, userCol="user_id", itemCol="item_id", ratingCol="score", coldStartStrategy="drop")
model = als.fit(ratings)

# 生成推荐 - 使用to_json转换为标准JSON，然后使用tab分隔避免CSV引号问题
userRecs = model.recommendForAllUsers(20) \
    .select(
        col("user_id"),
        to_json(col("recommendations.item_id")).alias("items_json"),
        lit("als").alias("algorithm"),
        date_format(current_timestamp(), "yyyy-MM-dd HH:mm:ss").alias("generated_at"),
        date_format(expr("current_timestamp() + interval 1 day"), "yyyy-MM-dd HH:mm:ss").alias("expires_at")
    )

print(f"生成 {userRecs.count()} 个用户推荐")

# 写入HDFS - 使用tab分隔符(\t)避免CSV引号转义问题
userRecs.coalesce(1).write.mode("overwrite").option("header", "false").option("delimiter", "\t").option("quote", "").csv("hdfs://localhost:9000/data/output/recommendation_snapshots")

print("推荐完成")
spark.stop()

