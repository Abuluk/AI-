# Redis缓存配置说明

## Redis安装和配置

### Windows环境

1. **下载Redis for Windows**
   ```bash
   # 从GitHub下载Redis for Windows
   # https://github.com/microsoftarchive/redis/releases
   # 或使用Chocolatey安装
   choco install redis-64
   ```

2. **启动Redis服务**
   ```bash
   # 启动Redis服务器
   redis-server
   
   # 或在后台启动
   redis-server --service-install
   redis-server --service-start
   ```

3. **验证Redis连接**
   ```bash
   redis-cli ping
   # 应该返回 PONG
   ```

### Linux环境

1. **安装Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install redis-server
   
   # CentOS/RHEL
   sudo yum install redis
   # 或
   sudo dnf install redis
   ```

2. **启动Redis服务**
   ```bash
   sudo systemctl start redis
   sudo systemctl enable redis
   ```

3. **验证安装**
   ```bash
   redis-cli ping
   ```

## Redis配置优化

### redis.conf配置建议

```conf
# 内存配置
maxmemory 512mb
maxmemory-policy allkeys-lru

# 持久化配置
save 900 1
save 300 10
save 60 10000

# 网络配置
bind 127.0.0.1
port 6379
timeout 0

# 日志配置
loglevel notice
logfile /var/log/redis/redis-server.log

# 数据库数量
databases 16
```

## AI推荐缓存策略

### 缓存键设计
- **格式**: `ai_recommend:{user_id}:{behavior_hash}`
- **示例**: `ai_recommend:123:abc123def456`
- **TTL**: 30分钟 (1800秒)

### 缓存数据结构
```json
{
  "success": true,
  "recommendations": [...],
  "analysis": "用户偏好分析",
  "market_insights": "市场洞察",
  "recommendation_type": "ai_behavior_based",
  "cached_at": "2024-01-01T12:00:00Z"
}
```

## 监控和维护

### Redis监控命令
```bash
# 查看Redis信息
redis-cli info

# 查看内存使用
redis-cli info memory

# 查看连接数
redis-cli info clients

# 查看缓存命中率
redis-cli info stats

# 查看所有AI推荐缓存键
redis-cli keys "ai_recommend:*"

# 清除所有AI推荐缓存
redis-cli eval "return redis.call('del', unpack(redis.call('keys', 'ai_recommend:*')))" 0
```

### 性能监控
```bash
# 实时监控Redis命令
redis-cli monitor

# 查看慢查询
redis-cli slowlog get 10
```

## 故障处理

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务是否启动
   - 检查端口6379是否被占用
   - 检查防火墙设置

2. **内存不足**
   - 增加maxmemory配置
   - 调整maxmemory-policy策略
   - 清理过期缓存

3. **性能问题**
   - 监控慢查询日志
   - 优化缓存键设计
   - 考虑Redis集群

### 备用方案

如果Redis不可用，系统会自动切换到内存缓存模式：
- 使用Python字典作为缓存
- 定期清理过期缓存
- 限制缓存大小防止内存溢出

## 部署检查清单

- [ ] Redis服务已安装并启动
- [ ] Redis配置已优化
- [ ] Python redis包已安装 (`pip install redis`)
- [ ] 网络连接正常 (127.0.0.1:6379)
- [ ] 内存配置充足
- [ ] 监控脚本已部署
- [ ] 备份策略已制定
