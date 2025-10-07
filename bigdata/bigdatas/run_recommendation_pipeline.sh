[nyt@hadoop01 ~]$ cat /opt/scripts/run_recommendation_pipeline.sh
#!/bin/bash
# /opt/scripts/run_recommendation_pipeline.sh

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
    log "开始推荐系统数据处理流水线"
    
    # 检查必要命令
    check_command sbt
    check_command spark-submit
    check_command hadoop
    check_command sqoop
    
    # 1. 构建Spark作业
    log "构建Spark作业..."
    cd /opt/spark-jobs
    sbt assembly || error_exit "Spark作业构建失败"
    
    # 检查JAR文件是否生成
    if [ ! -f "target/scala-2.12/recommendation-engine-assembly-1.0.jar" ]; then
        error_exit "JAR文件未生成，请检查构建过程"
    fi
    
    # 2. 提交Spark作业
    log "提交Spark作业到YARN..."
    spark-submit \
        --class com.example.recommendation.RecommendationEngine \
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
        || error_exit "Spark作业执行失败"
    
    # 3. 等待Spark作业完成并检查输出
    log "等待Spark作业完成..."
    sleep 60
    
    # 检查HDFS输出路径
    log "检查HDFS输出文件..."
    check_hdfs_path "/data/output/user_item_scores" || error_exit "用户-物品评分输出目录不存在"
    check_hdfs_path "/data/output/recommendation_snapshots" || error_exit "推荐快照输出目录不存在"
    
    # 4. 导出用户-物品评分到MySQL（可选，根据实际需求）
    log "导出用户-物品评分数据到MySQL..."
    # 注意：需要根据实际MySQL配置修改以下参数
    # sqoop export \
    #     --connect "jdbc:mysql://your-mysql-host:3306/your_database" \
    #     --username "your_username" \
    #     --password "your_password" \
    #     --table "user_item_scores" \
    #     --export-dir "/data/output/user_item_scores" \
    #     --input-fields-terminated-by ',' \
    #     --columns "user_id,item_id,score,algorithm,generated_at" \
    #     --batch \
    #     --update-mode allowinsert \
    #     --update-key "user_id,item_id,algorithm" \
    #     || log "WARNING: 用户-物品评分导出失败（可忽略，如果MySQL未配置）"
    
    # 5. 导出推荐快照到MySQL（可选，根据实际需求）
    log "导出推荐快照数据到MySQL..."
    # 注意：需要根据实际MySQL配置修改以下参数
    # sqoop export \
    #     --connect "jdbc:mysql://your-mysql-host:3306/your_database" \
    #     --username "your_username" \
    #     --password "your_password" \
    #     --table "recommendation_snapshots" \
    #     --export-dir "/data/output/recommendation_snapshots" \
    #     --input-fields-terminated-by ',' \
    #     --input-optionally-enclosed-by '\"' \
    #     --columns "user_id,recommended_items,algorithm,generated_at,expires_at" \
    #     --batch \
    #     || log "WARNING: 推荐快照导出失败（可忽略，如果MySQL未配置）"
    
    # 6. 备份输出数据到备份目录（推荐）
    log "备份输出数据..."
    backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    hadoop fs -mkdir -p /data/backup/$backup_timestamp
    hadoop fs -cp /data/output/user_item_scores /data/backup/$backup_timestamp/ || log "WARNING: 用户评分备份失败"
    hadoop fs -cp /data/output/recommendation_snapshots /data/backup/$backup_timestamp/ || log "WARNING: 推荐快照备份失败"
    
    # 7. 清理临时数据（可选）
    log "清理临时数据..."
    # hadoop fs -rm -r /data/output/user_item_scores || log "WARNING: 清理用户评分数据失败"
    # hadoop fs -rm -r /data/output/recommendation_snapshots || log "WARNING: 清理推荐快照数据失败"
    
    log "推荐系统数据处理流水线完成！"
    
    # 显示作业统计信息
    log "作业统计："
    hadoop fs -du -h /data/output/user_item_scores 2>/dev/null || echo "用户评分数据不可用"
    hadoop fs -du -h /data/output/recommendation_snapshots 2>/dev/null || echo "推荐快照数据不可用"
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
    check_command sqoop
    log "环境检查完成，所有必要命令可用"
    exit 0
fi

# 执行主函数
main "$@"
[nyt@hadoop01 ~]$ 
