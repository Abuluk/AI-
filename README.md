# 校园二手交易平台

一个基于FastAPI和Vue.js的现代化校园二手交易平台，集成了科大讯飞星火大模型AI智能推荐功能。

## 主要功能

- 🛍️ 商品发布、浏览、搜索
- 💬 实时聊天系统
- 👤 用户认证和个人资料管理
- 🤖 **AI智能推荐** - 基于科大讯飞星火大模型的智能价格分析和商品推荐
- 📱 响应式设计，支持移动端
- 🔍 高级搜索和筛选功能

## AI智能推荐功能

### 功能特点
- **智能价格分析**: AI分析当前网站商品的价格竞争力
- **低价好物推荐**: 从当前商品中挑选出价格最低且性价比最高的商品
- **市场洞察**: 提供市场分析和购买建议
- **多平台对比**: 模拟对比其他平台商品与当前网站商品

### 配置说明
详细配置说明请参考 [AI_INTEGRATION_README.md](./AI_INTEGRATION_README.md)

## 技术栈

### 后端
- **FastAPI** - 现代化Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **PostgreSQL** - 主数据库
- **科大讯飞星火大模型** - AI智能推荐

### 前端
- **Vue.js 3** - 渐进式JavaScript框架
- **Vue Router** - 前端路由
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd sjkwork
```

### 2. 安装依赖
```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
```

### 3. 配置环境变量
复制 `demo.env` 为 `.env` 并配置您的数据库和AI服务密钥：
```bash
cp demo.env .env
# 编辑 .env 文件，填入您的配置
```

### 4. 启动服务
```bash
# 启动后端服务
python main.py

# 启动前端服务（新终端）
cd frontend
npm run dev
```

## API文档

启动后端服务后，访问 `http://8.138.47.159:8000/docs` 查看完整的API文档。

## 更新日志

### 2024-06-22 更新
- items 表已添加 created_at 字段，支持按发布时间排序和显示
- 集成科大讯飞星火大模型，实现AI智能推荐功能
- 新增低价好物AI分析功能
- 优化用户界面，增加AI状态指示器

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License 