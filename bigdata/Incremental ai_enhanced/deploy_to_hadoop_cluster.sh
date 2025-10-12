#!/bin/bash
# deploy_to_hadoop_cluster.sh
# 将所有AI+大数据增量特征优化系统组件部署到Hadoop集群

# 设置环境变量
export HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
export SPARK_HOME=${SPARK_HOME:-/opt/spark}
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}
export PYTHON_HOME=${PYTHON_HOME:-/usr/bin/python3}

# 部署目录
DEPLOY_DIR="/opt/ai_recommendation_system"
CORE_DIR="$DEPLOY_DIR/core"
SPARK_JOBS_DIR="$DEPLOY_DIR/spark-jobs"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 错误处理函数
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error_exit "请使用root用户运行此脚本"
    fi
}

# 创建部署目录结构
create_directories() {
    log "创建部署目录结构..."
    
    mkdir -p $DEPLOY_DIR
    mkdir -p $CORE_DIR
    mkdir -p $SPARK_JOBS_DIR
    mkdir -p $DEPLOY_DIR/logs
    mkdir -p $DEPLOY_DIR/config
    mkdir -p $DEPLOY_DIR/scripts
    
    log "目录结构创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    log "安装Python依赖..."
    
    # 检查Python3是否安装
    if ! command -v python3 &> /dev/null; then
        log "安装Python3..."
        yum install -y python3 python3-pip || apt-get update && apt-get install -y python3 python3-pip
    fi
    
    # 安装Python包
    pip3 install numpy pandas asyncio aiohttp sqlalchemy pymysql redis
    
    log "Python依赖安装完成"
}

# 部署Scala Spark作业
deploy_spark_jobs() {
    log "部署Scala Spark作业..."
    
    # 复制Scala文件
    cp IncrementalAIFeatureGenerator.scala $SPARK_JOBS_DIR/
    cp IncrementalAIEnhancedRecommendationEngine.scala $SPARK_JOBS_DIR/
    
    # 创建build.sbt文件
    cat > $SPARK_JOBS_DIR/build.sbt << 'EOF'
name := "incremental-ai-recommendation-engine"

version := "1.0"

scalaVersion := "2.12.15"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.3.0",
  "org.apache.spark" %% "spark-sql" % "3.3.0",
  "org.apache.spark" %% "spark-mllib" % "3.3.0",
  "mysql" % "mysql-connector-java" % "8.0.33"
)

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}
EOF
    
    # 创建项目结构
    mkdir -p $SPARK_JOBS_DIR/src/main/scala/com/example/recommendation
    mkdir -p $SPARK_JOBS_DIR/project
    
    # 移动Scala文件到正确位置
    mv $SPARK_JOBS_DIR/IncrementalAIFeatureGenerator.scala $SPARK_JOBS_DIR/src/main/scala/com/example/recommendation/
    mv $SPARK_JOBS_DIR/IncrementalAIEnhancedRecommendationEngine.scala $SPARK_JOBS_DIR/src/main/scala/com/example/recommendation/
    
    log "Scala Spark作业部署完成"
}

# 部署Python AI服务
deploy_python_services() {
    log "部署Python AI服务..."
    
    # 复制Python文件
    cp core/ai_feature_cache.py $CORE_DIR/
    cp core/incremental_ai_optimizer.py $CORE_DIR/
    cp core/incremental_ai_integration_service.py $CORE_DIR/
    
    # 创建Python服务启动脚本
    cat > $DEPLOY_DIR/start_ai_services.sh << 'EOF'
#!/bin/bash
# 启动AI服务

export PYTHONPATH="$DEPLOY_DIR:$PYTHONPATH"
export HADOOP_CONF_DIR="/opt/hadoop/etc/hadoop"

# 启动AI集成服务
cd $DEPLOY_DIR
nohup python3 core/incremental_ai_integration_service.py health_check > logs/ai_service.log 2>&1 &

echo "AI服务已启动，日志文件: $DEPLOY_DIR/logs/ai_service.log"
EOF
    
    chmod +x $DEPLOY_DIR/start_ai_services.sh
    
    log "Python AI服务部署完成"
}

