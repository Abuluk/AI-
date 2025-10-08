#!/bin/bash
# Enhanced AI Recommendation Pipeline
# 增强AI推荐系统流水线 - 真正发挥AI价值的版本

# 设置环境变量
export HADOOP_HOME=${HADOOP_HOME:-/opt/hadoop}
export SPARK_HOME=${SPARK_HOME:-/opt/spark}
export SQOOP_HOME=${SQOOP_HOME:-/opt/sqoop}
export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}
export PYTHONPATH=${PYTHONPATH:-/opt/python}

# 添加到PATH
export PATH=$HADOOP_HOME/bin:$SPARK_HOME/bin:$SQOOP_HOME/bin:$JAVA_HOME/bin:$PYTHONPATH:$PATH

# AI服务配置
export XUNFEI_APP_ID=${XUNFEI_APP_ID:-""}
export XUNFEI_API_KEY=${XUNFEI_API_KEY:-""}
export XUNFEI_API_SECRET=${XUNFEI_API_SECRET:-""}
export XUNFEI_SPARK_URL=${XUNFEI_SPARK_URL:-"wss://spark-api.xf-yun.com/v3.1/chat"}

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

# 检查AI服务配置
check_ai_service() {
    log "检查AI服务配置..."
    
    if [ -z "$XUNFEI_APP_ID" ] || [ -z "$XUNFEI_API_KEY" ] || [ -z "$XUNFEI_API_SECRET" ]; then
        log "WARNING: AI配置不完整，将使用模拟AI分析"
        log "请设置以下环境变量："
        log "  XUNFEI_APP_ID     讯飞AI应用ID"
        log "  XUNFEI_API_KEY    讯飞AI API密钥"
        log "  XUNFEI_API_SECRET 讯飞AI API密钥"
        log "  XUNFEI_SPARK_URL  讯飞AI服务URL"
        return 1
    else
        log "AI服务配置检查通过"
        return 0
    fi
}

# 主函数
main() {
    log "开始增强AI推荐系统数据处理流水线"
    log "版本: Enhanced AI Recommendation Pipeline v2.0"
    log "特性: 商品语义理解 + 深度用户行为分析 + 多模型融合推荐"
    
    # 检查必要命令
    check_command sbt
    check_command spark-submit
    check_command hadoop
    check_command python3
    
    # 检查AI服务配置
    check_ai_service
    
    # 1. 编译Scala项目
    log "编译增强AI推荐系统..."
    cd /opt/recommendation
    if ! sbt compile; then
        error_exit "Scala项目编译失败"
    fi
    
    # 2. 检查HDFS连接
    log "检查HDFS连接..."
    if ! hadoop fs -ls / &> /dev/null; then
        error_exit "HDFS连接失败，请检查Hadoop服务状态"
    fi
    
    # 3. 运行增强AI特征生成器
    log "运行增强AI特征生成器..."
    if ! spark-submit \
        --class com.example.recommendation.EnhancedAIFeatureGenerator \
        --master yarn \
        --deploy-mode cluster \
        --driver-memory 4g \
        --executor-memory 6g \
        --executor-cores 3 \
        --num-executors 5 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
        target/scala-2.12/recommendation_2.12-1.0.jar; then
        error_exit "增强AI特征生成失败"
    fi
    
    # 4. 检查增强AI特征输出
    log "检查增强AI特征输出..."
    check_hdfs_path "/data/features/enhanced_ai" || error_exit "增强AI特征目录不存在"
    check_hdfs_path "/data/output/user_item_scores_enhanced_ai" || error_exit "增强AI评分数据目录不存在"
    
    # 5. 运行增强AI推荐算法
    log "运行增强AI推荐算法..."
    if ! spark-submit \
        --class com.example.recommendation.EnhancedAIRecommendationEngine \
        --master yarn \
        --deploy-mode cluster \
        --driver-memory 6g \
        --executor-memory 8g \
        --executor-cores 4 \
        --num-executors 8 \
        --conf spark.sql.adaptive.enabled=true \
        --conf spark.sql.adaptive.coalescePartitions.enabled=true \
        --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
        --conf spark.executor.extraJavaOptions="-XX:+UseG1GC -XX:MaxGCPauseMillis=200" \
        target/scala-2.12/recommendation_2.12-1.0.jar; then
        error_exit "增强AI推荐算法失败"
    fi
    
    # 6. 检查推荐结果
    log "检查推荐结果..."
    check_hdfs_path "/data/output/recommendations_enhanced_als" || error_exit "ALS推荐结果不存在"
    check_hdfs_path "/data/output/recommendations_enhanced_rf" || error_exit "随机森林推荐结果不存在"
    check_hdfs_path "/data/output/recommendations_enhanced_gbt" || error_exit "梯度提升推荐结果不存在"
    check_hdfs_path "/data/output/recommendations_enhanced_fused" || error_exit "融合推荐结果不存在"
    check_hdfs_path "/data/output/recommendation_snapshots_enhanced" || error_exit "推荐快照不存在"
    
    # 7. 数据备份
    log "备份推荐结果..."
    backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    hadoop fs -mkdir -p /data/backup/enhanced_ai_$backup_timestamp
    hadoop fs -cp /data/features/enhanced_ai /data/backup/enhanced_ai_$backup_timestamp/ || log "WARNING: 增强AI特征备份失败"
    hadoop fs -cp /data/output/user_item_scores_enhanced_ai /data/backup/enhanced_ai_$backup_timestamp/ || log "WARNING: 增强AI评分备份失败"
    hadoop fs -cp /data/output/recommendations_enhanced_fused /data/backup/enhanced_ai_$backup_timestamp/ || log "WARNING: 融合推荐备份失败"
    hadoop fs -cp /data/output/recommendation_snapshots_enhanced /data/backup/enhanced_ai_$backup_timestamp/ || log "WARNING: 推荐快照备份失败"
    
    log "增强AI推荐系统数据处理流水线完成！"
    show_results
}

