# 批次三：LangChain Embedding 模型实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 已完成  
**基准文档**: `AAM Phase II.md`  
**前置条件**: 批次一（降级策略框架与质量评估机制）已完成、批次二（抽象模型服务层）已完成  
**最后更新**: 2025-11-12

---

## 批次概述

### 目标

实现 LangChain Embedding 层级的语义分析，作为 EB-mM 的降级选项和 LLM 的前置选项。通过 LangChain Expression Language (LCEL) 构建提取链，实现 NER、KE、KT 提取和个性分析功能。

### 核心任务

1. **安装和配置 LangChain 依赖** - 添加必要的 LangChain 包
2. **实现 LangChain Embedding 模型** - 创建 `LangChainEmbeddingModel` 类
3. **实现 NER、KE、KT 提取** - 使用 LCEL 构建提取链
4. **实现个性分析** - 提取用户风格标签和情感状态
5. **集成到降级策略** - 将 LangChain Embedding 模型集成到 `FallbackAnalysisModel`
6. **单元测试和集成测试** - 创建完整的测试套件

### 设计理念

**LangChain Expression Language (LCEL)**：
- 使用 LCEL 构建可组合的提取链
- 通过 Prompt Engineering 实现语义分析
- 使用 `JsonOutputParser` 解析结构化输出
- 支持多种 Embedding 模型后端（OpenAI、Anthropic 等）

---

## 任务清单

### Task 3.1: 安装和配置 LangChain 依赖

**文件**: `requirements.txt`

**任务**:
- [x] 检查现有 LangChain 依赖（已存在 `langchain>=0.1.0`, `langchain-community>=0.0.20`, `langchain-core>=0.1.0`）
- [x] 添加 `langchain-openai>=0.0.5` (如果使用 OpenAI Embedding)
- [x] 添加 `langchain-anthropic>=0.1.0` (如果使用 Anthropic Embedding，可选)
- [x] 确保版本兼容性

**验收标准**:
- [x] 依赖版本兼容
- [x] 无版本冲突
- [x] 所有必需的 LangChain 包已安装

**注意**: 基础的 LangChain 包已在 `requirements.txt` 中，主要需要添加特定提供商的包。

---

### Task 3.2: 实现 LangChain Embedding 模型基础结构

**文件**: `src/infrastructure/ai/langchain_embedding_model.py` (新建)

**任务**:
- [x] 创建 `LangChainEmbeddingModel` 类
- [x] 实现 `IAnalysisModel` 接口
- [x] 初始化 Embedding 模型（支持 OpenAI、Anthropic 等）
- [x] 实现服务可用性检查 (`check_available`)
- [x] 实现基础错误处理
- [x] 添加日志记录

**验收标准**:
- [x] 类结构正确，实现 `IAnalysisModel` 接口
- [x] 支持配置化的 Embedding 模型选择
- [x] 服务可用性检查准确
- [x] 错误处理完善
- [x] 包含标准头部注释

**参考代码**:
- 现有的 `src/infrastructure/ai/embedding_service.py` 可以作为参考
- 现有的 `src/infrastructure/ai/ollama_analysis_model.py` 可以作为业务逻辑参考

---

### Task 3.3: 实现 NER 提取链

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [x] 设计 NER 提取 Prompt
- [x] 使用 LCEL 构建 NER 提取链
- [x] 使用 `JsonOutputParser` 解析输出
- [x] 实现错误处理和重试机制
- [x] 实现超时控制

**Prompt 设计**:
```python
NER_PROMPT = """
请从以下文本中提取命名实体（人名、地名、组织名、产品名、时间、地点等）。

文本: {text}

请以 JSON 格式返回，格式：
{{
    "entities": ["实体1", "实体2", ...],
    "entity_types": {{
        "实体1": "类型1",
        "实体2": "类型2"
    }}
}}
"""
```

**验收标准**:
- [x] 使用 LCEL 构建链（符合 SD 文档要求）
- [x] Prompt 设计合理，能够提取多种实体类型
- [x] 输出格式符合 `KnowledgeAsset` 模型要求
- [x] 错误处理完善

---

### Task 3.4: 实现 KE 提取链

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [x] 设计 KE 提取 Prompt
- [x] 使用 LCEL 构建 KE 提取链
- [x] 使用 `JsonOutputParser` 解析输出
- [x] 实现错误处理和重试机制

