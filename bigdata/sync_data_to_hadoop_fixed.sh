#!/bin/bash
# ============================================
# 数据同步脚本：从MySQL导出数据并同步到Hadoop HDFS
# ============================================

set -euo pipefail

# 配置参数
MYSQL_HOST=${MYSQL_HOST:-127.0.0.1}
MYSQL_PORT=${MYSQL_PORT:-3306}
MYSQL_USER=${MYSQL_USER:-root}
MYSQL_PWD=${MYSQL_PWD:-ershou2025}
MYSQL_DB=${MYSQL_DB:-ershou_xcx}

HADOOP_SERVER=${HADOOP_SERVER:-47.100.37.43}
HADOOP_USER=${HADOOP_USER:-root}
HADOOP_SSH_KEY=${HADOOP_SSH_KEY:-/root/.ssh/id_ed25519}

EXPORT_DIR=${EXPORT_DIR:-/var/www/export}
DATE_TAG=$(date +%F)
ALGO_NAME=als
TOPK=20

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "数据同步到Hadoop HDFS"
echo "=========================================="
echo ""

# 创建导出目录
mkdir -p "$EXPORT_DIR"

echo -e "${YELLOW}[1/4] 从MySQL导出用户行为数据...${NC}"

# 导出用户-物品评分数据
mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
  --user="$MYSQL_USER" --password="$MYSQL_PWD" \
  --default-character-set=utf8mb4 --skip-column-names --batch "$MYSQL_DB" <<SQL \
  > "$EXPORT_DIR/user_item_scores_${DATE_TAG}.csv"
WITH base AS (
  SELECT
    ub.user_id,
    ub.item_id,
    CASE ub.behavior_type
      WHEN 'view' THEN 1 WHEN 'like' THEN 3
      WHEN 'favorite' THEN 5 WHEN 'message' THEN 4
      ELSE 1 END AS w,
    ub.created_at
  FROM user_behaviors ub
  WHERE ub.created_at >= NOW() - INTERVAL 7 DAY
    AND ub.item_id IS NOT NULL
),
scored AS (
  SELECT user_id, item_id, SUM(w) AS score, MAX(created_at) AS updated_at
  FROM base GROUP BY user_id, item_id
)
SELECT user_id, item_id, score, DATE_FORMAT(updated_at, '%Y-%m-%d %H:%i:%s')
FROM scored
ORDER BY user_id, score DESC, item_id ASC;
SQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 用户行为数据导出成功${NC}"
else
    echo -e "${RED}✗ 用户行为数据导出失败${NC}"
    exit 1
fi

echo -e "${YELLOW}[2/4] 从MySQL导出推荐快照数据...${NC}"

# 导出推荐快照数据
mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
  --user="$MYSQL_USER" --password="$MYSQL_PWD" \
  --default-character-set=utf8mb4 --skip-column-names --batch "$MYSQL_DB" <<SQL \
  > "$EXPORT_DIR/recommendation_snapshots_${DATE_TAG}.csv"
WITH base AS (
  SELECT ub.user_id, ub.item_id,
         CASE ub.behavior_type
           WHEN 'view' THEN 1 WHEN 'like' THEN 3
           WHEN 'favorite' THEN 5 WHEN 'message' THEN 4
           ELSE 1 END AS w
  FROM user_behaviors ub
  WHERE ub.created_at >= NOW() - INTERVAL 7 DAY AND ub.item_id IS NOT NULL
),
scored AS (
  SELECT user_id, item_id, SUM(w) AS score
  FROM base GROUP BY user_id, item_id
),
ranked AS (
  SELECT user_id, item_id, score,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY score DESC, item_id ASC) rn
  FROM scored
),
topk AS (
  SELECT user_id, item_id, score FROM ranked WHERE rn <= ${TOPK}
)
SELECT
  user_id,
  CONCAT('"', GROUP_CONCAT(item_id ORDER BY score DESC, item_id ASC SEPARATOR ','), '"') AS items_json,
  '${ALGO_NAME}' AS algorithm,
  DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s') AS generated_at,
  DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 1 DAY), '%Y-%m-%d %H:%i:%s') AS expires_at
