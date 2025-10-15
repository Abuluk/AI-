# 推荐系统启动脚本说明

## 📁 脚本文件

### 1. `start_all_recommendation_services.sh` - 完整启动脚本
**用途**: 从零开始启动所有推荐服务（包括编译）

**执行内容**:
1. 停止Hadoop服务
2. 编译所有Scala项目（ai_enhanced、ai_enhanced_pro、bigdatas、Incremental ai_enhanced）
3. 启动Hadoop服务
4. 运行普通大数据推荐（ALS）
5. 运行AI增强推荐
6. 启动推荐API服务

**使用场景**: 
- 首次部署
- 代码更新后需要重新编译
- 完整重启所有服务

**执行命令**:
```bash
# 添加执行权限（首次）
chmod +x /opt/scripts/bigdata/start_all_recommendation_services.sh

# 以hadoop用户执行
su - hadoop
cd /opt/scripts/bigdata
./start_all_recommendation_services.sh
```

**预计耗时**: 10-15分钟（取决于编译速度）

---

### 2. `restart_recommendation_only.sh` - 快速重启推荐任务
**用途**: 不重新编译，只重新运行推荐任务

**执行内容**:
1. 检查并启动HDFS（如需要）
2. 运行普通大数据推荐
3. 运行AI增强推荐
4. 重启API服务

**使用场景**: 
- 数据更新后需要重新生成推荐
- API服务异常需要重启
- 快速刷新推荐结果

**执行命令**:
```bash
# 添加执行权限（首次）
chmod +x /opt/scripts/bigdata/restart_recommendation_only.sh

# 以hadoop用户执行
su - hadoop
cd /opt/scripts/bigdata
./restart_recommendation_only.sh
```

**预计耗时**: 3-5分钟

---

### 3. `stop_all_recommendation_services.sh` - 停止所有服务
**用途**: 停止所有推荐相关服务

**执行内容**:
1. 停止推荐API服务
2. 释放8080端口
3. 停止Hadoop服务

**使用场景**: 
- 服务器维护
- 更新部署前
- 释放系统资源

**执行命令**:
```bash
# 添加执行权限（首次）
chmod +x /opt/scripts/bigdata/stop_all_recommendation_services.sh

# 以hadoop用户执行
su - hadoop
cd /opt/scripts/bigdata
./stop_all_recommendation_services.sh
```

**预计耗时**: 10秒

---

## 🚀 快速开始

### 首次部署
```bash
# 1. 切换到hadoop用户
su - hadoop

# 2. 进入脚本目录
cd /opt/scripts/bigdata

# 3. 添加执行权限
chmod +x *.sh

# 4. 执行完整启动
./start_all_recommendation_services.sh
```

### 日常使用
```bash
# 重启推荐任务（数据更新后）
./restart_recommendation_only.sh

# 停止所有服务（维护前）
./stop_all_recommendation_services.sh
```

---

## 🔍 验证服务

### 检查服务状态
```bash
# 1. 检查HDFS
jps | grep -E "NameNode|DataNode"

# 2. 检查API服务
ps aux | grep recommendation_api.py

# 3. 测试API健康
curl http://127.0.0.1:8080/health

# 4. 查看统计信息
curl http://127.0.0.1:8080/stats | python3 -m json.tool
```

### 测试推荐功能
```bash
# 测试普通推荐（用户ID=1）
curl http://127.0.0.1:8080/recommendations/1 | python3 -m json.tool

# 测试AI推荐（用户ID=1）
curl http://127.0.0.1:8080/ai_recommendations/1 | python3 -m json.tool
```

---

## 📝 日志位置

| 服务 | 日志位置 |
|------|---------|
| 推荐API | `/tmp/recommendation_api.log` |
| Hadoop NameNode | `$HADOOP_HOME/logs/` |
| Spark作业 | 控制台输出 |

### 查看日志
```bash
# 查看API日志
tail -f /tmp/recommendation_api.log

# 查看Hadoop日志
tail -f $HADOOP_HOME/logs/hadoop-hadoop-namenode-*.log
```

---

## ⚠️ 常见问题

### 1. 编译时内存不足
**问题**: `sbt assembly` 时出现 `Killed` 错误
**解决**: 脚本已设置 `-Xmx512M`，如仍有问题可调整

### 2. 端口被占用
**问题**: API启动失败，提示端口8080被占用
**解决**: 
```bash
# 查找占用进程
netstat -tlnp | grep :8080

# 杀死进程
fuser -k 8080/tcp
```

### 3. HDFS连接失败
**问题**: `Connection refused` 到 localhost:9000
**解决**: 
```bash
# 检查HDFS是否运行
jps | grep NameNode

# 重启HDFS
stop-dfs.sh
start-dfs.sh
```

### 4. 权限问题
**问题**: Permission denied
**解决**: 
```bash
# 确保使用hadoop用户
whoami  # 应该输出 hadoop

# 如果是root，切换到hadoop
su - hadoop
```

---

## 📊 性能优化建议

1. **定期清理**: 每周执行一次完整启动脚本，清理缓存
2. **监控内存**: 如果内存不足，可适当降低Spark的内存配置
3. **日志轮转**: 定期清理 `/tmp/recommendation_api.log`

---

## 🔧 维护计划

| 频率 | 操作 | 脚本 |
|------|------|------|
| 每天 | 刷新推荐结果 | `restart_recommendation_only.sh` |
| 每周 | 完整重启服务 | `start_all_recommendation_services.sh` |
| 代码更新后 | 重新编译部署 | `start_all_recommendation_services.sh` |

---

## 📞 支持

如有问题，请检查：
1. 日志文件: `/tmp/recommendation_api.log`
2. HDFS数据: `hadoop fs -ls /data/output/`
3. 服务状态: `jps` 和 `ps aux | grep recommendation`

