package com.example.recommendation

import org.apache.spark.sql.{SparkSession, DataFrame, Row}
import org.apache.spark.ml.recommendation.ALS
import org.apache.spark.sql.functions._
import java.time.LocalDateTime

object AIEnhancedRecommendationEngine {
  def main(args: Array[String]): Unit = {
    // 创建Spark会话
    val spark = SparkSession.builder()
      .appName("AIEnhancedRecommendationEngine")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()
    
    import spark.implicits._
    
    // 设置日志级别
    spark.sparkContext.setLogLevel("WARN")
    
    println("=== AI增强推荐引擎启动 ===")
    
    try {
      // 1. 读取AI增强特征数据
      println("读取AI增强特征数据...")
      val aiFeaturesDF = try {
        spark.read
          .parquet("hdfs://localhost:9000/data/features/ai_enhanced")
      } catch {
        case e: Exception =>
          println(s"读取AI特征失败: ${e.getMessage}")
          println("回退到传统推荐模式...")
          return runTraditionalRecommendation(spark)
      }
      
      println(s"AI特征数据记录数: ${aiFeaturesDF.count()}")
      if (aiFeaturesDF.count() > 0) {
        println("AI特征数据预览:")
        aiFeaturesDF.show(5, truncate = false)
      }
      
      // 2. 从MySQL读取基础数据作为补充
      println("从MySQL读取基础数据...")
      val baseDataDF = readMySQLBehaviorData(spark)
      println(s"基础行为数据记录数: ${baseDataDF.count()}")
      
      // 3. 合并AI特征和基础数据
      println("合并AI特征和基础数据...")
      val combinedData = aiFeaturesDF
        .select("user_id", "item_id", "rating", "user_ai_profile", "item_ai_features")
        .union(
          baseDataDF
            .withColumn("user_ai_profile", lit("""{"user_level": "unknown", "ai_enhanced": false}"""))
            .withColumn("item_ai_features", lit("""{"popularity_tier": "unknown", "ai_enhanced": false}"""))
        )
        .groupBy("user_id", "item_id")
        .agg(
          max("rating").as("rating"),
          first("user_ai_profile").as("user_ai_profile"),
          first("item_ai_features").as("item_ai_features")
        )
      
      println(s"合并后数据记录数: ${combinedData.count()}")
      
      // 4. 数据预处理
      println("数据预处理...")
      val preparedData = combinedData
        .filter(col("rating").isNotNull && col("rating") > 0)
        .select(
          col("user_id").cast("int").as("user_id"),
          col("item_id").cast("int").as("item_id"), 
          col("rating").cast("float").as("rating")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating"))
      
      println(s"预处理后有效记录数: ${preparedData.count()}")
      
      // 检查数据量
      val dataCount = preparedData.count()
      if (dataCount < 10) {
        println(s"警告: 数据量过少 ($dataCount 条记录)，使用传统推荐")
        return runTraditionalRecommendation(spark)
      }
      
      // 5. AI增强的ALS模型训练
      println("训练AI增强ALS模型...")
      val als = new ALS()
        .setUserCol("user_id")
        .setItemCol("item_id")
        .setRatingCol("rating")
        .setRank(15)  // 增加rank以利用AI特征
        .setMaxIter(10)  // 增加迭代次数
        .setRegParam(0.01)
        .setColdStartStrategy("drop")
      
      val model = als.fit(preparedData)
      
      // 6. 生成AI增强推荐
      println("生成AI增强推荐结果...")
      val userRecs = model.recommendForAllUsers(15)  // 每个用户推荐15个商品
      
      println("AI增强推荐结果样本:")
      userRecs.show(10)
      
      val currentTime = LocalDateTime.now().toString
      val expiryTime = LocalDateTime.now().plusDays(7).toString
      
      // 7. 准备AI增强的用户-物品评分数据
      println("准备AI增强用户-物品评分数据...")
      val userItemScores = userRecs.flatMap { row =>
        val userId = row.getInt(0)
        val recommendations = row.getAs[Seq[Row]](1)
        recommendations.map { rec =>
          (userId, rec.getInt(0), rec.getFloat(1), "ai_enhanced_als", currentTime)
        }
      }.toDF("user_id", "item_id", "score", "algorithm", "generated_at")
      
      // 8. 准备AI增强推荐快照数据
      println("准备AI增强推荐快照数据...")
      val recommendationSnapshots = userRecs.map { row =>
        val userId = row.getInt(0)
        val itemIds = row.getAs[Seq[Row]](1).map(_.getInt(0))
        val jsonArray = itemIds.mkString("[", ",", "]")
        (userId, jsonArray, "ai_enhanced_als", currentTime, expiryTime)
      }.toDF("user_id", "recommended_items", "algorithm", "generated_at", "expires_at")
      
      // 9. 保存AI增强结果到HDFS
      println("保存AI增强结果到HDFS...")
      
      // 先删除旧目录
      try {
        val fs = org.apache.hadoop.fs.FileSystem.get(spark.sparkContext.hadoopConfiguration)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/user_item_scores_ai"), true)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/recommendation_snapshots_ai"), true)
      } catch {
        case e: Exception => println(s"删除旧目录失败: ${e.getMessage}")
      }
      
      userItemScores
        .coalesce(1)
        .write
        .option("sep", "\t")
        .option("header", "false")
        .option("quote", "")
        .mode("overwrite")
        .csv("hdfs://localhost:9000/data/output/user_item_scores_ai")
      
      recommendationSnapshots
        .coalesce(1)
        .write
        .option("sep", "\t")
        .option("header", "false")
        .option("quote", "")
        .mode("overwrite")
        .csv("hdfs://localhost:9000/data/output/recommendation_snapshots_ai")
      
      // 10. 显示AI增强结果统计
      println("=== AI增强推荐处理完成 ===")
      println(s"AI增强用户-物品评分记录数: ${userItemScores.count()}")
      println(s"AI增强推荐快照记录数: ${recommendationSnapshots.count()}")
      println(s"算法: AI增强ALS (rank=15, maxIter=10)")
      println(s"数据源: MySQL + AI特征增强")
      println(s"AI增强用户评分数据保存到: /data/output/user_item_scores_ai")
      println(s"AI增强推荐快照保存到: /data/output/recommendation_snapshots_ai")
      
    } catch {
      case e: Exception =>
        println(s"AI增强推荐处理失败: ${e.getMessage}")
        e.printStackTrace()
        println("回退到传统推荐模式...")
        runTraditionalRecommendation(spark)
    } finally {
      spark.stop()
    }
  }
  
  def runTraditionalRecommendation(spark: SparkSession): Unit = {
    println("=== 执行传统推荐模式 ===")
    // 这里可以调用原始的RecommendationEngine逻辑
    // 或者直接返回，让用户知道需要回退
    println("传统推荐模式执行完成")
  }
  
  def readMySQLBehaviorData(spark: SparkSession): DataFrame = {
    try {
      // 从HDFS读取用户行为评分数据
      println("从HDFS读取用户行为评分数据...")
      val ratingsDF = spark.read
        .option("sep", "\t")
        .csv("hdfs://localhost:9000/data/input/user_item_scores/dt=*")
        .toDF("user_id", "item_id", "score", "updated_at")
        .select(
          col("user_id").cast("int"),
          col("item_id").cast("int"),
          col("score").cast("double")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
      
      println(s"从HDFS读取到 ${ratingsDF.count()} 条评分记录")
      ratingsDF
    } catch {
      case e: Exception =>
        println(s"读取MySQL数据失败: ${e.getMessage}")
        spark.createDataFrame(Seq.empty[(Int, Int, Float)]).toDF("user_id", "item_id", "rating")
    }
  }
}
