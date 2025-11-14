# AAM Phase II: 语义分析与模型集成实施计划

**创建日期**: 2025-11-12  
**版本**: v2.0  
**状态**: 规划中  
**基准文档**: `AAM Agent SD v2.md`  
**前置条件**: Phase I (MVP) 已完成  
**最后更新**: 2025-11-12（v2.0 - 添加抽象模型服务层设计）

---

## 📋 阶段概述

### Phase II 目标

Phase II 的核心目标是**实现真实的语义分析能力**，替换当前的 Mock 实现，使系统能够真正执行"Classify For Labeling"（NER, KE, KT）和个性分析。

### 核心挑战

1. **模型集成复杂性**: 需要集成多个层级的 AI 模型（Eb-MM, LangChain Embedding, LLM）
2. **质量保证**: 需要建立质量评估机制，确保分析结果的质量
3. **成本控制**: 需要平衡成本和质量，优先使用低成本模型
4. **降级策略**: 需要实现智能降级，确保系统高可用性

### 设计原则

1. **降级优先**: 实现多层级降级策略（Eb-MM → LangChain Embedding → LLM）
2. **质量驱动**: 建立质量评估机制，自动评估和降级
3. **成本优化**: 优先使用低成本模型，仅在必要时使用 LLM
4. **渐进式实施**: 分批次实施，每批次可独立验证

---

## 🎯 Phase II 总体目标

### 功能目标

1. ✅ **实现真实的语义分析**
   - 替换 `MockAnalysisModel` 为真实的降级策略模型
   - 实现 NER (命名实体识别)
   - 实现 KE (知识提取)
   - 实现 KT (知识三元组提取)
   - 通过抽象模型服务层支持多种后端（Ollama、vLLM 等）

2. ✅ **实现个性分析**
   - 替换 Mock 个性分析为真实实现
   - 提取用户风格标签
   - 分析用户情感状态

3. ✅ **建立质量评估机制**
   - 定义质量评估标准
   - 实现自动质量评估
   - 实现基于质量的降级策略

4. ✅ **实现降级策略**
   - 优先级 1: Eb-MM (小模型)
   - 优先级 2: LangChain Embedding Model
   - 优先级 3: LLM (大模型)

### 非功能目标

1. **性能目标**
   - EB-mM 响应时间: < 1000ms (通过 Ollama/vLLM)
   - LangChain Embedding 响应时间: < 500ms
   - LLM 响应时间: < 2000ms

2. **质量目标**
   - 实体提取准确率: > 80%
   - 三元组提取准确率: > 75%
   - 个性分析准确率: > 70%

3. **成本目标**
   - EB-mM 使用率: > 70%
   - LLM 使用率: < 10%
   - 本地模型使用率: > 90% (Ollama/vLLM，零 API 成本)

---

## 📦 批次划分

Phase II 分为 **5 个批次**，每个批次都是可独立验证的模块：

### 批次一：降级策略框架与质量评估机制
**目标**: 建立降级策略框架和质量评估机制  
**优先级**: 🔴 最高  
**预计工期**: 1-2 周

### 批次二：抽象模型服务层（统一模型服务）
**目标**: 实现抽象模型服务层，支持多种后端（Ollama、vLLM、OpenAI API 等）  
**优先级**: 🔴 最高  
**预计工期**: 1-2 周  
**核心设计**: Provider Pattern，通过配置切换模型服务，无需修改代码

### 批次三：LangChain Embedding 模型实现
**目标**: 实现 LangChain Embedding 层级的语义分析  
**优先级**: 🟡 中  
**预计工期**: 1-2 周

### 批次四：EB-mM 模型集成（通过统一模型服务）
**目标**: 集成真实的 EB-mM 模型，通过 Ollama/vLLM 等挂载  
**优先级**: 🟡 中  
**预计工期**: 2-3 周  
**基础模型**: DeepSeek-R1 8B  
**训练方式**: LoRA 微调  
**部署方式**: 通过 Ollama 或 vLLM 服务挂载

### 批次五：LoRA 训练管道（可选，提前实施）
**目标**: 实现 LoRA 训练管道，基于 DeepSeek-R1 8B 训练 EB-mM  
**优先级**: 🟢 低（可与批次四并行）  
**预计工期**: 3-4 周

---

## 📝 批次一：降级策略框架与质量评估机制

### 1.1 目标

建立降级策略框架，实现质量评估机制，为后续模型集成奠定基础。

### 1.2 任务清单

