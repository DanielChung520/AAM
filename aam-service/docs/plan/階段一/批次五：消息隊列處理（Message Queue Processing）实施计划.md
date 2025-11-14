# 批次五：消息隊列處理（Message Queue Processing）实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 待批准  
**前置依赖**: 批次四（业务逻辑层实现）已完成

---

## 计划概述

根据 `AAM Agent SD v1.md` 的规范和 `AAM 服務第一階段 MVP 實施計劃.md`，完成批次五的消息队列处理实现。本批次实现 RabbitMQ 消费者，监听 `aam.dialogue.archive` 队列，处理对话归档消息，调用 `MemoryServiceImpl.archive()` 方法完成异步记忆写入。

---

## 任务清单

### 任务 5.1：RabbitMQ 配置管理

**文件**: `src/infrastructure/messaging/rabbitmq_config.py`

**任务内容**:

- [x] 定义 `RabbitMQConnection` 类
  - 封装 aio-pika 连接和通道管理
  - 实现连接重试机制（指数退避）
  - 实现连接健康检查
  - 实现优雅关闭（cleanup）
- [x] 实现 `setup_queue()` 函数
  - 声明队列 `aam.dialogue.archive`（持久化、非自动删除）
  - 配置队列参数（durable=True）
  - 返回队列名称
- [x] 实现 `setup_exchange()` 函数（可选）
  - 声明交换机 `aam.exchange`（如果需要）
  - 绑定队列到交换机（如果需要）
- [x] 实现连接池管理
  - 单例模式管理连接实例
  - 支持连接复用
  - 处理连接断开和重连

**参考规范**: SD 文件 3.1.1 节、5.1 节

**验收标准**:
- 封装 aio-pika 连接细节
- 实现连接重试机制
- 通过单元测试（使用 Mock）
- 符合配置化原则（使用 RabbitMQSettings）

---

### 任务 5.2：对话归档消费者实现

**文件**: `src/infrastructure/messaging/dialogue_consumer.py`

**任务内容**:

- [x] 定义 `DialogueArchiveConsumer` 类
  - 接收依赖注入：`memory_service: IMemoryService`
  - 接收依赖注入：`rabbitmq_config: RabbitMQConnection`
  - 实现 `start_consuming()` 方法（异步）
    - 建立 RabbitMQ 连接
    - 设置队列和交换机
    - 开始消费消息（basic_consume）
    - 在后台任务中运行消费循环
  - 实现 `stop_consuming()` 方法（异步）
    - 停止消费
    - 关闭连接
    - 等待正在处理的消息完成
- [x] 实现 `_process_message()` 方法（私有）
  - 接收原始消息（bytes）
  - 使用 Pydantic 验证消息（`DialogueArchiveMessage`）
  - 调用 `memory_service.archive(message)`
  - 处理成功：发送 ACK
  - 处理失败：发送 NACK（requeue=False，避免无限重试）
  - 记录结构化日志（包含 user_id, dialog_id, turn）
- [x] 实现错误处理
  - 消息格式错误：记录错误，发送 NACK（requeue=False）
  - 业务逻辑错误：记录错误，发送 NACK（requeue=False）
  - 连接错误：记录错误，实现重连机制
  - 使用 `return_exceptions=True` 确保一个消息失败不影响其他消息

**参考规范**: SD 文件 3.1.1 节、5.1 节、6.2 节类图

**验收标准**:
- 正确监听 `aam.dialogue.archive` 队列
- 使用 Pydantic 验证消息
- 调用 `MemoryServiceImpl.archive()` 方法
- 实现完善的错误处理和日志记录
- 通过单元测试（使用 Mock）
- 符合异步处理规范

---

### 任务 5.3：集成到主应用

**文件**: `src/main.py`

**任务内容**:

- [x] 在 `lifespan` 函数中集成消费者
  - 启动时：创建 `DialogueArchiveConsumer` 实例
  - 启动时：调用 `consumer.start_consuming()`（在后台任务中运行）
  - 关闭时：调用 `consumer.stop_consuming()`（优雅关闭）
  - 关闭时：等待所有消息处理完成（设置超时）
