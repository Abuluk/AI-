# AI智能推荐系统

## 功能概述

本系统实现了基于用户浏览行为序列的AI智能推荐功能，通过分析用户的浏览、点击、收藏等行为，为用户提供个性化的商品推荐。

## 核心特性

### 1. 用户行为记录
- **浏览行为**: 记录用户查看商品的行为
- **点击行为**: 记录用户点击商品的行为
- **收藏行为**: 记录用户收藏商品的行为
- **搜索行为**: 记录用户搜索关键词的行为

### 2. AI智能分析
- **行为序列分析**: 分析用户最近N个商品浏览行为
- **偏好识别**: 识别用户的商品分类、价格、成色偏好
- **个性化推荐**: 基于用户偏好推荐最合适的商品

### 3. 推荐策略
- **AI行为推荐**: 基于用户行为序列的智能推荐
- **热门商品推荐**: 当用户行为数据不足时的备用推荐
- **混合推荐**: 结合多种推荐策略的综合推荐

## 技术架构

### 数据库设计

#### 用户行为记录表 (user_behaviors)
```sql
CREATE TABLE user_behaviors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    item_id INT,
    behavior_type VARCHAR(20) NOT NULL,  -- view, click, favorite, like, search
    behavior_data JSON,                  -- 行为相关数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);
```

#### AI推荐配置表 (ai_recommendation_configs)
```sql
CREATE TABLE ai_recommendation_configs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSON,
    description VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### API接口

#### 用户端接口

1. **获取AI推荐商品**
   ```
   GET /api/v1/ai_strategy/recommendations?limit=10
   ```

2. **记录用户行为**
   ```
   POST /api/v1/ai_strategy/record-behavior
   {
     "behavior_type": "view",
     "item_id": 123,
     "behavior_data": {"title": "商品标题", "category": "1", "price": 100}
   }
   ```

3. **获取用户行为统计**
   ```
   GET /api/v1/ai_strategy/behavior-stats?days=30
   ```

#### 管理员接口

1. **获取AI推荐配置**
   ```
   GET /api/v1/admin/ai-recommendation/config
   ```

2. **更新AI推荐配置**
   ```
   PUT /api/v1/admin/ai-recommendation/config
   {
     "sequence_length": 10,
     "recommendation_count": 10,
     "enable_ai_analysis": true
   }
   ```

3. **获取AI推荐统计**
   ```
   GET /api/v1/admin/ai-recommendation/stats?days=30
   ```

4. **获取用户行为记录**
   ```
   GET /api/v1/admin/ai-recommendation/user-behaviors?user_id=123&limit=50
   ```

5. **测试AI推荐功能**
   ```
   GET /api/v1/admin/ai-recommendation/test?user_id=123&limit=5
   ```

## 配置参数

### AI推荐配置
- `sequence_length`: 用户行为序列长度 (默认: 10)
- `recommendation_count`: 推荐商品数量 (默认: 10)
- `category_weight`: 分类权重 (默认: 0.4)
- `price_weight`: 价格权重 (默认: 0.3)
- `condition_weight`: 成色权重 (默认: 0.2)
- `location_weight`: 地区权重 (默认: 0.1)
- `enable_ai_analysis`: 是否启用AI分析 (默认: true)
- `min_behavior_count`: 最少行为记录数 (默认: 3)
- `behavior_days`: 行为记录天数 (默认: 30)

## 使用说明

### 前端集成

1. **记录用户行为**
   ```javascript
   // 在商品卡片点击时记录浏览行为
   await api.recordUserBehavior('view', itemId, {
     title: item.title,
     category: item.category,
     price: item.price
   });
   ```

2. **获取AI推荐**
   ```javascript
   // 获取AI推荐商品
   const response = await api.getAIRecommendations(10);
   if (response.data.success) {
     const recommendations = response.data.recommendations;
     const analysis = response.data.analysis;
     const marketInsights = response.data.market_insights;
   }
   ```

### 管理员管理

1. **配置AI推荐参数**
   ```javascript
   await api.updateAIRecommendationConfig({
     sequence_length: 15,
     recommendation_count: 8,
     enable_ai_analysis: true
   });
   ```

2. **查看推荐统计**
   ```javascript
   const stats = await api.getAIRecommendationStats(30);
   console.log('活跃用户数:', stats.stats.active_users);
   console.log('总行为数:', stats.stats.total_behaviors);
   ```

## 推荐算法

### 1. 行为序列分析
- 获取用户最近N个浏览行为
- 分析行为模式和时间分布
- 提取用户偏好特征

### 2. 商品匹配算法
- 基于用户偏好计算商品匹配度
- 考虑分类、价格、成色、地区等因素
- 使用加权评分机制

### 3. AI智能分析
- 使用讯飞星火大模型进行深度分析
- 生成个性化推荐理由
- 提供市场洞察和建议

## 性能优化

### 1. 数据清理
- 定期清理旧的行为记录
- 保留最近90天的有效数据
- 优化数据库查询性能

### 2. 缓存策略
- 缓存用户行为统计结果
- 缓存热门商品推荐
- 减少重复计算

### 3. 异步处理
- 用户行为记录异步处理
- AI分析结果缓存
- 推荐结果预计算

## 监控和调试

### 1. 日志记录
- 记录AI推荐请求和响应
- 记录用户行为数据
- 记录推荐效果统计

### 2. 性能监控
- 监控AI分析响应时间
- 监控推荐准确率
- 监控用户行为数据质量

### 3. 调试工具
- 提供AI推荐测试接口
- 支持单用户推荐调试
- 提供推荐结果分析

## 扩展功能

### 1. 实时推荐
- 基于实时行为数据更新推荐
- 支持动态调整推荐策略
- 实现个性化推荐流

### 2. 协同过滤
- 基于相似用户的推荐
- 商品相似度计算
- 混合推荐策略

### 3. 深度学习
- 使用神经网络模型
- 更复杂的特征工程
- 端到端的推荐系统

## 注意事项

1. **隐私保护**: 用户行为数据需要严格保护，遵循隐私政策
2. **性能考虑**: AI分析可能耗时较长，需要合理的超时设置
3. **数据质量**: 确保用户行为数据的准确性和完整性
4. **推荐多样性**: 避免推荐结果过于单一，保持推荐多样性
5. **冷启动问题**: 新用户缺乏行为数据时的推荐策略

## 测试

运行测试脚本验证功能：
```bash
python test_ai_recommendation.py
```

测试包括：
- 用户行为记录
- 行为统计获取
- AI推荐功能
- 推荐结果验证
