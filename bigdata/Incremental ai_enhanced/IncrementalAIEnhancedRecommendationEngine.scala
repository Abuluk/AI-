package com.example.recommendation

import org.apache.spark.sql.{SparkSession, DataFrame, Row}
import org.apache.spark.ml.recommendation.ALS
import org.apache.spark.ml.linalg.{Vector, Vectors}
import org.apache.spark.sql.functions._
import org.apache.spark.ml.feature.VectorAssembler
import org.apache.spark.ml.regression.LinearRegression
import org.apache.spark.ml.Pipeline
import java.time.LocalDateTime
import scala.util.Random

object IncrementalAIEnhancedRecommendationEngine {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("IncrementalAIEnhancedRecommendationEngine")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()
    
    import spark.implicits._
    
    spark.sparkContext.setLogLevel("WARN")
    
    println("=== 增量AI增强推荐引擎启动 ===")
    
    try {
      // 1. 读取AI优化的特征矩阵
      println("读取AI优化的特征矩阵...")
      val (userFeaturesDF, itemFeaturesDF) = loadAIOptimizedFeatures(spark)
      
      if (userFeaturesDF.isEmpty || itemFeaturesDF.isEmpty) {
        println("AI特征矩阵为空，使用传统推荐")
        runTraditionalRecommendation(spark)
        return
      }
      
      println(s"用户特征矩阵: ${userFeaturesDF.count()} 条记录")
      println(s"物品特征矩阵: ${itemFeaturesDF.count()} 条记录")
      
      // 2. 从MySQL读取用户行为数据
      println("从MySQL读取用户行为数据...")
      val behaviorDataDF = readUserBehaviorData(spark)
      println(s"用户行为记录数: ${behaviorDataDF.count()}")
      
      if (behaviorDataDF.count() < 10) {
        println("数据量过少，使用传统推荐")
        runTraditionalRecommendation(spark)
        return
      }
      
      // 3. 构建增强的用户-物品交互数据
      println("构建增强的用户-物品交互数据...")
      val enhancedInteractionData = buildEnhancedInteractionData(spark, behaviorDataDF, userFeaturesDF, itemFeaturesDF)
      println(s"增强交互数据记录数: ${enhancedInteractionData.count()}")
      
      // 4. 训练AI增强的推荐模型
      println("训练AI增强的推荐模型...")
      val aiEnhancedModel = trainAIEnhancedModel(spark, enhancedInteractionData)
      
      // 5. 生成AI增强推荐结果
      println("生成AI增强推荐结果...")
      val aiRecommendations = generateAIEnhancedRecommendations(spark, aiEnhancedModel, enhancedInteractionData)
      
      // 6. 保存推荐结果
      println("保存推荐结果...")
      saveRecommendationResults(spark, aiRecommendations)
      
      // 7. 显示推荐统计信息
      displayRecommendationStatistics(spark, aiRecommendations)
      
      println("=== 增量AI增强推荐引擎完成 ===")
      
    } catch {
      case e: Exception =>
        println(s"增量AI增强推荐处理失败: ${e.getMessage}")
        e.printStackTrace()
        println("回退到传统推荐模式...")
        runTraditionalRecommendation(spark)
    } finally {
      spark.stop()
    }
  }
  
  def loadAIOptimizedFeatures(spark: SparkSession): (DataFrame, DataFrame) = {
    try {
      // 读取用户特征矩阵
      val userFeaturesDF = spark.read
        .parquet("hdfs://hadoop01:9000/data/features/ai_enhanced_incremental/user_features")
      
      // 读取物品特征矩阵
      val itemFeaturesDF = spark.read
        .parquet("hdfs://hadoop01:9000/data/features/ai_enhanced_incremental/item_features")
      
      println("AI优化特征矩阵加载成功")
      (userFeaturesDF, itemFeaturesDF)
      
    } catch {
      case e: Exception =>
        println(s"加载AI特征矩阵失败: ${e.getMessage}")
        (spark.emptyDataFrame, spark.emptyDataFrame)
    }
  }
  
  def readUserBehaviorData(spark: SparkSession): DataFrame = {
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
      return ratingsDF
      
      // 以下MySQL代码已废弃
      val url = "jdbc:mysql://192.168.0.108:3306/ershou"
      val user = "hadoop"
      val password = "20030208.."
      
      spark.read
        .format("jdbc")
        .option("url", url)
        .option("dbtable", 
          "(SELECT user_id, item_id, " +
          "CASE behavior_type " +
          "  WHEN 'view' THEN 1.0 " +
          "  WHEN 'like' THEN 4.0 " + 
          "  WHEN 'favorite' THEN 5.0 " +
          "  WHEN 'message' THEN 3.0 " +
          "  ELSE 2.0 END as rating " +
          "FROM user_behaviors WHERE item_id IS NOT NULL) as t")
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .load()
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating"))
        
    } catch {
      case e: Exception =>
        println(s"读取MySQL数据失败: ${e.getMessage}")
        generateTestBehaviorData(spark)
    }
  }
  
  def buildEnhancedInteractionData(spark: SparkSession, 
                                 behaviorDataDF: DataFrame,
                                 userFeaturesDF: DataFrame,
                                 itemFeaturesDF: DataFrame): DataFrame = {
    try {
      println("开始构建增强交互数据...")
      
      // 为行为数据添加特征向量
      val behaviorWithUserFeatures = behaviorDataDF
        .join(userFeaturesDF, behaviorDataDF("user_id") === userFeaturesDF("id"), "left")
        .select(
          behaviorDataDF("user_id"),
          behaviorDataDF("item_id"),
          behaviorDataDF("rating"),
          userFeaturesDF("feature_vector").as("user_feature_vector")
        )
      
      val behaviorWithBothFeatures = behaviorWithUserFeatures
        .join(itemFeaturesDF, behaviorWithUserFeatures("item_id") === itemFeaturesDF("id"), "left")
        .select(
          behaviorWithUserFeatures("user_id"),
          behaviorWithUserFeatures("item_id"),
          behaviorWithUserFeatures("rating"),
          behaviorWithUserFeatures("user_feature_vector"),
          itemFeaturesDF("feature_vector").as("item_feature_vector")
        )
      
      // 计算用户-物品特征相似度
      val enhancedData = behaviorWithBothFeatures
        .withColumn("feature_similarity", calculateFeatureSimilarity(col("user_feature_vector"), col("item_feature_vector")))
        .withColumn("ai_enhanced_rating", 
          col("rating") * (1.0 + col("feature_similarity") * 0.2)) // AI特征增强评分
        .withColumn("ai_processing_timestamp", current_timestamp())
        .withColumn("ai_model_version", lit("bailian-ai-enhanced-incremental-v3.0"))
      
      println("增强交互数据构建完成")
      enhancedData
      
    } catch {
      case e: Exception =>
        println(s"构建增强交互数据失败: ${e.getMessage}")
        behaviorDataDF
    }
  }
  
  def calculateFeatureSimilarity = udf { (userVector: Vector, itemVector: Vector) =>
    try {
      if (userVector != null && itemVector != null) {
        // 计算余弦相似度
        val userArray = userVector.toArray
        val itemArray = itemVector.toArray
        
        if (userArray.length == itemArray.length) {
          val dotProduct = userArray.zip(itemArray).map { case (u, i) => u * i }.sum
          val userNorm = math.sqrt(userArray.map(x => x * x).sum)
          val itemNorm = math.sqrt(itemArray.map(x => x * x).sum)
          
          if (userNorm > 0 && itemNorm > 0) {
            dotProduct / (userNorm * itemNorm)
          } else {
            0.0
          }
        } else {
          0.0
        }
      } else {
        0.0
      }
    } catch {
      case _: Exception => 0.0
    }
  }
  
  def trainAIEnhancedModel(spark: SparkSession, enhancedData: DataFrame): ALS = {
    try {
      println("开始训练AI增强推荐模型...")
      
      // 准备训练数据
      val trainingData = enhancedData
        .select(
          col("user_id").cast("int").as("user_id"),
          col("item_id").cast("int").as("item_id"),
          col("ai_enhanced_rating").cast("float").as("rating")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull && col("rating") > 0)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating"))
      
      println(s"训练数据记录数: ${trainingData.count()}")
      
      // 配置AI增强的ALS模型
      val als = new ALS()
        .setUserCol("user_id")
        .setItemCol("item_id")
        .setRatingCol("rating")
        .setRank(20)  // 增加rank以利用AI特征
        .setMaxIter(15)  // 增加迭代次数
        .setRegParam(0.01)
        .setAlpha(1.0)  // 隐式反馈参数
        .setColdStartStrategy("drop")
        .setNonnegative(true)  // 非负约束
        
      // 训练模型
      val model = als.fit(trainingData)
      
      println("AI增强推荐模型训练完成")
      model
      
    } catch {
      case e: Exception =>
        println(s"训练AI增强模型失败: ${e.getMessage}")
        throw e
    }
  }
  
  def generateAIEnhancedRecommendations(spark: SparkSession, 
                                      model: ALS, 
                                      enhancedData: DataFrame): DataFrame = {
    try {
      println("生成AI增强推荐结果...")
      
      // 获取所有用户
      val allUsers = enhancedData.select("user_id").distinct().collect().map(_.getInt(0))
      println(s"为 ${allUsers.length} 个用户生成推荐")
      
      // 为每个用户生成推荐
      val userRecs = model.recommendForAllUsers(20)  // 每个用户推荐20个商品
      
      println("AI增强推荐结果生成完成")
      userRecs
      
    } catch {
      case e: Exception =>
        println(s"生成AI增强推荐失败: ${e.getMessage}")
        throw e
    }
  }
  
  def saveRecommendationResults(spark: SparkSession, recommendations: DataFrame): Unit = {
    try {
      println("保存推荐结果...")
      
      val currentTime = LocalDateTime.now().toString
      val expiryTime = LocalDateTime.now().plusDays(7).toString
      
      // 准备用户-物品评分数据
      val userItemScores = recommendations.flatMap { row =>
        val userId = row.getInt(0)
        val recommendations = row.getAs[Seq[Row]](1)
        recommendations.map { rec =>
          (userId, rec.getInt(0), rec.getFloat(1), "ai_enhanced_incremental_als", currentTime)
        }
      }.toDF("user_id", "item_id", "score", "algorithm", "generated_at")
      
      // 准备推荐快照数据
      val recommendationSnapshots = recommendations.map { row =>
        val userId = row.getInt(0)
        val itemIds = row.getAs[Seq[Row]](1).map(_.getInt(0))
        val jsonArray = itemIds.mkString("[", ",", "]")
        (userId, jsonArray, "ai_enhanced_incremental_als", currentTime, expiryTime)
      }.toDF("user_id", "recommended_items", "algorithm", "generated_at", "expires_at")
      
      // 先删除旧目录
      try {
        val fs = org.apache.hadoop.fs.FileSystem.get(spark.sparkContext.hadoopConfiguration)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/user_item_scores_ai_incremental"), true)
        fs.delete(new org.apache.hadoop.fs.Path("/data/output/recommendation_snapshots_ai_incremental"), true)
      } catch {
        case e: Exception => println(s"删除旧目录失败: ${e.getMessage}")
      }
      
      // 保存用户-物品评分数据
      userItemScores
        .coalesce(1)
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/user_item_scores_ai_incremental")
      
      // 保存推荐快照数据
      recommendationSnapshots
        .coalesce(1)
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/recommendation_snapshots_ai_incremental")
      
      println("推荐结果保存完成")
      
    } catch {
      case e: Exception =>
        println(s"保存推荐结果失败: ${e.getMessage}")
    }
  }
  
  def displayRecommendationStatistics(spark: SparkSession, recommendations: DataFrame): Unit = {
    try {
      println("=== 增量AI增强推荐统计信息 ===")
      
      val totalRecommendations = recommendations.count()
      val userCount = recommendations.select("user_id").distinct().count()
      
      println(s"总推荐记录数: $totalRecommendations")
      println(s"推荐用户数: $userCount")
      println(s"平均每用户推荐数: ${totalRecommendations.toDouble / userCount}")
      println(s"算法: AI增强增量ALS (rank=20, maxIter=15)")
      println(s"数据源: MySQL + AI增量特征增强")
      println(s"AI增强用户评分数据: /data/output/user_item_scores_ai_incremental")
      println(s"AI增强推荐快照: /data/output/recommendation_snapshots_ai_incremental")
      
      // 显示推荐结果样本
      println("\n推荐结果样本:")
      recommendations.show(10, truncate = false)
      
    } catch {
      case e: Exception =>
        println(s"显示推荐统计信息失败: ${e.getMessage}")
    }
  }
  
  def runTraditionalRecommendation(spark: SparkSession): Unit = {
    println("=== 执行传统推荐模式 ===")
    
    try {
      // 读取基础行为数据
      val behaviorDataDF = readUserBehaviorData(spark)
      
      if (behaviorDataDF.count() < 10) {
        println("数据量过少，无法进行推荐")
        return
      }
      
      // 训练传统ALS模型
      val als = new ALS()
        .setUserCol("user_id")
        .setItemCol("item_id")
        .setRatingCol("rating")
        .setRank(10)
        .setMaxIter(10)
        .setRegParam(0.01)
        .setColdStartStrategy("drop")
      
      val trainingData = behaviorDataDF
        .select(
          col("user_id").cast("int").as("user_id"),
          col("item_id").cast("int").as("item_id"),
          col("rating").cast("float").as("rating")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating"))
      
      val model = als.fit(trainingData)
      val userRecs = model.recommendForAllUsers(10)
      
      // 保存传统推荐结果
      val currentTime = LocalDateTime.now().toString
      val userItemScores = userRecs.flatMap { row =>
        val userId = row.getInt(0)
        val recommendations = row.getAs[Seq[Row]](1)
        recommendations.map { rec =>
          (userId, rec.getInt(0), rec.getFloat(1), "traditional_als", currentTime)
        }
      }.toDF("user_id", "item_id", "score", "algorithm", "generated_at")
      
      userItemScores
        .coalesce(1)
        .write
        .option("sep", ",")
        .option("header", "true")
        .mode("overwrite")
        .csv("hdfs://hadoop01:9000/data/output/user_item_scores_traditional")
      
      println("传统推荐模式执行完成")
      
    } catch {
      case e: Exception =>
        println(s"传统推荐模式执行失败: ${e.getMessage}")
    }
  }
  
  def generateTestBehaviorData(spark: SparkSession): DataFrame = {
    import spark.implicits._
    
    println("生成测试行为数据...")
    val testData = Seq.tabulate(200) { i =>
      (Random.nextInt(20) + 1, Random.nextInt(30) + 1, Random.nextDouble() * 2 + 3)
    }
    
    testData.toDF("user_id", "item_id", "rating")
  }
}

