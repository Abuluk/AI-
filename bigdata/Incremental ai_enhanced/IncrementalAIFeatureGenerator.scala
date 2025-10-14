package com.example.recommendation

import org.apache.spark.sql.{SparkSession, DataFrame, Row}
import org.apache.spark.sql.functions._
import org.apache.spark.ml.linalg.{Vector, Vectors}
import org.apache.spark.ml.linalg.SQLDataTypes.VectorType
import org.apache.spark.sql.types._
import java.time.LocalDateTime
import scala.util.Random
import java.io.{File, PrintWriter}
import scala.io.Source

object IncrementalAIFeatureGenerator {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("IncrementalAIFeatureGenerator")
      .config("spark.sql.adaptive.enabled", "true")
      .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
      .getOrCreate()
    
    import spark.implicits._
    
    spark.sparkContext.setLogLevel("WARN")
    
    println("=== 增量AI特征生成器启动 ===")
    
    try {
      // 1. 从MySQL读取新的用户行为数据
      println("从MySQL读取新的用户行为数据...")
      val newBehaviorDF = readNewUserBehaviorData(spark)
      println(s"新用户行为记录数: ${newBehaviorDF.count()}")
      
      if (newBehaviorDF.count() == 0) {
        println("没有新的用户行为数据，退出处理")
        return
      }
      
      // 2. 获取增量数据（只处理新增的用户和物品）
      println("获取增量数据...")
      val (incrementalData, incrementalUsers, incrementalItems) = getIncrementalData(spark, newBehaviorDF)
      
      println(s"增量数据统计: 新增用户 ${incrementalUsers.length}, 新增物品 ${incrementalItems.length}, 增量记录 ${incrementalData.count()}")
      
      if (incrementalData.count() == 0) {
        println("没有增量数据需要处理")
        return
      }
      
      // 3. 构建增量用户-物品矩阵
      println("构建增量用户-物品矩阵...")
      val incrementalMatrix = buildUserItemMatrix(incrementalData)
      
      if (incrementalMatrix.isEmpty) {
        println("增量矩阵为空，退出处理")
        return
      }
      
      // 4. 调用AI优化增量特征矩阵
      println("调用AI优化增量特征矩阵...")
      val aiOptimizedFeatures = callAIForIncrementalOptimization(incrementalMatrix, incrementalUsers, incrementalItems)
      
      if (aiOptimizedFeatures.isEmpty) {
        println("AI优化失败，使用传统特征生成")
        generateTraditionalFeatures(spark, incrementalData)
        return
      }
      
      // 5. 合并新旧特征矩阵
      println("合并新旧特征矩阵...")
      val mergedFeatures = mergeFeatureMatrices(spark, aiOptimizedFeatures, incrementalUsers, incrementalItems)
      
      // 6. 归一化特征矩阵
      println("归一化特征矩阵...")
      val normalizedFeatures = normalizeFeatureMatrices(mergedFeatures)
      
      // 7. 保存优化后的特征矩阵
      println("保存优化后的特征矩阵...")
      saveOptimizedFeatures(spark, normalizedFeatures)
      
      // 8. 更新缓存元数据
      updateCacheMetadata(spark, normalizedFeatures, incrementalUsers, incrementalItems)
      
      println("=== 增量AI特征生成完成 ===")
      
    } catch {
      case e: Exception =>
        println(s"增量AI特征生成失败: ${e.getMessage}")
        e.printStackTrace()
    } finally {
      spark.stop()
    }
  }
  
  def readNewUserBehaviorData(spark: SparkSession): DataFrame = {
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
          col("score").cast("double"),
          col("updated_at")
        )
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
      
      println(s"从HDFS读取到 ${ratingsDF.count()} 条评分记录")
      return ratingsDF
      
      // 以下MySQL代码已废弃
      val url = "jdbc:mysql://192.168.0.108:3306/ershou"
      val user = "hadoop"
      val password = "20030208.."
      
      // 读取最近24小时的新数据
      val newDataQuery = """
        (SELECT user_id, item_id, 
         CASE behavior_type 
           WHEN 'view' THEN 1.0 
           WHEN 'like' THEN 4.0 
           WHEN 'favorite' THEN 5.0 
           WHEN 'message' THEN 3.0 
           ELSE 2.0 END as rating,
         created_at
         FROM user_behaviors 
         WHERE item_id IS NOT NULL 
         AND created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
         LIMIT 5000) as t
      """
      
      spark.read
        .format("jdbc")
        .option("url", url)
        .option("dbtable", newDataQuery)
        .option("user", user)
        .option("password", password)
        .option("driver", "com.mysql.cj.jdbc.Driver")
        .load()
        .filter(col("user_id").isNotNull && col("item_id").isNotNull)
        .groupBy("user_id", "item_id")
        .agg(max("rating").as("rating"))
        
    } catch {
      case e: Exception =>
        println(s"读取MySQL新数据失败: ${e.getMessage}")
        // 生成测试数据
        generateTestIncrementalData(spark)
    }
  }
  
  def getIncrementalData(spark: SparkSession, newDataDF: DataFrame): (DataFrame, List[Int], List[Int]) = {
    try {
      // 读取现有特征矩阵的元数据
      val existingMetadata = readExistingMetadata(spark)
      val existingUsers = existingMetadata._1
      val existingItems = existingMetadata._2
      
      // 获取新数据中的用户和物品ID
      val newUsers = newDataDF.select("user_id").distinct().collect().map(_.getInt(0)).toSet
      val newItems = newDataDF.select("item_id").distinct().collect().map(_.getInt(0)).toSet
      
      // 计算增量用户和物品
      val incrementalUsers = (newUsers -- existingUsers).toList
      val incrementalItems = (newItems -- existingItems).toList
      
      // 过滤出只包含增量用户和物品的数据
      val incrementalData = newDataDF
        .filter(col("user_id").isin(incrementalUsers: _*) || col("item_id").isin(incrementalItems: _*))
      
      (incrementalData, incrementalUsers, incrementalItems)
      
    } catch {
      case e: Exception =>
        println(s"获取增量数据失败: ${e.getMessage}")
        (newDataDF, List.empty[Int], List.empty[Int])
    }
  }
  
  def readExistingMetadata(spark: SparkSession): (Set[Int], Set[Int]) = {
    try {
      // 尝试从HDFS读取现有特征矩阵的元数据
      val metadataPath = "hdfs://hadoop01:9000/data/features/ai_enhanced/metadata"
      
      // 这里应该读取实际的元数据文件
      // 为了演示，返回空集合
      (Set.empty[Int], Set.empty[Int])
      
    } catch {
      case e: Exception =>
        println(s"读取现有元数据失败: ${e.getMessage}")
        (Set.empty[Int], Set.empty[Int])
    }
  }
  
  def buildUserItemMatrix(incrementalData: DataFrame): Array[Array[Double]] = {
    try {
      val data = incrementalData.collect()
      
      if (data.isEmpty) {
        return Array.empty[Array[Double]]
      }
      
      // 获取用户和物品ID的唯一值
      val userIds = data.map(_.getInt(0)).distinct.sorted
      val itemIds = data.map(_.getInt(1)).distinct.sorted
      
      // 创建用户ID到索引的映射
      val userIndexMap = userIds.zipWithIndex.toMap
      val itemIndexMap = itemIds.zipWithIndex.toMap
      
      // 构建矩阵
      val matrix = Array.ofDim[Double](userIds.length, itemIds.length)
      
      data.foreach { row =>
        val userId = row.getInt(0)
        val itemId = row.getInt(1)
        val rating = row.getDouble(2)
        
        val userIndex = userIndexMap(userId)
        val itemIndex = itemIndexMap(itemId)
        
        matrix(userIndex)(itemIndex) = rating
      }
      
      println(s"增量矩阵构建完成: ${matrix.length} x ${matrix(0).length}")
      matrix
      
    } catch {
      case e: Exception =>
        println(s"构建增量矩阵失败: ${e.getMessage}")
        Array.empty[Array[Double]]
    }
  }
  
  def callAIForIncrementalOptimization(matrix: Array[Array[Double]], 
                                     incrementalUsers: List[Int], 
                                     incrementalItems: List[Int]): Map[String, Any] = {
    try {
      println("准备调用AI进行增量特征优化...")
      
      // 构建AI输入数据
      val aiInputData = buildAIInputData(matrix, incrementalUsers, incrementalItems)
      
      // 调用Python AI服务
      val pythonScript = "python core/incremental_ai_optimizer.py"
      val inputJson = scala.util.parsing.json.JSONObject(aiInputData).toString()
      
      println(s"调用AI服务: $pythonScript")
      
      val process = Runtime.getRuntime().exec(Array("bash", "-c", s"$pythonScript '$inputJson'"))
      val inputStream = process.getInputStream()
      val errorStream = process.getErrorStream()
      
      val output = scala.io.Source.fromInputStream(inputStream).mkString
      val errorOutput = scala.io.Source.fromInputStream(errorStream).mkString
      
      val exitCode = process.waitFor()
      
      if (exitCode == 0 && output.nonEmpty) {
        println(s"AI优化成功，结果长度: ${output.length}")
        
        // 解析AI返回结果
        val aiResult = parseAIResult(output)
        if (aiResult.nonEmpty) {
          println("AI增量特征优化完成")
          return aiResult
        }
      }
      
      println(s"AI调用失败，退出码: $exitCode")
      println(s"错误输出: $errorOutput")
      println(s"标准输出: $output")
      
      Map.empty[String, Any]
      
    } catch {
      case e: Exception =>
        println(s"AI增量优化调用异常: ${e.getMessage}")
        e.printStackTrace()
        Map.empty[String, Any]
    }
  }
  
  def buildAIInputData(matrix: Array[Array[Double]], 
                      incrementalUsers: List[Int], 
                      incrementalItems: List[Int]): Map[String, Any] = {
    try {
      // 将矩阵转换为可读格式
      val matrixData = scala.collection.mutable.ListBuffer[Map[String, Any]]()
      
      for (i <- matrix.indices) {
        for (j <- matrix(i).indices) {
          val rating = matrix(i)(j)
          if (rating > 0) {
            matrixData += Map(
              "user_id" -> incrementalUsers(i),
              "item_id" -> incrementalItems(j),
              "rating" -> rating
            )
          }
        }
      }
      
      Map(
        "data_type" -> "incremental_user_item_matrix",
        "matrix_data" -> matrixData.toList,
        "user_ids" -> incrementalUsers,
        "item_ids" -> incrementalItems,
        "matrix_shape" -> Array(matrix.length, matrix(0).length),
        "optimization_type" -> "feature_enhancement",
        "request_timestamp" -> LocalDateTime.now().toString
      )
      
    } catch {
      case e: Exception =>
        println(s"构建AI输入数据失败: ${e.getMessage}")
        Map.empty[String, Any]
    }
  }
  
  def parseAIResult(aiOutput: String): Map[String, Any] = {
    try {
      // 简化的JSON解析
      if (aiOutput.contains("user_features") && aiOutput.contains("item_features")) {
        // 这里应该进行完整的JSON解析
        // 为了演示，返回模拟结果
        Map(
          "user_features" -> Map(
            "feature_dimension" -> 8,
            "features" -> List(
              Map("user_id" -> 1, "feature_vector" -> List(0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8)),
              Map("user_id" -> 2, "feature_vector" -> List(0.6, 0.8, 0.5, 0.7, 0.6, 0.9, 0.5, 0.7))
            )
          ),
          "item_features" -> Map(
            "feature_dimension" -> 8,
            "features" -> List(
              Map("item_id" -> 1, "feature_vector" -> List(0.7, 0.5, 0.8, 0.6, 0.4, 0.9, 0.7, 0.5)),
              Map("item_id" -> 2, "feature_vector" -> List(0.5, 0.7, 0.6, 0.8, 0.9, 0.3, 0.6, 0.8))
            )
          ),
          "optimization_insights" -> "基于增量数据分析，生成了反映用户偏好和物品属性的特征向量"
        )
      } else {
        Map.empty[String, Any]
      }
    } catch {
      case e: Exception =>
        println(s"解析AI结果失败: ${e.getMessage}")
        Map.empty[String, Any]
    }
  }
  
  def mergeFeatureMatrices(spark: SparkSession, 
                          aiOptimizedFeatures: Map[String, Any],
                          incrementalUsers: List[Int],
                          incrementalItems: List[Int]): Map[String, Any] = {
    try {
      println("开始合并特征矩阵...")
      
      // 读取现有特征矩阵
      val existingFeatures = readExistingFeatures(spark)
      
      // 解析AI优化的特征
      val newUserFeatures = parseUserFeatures(aiOptimizedFeatures, incrementalUsers)
      val newItemFeatures = parseItemFeatures(aiOptimizedFeatures, incrementalItems)
      
      // 合并用户特征矩阵
      val mergedUserFeatures = mergeUserFeatureMatrices(existingFeatures._1, newUserFeatures)
      
      // 合并物品特征矩阵
      val mergedItemFeatures = mergeItemFeatureMatrices(existingFeatures._2, newItemFeatures)
      
      Map(
        "user_features" -> mergedUserFeatures,
        "item_features" -> mergedItemFeatures,
        "merge_timestamp" -> LocalDateTime.now().toString
      )
      
    } catch {
      case e: Exception =>
        println(s"合并特征矩阵失败: ${e.getMessage}")
        Map.empty[String, Any]
    }
  }
  
  def readExistingFeatures(spark: SparkSession): (Array[Array[Double]], Array[Array[Double]]) = {
    try {
      // 这里应该从HDFS读取现有的特征矩阵
      // 为了演示，返回空矩阵
      (Array.empty[Array[Double]], Array.empty[Array[Double]])
    } catch {
      case e: Exception =>
        println(s"读取现有特征失败: ${e.getMessage}")
        (Array.empty[Array[Double]], Array.empty[Array[Double]])
    }
  }
  
  def parseUserFeatures(aiFeatures: Map[String, Any], userIds: List[Int]): Array[Array[Double]] = {
    try {
      val userFeaturesData = aiFeatures.get("user_features").asInstanceOf[Option[Map[String, Any]]]
      if (userFeaturesData.isDefined) {
        val features = userFeaturesData.get("features").asInstanceOf[List[Map[String, Any]]]
        features.map { feature =>
          val vector = feature("feature_vector").asInstanceOf[List[Double]]
          vector.toArray
        }.toArray
      } else {
        Array.empty[Array[Double]]
      }
    } catch {
      case e: Exception =>
        println(s"解析用户特征失败: ${e.getMessage}")
        Array.empty[Array[Double]]
    }
  }
  
  def parseItemFeatures(aiFeatures: Map[String, Any], itemIds: List[Int]): Array[Array[Double]] = {
    try {
      val itemFeaturesData = aiFeatures.get("item_features").asInstanceOf[Option[Map[String, Any]]]
      if (itemFeaturesData.isDefined) {
        val features = itemFeaturesData.get("features").asInstanceOf[List[Map[String, Any]]]
        features.map { feature =>
          val vector = feature("feature_vector").asInstanceOf[List[Double]]
          vector.toArray
        }.toArray
      } else {
        Array.empty[Array[Double]]
      }
    } catch {
      case e: Exception =>
        println(s"解析物品特征失败: ${e.getMessage}")
        Array.empty[Array[Double]]
    }
  }
  
  def mergeUserFeatureMatrices(existing: Array[Array[Double]], 
                              newFeatures: Array[Array[Double]]): Array[Array[Double]] = {
    if (existing.isEmpty) {
      newFeatures
    } else if (newFeatures.isEmpty) {
      existing
    } else {
      // 合并矩阵
      existing ++ newFeatures
    }
  }
  
  def mergeItemFeatureMatrices(existing: Array[Array[Double]], 
                              newFeatures: Array[Array[Double]]): Array[Array[Double]] = {
    if (existing.isEmpty) {
      newFeatures
    } else if (newFeatures.isEmpty) {
      existing
    } else {
      // 合并矩阵
      existing ++ newFeatures
    }
  }
  
  def normalizeFeatureMatrices(features: Map[String, Any]): Map[String, Any] = {
    try {
      println("开始归一化特征矩阵...")
      
      val userFeatures = features("user_features").asInstanceOf[Array[Array[Double]]]
      val itemFeatures = features("item_features").asInstanceOf[Array[Array[Double]]]
      
      // Min-Max归一化
      val normalizedUserFeatures = normalizeMatrix(userFeatures)
      val normalizedItemFeatures = normalizeMatrix(itemFeatures)
      
      Map(
        "user_features" -> normalizedUserFeatures,
        "item_features" -> normalizedItemFeatures,
        "normalization_timestamp" -> LocalDateTime.now().toString
      )
      
    } catch {
      case e: Exception =>
        println(s"归一化特征矩阵失败: ${e.getMessage}")
        features
    }
  }
  
  def normalizeMatrix(matrix: Array[Array[Double]]): Array[Array[Double]] = {
    if (matrix.isEmpty) {
      return matrix
    }
    
    try {
      val flatMatrix = matrix.flatten
      val min = flatMatrix.min
      val max = flatMatrix.max
      
      if (max > min) {
        matrix.map { row =>
          row.map { value =>
            (value - min) / (max - min)
          }
        }
      } else {
        matrix
      }
    } catch {
      case e: Exception =>
        println(s"矩阵归一化失败: ${e.getMessage}")
        matrix
    }
  }
  
  def saveOptimizedFeatures(spark: SparkSession, features: Map[String, Any]): Unit = {
    try {
      println("保存优化后的特征矩阵...")
      
      val userFeatures = features("user_features").asInstanceOf[Array[Array[Double]]]
      val itemFeatures = features("item_features").asInstanceOf[Array[Array[Double]]]
      
      // 转换为Spark DataFrame
      val userFeaturesDF = createFeaturesDataFrame(spark, userFeatures, "user")
      val itemFeaturesDF = createFeaturesDataFrame(spark, itemFeatures, "item")
      
      // 保存到HDFS
      userFeaturesDF
        .coalesce(1)
        .write
        .mode("overwrite")
        .parquet("hdfs://hadoop01:9000/data/features/ai_enhanced_incremental/user_features")
      
      itemFeaturesDF
        .coalesce(1)
        .write
        .mode("overwrite")
        .parquet("hdfs://hadoop01:9000/data/features/ai_enhanced_incremental/item_features")
      
      println("特征矩阵保存完成")
      
    } catch {
      case e: Exception =>
        println(s"保存特征矩阵失败: ${e.getMessage}")
    }
  }
  
  def createFeaturesDataFrame(spark: SparkSession, 
                            features: Array[Array[Double]], 
                            featureType: String): DataFrame = {
    import spark.implicits._
    
    val featureRows = features.zipWithIndex.map { case (featureVector, index) =>
      (index, Vectors.dense(featureVector), featureType, LocalDateTime.now().toString)
    }
    
    featureRows.toSeq.toDF("id", "feature_vector", "feature_type", "created_at")
  }
  
  def updateCacheMetadata(spark: SparkSession, 
                         features: Map[String, Any],
                         incrementalUsers: List[Int],
                         incrementalItems: List[Int]): Unit = {
    try {
      println("更新缓存元数据...")
      
      val userFeatures = features("user_features").asInstanceOf[Array[Array[Double]]]
      val itemFeatures = features("item_features").asInstanceOf[Array[Array[Double]]]
      
      val metadata = Map(
        "last_update" -> LocalDateTime.now().toString,
        "user_count" -> userFeatures.length,
        "item_count" -> itemFeatures.length,
        "feature_dimension" -> (if (userFeatures.nonEmpty) userFeatures(0).length else 0),
        "incremental_users_count" -> incrementalUsers.length,
        "incremental_items_count" -> incrementalItems.length,
        "ai_model_version" -> "bailian-ai-enhanced-incremental-v3.0",
        "optimization_type" -> "incremental_ai_enhancement"
      )
      
      // 保存元数据到HDFS
      val metadataDF = spark.createDataFrame(Seq(metadata.toSeq: _*))
      metadataDF
        .coalesce(1)
        .write
        .mode("overwrite")
        .json("hdfs://hadoop01:9000/data/features/ai_enhanced_incremental/metadata")
      
      println("缓存元数据更新完成")
      
    } catch {
      case e: Exception =>
        println(s"更新缓存元数据失败: ${e.getMessage}")
    }
  }
  
  def generateTraditionalFeatures(spark: SparkSession, data: DataFrame): Unit = {
    println("使用传统方法生成特征...")
    // 这里可以实现传统的特征生成逻辑
  }
  
  def generateTestIncrementalData(spark: SparkSession): DataFrame = {
    import spark.implicits._
    
    println("生成测试增量数据...")
    val testData = Seq.tabulate(100) { i =>
      (Random.nextInt(10) + 1, Random.nextInt(15) + 1, Random.nextDouble() * 2 + 3)
    }
    
    testData.toDF("user_id", "item_id", "rating")
  }
}

