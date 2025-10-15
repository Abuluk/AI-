#!/bin/bash
# ============================================
# 二手交易平台推荐系统一键启动脚本
# ============================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "二手交易平台推荐系统启动脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 基础目录
BIGDATA_DIR="/opt/scripts/bigdata"
JOBS_DIR="/opt/jobs"
DATA_SERVER="220.154.131.118"

# 设置环境变量
export HADOOP_HOME="/opt/hadoop/hadoop"
export SPARK_HOME="/opt/spark"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$PATH"

# 设置SBT环境变量
export TMPDIR=~/tmp
mkdir -p $TMPDIR
export SBT_OPTS="-Djava.io.tmpdir=$TMPDIR -Dsbt.global.base=$HOME/.sbt -Dsbt.boot.directory=$HOME/.sbt/boot -Dsbt.ivy.home=$HOME/.ivy2 -Xmx512M -Xms256M"

# ============================================
# 步骤0: 同步最新数据
# ============================================
echo -e "${YELLOW}[步骤 0/7] 同步最新数据...${NC}"
echo "从数据服务器同步最新用户行为数据..."
ssh -i /root/.ssh/id_ed25519 root@${DATA_SERVER} "/opt/jobs/sync_data_to_hadoop.sh"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据同步完成${NC}"
else
    echo -e "${RED}✗ 数据同步失败${NC}"
    exit 1
fi
echo ""

# ============================================
# 步骤1: 停止Hadoop服务
# ============================================
echo -e "${YELLOW}[步骤 1/7] 停止Hadoop服务...${NC}"
if jps | grep -q "NameNode"; then
    echo "正在停止HDFS..."
    $HADOOP_HOME/sbin/stop-dfs.sh 2>/dev/null || $HADOOP_HOME/bin/hdfs --daemon stop namenode
    sleep 3
    echo -e "${GREEN}✓ HDFS已停止${NC}"
else
    echo "HDFS未运行，跳过停止步骤"
fi
echo ""

# ============================================
# 步骤2: 编译所有Scala项目
# ============================================
echo -e "${YELLOW}[步骤 2/7] 编译所有Scala推荐引擎...${NC}"

# 定义需要编译的项目列表
SCALA_PROJECTS=(
    "ai_enhanced"
    "ai_enhanced_pro"
    "bigdatas"
    "Incremental ai_enhanced"
)

for project in "${SCALA_PROJECTS[@]}"; do
    PROJECT_DIR="${BIGDATA_DIR}/${project}"
    
    if [ -f "${PROJECT_DIR}/build.sbt" ]; then
        echo ""
        echo "----------------------------------------"
        echo "编译项目: ${project}"
        echo "----------------------------------------"
        
        cd "${PROJECT_DIR}"
        
        # 清理旧的编译文件
        echo "清理旧编译文件..."
        rm -rf target/ project/target/
        
        # 编译项目
        echo "开始编译（这可能需要几分钟）..."
        if sbt clean assembly; then
            echo -e "${GREEN}✓ ${project} 编译成功${NC}"
        else
            echo -e "${RED}✗ ${project} 编译失败${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ ${project} 没有build.sbt文件，跳过编译${NC}"
    fi
done

echo ""
echo -e "${GREEN}✓ 所有Scala项目编译完成${NC}"
echo ""

# ============================================
# 步骤3: 启动Hadoop服务
# ============================================
echo -e "${YELLOW}[步骤 3/7] 启动Hadoop服务...${NC}"
if ! jps | grep -q "NameNode"; then
    echo "正在启动HDFS..."
    $HADOOP_HOME/sbin/start-dfs.sh 2>/dev/null || {
        $HADOOP_HOME/bin/hdfs --daemon start namenode
        $HADOOP_HOME/bin/hdfs --daemon start datanode
    }
    
    # 等待HDFS启动
    echo "等待HDFS启动..."
    for i in {1..30}; do
        if jps | grep -q "NameNode"; then
            echo -e "${GREEN}✓ HDFS启动成功${NC}"
            break
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    
    # 验证HDFS
    sleep 3
    if hadoop fs -ls / >/dev/null 2>&1; then
        echo -e "${GREEN}✓ HDFS验证成功${NC}"
    else
        echo -e "${RED}✗ HDFS启动失败${NC}"
        exit 1
    fi
else
    echo "HDFS已在运行"
fi
echo ""

# ============================================
# 步骤4: 运行普通大数据推荐
# ============================================
echo -e "${YELLOW}[步骤 4/7] 运行普通大数据推荐（ALS）...${NC}"
if [ -f "${JOBS_DIR}/als_recommendation.py" ]; then
    echo "执行ALS推荐算法..."
    cd ${JOBS_DIR}
    
    if su - hadoop -c "cd ${JOBS_DIR} && python3 als_recommendation.py"; then
        echo -e "${GREEN}✓ ALS推荐生成成功${NC}"
        
        # 验证输出
        echo "验证推荐数据..."
        SNAPSHOT_COUNT=$(hadoop fs -cat /data/output/recommendation_snapshots/part-* 2>/dev/null | wc -l)
        echo "生成的推荐快照数: ${SNAPSHOT_COUNT}"
    else
        echo -e "${RED}✗ ALS推荐生成失败${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ 找不到 ${JOBS_DIR}/als_recommendation.py${NC}"
    exit 1
