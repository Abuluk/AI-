# Hadoop集群部署指南 - AI+大数据增量特征优化系统

## 概述

本指南将帮助您将所有AI+大数据增量特征优化系统组件部署到Hadoop集群上，实现统一管理和部署。

## 部署架构

```
Hadoop集群 (单节点或多节点)
├── Spark作业 (Scala)
│   ├── IncrementalAIFeatureGenerator.scala
│   └── IncrementalAIEnhancedRecommendationEngine.scala
├── Python AI服务
│   ├── core/ai_feature_cache.py
│   ├── core/incremental_ai_optimizer.py
│   └── core/incremental_ai_integration_service.py
├── 流水线脚本
│   └── run_incremental_ai_recommendation_pipeline.sh
├── HDFS存储
│   ├── /data/features/ai_enhanced_incremental/
│   ├── /data/output/
│   └── /data/cache/ai_features/
└── 系统服务
    ├── ai-recommendation.service
    └── 定时任务
```

## 部署步骤

### 1. 环境准备

```bash
# 确保Hadoop集群正常运行
hadoop version
spark-submit --version

# 检查Java环境
java -version

# 检查Python环境
python3 --version
```

### 2. 运行自动部署脚本

```bash
# 下载部署脚本
chmod +x deploy_to_hadoop_cluster.sh

# 运行部署脚本
sudo ./deploy_to_hadoop_cluster.sh

# 或者干跑模式查看将要执行的操作
sudo ./deploy_to_hadoop_cluster.sh -d
```

### 3. 手动部署（可选）

如果自动部署脚本不适用，可以手动执行以下步骤：

#### 3.1 创建目录结构
```bash
sudo mkdir -p /opt/ai_recommendation_system/{core,spark-jobs,logs,config,scripts}
sudo chown -R hadoop:hadoop /opt/ai_recommendation_system
```

#### 3.2 安装Python依赖
```bash
sudo yum install -y python3 python3-pip  # CentOS/RHEL
# 或
sudo apt-get update && sudo apt-get install -y python3 python3-pip  # Ubuntu/Debian

pip3 install numpy pandas asyncio aiohttp sqlalchemy pymysql redis
```

#### 3.3 部署Scala Spark作业
```bash
cd /opt/ai_recommendation_system/spark-jobs

# 创建build.sbt文件
cat > build.sbt << 'EOF'
name := "incremental-ai-recommendation-engine"
version := "1.0"
scalaVersion := "2.12.15"
libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.3.0",
  "org.apache.spark" %% "spark-sql" % "3.3.0",
  "org.apache.spark" %% "spark-mllib" % "3.3.0",
  "mysql" % "mysql-connector-java" % "8.0.33"
)
EOF

# 创建项目结构
mkdir -p src/main/scala/com/example/recommendation

# 复制Scala文件
cp IncrementalAIFeatureGenerator.scala src/main/scala/com/example/recommendation/
cp IncrementalAIEnhancedRecommendationEngine.scala src/main/scala/com/example/recommendation/

# 构建项目
sbt assembly
```

#### 3.4 部署Python AI服务
```bash
cd /opt/ai_recommendation_system

# 复制Python文件
cp core/ai_feature_cache.py core/
cp core/incremental_ai_optimizer.py core/
cp core/incremental_ai_integration_service.py core/
```

#### 3.5 创建HDFS目录
```bash
hadoop fs -mkdir -p /data/features/ai_enhanced_incremental/{user_features,item_features,metadata}
hadoop fs -mkdir -p /data/output/{user_item_scores_ai_incremental,recommendation_snapshots_ai_incremental}
hadoop fs -mkdir -p /data/cache/ai_features
hadoop fs -mkdir -p /data/backup
```

## 配置说明

### 1. 环境变量配置

编辑 `/opt/ai_recommendation_system/config/env.sh`：

```bash
#!/bin/bash
# 环境变量配置

export HADOOP_HOME=/opt/hadoop
export SPARK_HOME=/opt/spark
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PYTHON_HOME=/usr/bin/python3

export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_CONF_DIR=$SPARK_HOME/conf

export PATH=$HADOOP_HOME/bin:$SPARK_HOME/bin:$JAVA_HOME/bin:$PYTHON_HOME:$PATH

# AI配置 - 请修改为您的实际配置
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key"
export XUNFEI_API_SECRET="your_api_secret"
export XUNFEI_SPARK_URL="your_spark_url"

# 部署目录
export DEPLOY_DIR=/opt/ai_recommendation_system
export PYTHONPATH=$DEPLOY_DIR:$PYTHONPATH
```

### 2. AI配置文件

编辑 `/opt/ai_recommendation_system/config/ai_config.json`：

