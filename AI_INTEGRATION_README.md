# 科大讯飞星火大模型集成说明

## 功能概述

本项目已集成科大讯飞星火大模型，用于智能分析商品价格竞争力并提供个性化推荐。

## 主要功能

1. **智能价格分析**: AI分析当前网站商品的价格竞争力
2. **低价好物推荐**: 从当前商品中挑选出价格最低且性价比最高的商品
3. **市场洞察**: 提供市场分析和购买建议
4. **多平台对比**: 模拟对比其他平台商品与当前网站商品

## 配置步骤

### 1. 获取科大讯飞星火大模型API密钥

1. 访问 [科大讯飞开放平台](https://console.xfyun.cn/)
2. 注册并登录账号
3. 创建新应用，选择"星火大模型"服务
4. 获取以下信息：
   - APP_ID
   - API_KEY
   - API_SECRET

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，添加以下配置：

```env
# 科大讯飞星火大模型配置
XUNFEI_APP_ID=your_xunfei_app_id
XUNFEI_API_KEY=your_xunfei_api_key
XUNFEI_API_SECRET=your_xunfei_api_secret
XUNFEI_SPARK_URL=wss://spark-api.xf-yun.com/v3.1/chat
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 前端调用

在Vue组件中调用AI推荐服务：

```javascript
import api from '@/services/api'

// 获取AI分析的低价好物推荐
const response = await api.getAICheapDeals(10)
```

### 后端API

访问 `GET /api/v1/items/ai-cheap-deals` 获取AI推荐结果。

## API响应格式

### 成功响应

```json
{
  "success": true,
  "analysis": "价格竞争力分析结果",
  "market_insights": "市场洞察和建议",
  "recommendations": [
    {
      "id": 1,
      "title": "商品标题",
      "price": 1000,
      "condition": "good",
      "ai_reason": "推荐理由",
      "user": {
        "username": "用户名"
      }
    }
  ],
  "total_items_analyzed": 10
}
```

### 失败响应

```json
{
  "success": false,
  "message": "错误信息",
  "fallback_recommendations": [
    // 备用推荐商品列表
  ]
}
```

## 功能特点

1. **智能分析**: 使用AI分析商品价格、状态、类别等多维度信息
2. **容错机制**: 当AI服务不可用时，自动降级到基础推荐
3. **实时更新**: 每次访问都会重新分析当前商品数据
4. **用户友好**: 提供清晰的分析结果和市场洞察

## 注意事项

1. 确保科大讯飞API密钥配置正确
2. 网络连接稳定，AI服务需要访问外部API
3. 建议在生产环境中添加缓存机制以提高性能
4. 注意API调用频率限制

## 故障排除

### 常见问题

1. **AI服务连接失败**
   - 检查网络连接
   - 验证API密钥配置
   - 确认科大讯飞服务状态

2. **响应格式错误**
   - 检查商品数据格式
   - 验证AI服务返回的JSON格式

3. **性能问题**
   - 考虑添加缓存
   - 优化商品数据查询
   - 调整AI分析频率

## 技术支持

如有问题，请检查：
1. 环境变量配置
2. 网络连接状态
3. 科大讯飞服务状态
4. 应用日志信息 