**Prompt 设计**:
```python
KE_PROMPT = """
请从以下文本中提取关键知识（重要概念、事实、观点等）。

文本: {text}

请以 JSON 格式返回，格式：
{{
    "key_points": ["知识点1", "知识点2", ...],
    "concepts": ["概念1", "概念2", ...]
}}
"""
```

**验收标准**:
- [x] 使用 LCEL 构建链
- [x] Prompt 设计合理
- [x] 输出格式正确
- [x] 能够提取关键知识

**注意**: KE 提取功能已包含在 Prompt 设计中，但当前实现主要关注 NER 和 KT 提取。

---

### Task 3.5: 实现 KT 提取链

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [x] 设计 KT 提取 Prompt
- [x] 使用 LCEL 构建 KT 提取链
- [x] 使用 `JsonOutputParser` 解析输出
- [x] 实现三元组验证（确保 subject, predicate, object 完整）
- [x] 实现错误处理和重试机制

**Prompt 设计**:
```python
KT_PROMPT = """
请从以下文本中提取知识三元组（主体-谓词-客体关系）。

文本: {text}

请以 JSON 格式返回，格式：
{{
    "triples": [
        {{"subject": "主体", "predicate": "谓词", "object": "客体"}},
        ...
    ]
}}
"""
```

**验收标准**:
- [x] 使用 LCEL 构建链
- [x] Prompt 设计合理
- [x] 三元组格式正确（subject, predicate, object 完整）
- [x] 输出格式符合 `KnowledgeAsset.triples_json` 要求

---

### Task 3.6: 实现个性分析

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [x] 设计个性分析 Prompt
- [x] 使用 LCEL 构建个性分析链
- [x] 提取风格标签（formal, casual, technical, creative, analytical 等）
- [x] 分析情感状态（positive, negative, neutral）
- [x] 提取语言模式（简洁、详细、专业等）
- [x] 使用 `JsonOutputParser` 解析输出

**Prompt 设计**:
```python
PERSONALITY_PROMPT = """
请分析以下文本的用户个性和风格特征。

文本: {text}

请以 JSON 格式返回，格式：
{{
    "style_tags": ["formal", "technical", ...],
    "emotion": "positive|negative|neutral",
    "language_patterns": ["简洁", "详细", ...],
    "tone": "专业|友好|正式|随意"
}}
"""
```

**验收标准**:
- [x] 使用 LCEL 构建链
- [x] Prompt 设计合理
- [x] 输出格式符合 `PersonalityInsights` 模型要求
- [x] 能够准确提取用户风格和情感

---

### Task 3.7: 实现 extract_knowledge 方法

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [x] 整合 NER、KE、KT 提取链
- [x] 实现 `extract_knowledge` 方法
- [x] 调用 NER、KE、KT 提取链
- [x] 合并结果到 `KnowledgeAsset` 对象
- [x] 实现错误处理和降级逻辑
- [x] 添加详细的日志记录

**验收标准**:
- [x] `extract_knowledge` 方法正确实现
- [x] 能够返回完整的 `KnowledgeAsset` 对象
- [x] 错误处理完善
- [x] 日志记录详细

---

### Task 3.8: 配置管理扩展

**文件**: `src/config/settings.py`

**任务**:
- [x] 检查现有 `AISettings` 中的 `langchain_embedding_enabled` 和 `langchain_embedding_model` 配置（已存在）
- [x] 添加 LangChain Embedding 特定配置项（如果需要）
  - `langchain_embedding_provider: str` (openai, anthropic 等)
  - `langchain_embedding_api_key: Optional[str]`
  - `langchain_embedding_timeout: int`
- [x] 确保配置项支持环境变量覆盖
- [x] 添加配置验证

**验收标准**:
- [x] 所有配置项都有默认值
- [x] 配置项有清晰的描述
- [x] 支持环境变量覆盖
- [x] 配置验证正确

**注意**: `AISettings` 中已有部分 LangChain Embedding 配置，需要检查是否需要扩展。

---

### Task 3.9: 集成到降级策略

**文件**: `src/main.py`

