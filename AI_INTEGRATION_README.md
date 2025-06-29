# AI自动补全功能集成文档

## 概述

本项目集成了讯飞星火大模型的图片理解API，实现了商品图片的AI自动识别和商品信息补全功能。用户上传商品图片后，AI会自动识别商品类型、品牌、型号等信息，并自动填充到商品发布表单中。

## 功能特性

- 🖼️ **多图片支持**: 支持1-4张图片同时上传进行AI识别
- 🎯 **智能识别**: 自动识别商品标题、描述、分类、状态等信息
- 💰 **价格建议**: AI提供合理的价格范围建议
- ⚡ **实时响应**: 基于WebSocket的实时AI响应
- 🔄 **双版本支持**: 提供websocket-client和websockets两种实现

## 技术架构

### 后端实现

#### 1. AI服务模块 (`core/spark_ai.py`)

```python
class SparkAIService:
    def auto_complete_item_by_image(self, image_bytes_list: list) -> dict:
        """通过图片调用星火大模型自动补全商品信息"""
        
    async def auto_complete_item_by_image_ws(self, image_bytes_list: list) -> dict:
        """使用websockets库异步方式调用讯飞图片理解API"""
```

#### 2. API接口 (`api/endpoints/items.py`)

- `POST /api/v1/items/ai-auto-complete`: 标准版本
- `POST /api/v1/items/ai-auto-complete-ws`: websockets版本

### 前端实现

#### 1. API服务 (`frontend/src/services/api.js`)

```javascript
async aiAutoCompleteItemByImage(files) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    return axios.post('http://localhost:8000/api/v1/items/ai-auto-complete', formData, {
        headers: {
            Authorization: localStorage.getItem('access_token') ? `Bearer ${localStorage.getItem('access_token')}` : undefined
        }
    });
}
```

#### 2. 前端组件 (`frontend/src/views/PublishItem.vue`)

- 图片上传和预览
- AI自动补全按钮
- 表单自动填充
- 错误处理和用户反馈

## 讯飞API集成

### API配置

根据讯飞星火大模型图片理解API文档，实现了以下配置：

#### 请求参数

```json
{
    "header": {
        "app_id": "应用ID",
        "uid": "用户ID"
    },
    "parameter": {
        "chat": {
            "domain": "imagev3",
            "temperature": 0.5,
            "top_k": 4,
            "max_tokens": 2048,
            "chat_id": "会话ID"
        }
    },
    "payload": {
        "message": {
            "text": [
                {
                    "role": "user",
                    "content": [
                        {"text": "提示词"},
                        {"image": "base64编码的图片"}
                    ]
                }
            ]
        }
    }
}
```

#### 关键配置说明

- **domain**: 使用 `imagev3` (高级版) 获得更好的识别效果
- **temperature**: 0.5，平衡创造性和准确性
- **top_k**: 4，从4个候选中选择
- **max_tokens**: 2048，最大响应长度

### 鉴权机制

使用讯飞官方推荐的HMAC-SHA256签名鉴权：

```python
def _create_url(self) -> str:
    """生成鉴权url"""
    date = formatdate(timeval=None, localtime=False, usegmt=True)
    signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
    # ... 生成鉴权URL
```

## 使用指南

### 1. 环境配置

确保设置了以下环境变量：

```bash
XUNFEI_APP_ID=你的应用ID
XUNFEI_API_KEY=你的API密钥
XUNFEI_API_SECRET=你的API密钥
```

### 2. 启动服务

```bash
# 启动后端服务
python main.py

# 启动前端服务
cd frontend
npm run dev
```

### 3. 使用AI自动补全

1. 访问商品发布页面
2. 上传1-4张商品图片
3. 点击"AI自动补充"按钮
4. 等待AI识别完成
5. 核对并完善商品信息
6. 提交商品

### 4. 测试功能

运行测试脚本：

```bash
python test_ai_service.py
```

## 错误处理

### 常见错误及解决方案

1. **图片数量错误**
   - 错误: "the number of images is out of range [1,4]"
   - 解决: 确保上传1-4张图片

2. **配置错误**
   - 错误: "星火大模型配置不完整"
   - 解决: 检查环境变量设置

3. **网络连接错误**
   - 错误: "WebSocket连接失败"
   - 解决: 检查网络连接和防火墙设置

4. **图片格式错误**
   - 错误: "不支持的图片格式"
   - 解决: 使用jpg、jpeg、png格式

### 调试信息

后端会输出详细的调试信息：

```
上传图片数量：2
图片1 base64长度：123456
图片2 base64长度：789012
发送给讯飞的消息体结构：{...}
WebSocket已连接，发送消息...
收到讯飞响应：{...}
AI原始返回内容：{...}
```

## 性能优化

### 1. 图片处理优化

- 自动移除base64编码中的换行符
- 限制图片数量为1-4张
- 支持多种图片格式

### 2. 响应处理优化

- 使用WebSocket实现实时响应
- 设置30秒超时机制
- 异步处理避免阻塞

### 3. 错误恢复

- 自动重试机制
- 详细的错误信息
- 优雅的降级处理

## 扩展功能

### 1. 支持更多商品类型

可以通过修改提示词来支持更多商品类型的识别：

```python
prompt = """请识别以下商品类型：
- 电子产品（手机、电脑、耳机等）
- 服装鞋包
- 图书文娱
- 运动户外
- 家居家装
...
"""
```

### 2. 价格分析

可以扩展AI功能来分析市场价格：

```python
# 在提示词中添加价格分析要求
"请分析当前市场价格，提供合理的价格建议"
```

### 3. 多语言支持

可以扩展支持多语言识别：

```python
# 在parameter中添加语言设置
"parameter": {
    "chat": {
        "domain": "imagev3",
        "language": "zh-cn"  # 支持多语言
    }
}
```

## 注意事项

1. **API限制**: 注意讯飞API的调用频率和配额限制
2. **图片质量**: 建议使用清晰、光线充足的图片
3. **隐私保护**: 确保用户图片数据的安全处理
4. **成本控制**: 监控API调用成本，合理使用

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持基本的图片识别和商品信息补全
- 集成讯飞星火大模型API
- 提供双版本实现（websocket-client和websockets）

## 技术支持

如有问题，请检查：
1. 环境变量配置
2. 网络连接状态
3. 图片格式和大小
4. 后端服务日志

更多信息请参考讯飞开放平台文档：https://www.xfyun.cn/doc/spark/Web.html 