# 显示结果
show_results() {
    echo ""
    echo "=== 增强AI推荐系统处理结果 ==="
    echo ""
    echo "=== 数据源 ==="
    echo "数据来源: MySQL (完整用户行为数据 + 商品详细信息)"
    echo "AI特征路径: /data/features/enhanced_ai"
    echo "融合推荐结果路径: /data/output/recommendations_enhanced_fused"
    echo "推荐快照路径: /data/output/recommendation_snapshots_enhanced"
    echo "增强AI评分路径: /data/output/user_item_scores_enhanced_ai"
    echo ""
    echo "=== 处理结果 ==="
    hadoop fs -test -e "/data/features/enhanced_ai/_SUCCESS" 2>/dev/null && echo "增强AI特征生成: ✓ 成功" || echo "增强AI特征生成: ✗ 失败"
    hadoop fs -test -e "/data/output/recommendations_enhanced_fused/_SUCCESS" 2>/dev/null && echo "融合推荐生成: ✓ 成功" || echo "融合推荐生成: ✗ 失败"
    hadoop fs -test -e "/data/output/recommendation_snapshots_enhanced/_SUCCESS" 2>/dev/null && echo "推荐快照生成: ✓ 成功" || echo "推荐快照生成: ✗ 失败"
    hadoop fs -test -e "/data/output/user_item_scores_enhanced_ai/_SUCCESS" 2>/dev/null && echo "增强AI评分生成: ✓ 成功" || echo "增强AI评分生成: ✗ 失败"
    echo ""
    echo "=== 数据统计 ==="
    echo "增强AI特征数据:"
    hadoop fs -count "/data/features/enhanced_ai" 2>/dev/null || echo "无法统计增强AI特征数据"
    echo "融合推荐数据:"
    hadoop fs -count "/data/output/recommendations_enhanced_fused" 2>/dev/null || echo "无法统计融合推荐数据"
    echo "推荐快照数据:"
    hadoop fs -count "/data/output/recommendation_snapshots_enhanced" 2>/dev/null || echo "无法统计推荐快照数据"
    echo "增强AI评分数据:"
    hadoop fs -count "/data/output/user_item_scores_enhanced_ai" 2>/dev/null || echo "无法统计增强AI评分数据"
    echo ""
    echo "=== 系统特性 ==="
    echo "✓ 商品语义理解 - 分析商品标题、描述、分类等详细信息"
    echo "✓ 深度用户行为分析 - 分析用户行为模式、偏好、活跃度等"
    echo "✓ 多模型融合推荐 - ALS + 随机森林 + 梯度提升 + 模型融合"
    echo "✓ 个性化特征生成 - 基于AI分析生成个性化用户和商品特征"
    echo "✓ 智能推荐策略 - 基于用户画像和商品特征的智能匹配"
    echo ""
    echo "=== 下一步 ==="
    echo "1. 查看增强AI特征: hadoop fs -ls /data/features/enhanced_ai"
    echo "2. 查看融合推荐: hadoop fs -ls /data/output/recommendations_enhanced_fused"
    echo "3. 查看推荐快照: hadoop fs -ls /data/output/recommendation_snapshots_enhanced"
    echo "4. 查看增强AI评分: hadoop fs -ls /data/output/user_item_scores_enhanced_ai"
    echo "5. 查看推荐内容: hadoop fs -cat /data/output/recommendation_snapshots_enhanced/part-*.csv"
    echo ""
    echo "=== 性能优化建议 ==="
    echo "1. 监控Spark作业执行情况: yarn application -list"
    echo "2. 调整executor内存和核心数根据数据量"
    echo "3. 定期清理HDFS中的临时文件"
    echo "4. 监控AI API调用频率和成本"
    echo "5. 根据推荐效果调整模型参数"
}