#### Task 1.1.1: 创建降级策略模型接口扩展

**文件**: `src/core/interfaces/i_analysis_model.py`

**任务**:
- [ ] 扩展 `IAnalysisModel` 接口，添加质量评估方法
- [ ] 添加模型可用性检查方法
- [ ] 定义质量评估结果模型

**验收标准**:
- 接口定义清晰，支持质量评估
- 包含完整的类型注解
- 通过类型检查（mypy）

#### Task 1.1.2: 实现质量评估机制

**文件**: `src/infrastructure/ai/quality_evaluator.py` (新建)

**任务**:
- [ ] 创建 `QualityEvaluator` 类
- [ ] 实现实体提取质量评估
  - 评估实体数量
  - 评估实体类型多样性
  - 评估实体置信度
- [ ] 实现三元组质量评估
  - 评估三元组数量
  - 评估三元组完整性（subject, predicate, object）
  - 评估三元组合理性
- [ ] 实现综合质量评分（0.0 - 1.0）
- [ ] 实现质量阈值配置

**验收标准**:
- 质量评估算法合理
- 支持可配置的质量阈值
- 包含单元测试（覆盖率 > 80%）

#### Task 1.1.3: 实现降级策略管理器

**文件**: `src/infrastructure/ai/fallback_analysis_model.py` (新建)

**任务**:
- [ ] 创建 `FallbackAnalysisModel` 类
- [ ] 实现模型优先级管理
- [ ] 实现降级逻辑
  - 尝试 Eb-MM → 评估质量 → 不达标则降级
  - 尝试 LangChain Embedding → 评估质量 → 不达标则降级
  - 尝试 LLM → 直接使用（最后保障）
- [ ] 实现异常处理和降级
- [ ] 实现日志记录（记录使用的模型和降级原因）
- [ ] 实现模型可用性检查

**验收标准**:
- 降级逻辑正确
- 异常处理完善
- 日志记录详细
- 包含单元测试和集成测试

#### Task 1.1.4: 配置管理扩展

**文件**: `src/config/settings.py`

**任务**:
- [ ] 扩展 `AISettings` 类
- [ ] 添加 Eb-MM 配置项
  - `eb_mm_enabled: bool`
  - `eb_mm_model_path: str`
  - `eb_mm_lora_path: Optional[str]`
- [ ] 添加 LangChain Embedding 配置项
  - `langchain_embedding_enabled: bool`
  - `embedding_model: str`
- [ ] 添加 LLM 降级配置项
  - `llm_fallback_enabled: bool`
  - `llm_provider: str` (openai, anthropic, etc.)
  - `llm_model_name: str`
- [ ] 添加质量评估配置项
  - `quality_threshold: float` (0.0 - 1.0)
  - `quality_evaluation_enabled: bool`

**验收标准**:
- 所有配置项都有默认值
- 配置项有清晰的描述
- 支持环境变量覆盖

#### Task 1.1.5: 更新依赖注入

**文件**: `src/main.py`

**任务**:
- [ ] 更新 `lifespan` 函数
- [ ] 创建 `FallbackAnalysisModel` 实例
- [ ] 配置各层级模型（初始为 None，后续批次填充）
- [ ] 更新 `MemoryServiceImpl` 初始化

**验收标准**:
- 依赖注入正确
- 支持模型动态加载
- 异常处理完善

#### Task 1.1.6: 单元测试

**文件**: `tests/unit/test_fallback_analysis_model.py` (新建)

**任务**:
- [ ] 测试降级逻辑
- [ ] 测试质量评估
- [ ] 测试异常处理
- [ ] 测试日志记录

**验收标准**:
- 测试覆盖率 > 80%
- 所有边界情况都有测试

### 1.3 验收标准

- ✅ 降级策略框架完整实现
- ✅ 质量评估机制正常工作
- ✅ 配置管理支持所有模型层级
- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试通过

### 1.4 依赖关系

- **前置**: Phase I 已完成
- **后续**: 批次二、三、四、五依赖此批次

---

## 📝 批次二：抽象模型服务层（统一模型服务）

### 2.1 目标

实现抽象模型服务层，支持多种模型服务后端（Ollama、vLLM、OpenAI API 等），通过配置切换，无需修改代码。这是整个 Phase II 的基础架构。

### 2.2 设计理念

**Provider Pattern（提供者模式）**：
- 抽象模型服务接口（`IModelProvider`）
- 多种后端实现（Ollama、vLLM、OpenAI 等）
- 统一模型服务（`UnifiedModelService`）
- Provider 工厂（`ModelProviderFactory`）

