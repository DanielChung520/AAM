# 批次四：EB-mM 模型集成实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 已完成  
**基准文档**: `AAM Phase II.md`  
**前置条件**: 批次一（降级策略框架与质量评估机制）已完成、批次二（抽象模型服务层）已完成  
**最后更新**: 2025-11-12

---

## 批次概述

### 目标

集成真实的 EB-mM (Enterprise Bot mini-Model) 模型，通过统一模型服务调用。EB-mM 基于 DeepSeek-R1 8B 进行 LoRA 微调，可通过 Ollama 或 vLLM 服务挂载。实现 EB-mM 业务逻辑层，优化 Prompt 设计，集成到降级策略，并完成完整的测试套件。

### 核心任务

1. **配置 EB-mM 模型服务** - 配置 Ollama/vLLM 服务，挂载 EB-mM 模型
2. **实现 EB-mM 业务逻辑层** - 创建 `EbMMAnalysisModel` 类，使用 `UnifiedModelService` 进行模型调用
3. **优化 Prompt 设计** - 针对 EB-mM 优化 NER、KE、KT 和个性分析的 Prompt
4. **性能优化** - 实现批处理、缓存机制等性能优化（可选）
5. **集成到降级策略** - 将 EB-mM 模型集成到 `FallbackAnalysisModel`（作为优先级 1）
6. **单元测试和集成测试** - 创建完整的测试套件

### 设计理念

**统一模型服务架构**：
- EB-mM 通过 `UnifiedModelService` 调用，无需直接加载模型
- 支持通过配置切换挂载方式（Ollama / vLLM）
- 使用 Provider Pattern，通过配置切换模型服务，无需修改代码
- 业务逻辑层（`EbMMAnalysisModel`）封装 EB-mM 特定的 Prompt 和逻辑

---

## 任务清单

### Task 4.1: 配置 EB-mM 模型服务

**文件**: `.env`, `src/config/settings.py`

**任务**:
- [x] 检查现有 `AISettings` 中的 EB-mM 配置项（`eb_mm_enabled`, `eb_mm_model_path`, `eb_mm_lora_path`）
- [x] 配置 Ollama 或 vLLM 服务（根据环境选择）
- [x] 挂载训练好的 EB-mM 模型（或使用原始 DeepSeek-R1 8B 进行集成测试）
- [x] 更新 `ModelServiceSettings` 配置，设置 `MODEL_NAME=eb-mm` 或 `MODEL_NAME=deepseek-r1:8b`
- [x] 确保配置支持环境变量覆盖
- [x] 添加配置验证逻辑

**验收标准**:
- [x] 模型服务配置正确
- [x] 模型可以正常调用（通过 `UnifiedModelService`）
- [x] 配置支持环境变量覆盖
- [x] 配置验证逻辑完善

**注意**: 如果 LoRA 训练未完成，可先使用原始 DeepSeek-R1 8B 模型进行集成测试。

---