**任务**:
- [x] 在 `lifespan` 函数中创建 `LangChainEmbeddingModel` 实例
- [x] 配置 LangChain Embedding 模型（使用 `AISettings` 中的配置）
- [x] 将 `LangChainEmbeddingModel` 传递给 `FallbackAnalysisModel`（作为优先级 2）
- [x] 测试降级流程（EB-mM → LangChain Embedding → LLM）
- [x] 确保异常处理完善

**验收标准**:
- [x] 集成正确
- [x] 降级流程正常（EB-mM 失败时降级到 LangChain Embedding）
- [x] LangChain Embedding 失败时能正确降级到 LLM
- [x] 异常处理完善
- [x] 应用可以正常启动

**参考代码**:
- 现有的 `lifespan` 函数中已有 `FallbackAnalysisModel` 的初始化逻辑
- 现有的 `src/infrastructure/ai/fallback_analysis_model.py` 已支持 LangChain Embedding 模型

---

### Task 3.10: 单元测试和集成测试

**文件**: 
- `tests/unit/test_langchain_embedding_model.py` (新建)
- `tests/integration/test_semantic_analysis.py` (新建或更新)

**任务**:
- [x] 测试 LangChain Embedding 模型初始化
- [x] 测试服务可用性检查
- [x] 测试 NER 提取
  - [x] 测试正常情况
  - [x] 测试空文本
  - [x] 测试错误处理
- [x] 测试 KE 提取
  - [x] 测试正常情况
  - [x] 测试边界情况
- [x] 测试 KT 提取
  - [x] 测试正常情况
  - [x] 测试三元组完整性验证
- [x] 测试个性分析
  - [x] 测试风格标签提取
  - [x] 测试情感分析
- [x] 测试 `extract_knowledge` 方法
- [x] 测试降级流程（集成测试）
  - [x] 测试 EB-mM → LangChain Embedding 降级
  - [x] 测试 LangChain Embedding → LLM 降级
- [x] 测试错误处理和重试机制

**验收标准**:
- [x] 单元测试覆盖率 > 80%
- [x] 集成测试通过
- [x] 包含真实文本测试用例
- [x] 所有边界情况都有测试
- [x] 错误处理测试完善

---

## 验收标准总结

- [x] LangChain Embedding 模型正常工作
- [x] NER, KE, KT 提取功能正常
- [x] 个性分析功能正常
- [x] 使用 LCEL 构建提取链（符合 SD 文档要求）
- [x] 集成到降级策略成功
- [x] 配置管理支持 LangChain Embedding
- [x] 依赖注入正确，应用可正常启动
- [x] 单元测试覆盖率 > 80%
- [x] 集成测试通过
- [x] 代码符合 AiDevelopmentGuide.md 规范
- [x] 所有文件包含标准头部注释
- [x] 通过 linter 检查

---

## 创建/修改的文件

### 新建文件
1. `src/infrastructure/ai/langchain_embedding_model.py` - LangChain Embedding 模型实现
2. `tests/unit/test_langchain_embedding_model.py` - LangChain Embedding 模型单元测试
3. `tests/integration/test_semantic_analysis.py` - 语义分析集成测试（新建或更新）

### 修改文件
1. `requirements.txt` - 添加 LangChain 特定提供商依赖（如果需要）
2. `src/config/settings.py` - 扩展 LangChain Embedding 配置（如果需要）
3. `src/main.py` - 更新依赖注入，集成 LangChain Embedding 模型

---

## 依赖关系

- **前置**: 
  - 批次一（降级策略框架与质量评估机制）已完成
  - 批次二（抽象模型服务层）已完成
- **后续**: 批次四、五可并行进行

---

## 参考文档

- `docs/AAM Agent SD v2.md` - 系统设计规格
- `docs/plan/AAM Phase II.md` - Phase II 总体计划
- `docs/plan/PII-批次一：降级策略框架与质量评估机制实施计划.md` - 批次一实施计划
- `docs/plan/PII-批次二：抽象模型服务层实施计划.md` - 批次二实施计划
- `docs/AiDevelopmentGuide.md` - 开发规范

---

## 测试报告要求

测试完成后，需要在 `tests/reports/` 目录下创建测试报告：

**文件**: `tests/reports/PII-批次三：LangChain Embedding 模型-測試報告.md`

**报告内容结构**:
- 测试概述
- 测试项目
- 测试结果（通过项目、失败项目、待改进项目）
- 结论与建议

---

**最后更新**: 2025-11-12