# 部署流水线脚本
deploy_pipeline_scripts() {
    log "部署流水线脚本..."
    
    # 复制流水线脚本
    cp run_incremental_ai_recommendation_pipeline.sh $DEPLOY_DIR/scripts/
    chmod +x $DEPLOY_DIR/scripts/run_incremental_ai_recommendation_pipeline.sh
    
    # 创建定时任务脚本
    cat > $DEPLOY_DIR/scripts/schedule_incremental_processing.sh << 'EOF'
#!/bin/bash
# 定时执行增量AI推荐处理

# 设置环境变量
export HADOOP_HOME=/opt/hadoop
export SPARK_HOME=/opt/spark
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export DEPLOY_DIR=/opt/ai_recommendation_system

# 切换到部署目录
cd $DEPLOY_DIR

# 执行增量处理
./scripts/run_incremental_ai_recommendation_pipeline.sh

# 记录执行时间
echo "$(date): 增量AI推荐处理完成" >> logs/schedule.log
EOF
    
    chmod +x $DEPLOY_DIR/scripts/schedule_incremental_processing.sh
    
    log "流水线脚本部署完成"
}

# 创建配置文件
create_config_files() {
    log "创建配置文件..."
    
    # 创建AI配置文件
    cat > $DEPLOY_DIR/config/ai_config.json << 'EOF'
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
EOF
    
    # 创建环境变量文件
    cat > $DEPLOY_DIR/config/env.sh << 'EOF'
#!/bin/bash
# 环境变量配置

export HADOOP_HOME=/opt/hadoop
export SPARK_HOME=/opt/spark
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PYTHON_HOME=/usr/bin/python3

export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export SPARK_CONF_DIR=$SPARK_HOME/conf

export PATH=$HADOOP_HOME/bin:$SPARK_HOME/bin:$JAVA_HOME/bin:$PYTHON_HOME:$PATH

# AI配置
export XUNFEI_APP_ID="your_app_id"
export XUNFEI_API_KEY="your_api_key"
export XUNFEI_API_SECRET="your_api_secret"
export XUNFEI_SPARK_URL="your_spark_url"

# 部署目录
export DEPLOY_DIR=/opt/ai_recommendation_system
export PYTHONPATH=$DEPLOY_DIR:$PYTHONPATH
EOF
    
    chmod +x $DEPLOY_DIR/config/env.sh
    
    log "配置文件创建完成"
}

# 创建HDFS目录
create_hdfs_directories() {
    log "创建HDFS目录..."
    
    # 创建特征存储目录
    hadoop fs -mkdir -p /data/features/ai_enhanced_incremental/user_features
    hadoop fs -mkdir -p /data/features/ai_enhanced_incremental/item_features
    hadoop fs -mkdir -p /data/features/ai_enhanced_incremental/metadata
    
    # 创建输出目录
    hadoop fs -mkdir -p /data/output/user_item_scores_ai_incremental
    hadoop fs -mkdir -p /data/output/recommendation_snapshots_ai_incremental
    
    # 创建缓存目录
    hadoop fs -mkdir -p /data/cache/ai_features
    
    # 创建备份目录
    hadoop fs -mkdir -p /data/backup
    
    log "HDFS目录创建完成"
}

# 创建系统服务
create_system_services() {
    log "创建系统服务..."
    
    # 创建AI服务systemd服务文件
    cat > /etc/systemd/system/ai-recommendation.service << EOF
[Unit]
Description=AI Recommendation Service
After=network.target hadoop.service

[Service]
Type=simple
User=hadoop
Group=hadoop
WorkingDirectory=$DEPLOY_DIR
EnvironmentFile=$DEPLOY_DIR/config/env.sh
ExecStart=$DEPLOY_DIR/start_ai_services.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建定时任务
    cat > /etc/cron.d/ai-recommendation << EOF
# 每小时执行一次增量AI推荐处理
0 * * * * hadoop $DEPLOY_DIR/scripts/schedule_incremental_processing.sh
EOF
    
    # 重新加载systemd
    systemctl daemon-reload
    
    log "系统服务创建完成"
}

