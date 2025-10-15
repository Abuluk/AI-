#!/bin/bash
# ============================================
# 快速重启推荐任务（不重新编译）
# ============================================

set -e

echo "=========================================="
echo "快速重启推荐任务"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BIGDATA_DIR="/opt/scripts/bigdata"
JOBS_DIR="/opt/jobs"
DATA_SERVER="220.154.131.118"

# 设置环境变量
export HADOOP_HOME="/opt/hadoop/hadoop"
export SPARK_HOME="/opt/spark"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$SPARK_HOME/bin:$PATH"

# 0. 同步最新数据
echo -e "${YELLOW}[0/5] 同步最新数据...${NC}"
echo "从数据服务器同步最新用户行为数据..."
ssh -i /root/.ssh/id_ed25519 root@${DATA_SERVER} "/opt/jobs/sync_data_to_hadoop.sh"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据同步完成${NC}"
else
    echo -e "${RED}✗ 数据同步失败${NC}"
    exit 1
fi
echo ""

# 1. 确保HDFS运行
echo -e "${YELLOW}[1/5] 检查HDFS状态...${NC}"
if ! jps | grep -q "NameNode"; then
    echo "启动HDFS..."
    $HADOOP_HOME/sbin/start-dfs.sh 2>/dev/null || {
        $HADOOP_HOME/bin/hdfs --daemon start namenode
        $HADOOP_HOME/bin/hdfs --daemon start datanode
    }
    sleep 5
fi

if $HADOOP_HOME/bin/hadoop fs -ls / >/dev/null 2>&1; then
    echo -e "${GREEN}✓ HDFS正常${NC}"
else
    echo "HDFS启动失败"
    exit 1
fi
echo ""

# 2. 运行普通推荐
echo -e "${YELLOW}[2/5] 运行普通大数据推荐...${NC}"
cd ${JOBS_DIR}
su - hadoop -c "cd ${JOBS_DIR} && python3 als_recommendation.py"
echo -e "${GREEN}✓ 普通推荐完成${NC}"
echo ""

# 3. 运行AI推荐
echo -e "${YELLOW}[3/5] 运行AI增强推荐...${NC}"
cd "${BIGDATA_DIR}/ai_enhanced"

echo "生成AI特征..."
su - hadoop -c "cd ${BIGDATA_DIR}/ai_enhanced && spark-submit \
    --class com.example.recommendation.AIFeatureGenerator \
    --master local[2] \
    --driver-memory 512m \
    --executor-memory 512m \
    --conf spark.sql.adaptive.enabled=true \
    target/scala-2.12/ai-enhanced-recommendation-assembly-1.0.jar"

echo ""
echo "生成AI推荐..."
su - hadoop -c "cd ${BIGDATA_DIR}/ai_enhanced && spark-submit \
    --class com.example.recommendation.AIEnhancedRecommendationEngine \
    --master local[2] \
    --driver-memory 512m \
    --executor-memory 512m \
    --conf spark.sql.adaptive.enabled=true \
    target/scala-2.12/ai-enhanced-recommendation-assembly-1.0.jar"

echo -e "${GREEN}✓ AI推荐完成${NC}"
echo ""

# 4. 重启API服务
echo -e "${YELLOW}[4/5] 重启推荐API服务...${NC}"
pkill -f recommendation_api.py || true
sleep 2

cd /opt/scripts
nohup python3 recommendation_api.py > /tmp/recommendation_api.log 2>&1 &
sleep 3

if curl -s "http://127.0.0.1:8080/health" | grep -q "healthy"; then
    echo -e "${GREEN}✓ API服务已重启${NC}"
else
    echo "API服务启动失败"
    exit 1
fi
echo ""

# 5. 显示统计信息
echo -e "${YELLOW}[5/5] 显示推荐数据统计...${NC}"
echo "=========================================="
echo "推荐数据统计"
echo "=========================================="
curl -s "http://127.0.0.1:8080/stats" | python3 -m json.tool
echo ""

echo -e "${GREEN}推荐任务重启完成！${NC}"

