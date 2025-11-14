# 批次四：业务逻辑层实现（Business Logic Layer）实施计划

**创建日期**: 2025-11-12

**版本**: v1.0

**状态**: 待批准

**前置依赖**: 批次三（数据存取层实现）已完成

---

## 计划概述

根据 `AAM Agent SD v1.md` 的规范和 `AAM 服務第一階段 MVP 實施計劃.md`，完成批次四的业务逻辑层实现。本批次实现 `MemoryServiceImpl` 类，作为系统的核心业务逻辑层，协调数据存取和 AI 模型，实现 MCP 丰富化和对话归档功能。

---

## 任务清单

### 任务 4.1：MemoryServiceImpl 核心实现

**文件**: `src/core/services/memory_service.py`

**任务内容**:

- [ ] 定义 `MemoryServiceImpl` 类
  - 继承 `IMemoryService` 接口
  - 通过构造函数接收依赖注入：
    - `knowledge_store: IKnowledgeStore`
    - `persona_store: IPersonaStore`
    - `analysis_model: IAnalysisModel`
  - 实现 `enrich()` 方法（同步 API 调用）
    - 从 `PartialMCP` 中提取 `user_id` 和 `current_query`
    - **并行查询**知识库和用户画像：
      - 调用 `knowledge_store.search(query, user_id)` 检索相关知识
      - 调用 `persona_store.get(user_id)` 获取用户画像
    - 组装 `EnrichedMCP`：
      - 将检索到的文档转换为 `RetrievedDoc` 列表
      - 从用户画像中提取 `style_tags` 和 `sentiment_history`
      - 转换为 `UserProfileEnriched`（包含 `long_term_style_tags` 和 `current_sentiment`）
      - 创建 `RetrievedKnowledge`（docs 和 kg_triples）
      - 创建 `Metadata`（request_id, aam_version）
    - 返回完整的 `EnrichedMCP`
  - 实现 `archive()` 方法（异步处理）
    - 从 `DialogueArchiveMessage` 中提取对话内容
    - 构建文本内容：`user_query + " " + ai_response`
    - **并行调用** AI 模型进行分析：
      - 调用 `analysis_model.extract_knowledge(text, user_id, session_id)` 提取知识
      - 调用 `analysis_model.analyze_personality(text)` 分析个性
    - 保存知识资产：
      - 创建 `KnowledgeAsset` 对象
      - 调用 `knowledge_store.save(knowledge, text_content)` 保存到向量数据库
    - 更新用户画像：
      - 获取现有用户画像（`persona_store.get(user_id)`）
      - 合并新的个性分析结果到现有画像：
        - 更新 `style_tags`（累加计数）
        - 更新 `sentiment_history`（累加计数）
        - 更新 `last_updated` 时间戳
      - 调用 `persona_store.save_or_update(profile)` 保存更新后的画像

**参考规范**: SD 文件 3.1.1 节、3.1.2 节、5.1 节、5.2 节、6.2 节

**验收标准**:

- 实现 `IMemoryService` 接口
- 框架无关（不依赖 FastAPI 或 RabbitMQ）
- 通过依赖注入接收接口实现
- 使用 `asyncio.gather()` 实现并行查询
- 正确处理数据转换和组装
- 通过单元测试（使用 Mock）
- 符合业务逻辑规范

---

### 任务 4.2：数据转换辅助函数

**文件**: `src/core/services/memory_service.py`（同一文件）

**任务内容**:

- [ ] 实现 `_convert_user_profile_to_enriched()` 辅助方法
  - 将 `UserProfileDB` 转换为 `UserProfileEnriched`
  - 从 `style_tags` 字典中提取标签列表（转换为 `long_term_style_tags`）
  - 从 `sentiment_history` 字典中确定当前情感（选择计数最高的）
- [ ] 实现 `_merge_personality_insights()` 辅助方法
  - 合并 `PersonalityInsights` 到现有的 `UserProfileDB`
  - 累加 `style_tags` 计数
  - 累加 `sentiment_history` 计数
  - 更新 `last_updated` 时间戳

**验收标准**:

- 正确处理字典到列表的转换
- 正确处理情感状态的确定逻辑
- 正确处理计数累加逻辑
- 通过单元测试

---

### 任务 4.3：错误处理和日志记录

**文件**: `src/core/services/memory_service.py`（同一文件）

**任务内容**:

- [ ] 实现结构化日志记录
  - 使用 Python `logging` 模块
  - 记录关键操作（enrich、archive）
  - 包含上下文信息（`user_id`, `session_id`, `request_id`）
- [ ] 实现错误处理
  - 捕获并记录异常
  - 对于 `enrich()` 方法：如果查询失败，返回空结果而非抛出异常
  - 对于 `archive()` 方法：记录错误但允许继续处理（避免阻塞消息队列）

**验收标准**:

- 使用结构化日志格式
- 错误处理不影响系统稳定性
- 通过错误场景测试

---

### 任务 4.4：模块导出更新

**文件**: `src/core/services/__init__.py`

**任务内容**:

- [ ] 导出 `MemoryServiceImpl` 类
- [ ] 确保可以通过 `from src.core.services import MemoryServiceImpl` 导入

**验收标准**:

- 符合 Python 模块导出规范
- 可以通过统一导入使用

---

### 任务 4.5：创建单元测试

**文件**: `tests/unit/test_memory_service.py`

**任务内容**:

