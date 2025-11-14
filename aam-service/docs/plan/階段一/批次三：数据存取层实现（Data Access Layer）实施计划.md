# 批次三：数据存取层实现（Data Access Layer）实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 待批准  
**前置依赖**: 批次二（抽象接口定义）已完成

---

## 计划概述

根据 `AAM Agent SD v1.md` 的规范和 `AAM 服務第一階段 MVP 實施計劃.md`，完成批次三的数据存取层实现。本批次实现 ChromaDB 和 PostgreSQL 的具体数据存取逻辑，遵循 Repository Pattern，为业务逻辑层提供稳定的数据访问接口。

---

## 任务清单

### 任务 3.1：向量化服务实现

**文件**: `src/infrastructure/ai/embedding_service.py`

**任务内容**:
- [ ] 定义 `EmbeddingService` 类
  - 使用 Sentence Transformer 模型进行文本向量化
  - 支持模型加载和缓存
  - 实现 `embed_text(text: str) -> List[float]` 方法
  - 实现 `embed_batch(texts: List[str]) -> List[List[float]]` 方法（批量处理）
  - 从配置加载模型名称（`AISettings.embedding_model`）

**参考规范**: SD 文件 3.1.1 节（向量化步骤）

**验收标准**:
- 封装 Sentence Transformer 模型
- 支持单文本和批量文本向量化
- 通过单元测试
- 配置化模型名称

---

### 任务 3.2：ChromaDB 知识库实现

**文件**: `src/infrastructure/database/chroma_knowledge_store.py`

**任务内容**:
- [ ] 实现 `ChromaKnowledgeStore` 类
  - 继承 `IKnowledgeStore` 接口
  - 初始化 ChromaDB 客户端（使用 `ChromaDBSettings`）
  - 获取或创建 `knowledge_assets` collection
  - 实现 `save()` 方法
    - 接收 `KnowledgeAsset` 对象
    - 提取文本内容（需要从对话消息中提取）
    - 调用 `EmbeddingService` 进行向量化
    - 转换元数据（使用 `KnowledgeAsset.to_chromadb_metadata()`）
    - 存储到 ChromaDB collection
  - 实现 `search()` 方法
    - 接收查询字符串和 `user_id`
    - 向量化查询字符串
    - 执行混合搜索（向量相似度 + 元数据过滤 `user_id`）
    - 返回 `List[RetrievedDoc]`（包含 source, content, score）

**参考规范**: SD 文件 3.2 节、4.3.1 节、5.1 节

**验收标准**:
- 实现 Repository Pattern
- 封装所有 ChromaDB 特定逻辑
- 通过单元测试（使用 Mock ChromaDB 客户端）
- 正确处理向量化和元数据转换
- 符合 SD 文件规范

---

### 任务 3.3：PostgreSQL 数据库模型定义

**文件**: `src/infrastructure/database/models.py`

**任务内容**:
- [ ] 定义 SQLAlchemy ORM 模型 `UserProfileTable`
  - 对应 `UserProfileDB` Pydantic 模型
  - 表名：`user_profiles`
  - 字段：
    - `user_id` (VARCHAR, PRIMARY KEY)
    - `style_tags` (JSONB)
    - `sentiment_history` (JSONB)
    - `last_updated` (TIMESTAMP)
  - 实现与 `UserProfileDB` 的转换方法

**参考规范**: SD 文件 3.3 节、4.3.2 节

**验收标准**:
- 使用 SQLAlchemy 2.0+ 语法
- 支持异步操作
- 字段类型正确（JSONB 用于字典字段）
- 通过类型检查

---

### 任务 3.4：Alembic 数据库迁移

**文件**: `alembic/versions/xxxx_create_user_profiles_table.py`

**任务内容**:
- [ ] 创建 Alembic migration 脚本
  - 创建 `user_profiles` 表
  - 定义所有字段和约束
  - 创建索引（如需要）
  - 支持升级和降级操作

**参考规范**: SD 文件 3.3 节

**验收标准**:
- Migration 脚本可执行
- 支持升级和回滚
- 符合 Alembic 最佳实践

---

### 任务 3.5：PostgreSQL 用户画像实现

**文件**: `src/infrastructure/database/pg_persona_store.py`

**任务内容**:
- [ ] 实现 `PgPersonaStore` 类
  - 继承 `IPersonaStore` 接口
  - 初始化 SQLAlchemy 异步引擎和会话
  - 使用 `PostgresSettings.postgres_async_url`
  - 实现 `save_or_update()` 方法
    - 接收 `UserProfileDB` 对象
    - 转换为 SQLAlchemy 模型
    - 执行 UPSERT 操作（ON CONFLICT UPDATE）
    - 更新 `last_updated` 时间戳
  - 实现 `get()` 方法
    - 根据 `user_id` 查询
    - 转换为 `UserProfileDB` 对象
    - 如果不存在返回 `None`

**参考规范**: SD 文件 3.3 节、5.1 节

**验收标准**:
- 实现 Repository Pattern
- 封装所有 PostgreSQL 特定逻辑
- 使用异步 SQLAlchemy
- 正确处理 JSONB 字段
- 通过单元测试（使用 Mock 或测试数据库）
- 符合 SD 文件规范

---

### 任务 3.6：数据库连接管理

**文件**: `src/infrastructure/database/__init__.py`

**任务内容**:
- [ ] 创建数据库连接工厂函数
  - `create_chromadb_client(settings: ChromaDBSettings) -> ChromaClient`
  - `create_postgres_engine(settings: PostgresSettings) -> AsyncEngine`
  - `create_postgres_session(engine: AsyncEngine) -> AsyncSession`