- [x] 实现依赖注入
  - 创建 `MemoryServiceImpl` 实例（需要注入 `IKnowledgeStore`, `IPersonaStore`, `IAnalysisModel`）
  - 创建 `RabbitMQConnection` 实例（使用 `RabbitMQSettings`）
  - 创建 `DialogueArchiveConsumer` 实例
- [x] 实现优雅关闭
  - 捕获 SIGTERM 和 SIGINT 信号
  - 停止接收新消息
  - 等待正在处理的消息完成（最多等待 30 秒）
  - 关闭连接

**验收标准**:
- 应用启动时自动开始消费消息
- 应用关闭时优雅停止消费
- 正确处理信号和异常
- 通过集成测试

---

### 任务 5.4：模块导出更新

**文件**: `src/infrastructure/messaging/__init__.py`

**任务内容**:

- [x] 导出 `RabbitMQConnection` 类
- [x] 导出 `DialogueArchiveConsumer` 类
- [x] 导出 `setup_queue()` 和 `setup_exchange()` 函数
- [x] 确保可以通过 `from src.infrastructure.messaging import DialogueArchiveConsumer` 导入

**验收标准**:
- 符合 Python 模块导出规范
- 可以通过统一导入使用

---

### 任务 5.5：创建单元测试

**文件**: `tests/unit/test_dialogue_consumer.py`

**任务内容**:

- [x] 测试 `RabbitMQConnection` 类
  - 测试连接建立
  - 测试连接重试机制
  - 测试连接健康检查
  - 测试优雅关闭
  - 使用 Mock 隔离 aio-pika 依赖
- [x] 测试 `DialogueArchiveConsumer` 类
  - 测试 `start_consuming()` 方法
  - 测试 `stop_consuming()` 方法
  - 测试 `_process_message()` 方法
    - 测试正常流程：消息验证 -> 调用 archive() -> 发送 ACK
    - 测试消息格式错误：发送 NACK（requeue=False）
    - 测试业务逻辑错误：发送 NACK（requeue=False）
    - 测试连接错误：重连机制
  - 使用 Mock 隔离外部依赖（aio-pika, MemoryServiceImpl）
- [x] 测试错误处理
  - 测试消息解析失败的处理
  - 测试 `archive()` 方法抛出异常的处理
  - 测试连接断开的处理

**验收标准**:
- 所有测试用例通过
- 测试覆盖率 >= 85%
- 符合 pytest 测试规范
- 使用 Mock 隔离外部依赖

---

### 任务 5.6：创建集成测试

**文件**: `tests/integration/test_message_queue_integration.py`

**任务内容**:

- [x] 测试端到端消息处理流程
  - 启动 RabbitMQ（使用 docker-compose 或测试容器）
  - 发送测试消息到队列
  - 验证消息被正确消费和处理
  - 验证 `MemoryServiceImpl.archive()` 被调用
  - 验证知识资产和用户画像被保存
- [x] 测试错误场景
  - 测试无效消息格式的处理
  - 测试队列不可用时的处理
  - 测试消费者重启后的消息恢复

**验收标准**:
- 所有集成测试通过
- 使用测试容器或 Mock RabbitMQ
- 验证完整的消息处理流程

---

## 实施原则

1. **异步优先**: 使用 `asyncio` 和 `aio-pika` 的异步 API 实现消息消费
2. **错误容错**: 消息处理失败时记录日志但不阻塞队列，避免无限重试
3. **优雅关闭**: 应用关闭时等待正在处理的消息完成，避免数据丢失
4. **结构化日志**: 使用 `structlog` 记录结构化日志，包含上下文信息
5. **配置化**: 所有配置通过 `RabbitMQSettings` 加载，支持环境变量

---

## 文件组织

- RabbitMQ 配置: `src/infrastructure/messaging/rabbitmq_config.py`
- 消费者实现: `src/infrastructure/messaging/dialogue_consumer.py`
- 模块导出: `src/infrastructure/messaging/__init__.py`
- 主应用集成: `src/main.py`
- 单元测试: `tests/unit/test_dialogue_consumer.py`
- 集成测试: `tests/integration/test_message_queue_integration.py`

---

## 技术依赖

### 已安装依赖（requirements.txt）

