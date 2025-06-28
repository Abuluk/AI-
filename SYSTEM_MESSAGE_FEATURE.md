# 管理员系统消息功能

## 功能概述

当管理员执行特定操作时，系统会自动向相关用户发送系统消息通知：

1. **商品下架通知**: 管理员下架商品时，自动向商品所有者发送通知
2. **求购信息删除通知**: 管理员删除求购信息时，自动向求购信息发布者发送通知

## 功能特点

1. **自动触发**: 管理员在后台执行操作时，系统自动发送通知
2. **个性化消息**: 消息内容包含具体的商品/求购信息标题
3. **系统消息显示**: 在聊天界面中以特殊样式显示系统消息
4. **用户友好**: 提供明确的提示和确认对话框
5. **消息持久化**: 系统消息在相关商品/求购信息删除后仍然保留

## 实现细节

### 后端修改

1. **管理员API** (`api/endpoints/admin.py`)
   - 修改 `update_item_status` 函数 - 下架商品时发送通知
   - 修改 `delete_buy_request` 函数 - 删除求购信息时发送通知
   - 在删除求购信息前先删除相关普通消息，但保留系统消息
   - 使用 `crud_message.create_system_message` 发送消息

2. **数据库模型** (`db/models.py`)
   - 修改 `BuyRequest` 模型，移除 `messages` 关系的 `cascade="all, delete-orphan"` 设置
   - 确保系统消息在求购信息删除后仍然保留

3. **消息Schema** (`schemas/message.py`)
   - 修改 `SystemMessageCreate` 类，添加 `buy_request_id` 字段

4. **消息CRUD** (`crud/crud_message.py`)
   - 修改 `create_system_message` 函数，支持 `buy_request_id` 字段
   - 修改 `get_conversation_messages` 函数，支持显示系统消息
   - 修改 `get_public_system_messages` 函数，支持获取用户特定的系统消息

5. **消息API** (`api/endpoints/messages.py`)
   - 修改 `read_public_system_messages` 函数，支持获取当前用户的系统消息

## 问题修复

### 求购信息删除通知问题
**问题描述**: 管理员删除求购信息后，用户无法看到删除通知消息。

**原因分析**: 
1. `BuyRequest` 模型中的 `messages` 关系设置了 `cascade="all, delete-orphan"`
2. 当求购信息被删除时，所有相关的消息（包括系统消息）也被删除
3. 用户无法在消息中心看到删除通知

**解决方案**:
1. 移除 `BuyRequest` 模型中 `messages` 关系的 `cascade` 设置
2. 在删除求购信息前，手动删除相关的普通消息，但保留系统消息
3. 确保系统消息在求购信息删除后仍然可以正常显示

## 消息格式

### 商品下架通知
- **标题**: "商品下架通知"
- **内容**: "您的商品《{商品标题}》因不合规内容已被管理员下架。如有疑问，请联系客服。"
- **目标用户**: 商品所有者的用户ID
- **关联商品**: 被下架的商品ID

### 求购信息删除通知
- **标题**: "求购信息删除通知"
- **内容**: "您的求购信息《{求购标题}》因不合规内容已被管理员删除。如有疑问，请联系客服。"
- **目标用户**: 求购信息发布者的用户ID
- **关联求购**: 被删除的求购信息ID

## 使用流程

### 商品下架流程
1. 管理员登录后台
2. 进入商品管理页面
3. 找到要下架的商品
4. 点击"下架"按钮
5. 确认下架操作（会提示将发送系统消息）
6. 系统自动下架商品并发送通知消息
7. 商品所有者可以在消息中心看到系统通知

### 求购信息删除流程
1. 管理员登录后台
2. 进入求购信息管理页面
3. 找到要删除的求购信息
4. 点击"删除"按钮
5. 确认删除操作（会提示将发送系统消息）
6. 系统自动删除求购信息并发送通知消息
7. 求购信息发布者可以在消息中心看到系统通知

## 注意事项

1. **商品下架**: 只有从"在售"状态改为"已下架"状态时才会发送系统消息
2. **求购信息删除**: 删除求购信息时会立即发送系统消息
3. **系统消息发送失败不会影响主要操作**: 商品状态更新和求购信息删除
4. **系统消息在聊天界面中以特殊样式显示**: 不会影响正常对话
5. **用户可以在消息中心查看所有系统通知**
6. **系统消息持久化**: 即使相关商品或求购信息被删除，系统消息仍然保留