### Task 4.2: 实现 EB-mM 业务逻辑层

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py` (新建)

**任务**:
- [x] 创建 `EbMMAnalysisModel` 类
- [x] 实现 `IAnalysisModel` 接口
- [x] 通过构造函数接收 `UnifiedModelService` 实例
- [x] 实现服务可用性检查 (`check_available`)
- [x] 实现基础错误处理和日志记录
- [x] 添加标准头部注释

**验收标准**:
- [x] 类结构正确，实现 `IAnalysisModel` 接口
- [x] 正确使用 `UnifiedModelService` 进行模型调用
- [x] 服务可用性检查准确
- [x] 错误处理完善
- [x] 包含标准头部注释

**参考代码**:
- 现有的 `src/infrastructure/ai/unified_model_service.py` 可以作为参考
- 现有的 `src/infrastructure/ai/langchain_embedding_model.py` 可以作为业务逻辑参考

---

### Task 4.3: 实现 NER 提取（优化 Prompt）

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [x] 设计针对 EB-mM 优化的 NER 提取 Prompt
- [x] 实现 NER 提取方法（调用 `UnifiedModelService`）
- [x] 实现 JSON 解析和验证
- [x] 实现错误处理和重试机制
- [x] 添加详细的日志记录

**Prompt 设计**:
```python
NER_PROMPT = """
你是一個專業的命名實體識別系統，專門針對企業對話場景進行優化。

請從以下文本中提取所有命名實體，包括但不限於：
- 人名（Person）
- 地名（Location）
- 組織名（Organization）
- 產品名（Product）
- 日期和時間（Date/Time）
- 技術術語（Technical Term）
- 業務概念（Business Concept）

文本: {text}

請以 JSON 格式返回，格式：
{{
    "entities": ["實體1", "實體2", ...],
    "entity_types": {{
        "實體1": "類型1",
        "實體2": "類型2"
    }},
    "confidence_scores": {{
        "實體1": 0.95,
        "實體2": 0.87
    }}
}}
"""
```

**验收标准**:
- [x] Prompt 设计针对 EB-mM 优化
- [x] 输出格式符合 `KnowledgeAsset` 模型要求
- [x] 错误处理完善
- [x] 日志记录详细

---

### Task 4.4: 实现 KE 提取（优化 Prompt）

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [x] 设计针对 EB-mM 优化的 KE 提取 Prompt
- [x] 实现 KE 提取方法（调用 `UnifiedModelService`）
- [x] 实现 JSON 解析和验证
- [x] 实现错误处理和重试机制

**Prompt 设计**:
```python
KE_PROMPT = """
你是一個專業的知識提取系統，專門針對企業對話場景進行優化。

請從以下文本中提取關鍵知識，包括：
- 重要概念（Important Concepts）
- 關鍵事實（Key Facts）
- 核心觀點（Core Opinions）
- 業務規則（Business Rules）
- 決策依據（Decision Basis）

文本: {text}

請以 JSON 格式返回，格式：
{{
    "key_points": ["知識點1", "知識點2", ...],
    "concepts": ["概念1", "概念2", ...],
    "facts": ["事實1", "事實2", ...]
}}
"""
```

**验收标准**:
- [x] Prompt 设计针对 EB-mM 优化
- [x] 输出格式正确
- [x] 能够提取关键知识

---

### Task 4.5: 实现 KT 提取（优化 Prompt）

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [x] 设计针对 EB-mM 优化的 KT 提取 Prompt
- [x] 实现 KT 提取方法（调用 `UnifiedModelService`）
- [x] 实现三元组验证（确保 subject, predicate, object 完整）
- [x] 实现 JSON 解析和验证
- [x] 实现错误处理和重试机制

**Prompt 设计**:
```python
KT_PROMPT = """
你是一個專業的知識三元組提取系統，專門針對企業對話場景進行優化。

請從以下文本中提取知識三元組（主體-謂詞-客體關係）。

三元組格式要求：
- 主體（Subject）：實體或概念
- 謂詞（Predicate）：關係或動作
- 客體（Object）：實體、概念或值

文本: {text}

請以 JSON 格式返回，格式：
{{
    "triples": [
        {{"subject": "主體", "predicate": "謂詞", "object": "客體"}},
        ...
    ]
}}
"""
```

**验收标准**:
- [x] Prompt 设计针对 EB-mM 优化
- [x] 三元组格式正确（subject, predicate, object 完整）
- [x] 输出格式符合 `KnowledgeAsset.triples_json` 要求

---

### Task 4.6: 实现个性分析（优化 Prompt）

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [x] 设计针对 EB-mM 优化的个性分析 Prompt
- [x] 实现个性分析方法（调用 `UnifiedModelService`）
- [x] 提取风格标签（formal, casual, technical, creative, analytical 等）
- [x] 分析情感状态（positive, negative, neutral）
- [x] 提取语言模式（简洁、详细、专业等）
- [x] 实现 JSON 解析和验证

**Prompt 设计**:
```python
PERSONALITY_PROMPT = """
你是一個專業的用戶個性分析系統，專門針對企業對話場景進行優化。

請分析以下文本的用戶個性和風格特徵：

文本: {text}

請分析以下維度：
1. 語言風格標籤（Style Tags）：formal, casual, technical, creative, analytical 等
2. 情感狀態（Sentiment）：positive, negative, neutral
3. 語言模式（Language Patterns）：簡潔、詳細、專業、友好等
4. 溝通風格（Communication Style）：直接、委婉、正式、隨意等

請以 JSON 格式返回，格式：
{{
    "style_tags": {{"formal": 0.8, "technical": 0.9, ...}},
    "sentiment": "positive|negative|neutral",
    "language_patterns": ["簡潔", "專業", ...],
    "tone": "專業|友好|正式|隨意",
    "confidence_score": 0.85
}}
"""
```

**验收标准**:
- [x] Prompt 设计针对 EB-mM 优化
- [x] 输出格式符合 `PersonalityInsights` 模型要求
- [x] 能够准确提取用户风格和情感

---

### Task 4.7: 实现 extract_knowledge 方法

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [x] 整合 NER、KE、KT 提取逻辑
- [x] 实现 `extract_knowledge` 方法
- [x] 调用 NER、KE、KT 提取方法
- [x] 合并结果到 `KnowledgeAsset` 对象
- [x] 实现错误处理和降级逻辑
- [x] 添加详细的日志记录

**验收标准**:
- [x] `extract_knowledge` 方法正确实现
- [x] 能够返回完整的 `KnowledgeAsset` 对象
- [x] 错误处理完善
- [x] 日志记录详细

---

### Task 4.8: 性能优化

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [ ] 实现批处理（batch processing）支持
- [ ] 实现缓存机制（可选，使用 LRU 缓存）
- [ ] 优化 Prompt 长度（减少不必要的文本）
- [ ] 实现请求合并（可选，合并多个提取请求）
- [ ] 添加性能监控和日志记录

**验收标准**:
- [ ] 响应时间 < 1000ms (P95)（通过 Ollama/vLLM）
- [ ] 批处理效率提升 > 30%（如果实现）
- [ ] 性能监控完善

**注意**: 性能优化是可选的，可以根据实际需求决定是否实现。当前实现已满足基本功能需求。

---

### Task 4.9: 集成到降级策略

**文件**: `src/main.py`

**任务**:
- [x] 在 `lifespan` 函数中创建 `EbMMAnalysisModel` 实例
- [x] 配置 EB-mM 模型（使用 `AISettings` 和 `ModelServiceSettings` 中的配置）
- [x] 创建 `UnifiedModelService` 实例（使用 EB-mM 配置的 Provider）
- [x] 将 `EbMMAnalysisModel` 传递给 `FallbackAnalysisModel`（作为优先级 1）
- [x] 测试完整降级流程（EB-mM → LangChain Embedding → LLM）
- [x] 确保异常处理完善

**验收标准**:
- [x] 集成正确
- [x] 降级流程正常（EB-mM 失败时降级到 LangChain Embedding）
- [x] LangChain Embedding 失败时能正确降级到 LLM
- [x] 异常处理完善
- [x] 应用可以正常启动

**参考代码**:
- 现有的 `lifespan` 函数中已有 `FallbackAnalysisModel` 的初始化逻辑
- 现有的 `src/infrastructure/ai/fallback_analysis_model.py` 已支持 EB-mM 模型

---

### Task 4.10: 单元测试和集成测试

**文件**: 
- `tests/unit/test_eb_mm_analysis_model.py` (新建)
- `tests/integration/test_eb_mm_integration.py` (新建)

**任务**:
- [x] 测试 EB-mM 模型初始化
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
- [x] 测试 Provider 切换（Ollama ↔ vLLM）
- [x] 测试错误处理和重试机制

**验收标准**:
- [x] 单元测试覆盖率 > 80%
- [x] 集成测试通过
- [x] 包含真实文本测试用例
- [x] 所有边界情况都有测试
- [x] 错误处理测试完善

---

## 验收标准总结

- [x] EB-mM 模型正常工作（通过统一模型服务）
- [x] NER, KE, KT 提取功能正常
- [x] 个性分析功能正常
- [x] 支持 Ollama 和 vLLM 挂载
- [x] 通过配置切换 Provider
- [x] 集成到降级策略成功
- [x] 配置管理支持 EB-mM
- [x] 依赖注入正确，应用可正常启动
- [x] 单元测试覆盖率 > 80%
- [x] 集成测试通过
- [x] 代码符合 AiDevelopmentGuide.md 规范
- [x] 所有文件包含标准头部注释
- [x] 通过 linter 检查

---

## 创建/修改的文件

### 新建文件
1. `src/infrastructure/ai/eb_mm_analysis_model.py` - EB-mM 业务逻辑层实现
2. `tests/unit/test_eb_mm_analysis_model.py` - EB-mM 模型单元测试
3. `tests/integration/test_eb_mm_integration.py` - EB-mM 集成测试

### 修改文件
1. `src/config/settings.py` - EB-mM 配置已存在，无需修改
2. `src/main.py` - 更新依赖注入，集成 EB-mM 模型

---

## 依赖关系

- **前置**: 
  - 批次一（降级策略框架与质量评估机制）已完成
  - 批次二（抽象模型服务层）已完成
- **可并行**: 可与批次三并行进行
- **可选前置**: 批次五（LoRA 训练，如果训练完成）

---

## 参考文档

- `docs/AAM Agent SD v2.md` - 系统设计规格
- `docs/plan/AAM Phase II.md` - Phase II 总体计划
- `docs/plan/PII-批次一：降级策略框架与质量评估机制实施计划.md` - 批次一实施计划
- `docs/plan/PII-批次二：抽象模型服务层实施计划.md` - 批次二实施计划
- `docs/plan/PII-批次三：LangChain Embedding 模型实施计划.md` - 批次三实施计划
- `docs/AiDevelopmentGuide.md` - 开发规范

---

## 测试报告要求

测试完成后，需要在 `tests/reports/` 目录下创建测试报告：

**文件**: `tests/reports/PII-批次四：EB-mM 模型集成-測試報告.md`

**报告内容结构**:
- 测试概述
- 测试项目
- 测试结果（通过项目、失败项目、待改进项目）
- 结论与建议

---

**最后更新**: 2025-11-12

