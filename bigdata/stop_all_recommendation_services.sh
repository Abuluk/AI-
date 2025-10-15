#!/bin/bash
# ============================================
# 二手交易平台推荐系统停止脚本
# ============================================

echo "=========================================="
echo "停止所有推荐服务"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 停止推荐API服务
echo -e "${YELLOW}[1/2] 停止推荐API服务...${NC}"
if pgrep -f recommendation_api.py > /dev/null; then
    pkill -f recommendation_api.py
    sleep 2
    
    # 确认是否停止
    if pgrep -f recommendation_api.py > /dev/null; then
        echo "强制停止..."
        pkill -9 -f recommendation_api.py
    fi
    
    echo -e "${GREEN}✓ 推荐API服务已停止${NC}"
else
    echo "推荐API服务未运行"
fi

# 释放端口
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "释放端口8080..."
    fuser -k 8080/tcp 2>/dev/null || true
fi
echo ""

# 2. 停止Hadoop服务
echo -e "${YELLOW}[2/2] 停止Hadoop服务...${NC}"
# 设置环境变量
export HADOOP_HOME="/opt/hadoop/hadoop"
export PATH="$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

if jps | grep -q "NameNode"; then
    $HADOOP_HOME/sbin/stop-dfs.sh 2>/dev/null || {
        $HADOOP_HOME/bin/hdfs --daemon stop namenode
        $HADOOP_HOME/bin/hdfs --daemon stop datanode
    }
    
    sleep 3
    echo -e "${GREEN}✓ Hadoop服务已停止${NC}"
else
    echo "Hadoop服务未运行"
fi
echo ""

# 验证
echo "=========================================="
echo "服务状态验证"
echo "=========================================="
echo ""

echo "Java进程:"
jps | grep -v "Jps" || echo "无Java进程运行"
echo ""

echo "API端口:"
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "端口8080仍被占用"
else
    echo "端口8080已释放"
fi
echo ""

echo -e "${GREEN}所有服务已停止${NC}"