### 2.3 任务清单

#### Task 2.1.1: 创建抽象模型服务接口

**文件**: `src/core/interfaces/i_model_provider.py` (新建)

**任务**:
- [ ] 创建 `ModelProviderType` 枚举（ollama, vllm, openai, anthropic, custom）
- [ ] 创建 `IModelProvider` 抽象接口
  - `generate()`: 生成文本
  - `check_available()`: 检查服务可用性
  - `provider_type`: 返回提供商类型
- [ ] 定义接口文档和类型注解

**验收标准**:
- 接口定义清晰，支持多种 Provider
- 包含完整的类型注解
- 通过类型检查（mypy）

#### Task 2.1.2: 实现 Ollama Provider

**文件**: `src/infrastructure/ai/providers/ollama_provider.py` (新建)

**任务**:
- [ ] 创建 `OllamaProvider` 类
- [ ] 实现 `IModelProvider` 接口
- [ ] 使用 LangChain Ollama 集成
- [ ] 实现服务可用性检查
- [ ] 实现错误处理和重试机制
- [ ] 重构现有的 `OllamaAnalysisModel`（可选，或保留作为业务层）

**验收标准**:
- Provider 实现正确
- 错误处理完善
- 包含单元测试

#### Task 2.1.3: 实现 vLLM Provider

**文件**: `src/infrastructure/ai/providers/vllm_provider.py` (新建)

**任务**:
- [ ] 创建 `VLLMProvider` 类
- [ ] 实现 `IModelProvider` 接口
- [ ] 实现 OpenAI 兼容 API 调用
- [ ] 实现服务可用性检查
- [ ] 实现错误处理和重试机制

**验收标准**:
- Provider 实现正确
- 支持 OpenAI 兼容 API
- 错误处理完善

#### Task 2.1.4: 实现统一模型服务

**文件**: `src/infrastructure/ai/unified_model_service.py` (新建)

**任务**:
- [ ] 创建 `UnifiedModelService` 类
- [ ] 实现 `IAnalysisModel` 接口
- [ ] 使用 Provider 进行模型调用
- [ ] 实现 NER, KE, KT 提取（使用统一的 Prompt）
- [ ] 实现个性分析
- [ ] 实现错误处理和降级

**验收标准**:
- 统一服务正常工作
- 支持所有业务功能
- 错误处理完善

#### Task 2.1.5: 实现 Provider 工厂

**文件**: `src/infrastructure/ai/providers/provider_factory.py` (新建)

**任务**:
- [ ] 创建 `ModelProviderFactory` 类
- [ ] 实现 `create_provider()` 静态方法
- [ ] 根据配置创建对应的 Provider
- [ ] 实现配置验证

**验收标准**:
- 工厂模式正确实现
- 支持所有 Provider 类型
- 配置验证完善

#### Task 2.1.6: 配置管理扩展

**文件**: `src/config/settings.py`

**任务**:
- [ ] 创建 `ModelServiceSettings` 类
- [ ] 添加通用配置项
  - `provider_type: ModelProviderType` (ollama, vllm, openai 等)
  - `model_name: str`
  - `api_base_url: str`
  - `api_key: Optional[str]`
  - `timeout: int`
- [ ] 添加 Provider 特定配置项
  - Ollama: `ollama_model_name`, `ollama_base_url`
  - vLLM: `vllm_api_base_url`
  - OpenAI: `openai_api_base_url`, `openai_api_key`
- [ ] 更新 `Settings` 类，包含 `ModelServiceSettings`

**验收标准**:
- 所有配置项都有默认值
- 配置项有清晰的描述
- 支持环境变量覆盖

#### Task 2.1.7: 更新依赖注入

**文件**: `src/main.py`

**任务**:
- [ ] 在 `lifespan` 函数中创建 Provider
- [ ] 使用 `ModelProviderFactory` 创建 Provider
- [ ] 创建 `UnifiedModelService` 实例
- [ ] 更新 `MemoryServiceImpl` 初始化（暂时使用 UnifiedModelService）

**验收标准**:
- 依赖注入正确
- 支持配置切换 Provider
- 异常处理完善

#### Task 2.1.8: 单元测试和集成测试

**文件**: 
- `tests/unit/test_model_provider.py` (新建)
- `tests/unit/test_unified_model_service.py` (新建)
- `tests/integration/test_provider_switching.py` (新建)

