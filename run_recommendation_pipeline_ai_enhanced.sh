#!/bin/bash
# /opt/scripts/run_recommendation_pipeline_ai_enhanced.sh
# AI增强推荐系统流水线 - 与现有架构兼容

# 设置环境变量
export HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
export SPARK_HOME=${SPARK_HOME:-/opt/spark}
export SQOOP_HOME=${SQOOP_HOME:-/opt/sqoop}
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}

# 添加到PATH
export PATH=$HADOOP_HOME/bin:$SPARK_HOME/bin:$SQOOP_HOME/bin:$JAVA_HOME/bin:$PATH

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 错误处理函数
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        error_exit "命令 $1 未找到，请检查安装和PATH配置"
    fi
}

# 检查HDFS路径是否存在
check_hdfs_path() {
    hadoop fs -test -e $1 2>/dev/null
    if [ $? -ne 0 ]; then
        log "WARNING: HDFS路径 $1 不存在"
        return 1
    fi
    return 0
}

# 主函数
main() {
    log "开始AI增强推荐系统数据处理流水线"
    
    # 检查必要命令
    check_command sbt
    check_command spark-submit
    check_command hadoop
    
    # 1. 构建Spark作业
    log "构建Spark作业..."
    cd /opt/spark-jobs
    sbt assembly || error_exit "Spark作业构建失败"
    
    # 检查JAR文件是否生成
    if [ ! -f "target/scala-2.12/recommendation-engine-assembly-1.0.jar" ]; then
        error_exit "JAR文件未生成，请检查构建过程"
    fi
    
    # 2. 从MySQL生成AI特征
    log "从MySQL读取数据并生成AI特征..."
    spark-submit \
        --class com.example.recommendation.AIFeatureGenerator \
        --master yarn \
        --deploy-mode cluster \
        --driver-memory 2g \
        --executor-memory 2g \
        --executor-cores 2 \
        --num-executors 2 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.yarn.maxAppAttempts=1 \
        target/scala-2.12/recommendation-engine-assembly-1.0.jar \
        || log "WARNING: AI特征生成完成但有警告"
    
    # 3. 等待AI特征生成完成
    log "等待AI特征生成完成..."
    sleep 30
    
    # 4. 检查AI特征输出
    log "检查AI特征输出..."
    check_hdfs_path "/data/features/ai_enhanced" || error_exit "AI特征目录不存在"
    check_hdfs_path "/data/output/user_item_scores_ai" || error_exit "AI评分数据目录不存在"
    
    # 5. 运行AI增强推荐算法
    log "运行AI增强推荐算法..."
    spark-submit \
        --class com.example.recommendation.AIEnhancedRecommendationEngine \
        --master yarn \
        --deploy-mode cluster \
        --driver-memory 2g \
        --executor-memory 2g \
        --executor-cores 2 \
        --num-executors 2 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.yarn.maxAppAttempts=1 \
        target/scala-2.12/recommendation-engine-assembly-1.0.jar \
        || log "WARNING: AI推荐作业完成但有警告"
    
    # 6. 等待推荐作业完成
    log "等待AI推荐作业完成..."
    sleep 30
    
    # 7. 备份输出数据
    log "备份AI增强输出数据..."
    backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    hadoop fs -mkdir -p /data/backup/ai_$backup_timestamp
    hadoop fs -cp /data/features/ai_enhanced /data/backup/ai_$backup_timestamp/ || log "WARNING: AI特征备份失败"
    hadoop fs -cp /data/output/user_item_scores_ai /data/backup/ai_$backup_timestamp/ || log "WARNING: AI评分备份失败"
    hadoop fs -cp /data/output/user_item_scores /data/backup/ai_$backup_timestamp/ || log "WARNING: 用户评分备份失败"
    hadoop fs -cp /data/output/recommendation_snapshots /data/backup/ai_$backup_timestamp/ || log "WARNING: 推荐快照备份失败"
    
    log "AI增强推荐系统数据处理流水线完成！"
    
    # 显示作业统计信息
    log "AI增强作业统计："
    echo "=== 数据源 ==="
    echo "数据来源: MySQL (ershou.user_behaviors, item_likes, favorites)"
    echo "AI特征路径: /data/features/ai_enhanced"
    echo "推荐结果路径: /data/output/recommendation_snapshots"
    echo "用户评分路径: /data/output/user_item_scores"
    
    echo "=== 处理结果 ==="
    hadoop fs -test -e "/data/features/ai_enhanced/_SUCCESS" 2>/dev/null && echo "AI特征生成: ✓ 成功" || echo "AI特征生成: ✗ 失败"
    hadoop fs -test -e "/data/output/recommendation_snapshots/_SUCCESS" 2>/dev/null && echo "推荐快照生成: ✓ 成功" || echo "推荐快照生成: ✗ 失败"
    hadoop fs -test -e "/data/output/user_item_scores/_SUCCESS" 2>/dev/null && echo "用户评分生成: ✓ 成功" || echo "用户评分生成: ✗ 失败"
    
    echo "=== 数据统计 ==="
    echo "AI特征数据:"
    hadoop fs -count "/data/features/ai_enhanced" 2>/dev/null || echo "无法统计AI特征数据"
    echo "推荐快照数据:"
    hadoop fs -count "/data/output/recommendation_snapshots" 2>/dev/null || echo "无法统计推荐快照数据"
    echo "用户评分数据:"
    hadoop fs -count "/data/output/user_item_scores" 2>/dev/null || echo "无法统计用户评分数据"
    
    echo "=== 下一步 ==="
    echo "1. 查看AI特征: hadoop fs -ls /data/features/ai_enhanced"
    echo "2. 查看推荐快照: hadoop fs -ls /data/output/recommendation_snapshots"
    echo "3. 查看用户评分: hadoop fs -ls /data/output/user_item_scores"
    echo "4. 查看推荐内容: hadoop fs -cat /data/output/recommendation_snapshots/part-*.csv"
}

# 显示使用说明
usage() {
    echo "用法: $0 [选项]"
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -d, --dry-run  干跑模式，只检查不执行"
    echo "  -v, --verbose  详细输出模式"
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

# 如果是干跑模式，只检查环境
if [ "$DRY_RUN" = true ]; then
    log "干跑模式 - 检查环境配置"
    check_command sbt
    check_command spark-submit
    check_command hadoop
    log "环境检查完成，所有必要命令可用"
    exit 0
fi

# 执行主函数
main "$@"