- `pika>=1.3.2` - RabbitMQ 客户端（同步）
- `aio-pika>=9.0.0` - RabbitMQ 异步客户端（新增）
- `pydantic>=2.0.0` - 数据验证
- `asyncio` - 异步处理（Python 标准库）
- `structlog>=23.2.0` - 结构化日志

### 需要确认的依赖

- 检查 aio-pika 版本是否支持异步 API（已确认使用 aio-pika 9.0.0+）

---

## 验收标准总览

- [x] 实现 RabbitMQ 连接管理
- [x] 实现对话归档消费者
- [x] 正确监听 `aam.dialogue.archive` 队列
- [x] 使用 Pydantic 验证消息
- [x] 调用 `MemoryServiceImpl.archive()` 方法
- [x] 实现错误处理和日志记录
- [x] 实现优雅关闭
- [x] 集成到主应用生命周期
- [x] 通过类型检查（mypy）
- [x] 通过单元测试（pytest，覆盖率 >= 85%）
- [x] 通过集成测试
- [x] 代码包含标准头部注释
- [x] 符合项目开发规范（AiDevelopmentGuide.md）
- [x] 符合 SD 文件规范

---

## 实施顺序

1. **任务 5.1**: RabbitMQ 配置管理（基础设施）
2. **任务 5.2**: 对话归档消费者实现（核心功能）
3. **任务 5.4**: 模块导出更新（整合）
4. **任务 5.3**: 集成到主应用（整合）
5. **任务 5.5**: 创建单元测试（验证）
6. **任务 5.6**: 创建集成测试（端到端验证）

---

## 依赖关系

- **前置依赖**: 批次四（业务逻辑层实现）必须完成
- **内部依赖**: 
  - `DialogueArchiveConsumer` 依赖 `IMemoryService` 接口
  - `DialogueArchiveConsumer` 依赖 `RabbitMQConnection`
- **后续依赖**: 批次六（API 控制器）将独立实现，不依赖批次五

---

## 预计工作量

- RabbitMQ 配置管理: 2 小时
- 对话归档消费者实现: 4 小时
- 集成到主应用: 1.5 小时
- 模块导出更新: 0.5 小时
- 单元测试: 3 小时
- 集成测试: 2 小时
- **总计**: 约 13 小时

---

## 潜在风险和注意事项

1. **异步 API 选择**: 使用 `aio-pika` 替代 `pika` 以获得更好的异步支持
2. **消息确认机制**: 需要正确实现 ACK/NACK，避免消息丢失或无限重试
3. **优雅关闭**: 需要确保应用关闭时正在处理的消息能够完成，避免数据丢失
4. **连接重试**: 需要实现健壮的重连机制，处理 RabbitMQ 临时不可用的情况
5. **消息幂等性**: 虽然当前不实现，但需要考虑未来是否需要支持消息去重

---

## 关键实现细节

### RabbitMQConnection 实现要点

```python
class RabbitMQConnection:
    def __init__(self, settings: RabbitMQSettings):
        self.settings = settings
        self.connection = None
        self.channel = None
    
    async def connect(self):
        # 建立连接，实现重试机制
        pass
    
    async def setup_queue(self, queue_name: str):
        # 声明队列
        pass
    
    async def close(self):
        # 优雅关闭
        pass
```

### DialogueArchiveConsumer 实现要点

```python
class DialogueArchiveConsumer:
    def __init__(
        self,
        memory_service: IMemoryService,
        rabbitmq_connection: RabbitMQConnection
    ):
        self.memory_service = memory_service
        self.rabbitmq = rabbitmq_connection
    
    async def start_consuming(self):
        # 设置队列，开始消费
        await self.rabbitmq.setup_queue("aam.dialogue.archive")
        # 注册消息处理回调
        # 开始消费循环
    
    async def _process_message(self, channel, method, properties, body):
        # 解析和验证消息
        # 调用 memory_service.archive()
        # 发送 ACK/NACK
        pass
```

### 主应用集成要点

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    consumer = DialogueArchiveConsumer(...)
    consumer_task = asyncio.create_task(consumer.start_consuming())
    
    yield
    
    # 关闭时
    await consumer.stop_consuming()
    consumer_task.cancel()
    await asyncio.wait_for(consumer_task, timeout=30.0)
```

---

**最后更新**: 2025-11-12