# 设置权限
set_permissions() {
    log "设置文件权限..."
    
    # 设置目录所有者
    chown -R hadoop:hadoop $DEPLOY_DIR
    
    # 设置执行权限
    chmod +x $DEPLOY_DIR/scripts/*.sh
    chmod +x $DEPLOY_DIR/start_ai_services.sh
    chmod +x $DEPLOY_DIR/config/env.sh
    
    # 设置日志目录权限
    chmod 755 $DEPLOY_DIR/logs
    
    log "文件权限设置完成"
}

# 构建Spark作业
build_spark_jobs() {
    log "构建Spark作业..."
    
    cd $SPARK_JOBS_DIR
    
    # 检查sbt是否安装
    if ! command -v sbt &> /dev/null; then
        log "安装sbt..."
        curl -L https://github.com/sbt/sbt/releases/download/v1.8.2/sbt-1.8.2.tgz | tar xz -C /opt/
        ln -s /opt/sbt/bin/sbt /usr/local/bin/sbt
    fi
    
    # 构建项目
    sbt assembly
    
    if [ $? -eq 0 ]; then
        log "Spark作业构建成功"
    else
        error_exit "Spark作业构建失败"
    fi
}

# 测试部署
test_deployment() {
    log "测试部署..."
    
    # 测试HDFS连接
    hadoop fs -ls / > /dev/null
    if [ $? -eq 0 ]; then
        log "HDFS连接测试成功"
    else
        error_exit "HDFS连接测试失败"
    fi
    
    # 测试Python服务
    cd $DEPLOY_DIR
    source config/env.sh
    python3 -c "import numpy, pandas, asyncio; print('Python依赖测试成功')"
    
    # 测试AI服务
    python3 core/incremental_ai_integration_service.py health_check
    
    log "部署测试完成"
}

# 显示部署信息
show_deployment_info() {
    log "=== 部署完成 ==="
    
    echo "部署目录: $DEPLOY_DIR"
    echo "Spark作业目录: $SPARK_JOBS_DIR"
    echo "Python服务目录: $CORE_DIR"
    echo "配置文件目录: $DEPLOY_DIR/config"
    echo "日志目录: $DEPLOY_DIR/logs"
    
    echo ""
    echo "=== 使用方法 ==="
    echo "1. 启动AI服务:"
    echo "   systemctl start ai-recommendation"
    echo ""
    echo "2. 运行增量处理:"
    echo "   $DEPLOY_DIR/scripts/run_incremental_ai_recommendation_pipeline.sh"
    echo ""
    echo "3. 查看服务状态:"
    echo "   systemctl status ai-recommendation"
    echo ""
    echo "4. 查看日志:"
    echo "   tail -f $DEPLOY_DIR/logs/ai_service.log"
    echo ""
    echo "5. 手动测试AI服务:"
    echo "   cd $DEPLOY_DIR && python3 core/incremental_ai_integration_service.py health_check"
    
    echo ""
    echo "=== 配置文件 ==="
    echo "AI配置: $DEPLOY_DIR/config/ai_config.json"
    echo "环境变量: $DEPLOY_DIR/config/env.sh"
    echo "请根据实际情况修改配置文件中的参数"
}

# 主函数
main() {
    log "开始部署AI+大数据增量特征优化系统到Hadoop集群"
    
    check_root
    create_directories
    install_python_dependencies
    deploy_spark_jobs
    deploy_python_services
    deploy_pipeline_scripts
    create_config_files
    create_hdfs_directories
    create_system_services
    set_permissions
    build_spark_jobs
    test_deployment
    show_deployment_info
    
    log "部署完成！"
}

# 显示使用说明
usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -d, --dry-run  干跑模式，只检查不执行"
    echo "  -v, --verbose  详细输出模式"
    echo ""
    echo "此脚本将把所有AI+大数据组件部署到Hadoop集群上"
}

# 参数解析
VERBOSE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            usage
            exit 1
            ;;
    esac
done

# 如果是干跑模式，只显示将要执行的操作
if [ "$DRY_RUN" = true ]; then
    log "干跑模式 - 显示将要执行的操作"
    echo "1. 创建部署目录结构"
    echo "2. 安装Python依赖"
    echo "3. 部署Scala Spark作业"
    echo "4. 部署Python AI服务"
    echo "5. 部署流水线脚本"
    echo "6. 创建配置文件"
    echo "7. 创建HDFS目录"
    echo "8. 创建系统服务"
    echo "9. 设置文件权限"
    echo "10. 构建Spark作业"
    echo "11. 测试部署"
    exit 0
fi

# 执行主函数
main "$@"