**任务**:
- [ ] 测试 Provider 接口
- [ ] 测试 Ollama Provider
- [ ] 测试 vLLM Provider
- [ ] 测试统一模型服务
- [ ] 测试 Provider 工厂
- [ ] 测试配置切换

**验收标准**:
- 单元测试覆盖率 > 80%
- 集成测试通过
- 包含 Provider 切换测试

### 2.4 验收标准

- ✅ 抽象模型服务接口完整实现
- ✅ Ollama Provider 正常工作
- ✅ vLLM Provider 正常工作（可选，可延后）
- ✅ 统一模型服务正常工作
- ✅ Provider 工厂正常工作
- ✅ 配置管理支持所有 Provider
- ✅ 单元测试覆盖率 > 80%
- ✅ 集成测试通过

### 2.5 依赖关系

- **前置**: 批次一（降级策略框架）
- **后续**: 批次三、四依赖此批次

---

## 📝 批次三：LangChain Embedding 模型实现

### 3.1 目标

实现 LangChain Embedding 层级的语义分析，作为 EB-mM 的降级选项和 LLM 的前置选项。

### 3.2 任务清单

#### Task 3.1.1: 安装 LangChain 依赖

**文件**: `requirements.txt`

**任务**:
- [ ] 添加 `langchain>=0.1.0`
- [ ] 添加 `langchain-openai>=0.0.5` (如果使用 OpenAI)
- [ ] 添加 `langchain-anthropic>=0.1.0` (如果使用 Anthropic)
- [ ] 添加 `langchain-core>=0.1.0`

**验收标准**:
- 依赖版本兼容
- 无版本冲突

#### Task 3.1.2: 实现 LangChain Embedding 模型

**文件**: `src/infrastructure/ai/langchain_embedding_model.py` (新建)

**任务**:
- [ ] 创建 `LangChainEmbeddingModel` 类
- [ ] 实现 `IAnalysisModel` 接口
- [ ] 使用 LCEL (LangChain Expression Language) 构建提取链
- [ ] 实现 NER 提取 Prompt
- [ ] 实现 KE 提取 Prompt
- [ ] 实现 KT 提取 Prompt
- [ ] 使用 `JsonOutputParser` 解析输出
- [ ] 实现错误处理和重试机制

