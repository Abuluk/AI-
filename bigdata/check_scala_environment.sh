#!/bin/bash
# 检查Scala/Spark环境是否具备

echo "=========================================="
echo "检查Scala/Spark推荐系统环境"
echo "=========================================="

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1: $(command -v $1)"
        if [ "$1" = "sbt" ]; then
            sbt --version 2>/dev/null | head -n 1
        elif [ "$1" = "spark-submit" ]; then
            spark-submit --version 2>&1 | grep "version" | head -n 1
        elif [ "$1" = "scala" ]; then
            scala -version 2>&1 | head -n 1
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $1: 未安装"
        return 1
    fi
}

check_path() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} 目录存在: $1"
        return 0
    else
        echo -e "${YELLOW}!${NC} 目录不存在: $1"
        return 1
    fi
}

missing_deps=0

echo ""
echo "1. 检查必需命令:"
check_command "sbt" || missing_deps=$((missing_deps+1))
check_command "scala" || missing_deps=$((missing_deps+1))
check_command "spark-submit" || missing_deps=$((missing_deps+1))
check_command "hadoop" || missing_deps=$((missing_deps+1))
check_command "java" || missing_deps=$((missing_deps+1))

echo ""
echo "2. 检查可选命令:"
check_command "sqoop"

echo ""
echo "3. 检查环境变量:"
echo "HADOOP_HOME: ${HADOOP_HOME:-未设置}"
echo "SPARK_HOME: ${SPARK_HOME:-未设置}"
echo "JAVA_HOME: ${JAVA_HOME:-未设置}"
echo "SCALA_HOME: ${SCALA_HOME:-未设置}"

echo ""
echo "4. 检查关键目录:"
check_path "/opt/spark"
check_path "/opt/hadoop"
check_path "/opt/spark-jobs"

echo ""
echo "5. 检查MySQL连接:"
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✓${NC} MySQL客户端已安装"
    # 不实际连接，避免密码问题
else
    echo -e "${YELLOW}!${NC} MySQL客户端未安装（可选）"
fi

echo ""
echo "6. 检查HDFS:"
if hadoop fs -ls / &> /dev/null; then
    echo -e "${GREEN}✓${NC} HDFS可访问"
    echo "HDFS根目录内容:"
    hadoop fs -ls / 2>/dev/null | head -n 5
else
    echo -e "${RED}✗${NC} HDFS不可访问"
    missing_deps=$((missing_deps+1))
fi

echo ""
echo "=========================================="
if [ $missing_deps -eq 0 ]; then
    echo -e "${GREEN}✓ 环境检查通过！可以使用Scala版本${NC}"
    echo ""
    echo "下一步:"
    echo "1. 上传Scala源文件到服务器"
    echo "2. 配置build.sbt"
    echo "3. 运行 sbt assembly 构建"
    echo "4. 运行推荐脚本"
else
    echo -e "${RED}✗ 环境不完整，缺少 $missing_deps 个必需组件${NC}"
    echo ""
    echo "建议:"
    echo "1. 如果可以安装Scala环境，使用完整的Scala版本"
    echo "2. 否则使用简化的Python版本（als_ai_enhanced_recommendation.py）"
fi
echo "=========================================="

