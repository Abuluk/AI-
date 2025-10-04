# 校园二手交易平台

一个基于FastAPI和Vue.js的现代化校园二手交易平台，集成了多种AI智能推荐系统，包括AI大模型、大数据推荐和AI增强推荐功能。

## 🌟 主要功能

### 核心功能
- 🛍️ **商品管理** - 发布、浏览、搜索、分类筛选
- 💬 **实时聊天** - 用户间私聊、系统消息通知
- 👤 **用户系统** - 注册登录、个人资料、好友关系
- 📱 **移动端适配** - 响应式设计，完美支持手机端
- 🔍 **高级搜索** - 多条件筛选、智能搜索

### 社交功能
- 👥 **好友系统** - 添加好友、好友动态
- 🚫 **黑名单管理** - 屏蔽不良用户
- 💬 **评论系统** - 商品评论、回复互动
- ❤️ **收藏点赞** - 收藏商品、点赞评论

### 商家功能
- 🏪 **商家认证** - 商家申请、管理员审核
- 📊 **商贩检测** - AI自动检测商贩行为
- 🎯 **商家展示** - 智能展示商家商品

### 求购功能
- 📝 **求购发布** - 发布求购信息
- 💰 **预算设置** - 设置求购预算
- 📷 **图片上传** - 支持求购图片

## 🤖 AI智能推荐系统

### 多层级推荐架构
1. **AI大模型推荐** - 基于用户行为序列的智能分析
2. **大数据推荐** - 基于Hadoop的协同过滤推荐
3. **AI增强推荐** - 集成AI大模型的深度推荐

### AI功能特点
- **智能行为分析**: 分析用户浏览、点击、收藏等行为模式
- **个性化推荐**: 基于用户偏好推荐最合适的商品
- **市场洞察**: 提供商品价格分析和市场趋势
- **实时学习**: 持续学习用户行为，优化推荐效果
- **多算法融合**: 结合多种推荐算法，提供更精准的推荐

### 推荐配置
- **并发控制**: 支持高并发AI请求处理
- **缓存机制**: Redis缓存提升响应速度
- **限流保护**: 防止恶意请求，保护系统稳定
- **降级策略**: AI服务异常时自动降级到基础推荐

## 🛠️ 技术栈

### 后端技术
- **FastAPI** - 现代化Python Web框架，自动生成API文档
- **SQLAlchemy** - 强大的ORM数据库操作
- **MySQL** - 主数据库，支持高并发
- **Alembic** - 数据库迁移管理
- **Redis** - 缓存和会话存储
- **WebSocket** - 实时通信支持

### AI技术栈
- **AI大模型** - 智能语言模型
- **AI增强算法** - 深度推荐算法
- **Hadoop** - 大数据处理平台
- **Spark** - 分布式计算引擎

### 前端技术
- **Vue.js 3** - 渐进式JavaScript框架
- **Vue Router** - 前端路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP客户端
- **Vite** - 现代化构建工具

### 开发工具
- **Alembic** - 数据库版本控制
- **APScheduler** - 定时任务调度
- **WebSocket** - 实时通信
- **CORS** - 跨域资源共享

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Redis 6.0+

### 1. 克隆项目
```bash
git clone <repository-url>
cd sjkwork
```

### 2. 安装后端依赖
```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖
```bash
cd frontend
npm install
```

### 4. 配置环境变量
创建 `.env` 文件并配置：
```bash
# 数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=ershou

# AI服务配置
AI_APP_ID=your_app_id
AI_API_KEY=your_api_key
AI_API_SECRET=your_api_secret
AI_MODEL_URL=your_model_url

# 其他配置
SECRET_KEY=your-secret-key
```

### 5. 数据库初始化
```bash
# 创建数据库迁移
alembic upgrade head

# 或手动创建数据库
mysql -u root -p
CREATE DATABASE ershou CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. 启动服务
```bash
# 启动后端服务
python main.py

# 启动前端服务（新终端）
cd frontend
npm run dev
```

### 7. 访问应用
- 前端应用: http://localhost:5173
- API文档: http://localhost:8000/docs
- 管理后台: http://localhost:5173/admin

## 📊 数据库设计

### 核心表结构
- **users** - 用户信息表
- **items** - 商品信息表
- **messages** - 消息表
- **favorites** - 收藏表
- **comments** - 评论表
- **buy_requests** - 求购信息表
- **merchants** - 商家信息表
- **user_behaviors** - 用户行为表
- **ai_recommendation_configs** - AI推荐配置表

### 特色功能表
- **merchant_detection_histories** - 商贩检测历史
- **item_sorting_metrics** - 商品排序指标
- **ai_features** - AI特征数据
- **feedback** - 用户反馈

## 🔧 API接口

### 认证接口
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/logout` - 用户登出

### 商品接口
- `GET /api/v1/items` - 获取商品列表
- `POST /api/v1/items` - 发布商品
- `GET /api/v1/items/{id}` - 获取商品详情
- `PUT /api/v1/items/{id}` - 更新商品
- `DELETE /api/v1/items/{id}` - 删除商品

### AI推荐接口
- `GET /api/v1/ai_strategy/recommendations` - 获取AI推荐
- `POST /api/v1/ai_strategy/record-behavior` - 记录用户行为
- `GET /api/v1/ai_strategy/behavior-stats` - 获取行为统计

### 消息接口
- `GET /api/v1/messages` - 获取消息列表
- `POST /api/v1/messages` - 发送消息
- `PUT /api/v1/messages/{id}/read` - 标记已读

## 📈 系统特性

### 性能优化
- **并发处理**: 支持高并发AI请求
- **缓存机制**: Redis缓存提升响应速度
- **数据库优化**: 索引优化、查询优化
- **前端优化**: 懒加载、图片压缩

### 安全特性
- **JWT认证**: 安全的用户认证机制
- **权限控制**: 基于角色的访问控制
- **数据验证**: 严格的输入验证
- **SQL注入防护**: ORM自动防护

### 监控运维
- **请求监控**: AI推荐请求统计
- **错误日志**: 详细的错误日志记录
- **健康检查**: 服务健康状态监控
- **限流保护**: 防止系统过载

## 📝 更新日志

### v2.0.0
- 🎉 全新AI推荐系统架构
- 🤖 集成AI大模型
- 📊 新增大数据推荐功能
- 🔧 优化系统性能和稳定性
- 📱 完善移动端体验

### v1.5.0
- ✨ 新增商品排序功能
- 🏪 完善商家认证系统
- 💬 优化聊天系统
- 🔍 增强搜索功能

### v1.0.0
- 🎉 初始版本发布
- 🛍️ 基础商品交易功能
- 👤 用户系统
- 💬 实时聊天

## 📞 联系我们

- 邮箱: [2720691438@qq.com]

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 