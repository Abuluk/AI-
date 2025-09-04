# 数据库配置说明

## 概述
本项目已统一数据库配置，使用MySQL数据库，所有配置都集中在 `core/config.py` 文件中。

## 配置结构

### 1. 核心配置文件
- **`core/config.py`**: 统一的配置管理
- **`db/session.py`**: 数据库连接管理
- **`db/migrations/env.py`**: 数据库迁移配置

### 2. 数据库配置参数
```python
# MySQL 数据库配置
MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "20030208..")
MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB: str = os.getenv("MYSQL_DB", "ershou")
DATABASE_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_SERVER}:{MYSQL_PORT}/{MYSQL_DB}"
```

### 3. 环境变量支持
可以通过 `.env` 文件或系统环境变量覆盖默认配置：

```bash
# .env 文件示例
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_SERVER=localhost
MYSQL_PORT=3306
MYSQL_DB=ershou
SECRET_KEY=your-secret-key
```

## 使用方法

### 1. 启动服务
```bash
# 使用PowerShell脚本启动（推荐）
.\start_services.ps1

# 或手动启动
python main.py
cd frontend && npm run dev
```

### 2. 数据库迁移
```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

### 3. 数据库连接测试
```bash
# 测试API连接
curl http://127.0.0.1:8000/api/v1/items?skip=0&limit=5
```

## 配置优势

### 1. 统一管理
- 所有数据库相关配置都在 `core/config.py` 中
- 支持环境变量覆盖
- 避免硬编码

### 2. 环境隔离
- 开发、测试、生产环境可以使用不同的配置
- 通过环境变量轻松切换

### 3. 安全性
- 敏感信息（如密码）可以通过环境变量管理
- `.env` 文件已添加到 `.gitignore`

### 4. 可维护性
- 配置集中，易于维护
- 支持热重载
- 清晰的配置结构

## 故障排除

### 1. 循环导入问题
如果遇到循环导入错误，检查：
- `core/security.py` 中的导入
- 确保 `get_db` 在函数内部导入

### 2. 数据库连接问题
- 确认MySQL服务正在运行
- 检查数据库用户名和密码
- 确认数据库名称存在

### 3. 迁移问题
- 确认 `alembic.ini` 中的配置
- 检查 `db/migrations/env.py` 是否正确导入配置

## 注意事项

1. **生产环境**: 请修改默认密码和密钥
2. **备份**: 定期备份数据库
3. **权限**: 确保数据库用户有足够权限
4. **版本控制**: `.env` 文件不要提交到版本控制

## 相关文件

- `core/config.py`: 主配置文件
- `db/session.py`: 数据库会话管理
- `db/migrations/env.py`: 迁移环境配置
- `alembic.ini`: Alembic配置文件
- `.env`: 环境变量文件（需要手动创建）
- `.gitignore`: Git忽略文件配置 