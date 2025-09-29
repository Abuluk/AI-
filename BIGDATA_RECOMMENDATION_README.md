# 大数据推荐功能集成说明

## 功能概述

为web端项目添加了大数据推荐功能，作为新的排序类型"大数据推荐"，集成Hadoop推荐系统，为推荐商品添加特殊标识。

## 实现内容

### 1. 后端实现

#### 1.1 大数据推荐服务 (`core/bigdata_recommendation_service.py`)
- 集成Hadoop推荐API客户端
- 提供推荐商品获取和格式化功能
- 支持缓存机制（5分钟TTL）
- 包含连接测试功能

#### 1.2 API端点扩展 (`api/endpoints/items.py`)
- 新增 `bigdata_recommendation` 排序类型
- 支持用户ID参数传递
- 为推荐商品添加标识字段：
  - `is_bigdata_recommended`: true
  - `recommendation_source`: "bigdata"
  - `recommendation_algorithm`: "als"
  - `recommendation_reason`: "基于大数据分析推荐"

### 2. 前端实现

#### 2.1 排序选项 (`frontend/src/views/Home.vue`)
- 在排序下拉菜单中添加"大数据推荐"选项
- 更新排序参数转换逻辑
- 自动传递用户ID给API

#### 2.2 商品卡片标识 (`frontend/src/components/ProductCard.vue`)
- 添加"大数据推荐"标识徽章
- 使用渐变背景和阴影效果
- 位置在商品图片左上角

## 使用方法

### 1. 用户操作
1. 在首页排序下拉菜单中选择"大数据推荐"
2. 系统会自动调用Hadoop推荐API获取个性化推荐
3. 推荐商品会显示"大数据推荐"标识

### 2. API调用
```bash
GET /api/v1/items?order_by=bigdata_recommendation&user_id=1&limit=10
```

### 3. 响应格式
```json
[
  {
    "id": 151,
    "title": "商品标题",
    "price": 100.0,
    "is_bigdata_recommended": true,
    "recommendation_source": "bigdata",
    "recommendation_algorithm": "als",
    "recommendation_reason": "基于大数据分析推荐",
    // ... 其他商品字段
  }
]
```

## 技术特点

### 1. 缓存机制
- 内存缓存，5分钟TTL
- 减少对Hadoop服务的重复请求
- 提高响应速度

### 2. 错误处理
- 连接超时处理
- 服务不可用降级
- 详细的错误日志

### 3. 用户体验
- 需要用户登录才能使用
- 未登录时返回空结果
- 清晰的推荐标识显示

## 配置说明

### Hadoop服务配置
在 `core/bigdata_recommendation_service.py` 中：
```python
def __init__(self, hadoop_ip="192.168.174.128", hadoop_port=8080):
```

### 缓存配置
```python
self.cache_ttl = 300  # 缓存5分钟
```

## 测试验证

功能已通过以下测试：
1. ✅ Hadoop服务连接测试
2. ✅ API端点响应测试
3. ✅ 用户ID参数传递测试
4. ✅ 推荐标识显示测试
5. ✅ 前端UI集成测试

## 注意事项

1. **用户登录要求**: 大数据推荐需要用户ID，未登录用户无法使用
2. **Hadoop服务依赖**: 需要Hadoop推荐服务正常运行
3. **网络超时**: 设置了10秒超时，避免长时间等待
4. **缓存策略**: 5分钟缓存，平衡性能和实时性

## 扩展建议

1. 可以添加推荐质量评分显示
2. 可以添加推荐原因的详细说明
3. 可以添加推荐商品的个性化标签
4. 可以添加推荐效果的统计和分析