## 技术实现

### 系统消息数据结构

```python
class SystemMessageCreate(BaseModel):
    content: str
    title: Optional[str] = None
    target_users: Optional[str] = None  # "all", "buyers", "sellers", 或用户ID列表
    item_id: Optional[int] = None  # 系统消息可以关联到特定商品，也可以为空
    buy_request_id: Optional[int] = None  # 系统消息可以关联到特定求购信息，也可以为空
```

### 数据库关系

```python
class Message(Base):
    # ... 其他字段
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    buy_request_id = Column(Integer, ForeignKey("buy_requests.id"), nullable=True)
    is_system = Column(Boolean, default=False)  # 系统消息标识
    title = Column(String(200), nullable=True)  # 系统消息标题
    target_users = Column(String(500), nullable=True)  # 目标用户
```

### 消息删除逻辑

```python
# 删除与该求购信息相关的普通消息（非系统消息）
db.query(Message).filter(
    Message.buy_request_id == buy_request_id,
    Message.is_system == False
).delete()

# 删除求购信息（系统消息保留）
db.delete(buy_request)
```

## 扩展功能

该功能可以扩展支持：
1. 其他类型的系统消息（如商品上架通知、违规警告等）
2. 批量发送系统消息
3. 系统消息模板管理
4. 消息发送历史记录
5. 更多管理员操作的通知（如用户封禁、内容审核等）

## 测试方法

可以使用提供的测试脚本 `test_system_message.py` 来验证功能：

```bash
python test_system_message.py
```

测试脚本会：
1. 管理员登录
2. 获取商品列表
3. 下架一个在售商品
4. 检查系统消息是否创建
5. 重新上架商品

## 注意事项

1. 只有从"在售"状态改为"已下架"状态时才会发送系统消息
2. 系统消息发送失败不会影响商品状态更新
3. 系统消息在聊天界面中以特殊样式显示，不会影响正常对话
4. 用户可以在消息中心查看所有系统通知

## 技术实现

### 系统消息数据结构

```python
{
    "id": 消息ID,
    "title": "商品下架通知"
}
```

### 数据库字段

- `is_system`: 标识是否为系统消息
- `title`: 系统消息标题
- `target_users`: 目标用户（可以是用户ID或"all"）
- `item_id`: 关联的商品ID（可选）
- `buy_request_id`: 关联的求购信息ID（可选）

## 技术实现

### 系统消息数据结构

```python
{
    "id": 消息ID,
    "title": "商品下架通知" | "求购信息删除通知",
    "content": "具体通知内容",
    "user_id": 管理员ID,
    "item_id": 商品ID (可选),
    "buy_request_id": 求购信息ID (可选),
    "is_system": True,
    "target_users": "目标用户ID",
    "created_at": 创建时间
}
```

### 数据库字段

- `is_system`: 标识是否为系统消息
- `title`: 系统消息标题
- `target_users`: 目标用户（可以是用户ID或"all"）
- `item_id`: 关联的商品ID（可选）
- `buy_request_id`: 关联的求购信息ID（可选）

## 扩展功能

该功能可以扩展支持：
1. 其他类型的系统消息（如商品上架通知、违规警告等）
2. 批量发送系统消息
3. 系统消息模板管理
4. 消息发送历史记录
5. 更多管理员操作的通知（如用户封禁、内容审核等）

## 测试方法

可以使用提供的测试脚本 `test_system_message.py` 来验证功能：

```bash
python test_system_message.py
```

测试脚本会：
1. 管理员登录
2. 获取商品列表
3. 下架一个在售商品
4. 检查系统消息是否创建
5. 重新上架商品

## 注意事项

1. 只有从"在售"状态改为"已下架"状态时才会发送系统消息
2. 系统消息发送失败不会影响商品状态更新
3. 系统消息在聊天界面中以特殊样式显示，不会影响正常对话
4. 用户可以在消息中心查看所有系统通知

## 技术实现

### 系统消息数据结构

```python
{
    "id": 消息ID,
    "title": "商品下架通知"
}
```

### 数据库字段

- `