# 帮助信息
show_help() {
    echo "增强AI推荐系统流水线"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --check    仅检查系统状态"
    echo "  -t, --test     运行测试模式"
    echo ""
    echo "环境变量:"
    echo "  XUNFEI_APP_ID     讯飞AI应用ID"
    echo "  XUNFEI_API_KEY    讯飞AI API密钥"
    echo "  XUNFEI_API_SECRET 讯飞AI API密钥"
    echo "  XUNFEI_SPARK_URL  讯飞AI服务URL"
    echo ""
    echo "示例:"
    echo "  $0                    # 运行完整流水线"
    echo "  $0 --check            # 检查系统状态"
    echo "  $0 --test             # 运行测试模式"
}

# 检查系统状态
check_system() {
    log "检查系统状态..."
    
    # 检查Hadoop
    if hadoop fs -ls / &> /dev/null; then
        echo "✓ Hadoop: 正常"
    else
        echo "✗ Hadoop: 异常"
    fi
    
    # 检查Spark
    if spark-submit --version &> /dev/null; then
        echo "✓ Spark: 正常"
    else
        echo "✗ Spark: 异常"
    fi
    
    # 检查Python
    if python3 --version &> /dev/null; then
        echo "✓ Python: 正常"
    else
        echo "✗ Python: 异常"
    fi
    
    # 检查AI配置
    if [ -n "$XUNFEI_APP_ID" ] && [ -n "$XUNFEI_API_KEY" ] && [ -n "$XUNFEI_API_SECRET" ]; then
        echo "✓ AI配置: 完整"
    else
        echo "✗ AI配置: 不完整"
    fi
    
    # 检查HDFS路径
    echo "HDFS路径状态:"
    check_hdfs_path "/data/features/enhanced_ai" && echo "  ✓ 增强AI特征" || echo "  ✗ 增强AI特征"
    check_hdfs_path "/data/output/recommendations_enhanced_fused" && echo "  ✓ 融合推荐" || echo "  ✗ 融合推荐"
    check_hdfs_path "/data/output/recommendation_snapshots_enhanced" && echo "  ✓ 推荐快照" || echo "  ✗ 推荐快照"
}

# 测试模式
test_mode() {
    log "运行测试模式..."
    
    # 运行小规模测试
    log "运行增强AI特征生成器测试..."
    if ! spark-submit \
        --class com.example.recommendation.EnhancedAIFeatureGenerator \
        --master local[2] \
        --driver-memory 2g \
        --executor-memory 2g \
        --conf spark.sql.adaptive.enabled=true \
        target/scala-2.12/recommendation_2.12-1.0.jar; then
        error_exit "增强AI特征生成器测试失败"
    fi
    
    log "测试模式完成"
}

# 解析命令行参数
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -c|--check)
        check_system
        exit 0
        ;;
    -t|--test)
        test_mode
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "未知选项: $1"
        show_help
        exit 1
        ;;
esac