**Prompt 设计示例**:
```python
NER_PROMPT = """
请从以下文本中提取命名实体（人名、地名、组织名、产品名等）。

文本: {text}

请以 JSON 格式返回，格式：
{{
    "entities": ["实体1", "实体2", ...]
}}
"""

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
- 使用 LCEL 构建链（符合 SD 文档要求）
- Prompt 设计合理
- 输出格式正确
- 错误处理完善

#### Task 3.1.3: 实现个性分析

**文件**: `src/infrastructure/ai/langchain_embedding_model.py`

**任务**:
- [ ] 实现个性分析 Prompt
- [ ] 提取风格标签（formal, casual, technical, etc.）
- [ ] 分析情感状态（positive, negative, neutral）
- [ ] 提取语言模式

**验收标准**:
- 个性分析结果合理
- 输出格式符合 `PersonalityInsights` 模型

#### Task 3.1.4: 集成到降级策略

**文件**: `src/main.py`

**任务**:
- [ ] 创建 `LangChainEmbeddingModel` 实例
- [ ] 配置到 `FallbackAnalysisModel`
- [ ] 测试降级流程

**验收标准**:
- 集成正确
- 降级流程正常

#### Task 3.1.5: 单元测试和集成测试

**文件**: 
- `tests/unit/test_langchain_embedding_model.py` (新建)
- `tests/integration/test_semantic_analysis.py` (新建)

**任务**:
- [ ] 测试 NER 提取
- [ ] 测试 KE 提取
- [ ] 测试 KT 提取
- [ ] 测试个性分析
- [ ] 测试降级流程
- [ ] 测试错误处理

**验收标准**:
- 单元测试覆盖率 > 80%
- 集成测试通过
- 包含真实文本测试用例

### 3.3 验收标准

- ✅ LangChain Embedding 模型正常工作
- ✅ NER, KE, KT 提取功能正常
- ✅ 个性分析功能正常
- ✅ 集成到降级策略成功
- ✅ 测试覆盖率 > 80%

### 3.4 依赖关系

- **前置**: 批次一（降级策略框架）、批次二（抽象模型服务层）
- **后续**: 批次四、五可并行进行

---

## 📝 批次四：EB-mM 模型集成（通过统一模型服务）

### 4.1 目标

集成真实的 EB-mM (Enterprise Bot mini-Model) 模型，通过统一模型服务调用。EB-mM 基于 DeepSeek-R1 8B 进行 LoRA 微调，可通过 Ollama 或 vLLM 服务挂载。

### 4.2 设计说明

**模型架构**:
- **基础模型**: DeepSeek-R1 8B (deepseek-r1:8b)
- **训练方式**: LoRA 微调
- **部署方式**: 通过 Ollama 或 vLLM 服务挂载
- **模型名称**: EB-mM (Enterprise Bot mini-Model)

**服务架构**:
- EB-mM 通过统一模型服务（`UnifiedModelService`）调用
- 支持通过配置切换挂载方式（Ollama / vLLM）
- 无需修改代码，只需更新配置

### 4.3 任务清单

#### Task 4.1.1: 准备 EB-mM 模型（LoRA 训练）

**文件**: `src/training/` (新建训练目录)

**任务**:
- [ ] 从 ChromaDB 导出训练数据
- [ ] 格式化训练数据（Instruction JSONL）
- [ ] 配置 LoRA 训练参数
- [ ] 使用 PEFT 进行 LoRA 微调
- [ ] 验证训练后的模型性能
- [ ] 保存 LoRA 适配器

**验收标准**:
- 训练数据质量合格
- LoRA 适配器训练完成
- 模型性能达到目标（NER > 80%, KT > 75%）

**注意**: 如果训练未完成，可先使用原始 DeepSeek-R1 8B 模型进行集成测试

#### Task 4.1.2: 配置 EB-mM 模型服务

**文件**: `.env`, `src/config/settings.py`

**任务**:
- [ ] 配置 Ollama 或 vLLM 服务
- [ ] 挂载训练好的 EB-mM 模型（或使用原始 DeepSeek-R1 8B）
- [ ] 更新 `ModelServiceSettings` 配置
- [ ] 设置 `MODEL_NAME=eb-mm` 或 `MODEL_NAME=deepseek-r1:8b`

**验收标准**:
- 模型服务配置正确
- 模型可以正常调用
- 配置支持环境变量覆盖

#### Task 4.1.3: 实现 EB-mM 业务逻辑层

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py` (新建)

**任务**:
- [ ] 创建 `EbMMAnalysisModel` 类
- [ ] 实现 `IAnalysisModel` 接口
- [ ] 使用 `UnifiedModelService` 进行模型调用
- [ ] 实现 NER 提取 Prompt 和逻辑
- [ ] 实现 KE 提取 Prompt 和逻辑
- [ ] 实现 KT 提取 Prompt 和逻辑
- [ ] 实现个性分析 Prompt 和逻辑

**验收标准**:
- 业务逻辑层正确实现
- 所有功能正常工作
- Prompt 设计优化

#### Task 4.1.4: 性能优化

**文件**: `src/infrastructure/ai/eb_mm_analysis_model.py`

**任务**:
- [ ] 实现批处理（batch processing）
- [ ] 实现缓存机制
- [ ] 优化 Prompt 长度
- [ ] 实现请求合并

**验收标准**:
- 响应时间 < 1000ms (P95)（通过 Ollama/vLLM）
- 批处理效率提升 > 30%

#### Task 4.1.5: 集成到降级策略

**文件**: `src/main.py`

**任务**:
- [ ] 创建 `EbMMAnalysisModel` 实例
- [ ] 配置到 `FallbackAnalysisModel`（作为优先级 1）
- [ ] 测试完整降级流程

**验收标准**:
- 集成正确
- 降级流程正常
- EB-mM 使用率 > 70%

#### Task 4.1.6: 单元测试和集成测试

**文件**: 
- `tests/unit/test_eb_mm_analysis_model.py` (新建)
- `tests/integration/test_eb_mm_integration.py` (新建)

**任务**:
- [ ] 测试模型服务调用
- [ ] 测试 NER 提取
- [ ] 测试 KE 提取
- [ ] 测试 KT 提取
- [ ] 测试个性分析
- [ ] 测试性能
- [ ] 测试降级流程
- [ ] 测试 Provider 切换（Ollama ↔ vLLM）

**验收标准**:
- 单元测试覆盖率 > 80%
- 集成测试通过
- 性能测试通过
- Provider 切换测试通过

### 4.4 验收标准

