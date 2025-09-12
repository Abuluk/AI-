# 商品排序功能说明

## 功能概述

商品排序功能是一个基于时序动态权重的智能排序系统，能够根据商品的行为数据、卖家活跃度等信息，动态调整商品在列表中的排序位置。

## 核心特性

### 1. 时序动态权重排序
- **时间窗口**: 系统按设定的时间间隔（默认30分钟）收集商品行为数据
- **动态对比**: 比较当前时间段与上一个时间段的数据变化
- **权重计算**: 基于多项指标计算商品的综合权重

### 2. 对抗曲线算法
- **位置变化分析**: 分析商品排名位置的变化趋势
- **对抗调整**: 根据位置变化动态调整权重
- **平滑过渡**: 使用对数函数平滑权重变化，避免剧烈波动

### 3. 多维度指标
- **浏览量**: 商品在时间段内的浏览次数
- **互动数据**: 点赞数、收藏数、消息数
- **卖家活跃度**: 基于卖家行为计算的活跃度分数

## 数据库表结构

### 1. item_sorting_metrics (商品排序指标表)
记录商品在特定时间段内的行为数据：
- `item_id`: 商品ID
- `time_window_start/end`: 时间窗口
- `views_count`: 浏览量
- `likes_count`: 点赞数
- `favorites_count`: 收藏数
- `messages_count`: 消息数
- `seller_activity_score`: 卖家活跃度分数
- `position_rank`: 排名位置

### 2. item_sorting_weights (商品排序权重表)
记录商品的动态权重：
- `item_id`: 商品ID
- `time_period`: 时间周期标识
- `base_weight`: 基础权重
- `trend_weight`: 趋势权重
- `position_weight`: 位置权重
- `final_weight`: 最终权重
- `ranking_position`: 最终排名位置

### 3. sorting_configs (排序配置表)
存储排序算法的配置参数：
- `config_key`: 配置键
- `config_value`: 配置值（JSON格式）
- `description`: 配置描述

## API接口

### 1. 获取当前指标数据
```
GET /api/v1/item-sorting/metrics/current?time_window_minutes=30
```

### 2. 获取商品历史指标
```
GET /api/v1/item-sorting/metrics/history/{item_id}?limit=10
```

### 3. 获取当前权重数据
```
GET /api/v1/item-sorting/weights/current?time_period=2024-01-15-10:00&limit=100
```

### 4. 获取动态排序商品列表
```
GET /api/v1/item-sorting/sorted-items?page=1&size=20&time_period=2024-01-15-10:00
```

### 5. 运行排序算法（管理员）
```
POST /api/v1/item-sorting/run-algorithm?time_window_minutes=30
```

### 6. 获取排序配置
```
GET /api/v1/item-sorting/config
```

### 7. 更新排序配置（管理员）
```
PUT /api/v1/item-sorting/config
```

### 8. 获取排序趋势分析
```
GET /api/v1/item-sorting/analytics/trend?days=7
```

### 9. 获取单个商品排序分析
```
GET /api/v1/item-sorting/analytics/item/{item_id}?days=7
```

## 集成到商品列表

在商品列表API中新增了 `dynamic_sort` 排序选项：

```
GET /api/v1/items?order_by=dynamic_sort&skip=0&limit=20
```

## 算法详解

### 1. 权重计算公式

```
最终权重 = 基础权重 × 0.4 + 趋势权重 × 0.35 + 位置权重 × 0.25
```

### 2. 趋势权重计算

基于与上一周期的对比：
- 浏览量增长率权重: 30%
- 点赞增长率权重: 25%
- 收藏增长率权重: 20%
- 消息增长率权重: 15%
- 活跃度增长率权重: 10%

### 3. 位置权重计算（对抗曲线）

```
位置变化 = 上一周期排名 - 当前排名
位置调整 = log(1 + |位置变化|) × 调整系数
位置权重 = 1.0 + 位置调整 × 位置因子
```

### 4. 卖家活跃度计算

```
活跃度分数 = 发布商品数 × 0.4 + 回复消息数 × 0.3 + 登录活跃度 × 0.3
```

## 定时任务

系统自动运行定时任务：
- **频率**: 每30分钟执行一次
- **功能**: 收集指标数据、计算权重、更新排序
- **调度器**: 使用APScheduler实现

## 配置管理

### 默认配置

1. **时间窗口**: 30分钟
2. **权重占比**: 基础40% + 趋势35% + 位置25%
3. **趋势权重范围**: 0.5 - 1.5
4. **位置权重范围**: 0.7 - 1.3
5. **最大活跃度分数**: 10.0

### 配置初始化

运行初始化脚本：
```bash
python init_sorting_config.py
```

## 使用示例

### 1. 获取动态排序的商品列表
```python
import requests

# 获取按动态权重排序的商品
response = requests.get("http://localhost:8000/api/v1/items?order_by=dynamic_sort&limit=20")
items = response.json()
```

### 2. 手动运行排序算法
```python
# 管理员权限
headers = {"Authorization": "Bearer <admin_token>"}
response = requests.post(
    "http://localhost:8000/api/v1/item-sorting/run-algorithm?time_window_minutes=30",
    headers=headers
)
result = response.json()
```

### 3. 查看商品排序分析
```python
# 查看商品ID为123的排序分析
response = requests.get("http://localhost:8000/api/v1/item-sorting/analytics/item/123?days=7")
analytics = response.json()
```

## 监控和维护

### 1. 日志监控
系统会记录排序算法的运行日志：
- 任务启动/停止
- 算法执行结果
- 错误信息

### 2. 性能优化
- 数据库索引优化
- 批量数据处理
- 缓存机制

### 3. 数据清理
建议定期清理历史数据：
- 保留最近30天的指标数据
- 保留最近7天的权重数据
- 清理过期的配置记录

## 扩展功能

### 1. 个性化排序
- 基于用户行为偏好
- 地理位置权重
- 价格敏感度

### 2. A/B测试
- 不同排序算法对比
- 权重参数调优
- 效果评估

### 3. 实时调整
- 动态调整时间窗口
- 自适应权重参数
- 异常检测和处理

## 注意事项

1. **数据一致性**: 确保UserBehavior表中有完整的行为记录
2. **性能影响**: 排序算法会增加数据库负载，建议在低峰期运行
3. **配置备份**: 定期备份排序配置，避免参数丢失
4. **监控告警**: 设置算法运行失败的告警机制
5. **版本兼容**: 升级时注意数据库迁移的兼容性

