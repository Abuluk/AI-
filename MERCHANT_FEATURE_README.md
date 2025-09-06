# 商家功能说明

## 功能概述

本次更新添加了完整的商家功能，包括商家认证、商品展示频率控制、管理员管理等功能。

## 主要功能

### 1. 商家认证功能

#### 用户端功能
- **申请商家认证**: 用户可以在个人主页申请成为商家
- **查看认证状态**: 用户可以查看自己的商家认证状态
- **更新商家信息**: 待审核状态下可以更新商家信息

#### API端点
```
POST /api/v1/merchants/apply          # 申请商家认证
GET  /api/v1/merchants/my             # 获取我的商家信息
PUT  /api/v1/merchants/my             # 更新我的商家信息
```

### 2. 商家商品展示频率功能

#### 用户端功能
- **设置展示频率**: 用户可以设置商家商品的展示频率（每几个商品展示一个商家商品）
- **查看当前配置**: 用户可以查看当前的展示配置

#### API端点
```
GET /api/v1/merchants/display-config  # 获取我的展示配置
PUT /api/v1/merchants/display-config  # 更新我的展示配置
```

### 3. 管理员管理功能

#### 管理员功能
- **审核商家申请**: 管理员可以审核用户的商家认证申请
- **管理商家列表**: 查看所有商家信息
- **创建待定商家**: 管理员可以添加用户为待定商家
- **设置默认展示频率**: 管理员可以设置全局默认的商家商品展示频率

#### API端点
```
GET  /api/v1/merchants/admin/pending                    # 获取待审核商家列表
GET  /api/v1/merchants/admin/all                        # 获取所有商家列表
PUT  /api/v1/merchants/admin/{merchant_id}/status       # 更新商家状态
POST /api/v1/merchants/admin/pending                    # 创建待定商家
DELETE /api/v1/merchants/admin/{merchant_id}            # 删除商家
GET  /api/v1/merchants/admin/display-config/default     # 获取默认展示配置
PUT  /api/v1/merchants/admin/display-config/default     # 更新默认展示配置
```

### 4. 待定商家系统

#### 功能说明
- 管理员可以将用户添加为待定商家
- 待定商家需要完成商家认证才能发布商品
- 成为待定商家时，用户的所有已发布商品会被自动下架

#### 工作流程
1. 管理员添加用户为待定商家
2. 用户收到通知，需要完成商家认证
3. 用户提交商家认证申请
4. 管理员审核申请
5. 审核通过后，用户成为正式商家，可以发布商品

### 5. 商品展示逻辑

#### 展示规则
- 商家商品按照设置的展示频率进行展示
- 展示频率对分类筛选和排序都生效
- 支持个人配置和全局默认配置
- 商家商品会标记为 `is_merchant_item: true`

#### 商品列表API更新
```
GET /api/v1/items?user_id={user_id}  # 支持用户ID参数获取个人展示配置
```

## 数据库变更

### 新增表
1. **merchants** - 商家信息表
2. **merchant_display_configs** - 商家展示配置表

### 修改表
1. **users** - 添加 `is_merchant` 和 `is_pending_merchant` 字段
2. **items** - 添加 `is_merchant_item` 字段

## 使用示例

### 1. 用户申请商家认证

```python
import requests

# 用户登录
login_data = {
    "identifier": "user@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/api/v1/auth/login", data=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 申请商家认证
merchant_data = {
    "business_name": "我的商店",
    "business_license": "123456789012345",
    "contact_person": "张三",
    "contact_phone": "13800138000",
    "business_address": "北京市朝阳区测试街道123号",
    "business_description": "专业销售二手商品"
}
response = requests.post("http://localhost:8000/api/v1/merchants/apply", json=merchant_data, headers=headers)
```

### 2. 设置商家商品展示频率

```python
# 设置展示频率为每3个商品展示1个商家商品
config_data = {"display_frequency": 3}
response = requests.put("http://localhost:8000/api/v1/merchants/display-config", json=config_data, headers=headers)
```

### 3. 管理员审核商家申请

```python
# 管理员登录
admin_headers = {"Authorization": f"Bearer {admin_token}"}

# 审核通过
status_data = {
    "status": "approved"
}
response = requests.put("http://localhost:8000/api/v1/merchants/admin/1/status", json=status_data, headers=admin_headers)

# 审核拒绝
status_data = {
    "status": "rejected",
    "reject_reason": "营业执照信息不完整"
}
response = requests.put("http://localhost:8000/api/v1/merchants/admin/1/status", json=status_data, headers=admin_headers)
```

### 4. 获取商品列表（支持商家商品展示）

```python
# 获取商品列表，使用用户个人展示配置
response = requests.get("http://localhost:8000/api/v1/items?user_id=1")

# 获取商品列表，使用全局默认配置
response = requests.get("http://localhost:8000/api/v1/items")
```

## 注意事项

1. **权限控制**: 商家管理功能需要管理员权限
2. **数据一致性**: 成为待定商家时，用户的所有商品会被自动下架
3. **展示频率**: 展示频率最小为1，最大为100
4. **状态管理**: 商家状态包括 pending（待审核）、approved（已认证）、rejected（已拒绝）
5. **配置优先级**: 用户个人配置优先于全局默认配置

## 测试

运行测试脚本验证功能：

```bash
python test_merchant.py
```

## 更新日志

- 添加商家认证系统
- 实现商家商品展示频率控制
- 添加管理员商家管理功能
- 实现待定商家系统
- 更新商品展示逻辑支持商家商品
- 添加相关数据库表和字段

