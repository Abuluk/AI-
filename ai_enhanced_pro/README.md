# 增强AI推荐系统 (Enhanced AI Recommendation System)

## 🚀 项目概述

这是一个真正发挥AI价值的推荐系统，通过商品语义理解、深度用户行为分析和多模型融合，实现智能化的个性化推荐。

## ✨ 核心特性

### 1. **商品语义理解**
- 分析商品标题、描述、分类等详细信息
- 提取商品特征标签和语义信息
- 基于商品内容进行智能分类和推荐

### 2. **深度用户行为分析**
- 分析用户行为模式、偏好、活跃度
- 识别用户类型（价格敏感型、质量追求型、探索型等）
- 生成个性化用户画像

### 3. **多模型融合推荐**
- **ALS模型**: 协同过滤推荐
- **随机森林**: 基于特征的推荐
- **梯度提升**: 非线性特征学习
- **模型融合**: 智能权重融合

### 4. **个性化特征生成**
- 基于AI分析生成个性化用户特征
- 基于商品语义生成商品特征
- 智能特征工程和特征选择

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MySQL数据库    │    │   增强AI服务     │    │   HDFS存储      │
│                 │    │                 │    │                 │
│ • 用户行为数据   │───▶│ • 语义理解      │───▶│ • AI特征存储    │
│ • 商品详细信息   │    │ • 行为分析      │    │ • 推荐结果存储  │
│ • 用户画像数据   │    │ • 特征生成      │    │ • 模型数据存储  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 数据预处理模块   │    │  AI分析模块     │    │ 推荐引擎模块    │
│                 │    │                 │    │                 │
│ • 数据清洗      │    │ • 用户行为分析  │    │ • ALS推荐       │
│ • 特征工程      │    │ • 商品语义分析  │    │ • 随机森林推荐  │
│ • 数据增强      │    │ • 个性化推荐    │    │ • 梯度提升推荐  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │  模型融合模块    │
                    │                 │
                    │ • 智能权重融合  │
                    │ • 推荐结果优化  │
                    │ • 最终推荐生成  │
                    └─────────────────┘
```

## 📁 项目结构

```
ai_enhanced_pro/
├── EnhancedAIFeatureGenerator.scala    # 增强AI特征生成器
├── EnhancedAIRecommendationEngine.scala # 增强AI推荐引擎
├── EnhancedAIService.py               # 增强AI服务
├── run_enhanced_ai_pipeline.sh        # 处理流水线脚本
├── build.sbt                          # 构建配置
└── README.md                          # 项目说明
```

## 🛠️ 技术栈

- **大数据处理**: Apache Spark 3.3.0
- **存储**: Apache Hadoop HDFS
- **数据库**: MySQL 8.0
- **AI服务**: 讯飞星火大模型
- **机器学习**: Spark MLlib, 随机森林, 梯度提升
- **编程语言**: Scala 2.12, Python 3.8

## 🚀 快速开始

### 1. 环境准备

```bash
# 设置环境变量
export HADOOP_HOME=/opt/hadoop
export SPARK_HOME=/opt/spark
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# 设置AI服务配置
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key"
export XUNFEI_API_SECRET="your_api_secret"
export XUNFEI_SPARK_URL="wss://spark-api.xf-yun.com/v3.1/chat"
```

### 2. 编译项目

```bash
cd ai_enhanced_pro
sbt compile
sbt assembly
```

### 3. 运行流水线

```bash
# 运行完整流水线
./run_enhanced_ai_pipeline.sh

# 检查系统状态
./run_enhanced_ai_pipeline.sh --check

# 运行测试模式
./run_enhanced_ai_pipeline.sh --test
```

## 📊 数据流程

### 1. **数据输入**
- 从MySQL读取完整的用户行为数据
- 包含商品详细信息（标题、描述、分类、价格等）
- 包含用户行为序列（浏览、点赞、收藏、消息等）

### 2. **AI分析**
- **用户行为分析**: 分析用户偏好、活跃度、行为模式
- **商品语义分析**: 理解商品内容、分类、特征
- **个性化推荐**: 基于用户画像和商品特征生成推荐

### 3. **特征生成**
- 生成个性化用户特征
- 生成商品语义特征
- 计算用户-商品匹配度

### 4. **模型训练**
- 训练多个推荐模型
- 进行模型融合
- 生成最终推荐结果

## 🔧 配置说明

### AI服务配置
```bash
# 讯飞星火大模型配置
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key"
export XUNFEI_API_SECRET="your_api_secret"
export XUNFEI_SPARK_URL="wss://spark-api.xf-yun.com/v3.1/chat"
```

### Spark配置
```scala
// 在build.sbt中配置
javaOptions ++= Seq(
  "-Xmx4g",
  "-XX:+UseG1GC",
  "-XX:MaxGCPauseMillis=200"
)
```

### HDFS路径配置
```
/data/features/enhanced_ai/          # 增强AI特征存储
/data/output/recommendations_*/      # 各模型推荐结果
/data/output/recommendation_snapshots_enhanced/  # 推荐快照
```

## 📈 性能优化

### 1. **Spark优化**
- 启用自适应查询执行
- 使用Kryo序列化
- 优化executor内存和核心数
- 启用G1垃圾收集器

### 2. **AI服务优化**
- 实现请求缓存机制
- 批量处理AI请求
- 设置合理的超时时间
- 实现降级策略

### 3. **存储优化**
- 使用Parquet格式存储
- 实现数据分区
- 定期清理临时文件
- 压缩存储数据

## 🔍 监控和调试

### 1. **日志监控**
```bash
# 查看Spark作业日志
yarn logs -applicationId <application_id>

# 查看HDFS操作日志
hadoop fs -ls /data/features/enhanced_ai/
```

### 2. **性能监控**
```bash
# 查看Spark作业状态
yarn application -list

# 查看HDFS使用情况
hadoop fs -du -h /data/
```

### 3. **推荐效果评估**
```bash
# 查看推荐结果
hadoop fs -cat /data/output/recommendation_snapshots_enhanced/part-*.csv

# 查看推荐统计
hadoop fs -count /data/output/recommendations_enhanced_fused/
```

## 🐛 故障排除

### 1. **常见问题**
- **AI服务连接失败**: 检查网络连接和API配置
- **HDFS写入失败**: 检查HDFS服务状态和权限
- **Spark作业失败**: 检查资源分配和依赖配置
- **内存不足**: 调整executor内存配置

### 2. **调试步骤**
1. 检查环境变量配置
2. 验证Hadoop和Spark服务状态
3. 查看详细错误日志
4. 检查数据格式和路径
5. 验证AI服务连接

## 📚 API文档

### EnhancedAIService.py

#### 用户行为分析
```python
async def analyze_user_behavior_deep(user_behaviors: List[Dict[str, Any]]) -> Dict[str, Any]
```

#### 商品语义分析
```python
async def analyze_item_semantic(items_data: List[Dict[str, Any]]) -> Dict[str, Any]
```

#### 个性化推荐
```python
async def generate_personalized_recommendations(
    user_profile: Dict[str, Any], 
    item_features: Dict[str, Any], 
    available_items: List[Dict[str, Any]],
    limit: int = 10
) -> Dict[str, Any]
```

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用Apache 2.0许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 📞 联系方式

- 项目维护者: AI Team
- 邮箱: ai-team@example.com
- 项目地址: https://github.com/example/enhanced-ai-recommendation

## 🙏 致谢

感谢以下开源项目的支持：
- Apache Spark
- Apache Hadoop
- 讯飞星火大模型
- MySQL
- Scala社区