```json
{
  "ai_provider": "xunfei",
  "xunfei": {
    "app_id": "${XUNFEI_APP_ID}",
    "api_key": "${XUNFEI_API_KEY}",
    "api_secret": "${XUNFEI_API_SECRET}",
    "spark_url": "${XUNFEI_SPARK_URL}"
  },
  "cache": {
    "cache_dir": "/data/cache/ai_features",
    "cache_ttl": 1800,
    "max_cache_size_mb": 1024
  },
  "database": {
    "mysql_url": "jdbc:mysql://192.168.0.108:3306/ershou",
    "mysql_user": "hadoop",
    "mysql_password": "20030208.."
  },
  "hdfs": {
    "namenode": "hdfs://hadoop01:9000",
    "features_path": "/data/features/ai_enhanced_incremental",
    "output_path": "/data/output"
  }
}
```

## 使用方法

### 1. 启动AI服务

```bash
# 使用systemd服务启动
sudo systemctl start ai-recommendation
sudo systemctl enable ai-recommendation

# 查看服务状态
sudo systemctl status ai-recommendation

# 查看服务日志
sudo journalctl -u ai-recommendation -f
```

### 2. 运行增量处理

```bash
# 手动运行增量处理
cd /opt/ai_recommendation_system
./scripts/run_incremental_ai_recommendation_pipeline.sh

# 查看处理日志
tail -f logs/ai_service.log
```

### 3. 测试AI服务

```bash
# 健康检查
cd /opt/ai_recommendation_system
source config/env.sh
python3 core/incremental_ai_integration_service.py health_check

# 获取统计信息
python3 core/incremental_ai_integration_service.py statistics

# 测试推荐功能
python3 core/incremental_ai_integration_service.py get_recommendations 1 10
```

### 4. 查看HDFS数据

```bash
# 查看特征矩阵
hadoop fs -ls /data/features/ai_enhanced_incremental/

# 查看推荐结果
hadoop fs -ls /data/output/recommendation_snapshots_ai_incremental/

# 查看推荐内容
hadoop fs -cat /data/output/recommendation_snapshots_ai_incremental/part-*.csv
```

## 监控和维护

### 1. 系统监控

```bash
# 查看HDFS使用情况
hadoop fs -df -h

# 查看Spark作业状态
yarn application -list

# 查看系统资源使用
top
htop
```

### 2. 日志管理

```bash
# 查看AI服务日志
tail -f /opt/ai_recommendation_system/logs/ai_service.log

# 查看Spark作业日志
yarn logs -applicationId application_xxx

# 查看系统服务日志
sudo journalctl -u ai-recommendation -f
```

### 3. 数据备份

```bash
# 备份特征矩阵
hadoop fs -cp /data/features/ai_enhanced_incremental /data/backup/features_$(date +%Y%m%d)

# 备份推荐结果
hadoop fs -cp /data/output /data/backup/output_$(date +%Y%m%d)
```

## 故障排除

### 1. 常见问题

**问题1：Python依赖缺失**
```bash
# 重新安装Python依赖
pip3 install numpy pandas asyncio aiohttp sqlalchemy pymysql redis
```

**问题2：HDFS连接失败**
```bash
# 检查Hadoop服务状态
sudo systemctl status hadoop-namenode
sudo systemctl status hadoop-datanode

# 检查HDFS连接
hadoop fs -ls /
```

**问题3：Spark作业失败**
```bash
# 检查Spark配置
cat $SPARK_HOME/conf/spark-defaults.conf

# 查看Spark作业日志
yarn logs -applicationId application_xxx
```

**问题4：AI服务无法启动**
```bash
# 检查AI配置
echo $XUNFEI_APP_ID
echo $XUNFEI_API_KEY

# 检查Python路径
echo $PYTHONPATH

# 手动启动AI服务
cd /opt/ai_recommendation_system
source config/env.sh
python3 core/incremental_ai_integration_service.py health_check
```

### 2. 性能优化

**内存优化**
```bash
# 调整Spark内存配置
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=4g
export SPARK_EXECUTOR_CORES=2
```

**HDFS优化**
```bash
# 调整HDFS块大小
hadoop fs -Ddfs.blocksize=134217728 -put large_file.txt /data/
```

## 扩展功能

### 1. 多节点部署

如果需要在多节点Hadoop集群上部署：

```bash
# 在NameNode上部署主服务
# 在DataNode上部署计算节点

# 修改配置文件中的HDFS地址
# 确保所有节点都能访问AI服务
```

### 2. 高可用配置

```bash
# 配置Hadoop高可用
# 配置Spark高可用
# 配置AI服务高可用
```

### 3. 监控集成

```bash
# 集成Prometheus监控
# 集成Grafana仪表板
# 配置告警规则
```

## 总结

通过本指南，您可以将所有AI+大数据增量特征优化系统组件部署到Hadoop集群上，实现：

1. **统一部署**：所有组件在同一个集群上
2. **统一管理**：使用systemd服务管理
3. **自动化运行**：定时任务自动执行
4. **完整监控**：日志和状态监控
5. **易于维护**：标准化的部署和维护流程

这种部署方式简化了系统架构，降低了运维复杂度，同时保持了高性能和可扩展性。