- ✅ EB-mM 模型正常工作（通过统一模型服务）
- ✅ NER, KE, KT 提取功能正常
- ✅ 个性分析功能正常
- ✅ 支持 Ollama 和 vLLM 挂载
- ✅ 通过配置切换 Provider
- ✅ 集成到降级策略成功
- ✅ 测试覆盖率 > 80%

### 4.5 依赖关系

- **前置**: 批次一（降级策略框架）、批次二（抽象模型服务层）
- **可并行**: 可与批次三并行进行
- **可选前置**: 批次五（LoRA 训练，如果训练完成）

---

## 📝 批次五：LoRA 训练管道（可选，提前实施）

### 5.1 目标

实现 LoRA 训练管道，基于 DeepSeek-R1 8B 训练 EB-mM (Enterprise Bot mini-Model) LoRA 适配器。

### 5.2 任务清单

#### Task 5.1.1: 数据导出器

**文件**: `src/training/data_exporter.py` (新建)

**任务**:
- [ ] 连接 ChromaDB 和 PostgreSQL
- [ ] 导出过去 N 天的对话数据
- [ ] 数据清洗和过滤（保留高质量数据）
- [ ] 格式化为 Instruction JSONL 格式

**验收标准**:
- 数据导出正确
- 数据质量合格
- 格式符合训练要求

#### Task 5.1.2: LoRA 训练脚本

**文件**: `src/training/train_lora.py` (新建)

**任务**:
- [ ] 使用 Hugging Face Transformers 加载 DeepSeek-R1 8B
- [ ] 配置 PEFT LoRA 参数（rank, alpha, target_modules）
- [ ] 实现训练循环
- [ ] 实现模型验证和评估
- [ ] 保存 LoRA 适配器

**验收标准**:
- 训练脚本可运行
- LoRA 适配器训练完成
- 模型性能达到目标

#### Task 5.1.3: 模型版本管理

**文件**: `src/training/model_repository.py` (新建)

**任务**:
- [ ] 实现模型版本化
- [ ] 实现模型存储（本地或 S3）
- [ ] 实现模型加载接口

**验收标准**:
- 版本管理正确
- 模型存储和加载正常

### 5.3 验收标准

- ✅ 训练管道完整实现
- ✅ LoRA 适配器训练完成
- ✅ 模型性能达到目标
- ✅ 版本管理正常

### 5.4 依赖关系

- **前置**: Phase I 已完成（需要 ChromaDB 中有数据）
- **可并行**: 可与批次二、三、四并行进行

---

## 🔄 批次执行顺序建议

### 推荐执行顺序

```
批次一 (降级策略框架)
    ↓
批次二 (抽象模型服务层) ──┐
    ↓                      │
批次三 (LangChain Embedding) ──┤ 可并行
    ↓                            │
批次四 (EB-mM 集成) ────────────┤
    ↓                            │
批次五 (LoRA 训练) ─────────────┘ (可选，可提前)
```

### 执行策略

1. **批次一必须首先完成**（为后续批次提供框架）
2. **批次二必须其次完成**（为模型集成提供基础架构）
3. **批次三和批次四可以并行**（互不依赖）
4. **批次五可以提前进行**（不阻塞其他批次，但需要数据积累）
5. **批次四可以在模型训练完成后进行**（如果批次五完成，使用训练好的模型；否则使用原始 DeepSeek-R1 8B）

---

## 📊 质量保证

### 测试策略

每个批次都需要：

1. **单元测试**
   - 覆盖率 > 80%
   - 包含边界情况测试
   - 包含错误处理测试

2. **集成测试**
   - 测试与现有系统的集成
   - 测试降级流程
   - 测试端到端流程

3. **性能测试**
   - 响应时间测试
   - 并发测试
   - 负载测试

4. **质量测试**
   - 准确率测试
   - 召回率测试
   - 质量评估测试

### 验收标准

每个批次完成后需要：

- ✅ 所有任务完成
- ✅ 单元测试通过（覆盖率 > 80%）
- ✅ 集成测试通过
- ✅ 代码审查通过
- ✅ 文档更新完成
- ✅ 测试报告生成

---

## 📈 监控与指标

### 关键指标

1. **性能指标**
   - 各层级模型响应时间
   - 各层级模型使用率
   - 降级频率

2. **质量指标**
   - 实体提取准确率
   - 三元组提取准确率
   - 个性分析准确率
   - 质量评估分数分布

3. **成本指标**
   - 各层级模型调用成本
   - 总成本趋势
   - 成本占比

