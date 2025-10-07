#!/bin/bash
# 推荐系统数据访问API（基于HDFS）

HDFS_BASE_PATH="/data/output"
LOG_FILE="/opt/scripts/logs/data_access.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 获取用户推荐
get_user_recommendations() {
    local user_id="$1"
    local limit="${2:-10}"
    local recommendation_type="${3:-bigdata}"  # 默认为大数据推荐
    
    log "获取用户 $user_id 的 $recommendation_type 推荐，限制: $limit 条"
    
    # 根据推荐类型选择不同的路径
    local hdfs_path
    if [ "$recommendation_type" = "ai" ]; then
        hdfs_path="$HDFS_BASE_PATH/recommendation_snapshots_ai"
    else
        hdfs_path="$HDFS_BASE_PATH/recommendation_snapshots"
    fi
    
    # 从HDFS读取推荐快照
    local result=$(hadoop fs -cat "$hdfs_path/part-*" 2>/dev/null | \
        grep "^$user_id," | head -1)
    
    if [ -n "$result" ]; then
        echo "$result"
        log "成功找到用户 $user_id 的 $recommendation_type 推荐"
    else
        log "未找到用户 $user_id 的 $recommendation_type 推荐"
        echo "null"
    fi
}

# 获取用户-物品评分
get_user_item_scores() {
    local user_id="$1"
    local recommendation_type="${2:-bigdata}"  # 默认为大数据推荐
    
    log "获取用户 $user_id 的 $recommendation_type 物品评分"
    
    # 根据推荐类型选择不同的路径
    local hdfs_path
    if [ "$recommendation_type" = "ai" ]; then
        hdfs_path="$HDFS_BASE_PATH/user_item_scores_ai"
    else
        hdfs_path="$HDFS_BASE_PATH/user_item_scores"
    fi
    
    # 从HDFS读取评分数据
    hadoop fs -cat "$hdfs_path/part-*" 2>/dev/null | \
        grep "^$user_id," | sort -t, -k3 -nr
}

# 获取热门推荐（降级方案）
get_popular_recommendations() {
    local limit="${1:-20}"
    
    log "获取热门推荐，限制: $limit 条"
    
    # 统计物品被推荐的次数
    hadoop fs -cat "$HDFS_BASE_PATH/user_item_scores/part-*" 2>/dev/null | \
        awk -F, '{print $2}' | sort | uniq -c | sort -nr | head -$limit | \
        awk '{print $2}'
}

# 检查数据新鲜度
check_data_freshness() {
    log "检查数据新鲜度..."
    
    # 检查_SUCCESS文件时间戳
    local success_file=$(hadoop fs -ls "$HDFS_BASE_PATH/user_item_scores/_SUCCESS" 2>/dev/null)
    
    if [ -n "$success_file" ]; then
        local timestamp=$(echo "$success_file" | awk '{print $6, $7}')
        log "数据最后更新时间: $timestamp"
        echo "$timestamp"
    else
        log "警告: 未找到_SUCCESS文件，数据可能不完整"
        echo "unknown"
    fi
}

# 数据统计
get_statistics() {
    log "获取数据统计信息"
    
    echo "=== 推荐系统数据统计 ==="
    echo "用户评分记录数: $(hadoop fs -cat "$HDFS_BASE_PATH/user_item_scores/part-*" 2>/dev/null | wc -l)"
    echo "推荐快照记录数: $(hadoop fs -cat "$HDFS_BASE_PATH/recommendation_snapshots/part-*" 2>/dev/null | wc -l)"
    echo "数据更新时间: $(check_data_freshness)"
}

# Web API模拟（可选，用于测试）
start_simple_api() {
    log "启动推荐数据API服务（端口8080）"
    python /opt/scripts/recommendation_api.py
}

# 主函数
main() {
    case "$1" in
        "get-user")
            get_user_recommendations "$2" "$3" "$4"
            ;;
        "get-scores")
            get_user_item_scores "$2" "$3"
            ;;
        "get-popular")
            get_popular_recommendations "$2"
            ;;
        "stats")
            get_statistics
            ;;
        "freshness")
            check_data_freshness
            ;;
        "api")
            start_simple_api
            ;;
        "help")
            echo "用法: $0 [command]"
            echo "命令:"
            echo "  get-user <user_id> [limit] [type]   获取用户推荐 (type: bigdata|ai)"
            echo "  get-scores <user_id> [type]         获取用户评分 (type: bigdata|ai)"
            echo "  get-popular [limit]                 获取热门推荐"
            echo "  stats                               数据统计"
            echo "  freshness                           检查数据新鲜度"
            echo "  api                                 启动简单API服务"
            echo ""
            echo "示例:"
            echo "  $0 get-user 1 10 bigdata    # 获取用户1的大数据推荐"
            echo "  $0 get-user 1 10 ai         # 获取用户1的AI增强推荐"
            echo "  $0 get-scores 1 bigdata     # 获取用户1的大数据评分"
            echo "  $0 get-scores 1 ai          # 获取用户1的AI增强评分"
            ;;
        *)
            echo "未知命令: $1"
            echo "使用: $0 help 查看帮助"
            ;;
    esac
}

# 创建日志目录
mkdir -p /opt/scripts/logs

main "$@"