FROM topk
GROUP BY user_id;
SQL

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 推荐快照数据导出成功${NC}"
else
    echo -e "${RED}✗ 推荐快照数据导出失败${NC}"
    exit 1
fi

echo -e "${YELLOW}[3/4] 上传数据到Hadoop HDFS...${NC}"

# 检查导出的数据
SCORES_COUNT=$(wc -l < "$EXPORT_DIR/user_item_scores_${DATE_TAG}.csv")
SNAPSHOTS_COUNT=$(wc -l < "$EXPORT_DIR/recommendation_snapshots_${DATE_TAG}.csv")

echo "导出的评分数据: ${SCORES_COUNT} 条"
echo "导出的推荐快照: ${SNAPSHOTS_COUNT} 条"

# 上传到Hadoop服务器
echo "上传评分数据到HDFS..."
scp -i "$HADOOP_SSH_KEY" "$EXPORT_DIR/user_item_scores_${DATE_TAG}.csv" \
    "$HADOOP_USER@$HADOOP_SERVER:/tmp/user_item_scores_${DATE_TAG}.csv"

echo "上传推荐快照到HDFS..."
scp -i "$HADOOP_SSH_KEY" "$EXPORT_DIR/recommendation_snapshots_${DATE_TAG}.csv" \
    "$HADOOP_USER@$HADOOP_SERVER:/tmp/recommendation_snapshots_${DATE_TAG}.csv"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据上传到Hadoop服务器成功${NC}"
else
    echo -e "${RED}✗ 数据上传到Hadoop服务器失败${NC}"
    exit 1
fi

echo -e "${YELLOW}[4/4] 将数据导入HDFS...${NC}"

# 在Hadoop服务器上导入数据到HDFS
ssh -i "$HADOOP_SSH_KEY" "$HADOOP_USER@$HADOOP_SERVER" << 'REMOTE_SCRIPT'
set -e

# 设置Hadoop环境
export HADOOP_HOME="/opt/hadoop/hadoop"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

# 获取当前日期
CURRENT_DATE=$(date +%F)

# 以hadoop用户身份创建HDFS目录
su - hadoop -c "hadoop fs -mkdir -p /data/input/user_item_scores/dt=$CURRENT_DATE"
su - hadoop -c "hadoop fs -mkdir -p /data/output"

# 以hadoop用户身份上传评分数据到HDFS
echo "上传评分数据到HDFS..."
su - hadoop -c "hadoop fs -rm -f /data/input/user_item_scores/dt=$CURRENT_DATE/part-00000"
su - hadoop -c "hadoop fs -put /tmp/user_item_scores_$CURRENT_DATE.csv /data/input/user_item_scores/dt=$CURRENT_DATE/part-00000"

# 以hadoop用户身份上传推荐快照到HDFS
echo "上传推荐快照到HDFS..."
su - hadoop -c "hadoop fs -rm -f /data/output/recommendation_snapshots/part-00000"
su - hadoop -c "hadoop fs -put /tmp/recommendation_snapshots_$CURRENT_DATE.csv /data/output/recommendation_snapshots/part-00000"

# 清理临时文件
rm -f /tmp/user_item_scores_$CURRENT_DATE.csv
rm -f /tmp/recommendation_snapshots_$CURRENT_DATE.csv

echo "数据导入HDFS完成"
REMOTE_SCRIPT

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 数据导入HDFS成功${NC}"
else
    echo -e "${RED}✗ 数据导入HDFS失败${NC}"
    exit 1
fi

# 清理旧文件
find "$EXPORT_DIR" -type f -name 'user_item_scores_*.csv' -mtime +7 -delete || true
find "$EXPORT_DIR" -type f -name 'recommendation_snapshots_*.csv' -mtime +7 -delete || true

echo ""
echo "=========================================="
echo -e "${GREEN}数据同步完成！${NC}"
echo "=========================================="
echo "同步日期: ${DATE_TAG}"
echo "评分数据: ${SCORES_COUNT} 条"
echo "推荐快照: ${SNAPSHOTS_COUNT} 条"
echo ""
