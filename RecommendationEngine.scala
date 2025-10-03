package com.example.recommendation

import org.apache.spark.sql.{SparkSession, DataFrame, Row}
import org.apache.spark.ml.recommendation.ALS
import org.apache.spark.sql.functions._
import java.time.LocalDateTime

object RecommendationEngine {
  def main(args: Array[String]): Unit = {
    // 创建Spark会话
    val spark = SparkSession.builder()
      .appName("RecommendationEngine")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()
    
    import spark.implicits._
    
    // 设置日志级别
    spark.sparkContext.setLogLevel("WARN")
    
    println("开始推荐系统数据处理...")
    
    try {
      // 1. 从MySQL读取所有数据
      println("从MySQL读取数据...")
      
      // 读取用户数据
      val usersDF = readMySQLTable(spark, "users")
      println(s"用户数量: ${usersDF.count()}")
      if (usersDF.count() > 0) usersDF.show(5)
      
      // 读取商品数据
      val itemsDF = readMySQLTable(spark, "items")
      println(s"商品数量: ${itemsDF.count()}")
      if (itemsDF.count() > 0) itemsDF.show(5)
      
      // 2. 构建用户行为评分数据
      println("构建用户行为评分数据...")
      
      // 方法1: 使用user_behaviors表（如果有评分信息）
      val behaviorDF = try {
        // 尝试从user_behaviors表读取，假设behavior_data包含评分
        spark.read
          .format("jdbc")
          .option("url", "jdbc:mysql://192.168.0.103:3306/ershou")
          .option("dbtable", 
            "(SELECT user_id, item_id, " +
            "CASE behavior_type " +
            "  WHEN 'view' THEN 1.0 " +
            "  WHEN 'like' THEN 4.0 " + 
            "  WHEN 'favorite' THEN 5.0 " +
            "  WHEN 'message' THEN 3.0 " +
            "  ELSE 2.0 END as rating " +
            "FROM user_behaviors WHERE item_id IS NOT NULL) as t")
          .option("user", "hadoop")
          .option("password", "20030208..")
          .option("driver", "com.mysql.cj.jdbc.Driver")
          .load()
      } catch {
        case e: Exception =>
          println(s"从user_behaviors表读取失败: ${e.getMessage}")
          // 方法2: 使用item_likes表作为基础评分数据
          spark.read
            .format("jdbc")
            .option("url", "jdbc:mysql://192.168.0.103:3306/ershou")
            .option("dbtable", 
              "(SELECT user_id, item_id, 5.0 as rating FROM item_likes WHERE item_id IS NOT NULL " +
              "UNION ALL " +
              "SELECT user_id, item_id, 4.0 as rating FROM favorites WHERE item_id IS NOT NULL) as t")
            .option("user", "hadoop")
            .option("password", "20030208..")
            .option("driver", "com.mysql.cj.jdbc.Driver")
            .load()
      }
      
      println(s"用户行为记录数: ${behaviorDF.count()}")
      if (behaviorDF.count() > 0) behaviorDF.show(10)
      
      // 3. 数据预处理
      println("数据预处理...")
      val preparedData = behaviorDF
        .filter(col("rating").isNotNull && col("rating") > 0)
        .select(
          col("user_id").cast("int").as("user_id"),
          col("item_id").cast("int").as("item_id"), 
          col("rating").cast("float").as("rating")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating")) // 同一用户对同一物品取最高评分
      
      println("预处理后数据样本:")
      preparedData.show(10)
      println(s"有效行为记录数: ${preparedData.count()}")
      
      // 检查是否有足够的数据进行训练
      val dataCount = preparedData.count()
      if (dataCount < 10) {
        println(s"警告: 数据量过少 ($dataCount 条记录)，可能影响模型效果")
        if (dataCount == 0) {
          println("错误: 没有有效数据，无法训练模型")
          createEmptyOutputFiles(spark)
          return
        }
      }
      
      // 4. ALS模型训练
      println("训练ALS模型...")
      val als = new ALS()
        .setUserCol("user_id")
        .setItemCol("item_id")
        .setRatingCol("rating")
        .setRank(10)
        .setMaxIter(5)
        .setRegParam(0.01)
        .setColdStartStrategy("drop")
      
      val model = als.fit(preparedData)
      
      // 5. 生成推荐
      println("生成推荐结果...")
      val userRecs = model.recommendForAllUsers(10) // 每个用户推荐10个商品
      
      println("推荐结果样本:")
      userRecs.show(10)
      
      val currentTime = LocalDateTime.now().toString
      val expiryTime = LocalDateTime.now().plusDays(7).toString
      
      // 6. 准备user_item_scores表数据
      println("准备用户-物品评分数据...")
      val userItemScores = userRecs.flatMap { row =>
        val userId = row.getInt(0)
        val recommendations = row.getAs[Seq[Row]](1)
        recommendations.map { rec =>
          (userId, rec.getInt(0), rec.getFloat(1), "als", currentTime)
        }
      }.toDF("user_id", "item_id", "score", "algorithm", "generated_at")
      
      // 7. 准备recommendation_snapshots表数据
      println("准备推荐快照数据...")
      val recommendationSnapshots = userRecs.map { row =>
        val userId = row.getInt(0)
        val itemIds = row.getAs[Seq[Row]](1).map(_.getInt(0))
        val jsonArray = itemIds.mkString("[", ",", "]")
        (userId, jsonArray, "als", currentTime, expiryTime)
      }.toDF("user_id", "recommended_items", "algorithm", "generated_at", "expires_at")
      
      // 8. 保存结果到HDFS - 修复：使用单个分区避免重复标题
      println("保存结果到HDFS...")
      
      // 先删除旧目录
      try {
        val fs = org.apache.hadoop.fs.FileSystem.get(spark.sparkContext.hadoopConfiguration)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/user_item_scores"), true)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/recommendation_snapshots"), true)
      } catch {
        case e: Exception => println(s"删除旧目录失败: ${e.getMessage}")
      }
      
      userItemScores
        .coalesce(1)  // 修复：使用单个分区
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/user_item_scores")
      
      recommendationSnapshots
        .coalesce(1)  // 修复：使用单个分区
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/recommendation_snapshots")
      
      // 9. 显示结果统计
      println("数据处理完成！")
      println(s"生成的用户-物品评分记录数: ${userItemScores.count()}")
      println(s"生成的推荐快照记录数: ${recommendationSnapshots.count()}")
      println(s"用户评分数据保存到: /data/output/user_item_scores")
      println(s"推荐快照保存到: /data/output/recommendation_snapshots")
      
    } catch {
      case e: Exception =>
        println(s"处理失败: ${e.getMessage}")
        e.printStackTrace()
        createEmptyOutputFiles(spark)
    } finally {
      spark.stop()
    }
  }
  
  def readMySQLTable(spark: SparkSession, tableName: String): DataFrame = {
    try {
      println(s"正在读取MySQL表: $tableName")
      
      // 请根据您的实际MySQL配置修改以下参数
      val url = "jdbc:mysql://192.168.0.103:3306/ershou"
      val user = "hadoop" 
      val password = "20030208.."
      
      val df = spark.read
        .format("jdbc")
        .option("url", url)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .option("dbtable", tableName)
        .option("user", user)
        .option("password", password)
        .load()
      
      println(s"成功读取表 $tableName: ${df.count()} 条记录")
      df
    } catch {
      case e: Exception =>
        println(s"读取MySQL表 $tableName 失败: ${e.getMessage}")
        // 返回空的DataFrame避免流程中断
        spark.createDataFrame(Seq.empty[(Int, String)]).toDF("id", "name")
    }
  }
  
  def createEmptyOutputFiles(spark: SparkSession): Unit = {
    try {
      println("创建空的输出文件作为占位符...")
      
      spark.createDataFrame(Seq.empty[(Int, Int, Float, String, String)])
        .toDF("user_id", "item_id", "score", "algorithm", "generated_at")
        .coalesce(1)
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/user_item_scores")
      
      spark.createDataFrame(Seq.empty[(Int, String, String, String, String)])
        .toDF("user_id", "recommended_items", "algorithm", "generated_at", "expires_at")
        .coalesce(1)
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/recommendation_snapshots")
      
      println("空的输出文件创建完成")
    } catch {
      case ex: Exception =>
        println(s"创建空输出文件失败: ${ex.getMessage}")
    }
  }
}