- [ ] 测试 `enrich()` 方法
  - 测试正常流程：并行查询知识库和用户画像
  - 测试知识库返回空结果的情况
  - 测试用户画像不存在的情况
  - 测试数据转换正确性
  - 使用 Mock 隔离外部依赖
- [ ] 测试 `archive()` 方法
  - 测试正常流程：并行调用 AI 模型，保存知识和更新画像
  - 测试新用户画像创建
  - 测试现有用户画像更新（计数累加）
  - 测试 AI 模型调用失败的处理
  - 使用 Mock 隔离外部依赖
- [ ] 测试辅助方法
  - 测试 `_convert_user_profile_to_enriched()`
  - 测试 `_merge_personality_insights()`
- [ ] 测试错误处理
  - 测试知识库查询失败的处理
  - 测试用户画像查询失败的处理
  - 测试 AI 模型调用失败的处理

**验收标准**:

- 所有测试用例通过
- 测试覆盖率 >= 85%
- 符合 pytest 测试规范
- 使用 Mock 隔离外部依赖

---

## 实施原则

1. **框架无关**: `MemoryServiceImpl` 不依赖 FastAPI 或 RabbitMQ，保持业务逻辑的纯净性
2. **依赖注入**: 所有外部依赖通过构造函数注入，便于测试和替换
3. **并行处理**: 使用 `asyncio.gather()` 实现并行查询，提高性能
4. **错误容错**: 错误处理不影响系统稳定性，记录日志但不阻塞流程
5. **数据转换**: 正确处理不同数据模型之间的转换

---

## 文件组织

- 服务实现: `src/core/services/memory_service.py`
- 测试文件: `tests/unit/test_memory_service.py`
- 模块导出: `src/core/services/__init__.py`

---

## 技术依赖

### 已安装依赖（requirements.txt）

- `pydantic>=2.0.0` - 数据验证
- `asyncio` - 异步处理和并行查询（Python 标准库）

### 需要确认的依赖

- 检查日志库配置（使用 Python 标准库 `logging` 或第三方库如 `structlog`）

---

## 验收标准总览

- [ ] 实现 `IMemoryService` 接口
- [ ] 框架无关（不依赖 FastAPI 或 RabbitMQ）
- [ ] 通过依赖注入接收接口实现
- [ ] 实现并行查询（使用 `asyncio.gather()`）
- [ ] 正确处理数据转换和组装
- [ ] 实现错误处理和日志记录
- [ ] 通过类型检查（mypy）
- [ ] 通过单元测试（pytest，覆盖率 >= 85%）
- [ ] 代码包含标准头部注释
- [ ] 符合项目开发规范（AiDevelopmentGuide.md）
- [ ] 符合 SD 文件规范

---

## 实施顺序

1. **任务 4.1**: MemoryServiceImpl 核心实现（主要业务逻辑）
2. **任务 4.2**: 数据转换辅助函数（支持功能）
3. **任务 4.3**: 错误处理和日志记录（完善功能）
4. **任务 4.4**: 模块导出更新（整合）
5. **任务 4.5**: 创建单元测试（验证）

---

## 依赖关系

- **前置依赖**: 批次三（数据存取层实现）必须完成
- **内部依赖**: 
  - `enrich()` 方法依赖 `IKnowledgeStore` 和 `IPersonaStore`
  - `archive()` 方法依赖 `IKnowledgeStore`、`IPersonaStore` 和 `IAnalysisModel`
- **后续依赖**: 批次五（消息队列处理）和批次六（API 控制器）将使用 `MemoryServiceImpl`

---

## 预计工作量

- MemoryServiceImpl 核心实现: 3 小时
- 数据转换辅助函数: 1 小时
- 错误处理和日志记录: 1 小时
- 模块导出更新: 0.5 小时
- 单元测试: 2.5 小时
- **总计**: 约 8 小时

---

## 潜在风险和注意事项

1. **并行查询性能**: 使用 `asyncio.gather()` 时需要注意异常处理，确保一个查询失败不影响另一个
2. **数据转换逻辑**: `UserProfileDB` 到 `UserProfileEnriched` 的转换需要正确处理字典到列表的转换
3. **计数累加逻辑**: 合并个性分析结果时，需要正确处理计数累加，避免数据丢失
4. **错误处理策略**: `enrich()` 和 `archive()` 的错误处理策略不同，需要仔细设计
5. **日志记录**: 结构化日志需要包含足够的上下文信息，便于问题追踪

---

## 关键实现细节

### enrich() 方法实现要点

```python
async def enrich(self, mcp: PartialMCP) -> EnrichedMCP:
    # 1. 提取查询信息
    user_id = mcp.user_profile.user_id
    query = mcp.session_context.current_query
    
    # 2. 并行查询
    knowledge_docs, user_profile = await asyncio.gather(
        self.knowledge_store.search(query, user_id),
        self.persona_store.get(user_id)
    )
    
    # 3. 数据转换和组装
    # ... 组装 EnrichedMCP
```

### archive() 方法实现要点

```python
async def archive(self, message: DialogueArchiveMessage) -> None:
    # 1. 构建文本内容
    text = f"{message.user_query} {message.ai_response}"
    
    # 2. 并行调用 AI 模型
    knowledge, personality = await asyncio.gather(
        self.analysis_model.extract_knowledge(text, message.user_id, session_id),
        self.analysis_model.analyze_personality(text)
    )
    
    # 3. 保存知识资产
    await self.knowledge_store.save(knowledge, text)
    
    # 4. 更新用户画像
    # ... 合并并保存
```

---

**最后更新**: 2025-11-12