### 监控实现

- 使用结构化日志记录所有模型调用
- 使用 Prometheus 指标（后续实现）
- 定期生成质量报告

---

## 🚨 风险与应对

### 风险识别

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| Eb-MM 模型训练延迟 | 高 | 中 | 批次四可延后，批次二、三先完成 |
| LangChain API 变更 | 中 | 低 | 使用稳定版本，及时更新 |
| LLM 成本超预算 | 高 | 中 | 实现严格的成本控制机制 |
| 质量评估不准确 | 中 | 中 | 持续优化评估算法，人工审核 |
| 性能不达标 | 中 | 中 | 性能优化，必要时使用缓存 |

### 应对策略

1. **渐进式实施**: 每个批次独立验证，降低风险
2. **降级保障**: 多层级降级确保系统可用性
3. **成本控制**: 严格的成本上限和限流机制
4. **质量监控**: 持续监控质量指标，及时调整

---

## 📚 参考文档

### 内部文档

- `AAM Agent SD v1.md` - 系统设计规格
- `AAM_SD_实施进度报告.md` - Phase I 进度报告
- `AAM 服務第一階段 MVP 實施計劃.md` - Phase I 实施计划
- `语义分析降级策略设计.md` - 降级策略设计文档

### 外部文档

- LangChain Documentation: https://python.langchain.com/
- Transformers Documentation: https://huggingface.co/docs/transformers/
- PEFT Documentation: https://huggingface.co/docs/peft/

---

## 📝 附录

### A. 质量评估算法详细设计

```python
def evaluate_quality(knowledge: KnowledgeAsset) -> float:
    """
    质量评估算法
    
    评估维度：
    1. 实体提取质量 (0-0.5)
       - 实体数量: 0-0.2
       - 实体类型多样性: 0-0.2
       - 实体置信度: 0-0.1
    
    2. 三元组质量 (0-0.5)
       - 三元组数量: 0-0.2
       - 三元组完整性: 0-0.2
       - 三元组置信度: 0-0.1
    
    总分: 0.0 - 1.0
    """
    score = 0.0
    
    # 实体提取质量
    if knowledge.entities:
        # 数量评分
        entity_count_score = min(0.2, len(knowledge.entities) * 0.05)
        score += entity_count_score
        
        # 类型多样性评分（需要实体类型信息）
        # TODO: 实现类型多样性评估
    
    # 三元组质量
    try:
        triples = json.loads(knowledge.triples_json)
        if triples:
            # 数量评分
            triple_count_score = min(0.2, len(triples) * 0.05)
            score += triple_count_score
            
            # 完整性评分
            complete_triples = [
                t for t in triples 
                if t.get("subject") and t.get("predicate") and t.get("object")
            ]
            completeness_score = (len(complete_triples) / len(triples)) * 0.2
            score += completeness_score
    except:
        pass
    
    return min(1.0, score)
```

### B. 降级策略流程图

```
开始提取知识
    ↓
EB-mM 可用?
    ├─ 是 → 调用 EB-mM (通过统一模型服务)
    │        ↓
    │        ├─ Provider: Ollama/vLLM
    │        └─ 模型: EB-mM (DeepSeek-R1 8B + LoRA)
    │        ↓
    │    质量评估
    │        ├─ 质量 >= 阈值 → 返回结果 ✅
    │        └─ 质量 < 阈值 → 降级到 LangChain Embedding
    │
    └─ 否 → 降级到 LangChain Embedding
                ↓
            LangChain Embedding 可用?
                ├─ 是 → 调用 LangChain Embedding
                │        ↓
                │    质量评估
                │        ├─ 质量 >= 阈值 → 返回结果 ✅
                │        └─ 质量 < 阈值 → 降级到 LLM
                │
                └─ 否 → 降级到 LLM
                            ↓
                        LLM 可用? (通过统一模型服务)
                            ├─ 是 → 调用 LLM (原始 DeepSeek-R1 8B 或其他模型)
                            │        ↓
                            │        ├─ Provider: Ollama/vLLM/OpenAI
                            │        └─ 返回结果 ✅
                            └─ 否 → 返回空结果 ⚠️
```

### B.1 抽象模型服务层架构图