- [ ] 实现连接池管理
  - PostgreSQL 连接池配置
  - 连接生命周期管理
- [ ] 导出所有 Store 类和工厂函数

**验收标准**:
- 连接工厂函数可复用
- 连接池配置合理
- 支持优雅关闭

---

### 任务 3.7：模块导出更新

**文件**: 
- `src/infrastructure/__init__.py`
- `src/infrastructure/database/__init__.py`
- `src/infrastructure/ai/__init__.py`

**任务内容**:
- [ ] 导出 `ChromaKnowledgeStore` 和 `PgPersonaStore`
- [ ] 导出 `EmbeddingService`
- [ ] 导出数据库连接工厂函数

**验收标准**:
- 所有类都可以通过统一导入使用
- 符合 Python 模块导出规范

---

### 任务 3.8：创建单元测试

**文件**: 
- `tests/unit/test_embedding_service.py`
- `tests/unit/test_chroma_knowledge_store.py`
- `tests/unit/test_pg_persona_store.py`
- `tests/unit/test_database_models.py`

**任务内容**:
- [ ] 测试 `EmbeddingService` 的向量化功能
- [ ] 测试 `ChromaKnowledgeStore` 的 save 和 search 方法（使用 Mock）
- [ ] 测试 `PgPersonaStore` 的 save_or_update 和 get 方法（使用 Mock 或测试数据库）
- [ ] 测试数据库模型转换
- [ ] 测试连接工厂函数

**验收标准**:
- 所有测试用例通过
- 测试覆盖率 >= 85%
- 符合 pytest 测试规范
- 使用 Mock 隔离外部依赖

---

## 实施原则

1. **Repository Pattern**: 所有数据存取类实现对应的接口，封装数据库特定逻辑
2. **配置化**: 所有数据库连接参数从配置类加载
3. **异步优先**: 所有数据库操作使用异步方法
4. **类型安全**: 所有方法包含完整的类型注解
5. **测试驱动**: 每个实现类都有对应的测试用例

---

## 文件组织

- 向量化服务: `src/infrastructure/ai/embedding_service.py`
- ChromaDB 实现: `src/infrastructure/database/chroma_knowledge_store.py`
- PostgreSQL 模型: `src/infrastructure/database/models.py`
- PostgreSQL 实现: `src/infrastructure/database/pg_persona_store.py`
- 数据库迁移: `alembic/versions/`
- 连接管理: `src/infrastructure/database/__init__.py`
- 测试文件: `tests/unit/`

---

## 技术依赖

### 已安装依赖（requirements.txt）
- `chromadb>=0.4.18` - ChromaDB 客户端
- `psycopg2-binary>=2.9.9` - PostgreSQL 驱动
- `sqlalchemy[asyncio]>=2.0.23` - SQLAlchemy 异步支持
- `alembic>=1.12.1` - 数据库迁移工具
- `sentence-transformers>=2.2.2` - 向量化模型
- `asyncpg>=0.29.0` - PostgreSQL 异步驱动（SQLAlchemy 需要）

### 需要确认的依赖
- 检查 `asyncpg` 是否在 requirements.txt 中（SQLAlchemy async 需要）

---

## 验收标准总览

- [ ] 所有 Store 类实现对应的接口
- [ ] 封装所有数据库特定逻辑
- [ ] 使用配置类加载连接参数
- [ ] 支持异步操作
- [ ] 通过类型检查（mypy）
- [ ] 通过单元测试（pytest）
- [ ] 代码包含标准头部注释
- [ ] 符合项目开发规范（AiDevelopmentGuide.md）
- [ ] 符合 SD 文件规范

---

## 实施顺序

1. **任务 3.1**: 向量化服务实现（基础服务）
2. **任务 3.3**: PostgreSQL 数据库模型定义（数据模型）
3. **任务 3.4**: Alembic 数据库迁移（数据库结构）
4. **任务 3.2**: ChromaDB 知识库实现（依赖任务 3.1）
5. **任务 3.5**: PostgreSQL 用户画像实现（依赖任务 3.3）
6. **任务 3.6**: 数据库连接管理（整合）
7. **任务 3.7**: 模块导出更新
8. **任务 3.8**: 创建单元测试

---

## 依赖关系

- **前置依赖**: 批次二（抽象接口定义）必须完成
- **内部依赖**: 
  - ChromaDB 实现依赖向量化服务
  - PostgreSQL 实现依赖数据库模型和迁移
- **后续依赖**: 批次四（业务逻辑层实现）将使用这些 Store 实现

---

## 预计工作量

- 向量化服务: 1 小时
- ChromaDB 实现: 2 小时
- PostgreSQL 模型和迁移: 1.5 小时
- PostgreSQL 实现: 2 小时
- 连接管理: 1 小时
- 模块导出: 0.5 小时
- 单元测试: 2.5 小时
- **总计**: 约 10.5 小时

---

## 潜在风险和注意事项

1. **ChromaDB 文本内容来源**: `KnowledgeAsset` 模型中没有直接的文本内容字段，需要明确文本来源（可能是对话消息的 user_query + ai_response）
2. **向量化性能**: 批量向量化可以提高性能，需要考虑批量大小
3. **PostgreSQL JSONB 字段**: 需要正确处理字典和列表的序列化/反序列化
4. **异步操作**: 确保所有数据库操作使用异步方法，避免阻塞
5. **错误处理**: 需要实现完善的错误处理和日志记录

---

**最后更新**: 2025-11-12