fi
echo ""

# ============================================
# 步骤5: 运行AI增强推荐
# ============================================
echo -e "${YELLOW}[步骤 5/7] 运行AI增强推荐...${NC}"

cd "${BIGDATA_DIR}/ai_enhanced"

# 5.1 生成AI特征
echo ""
echo "----------------------------------------"
echo "5.1 生成AI特征..."
echo "----------------------------------------"
if su - hadoop -c "cd ${BIGDATA_DIR}/ai_enhanced && spark-submit \
    --class com.example.recommendation.AIFeatureGenerator \
    --master local[2] \
    --driver-memory 512m \
    --executor-memory 512m \
    --conf spark.sql.adaptive.enabled=true \
    target/scala-2.12/ai-enhanced-recommendation-assembly-1.0.jar"; then
    echo -e "${GREEN}✓ AI特征生成成功${NC}"
else
    echo -e "${RED}✗ AI特征生成失败${NC}"
    exit 1
fi

# 5.2 生成AI推荐
echo ""
echo "----------------------------------------"
echo "5.2 生成AI推荐结果..."
echo "----------------------------------------"
if su - hadoop -c "cd ${BIGDATA_DIR}/ai_enhanced && spark-submit \
    --class com.example.recommendation.AIEnhancedRecommendationEngine \
    --master local[2] \
    --driver-memory 512m \
    --executor-memory 512m \
    --conf spark.sql.adaptive.enabled=true \
    target/scala-2.12/ai-enhanced-recommendation-assembly-1.0.jar"; then
    echo -e "${GREEN}✓ AI推荐生成成功${NC}"
    
    # 验证输出
    echo "验证AI推荐数据..."
    AI_SNAPSHOT_COUNT=$(hadoop fs -cat /data/output/recommendation_snapshots_ai/part-* 2>/dev/null | wc -l)
    echo "生成的AI推荐快照数: ${AI_SNAPSHOT_COUNT}"
else
    echo -e "${RED}✗ AI推荐生成失败${NC}"
    exit 1
fi
echo ""

# ============================================
# 步骤6: 启动推荐API服务
# ============================================
echo -e "${YELLOW}[步骤 6/7] 启动推荐API服务...${NC}"

# 停止旧的API服务
echo "停止旧的API服务..."
pkill -f recommendation_api.py || true
sleep 2

# 确认端口已释放
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "端口8080仍被占用，强制释放..."
    fuser -k 8080/tcp 2>/dev/null || true
    sleep 2
fi

# 启动新的API服务
echo "启动推荐API服务..."
cd /opt/scripts
nohup python3 recommendation_api.py > /tmp/recommendation_api.log 2>&1 &
API_PID=$!

# 等待API启动
echo "等待API服务启动..."
sleep 5

# 验证API服务
if curl -s "http://127.0.0.1:8080/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ 推荐API服务启动成功 (PID: ${API_PID})${NC}"
    echo "API日志: /tmp/recommendation_api.log"
else
    echo -e "${RED}✗ 推荐API服务启动失败${NC}"
    exit 1
fi
echo ""

# ============================================
# 步骤7: 完成总结
# ============================================
echo -e "${YELLOW}[步骤 7/7] 完成总结...${NC}"
echo "=========================================="
echo -e "${GREEN}所有服务启动完成！${NC}"
echo "=========================================="
echo ""
echo "服务状态:"
echo "----------------------------------------"
echo "1. Hadoop HDFS:"
jps | grep -E "NameNode|DataNode" || echo "   未运行"
echo ""

echo "2. 推荐API服务:"
echo "   PID: ${API_PID}"
echo "   URL: http://0.0.0.0:8080"
echo "   日志: /tmp/recommendation_api.log"
echo ""

echo "3. 数据统计:"
curl -s "http://127.0.0.1:8080/stats" 2>/dev/null | python3 -m json.tool 2>/dev/null || echo "   无法获取统计信息"
echo ""

echo "测试命令:"
echo "----------------------------------------"
echo "# 测试健康检查"
echo "curl http://127.0.0.1:8080/health"
echo ""
echo "# 测试普通推荐（用户ID=1）"
echo "curl http://127.0.0.1:8080/recommendations/1"
echo ""
echo "# 测试AI推荐（用户ID=1）"
echo "curl http://127.0.0.1:8080/ai_recommendations/1"
echo ""
echo "# 查看统计信息"
echo "curl http://127.0.0.1:8080/stats"
echo ""

echo "查看日志:"
echo "----------------------------------------"
echo "tail -f /tmp/recommendation_api.log"
echo ""

echo "停止服务:"
echo "----------------------------------------"
echo "kill ${API_PID}  # 停止API服务"
echo "stop-dfs.sh      # 停止HDFS"
echo ""

echo -e "${GREEN}启动完成！${NC}"

