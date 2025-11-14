# 批次二：抽象接口定义（Interface Layer）实施计划

**创建日期**: 2025-11-12
**版本**: v1.0
**状态**: 待批准
**前置依赖**: 批次一（数据协议定义）已完成

---

## 计划概述

根据 `AAM Agent SD v1.md` 的规范和 `AAM 服務第一階段 MVP 實施計劃.md`，完成批次二的抽象接口定义。本批次实现依赖倒置原则（DIP），为后续的数据存取层和业务逻辑层提供稳定的抽象接口。

---

## 任务清单

### 任务 2.1：定义 PersonalityInsights 模型

**文件**: `src/models/domain/personality.py`

**任务内容**:

- [ ] 定义 `PersonalityInsights` Pydantic 模型
- `style_tags: Dict[str, int]` - 风格标签字典（例如：{"formal": 10, "casual": 5}）
- `sentiment: str` - 情感状态（例如："positive", "negative", "neutral"）
- `language_patterns: List[str]` - 语言模式列表（可选）
- `confidence_score: float` - 分析置信度分数（0.0-1.0）

**参考规范**: SD 文件 6.2 节类图（IAnalysisModel.analyze_personality 返回类型）

**验收标准**:

- 使用 Pydantic BaseModel
- 包含完整的类型注解
- 符合 SD 文件规范
- 通过类型检查

---

### 任务 2.2：定义记忆服务接口

**文件**: `src/core/interfaces/i_memory_service.py`

**任务内容**:

- [ ] 定义 `IMemoryService` 抽象类（继承 `abc.ABC`）
- `async def enrich(mcp: PartialMCP) -> EnrichedMCP` - 丰富化 MCP
- `async def archive(message: DialogueArchiveMessage) -> None` - 归档对话消息

**参考规范**: SD 文件 6.2 节类图

**验收标准**:

- 使用 `@abstractmethod` 装饰器
- 所有方法包含完整的类型注解
- 符合依赖倒置原则
- 通过类型检查（mypy）

---

### 任务 2.3：定义知识库接口

**文件**: `src/core/interfaces/i_knowledge_store.py`

**任务内容**:

- [ ] 定义 `IKnowledgeStore` 抽象类（继承 `abc.ABC`）
- `async def save(knowledge: KnowledgeAsset) -> None` - 保存知识资产
- `async def search(query: str, user_id: str, limit: int = 10) -> List[RetrievedDoc]` - 搜索相关知识

**参考规范**: SD 文件 6.2 节类图

**验收标准**:

- 使用 `@abstractmethod` 装饰器
- 所有方法包含完整的类型注解
- 符合 Repository Pattern
- 通过类型检查

---

### 任务 2.4：定义用户画像接口

**文件**: `src/core/interfaces/i_persona_store.py`

**任务内容**:

- [ ] 定义 `IPersonaStore` 抽象类（继承 `abc.ABC`）
- `async def save_or_update(profile: UserProfileDB) -> None` - 保存或更新用户画像
- `async def get(user_id: str) -> Optional[UserProfileDB]` - 获取用户画像

**参考规范**: SD 文件 6.2 节类图

**验收标准**:

- 使用 `@abstractmethod` 装饰器
- 所有方法包含完整的类型注解
- 使用 Optional 处理用户不存在的情况
- 通过类型检查

---

### 任务 2.5：定义分析模型接口

**文件**: `src/core/interfaces/i_analysis_model.py`

**任务内容**:

- [ ] 定义 `IAnalysisModel` 抽象类（继承 `abc.ABC`）
- `async def extract_knowledge(text: str, user_id: str, session_id: str) -> KnowledgeAsset` - 提取知识
- `async def analyze_personality(text: str) -> PersonalityInsights` - 分析用户个性

**参考规范**: SD 文件 6.2 节类图

**验收标准**:

- 使用 `@abstractmethod` 装饰器
- 所有方法包含完整的类型注解
- 符合 AI 模型适配器接口规范
- 通过类型检查

---

### 任务 2.6：更新模块导出

**文件**:

- `src/models/domain/__init__.py`
- `src/models/__init__.py`
- `src/core/interfaces/__init__.py`

**任务内容**:

- [ ] 导出 `PersonalityInsights` 模型
- [ ] 导出所有接口类（IMemoryService, IKnowledgeStore, IPersonaStore, IAnalysisModel）

**验收标准**:

- 所有接口和模型都可以通过统一导入使用
- 符合 Python 模块导出规范

---

### 任务 2.7：创建单元测试

**文件**:

- `tests/unit/test_personality_model.py`
- `tests/unit/test_interfaces.py`

**任务内容**:

- [ ] 测试 `PersonalityInsights` 模型的验证和序列化
- [ ] 测试所有接口的抽象方法定义
- [ ] 测试接口不能被直接实例化
- [ ] 测试接口的实现类必须实现所有抽象方法

**验收标准**:

- 所有测试用例通过
- 测试覆盖率 >= 90%
- 符合 pytest 测试规范

---

## 实施原则

1. **依赖倒置原则**: 所有接口定义在 `src/core/interfaces/`，业务逻辑依赖抽象接口
2. **协议优先**: PersonalityInsights 模型使用 Pydantic BaseModel
3. **类型安全**: 所有接口方法包含完整的类型注解
4. **测试驱动**: 每个接口都有对应的测试用例

---

## 文件组织

- 模型文件: `src/models/domain/personality.py`
- 接口文件: `src/core/interfaces/`
- `i_memory_service.py`
- `i_knowledge_store.py`
- `i_persona_store.py`
- `i_analysis_model.py`
- 测试文件: `tests/unit/`
- `test_personality_model.py`
- `test_interfaces.py`

---

## 验收标准总览

- [ ] 所有接口使用 `abc.ABC` 和 `@abstractmethod`
- [ ] 所有方法包含完整的类型注解
- [ ] PersonalityInsights 模型符合 Pydantic 规范
- [ ] 通过类型检查（mypy）
- [ ] 通过单元测试（pytest）
- [ ] 代码包含标准头部注释
- [ ] 符合项目开发规范（AiDevelopmentGuide.md）
- [ ] 符合 SD 文件规范

---

## 实施顺序

1. **任务 2.1**: 定义 PersonalityInsights 模型（基础模型）
2. **任务 2.2-2.5**: 定义四个核心接口（可并行）
3. **任务 2.6**: 更新模块导出
4. **任务 2.7**: 创建单元测试

---

## 依赖关系

- **前置依赖**: 批次一（数据协议定义）必须完成
- **后续依赖**: 批次三（数据存取层实现）将实现这些接口

---

## 预计工作量

- PersonalityInsights 模型: 0.5 小时
- 四个接口定义: 1 小时
- 模块导出更新: 0.5 小时
- 单元测试: 1.5 小时
- **总计**: 约 3.5 小时

---

**最后更新**: 2025-11-12