```
┌─────────────────────────────────────────┐
│      IAnalysisModel (业务接口)          │
│  (extract_knowledge, analyze_personality)│
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   UnifiedModelService (统一模型服务)      │
│   - 路由到具体的 Provider                │
│   - 统一错误处理                        │
│   - 统一日志记录                        │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
┌─────▼─────┐ ┌──▼──────┐ ┌──▼────────┐
│ Ollama    │ │ vLLM    │ │ OpenAI    │
│ Provider  │ │ Provider│ │ Provider  │
└───────────┘ └─────────┘ └───────────┘
      │           │           │
      └───────────┴───────────┘
                  │
        ┌─────────▼─────────┐
        │  ModelProviderFactory │
        │  (根据配置创建 Provider) │
        └─────────────────────┘
```

### C. 配置示例

```bash
# .env 文件示例

# ============================================
# 统一模型服务配置（抽象层）
# ============================================
# Provider 类型: ollama, vllm, openai, anthropic, custom
MODEL_PROVIDER_TYPE=ollama

# 模型名称（EB-mM 或原始模型）
MODEL_NAME=eb-mm
# 或使用原始模型: MODEL_NAME=deepseek-r1:8b

# API 基础 URL（通用）
MODEL_API_BASE_URL=http://localhost:11434

# API Key（如果需要）
MODEL_API_KEY=

# 超时时间
MODEL_TIMEOUT=120

# ============================================
# Ollama 特定配置
# ============================================
OLLAMA_MODEL_NAME=eb-mm
# 或: OLLAMA_MODEL_NAME=deepseek-r1:8b

# ============================================
# vLLM 特定配置（可选）
# ============================================
VLLM_API_BASE_URL=http://localhost:8000/v1

# ============================================
# EB-mM 配置（业务层）
# ============================================
EB_MM_ENABLED=true
EB_MM_BASE_MODEL=deepseek-r1:8b
EB_MM_LORA_ADAPTER_PATH=/app/models/eb-mm-lora-v1

# ============================================
# LangChain Embedding 配置
# ============================================
AI_LANGCHAIN_EMBEDDING_ENABLED=true
AI_EMBEDDING_MODEL=text-embedding-ada-002

# ============================================
# 质量评估配置
# ============================================
AI_QUALITY_THRESHOLD=0.7
AI_QUALITY_EVALUATION_ENABLED=true
```

---

## ✅ 检查清单

### 批次一检查清单

- [ ] 降级策略框架实现
- [ ] 质量评估机制实现
- [ ] 配置管理扩展
- [ ] 依赖注入更新
- [ ] 单元测试完成（覆盖率 > 80%）
- [ ] 集成测试通过
- [ ] 文档更新完成

### 批次二检查清单

- [ ] LangChain 依赖安装
- [ ] LangChain Embedding 模型实现
- [ ] NER, KE, KT 提取功能
- [ ] 个性分析功能
- [ ] 集成到降级策略
- [ ] 单元测试完成（覆盖率 > 80%）
- [ ] 集成测试通过
- [ ] 文档更新完成

### 批次二检查清单

- [ ] 抽象模型服务接口实现
- [ ] Ollama Provider 实现
- [ ] vLLM Provider 实现（可选）
- [ ] 统一模型服务实现
- [ ] Provider 工厂实现
- [ ] 配置管理扩展
- [ ] 依赖注入更新
- [ ] 单元测试完成（覆盖率 > 80%）
- [ ] 集成测试通过
- [ ] 文档更新完成

### 批次三检查清单

- [ ] LangChain 依赖安装
- [ ] LangChain Embedding 模型实现
- [ ] NER, KE, KT 提取功能
- [ ] 个性分析功能
- [ ] 集成到降级策略
- [ ] 单元测试完成（覆盖率 > 80%）
- [ ] 集成测试通过
- [ ] 文档更新完成

### 批次四检查清单

- [ ] EB-mM 模型服务配置
- [ ] EB-mM 业务逻辑层实现
- [ ] NER 提取实现
- [ ] KE 提取实现
- [ ] KT 提取实现
- [ ] 个性分析实现
- [ ] 性能优化
- [ ] 集成到降级策略
- [ ] Provider 切换测试（Ollama ↔ vLLM）
- [ ] 单元测试完成（覆盖率 > 80%）
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 文档更新完成

### 批次五检查清单（可选）

- [ ] 数据导出器实现
- [ ] LoRA 训练脚本实现
- [ ] 模型版本管理实现
- [ ] 训练数据准备完成
- [ ] LoRA 适配器训练完成
- [ ] 模型性能验证通过
- [ ] 文档更新完成

---

**最后更新**: 2025-11-12  
**下次审查**: 批次一开始前

