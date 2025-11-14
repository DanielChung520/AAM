# 批次二：抽象模型服务层（统一模型服务）实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 规划中  
**基准文档**: `AAM Phase II.md`  
**前置条件**: 批次一（降级策略框架与质量评估机制）已完成  
**最后更新**: 2025-11-12

---

## 批次概述

### 目标

实现抽象模型服务层，支持多种模型服务后端（Ollama、vLLM、OpenAI API 等），通过配置切换，无需修改代码。这是整个 Phase II 的基础架构。

### 核心任务

1. **创建抽象模型服务接口** - 定义 `IModelProvider` 接口
2. **实现 Ollama Provider** - 封装 Ollama 服务调用
3. **实现 vLLM Provider** - 封装 vLLM 服务调用（可选）
4. **实现统一模型服务** - 创建 `UnifiedModelService` 类
5. **实现 Provider 工厂** - 创建 `ModelProviderFactory` 类
6. **配置管理扩展** - 扩展 `Settings` 类支持模型服务配置
7. **更新依赖注入** - 更新 `main.py` 中的依赖注入
8. **单元测试和集成测试** - 创建完整的测试套件

### 设计理念

**Provider Pattern（提供者模式）**：
- 抽象模型服务接口（`IModelProvider`）
- 多种后端实现（Ollama、vLLM、OpenAI 等）
- 统一模型服务（`UnifiedModelService`）
- Provider 工厂（`ModelProviderFactory`）

---

## 任务清单

### Task 2.1: 创建抽象模型服务接口

**文件**: `src/core/interfaces/i_model_provider.py` (新建)

**任务**:
- [ ] 创建 `ModelProviderType` 枚举（ollama, vllm, openai, anthropic, custom）
- [ ] 创建 `IModelProvider` 抽象接口
  - `generate(prompt: str, **kwargs) -> str`: 生成文本
  - `check_available() -> bool`: 检查服务可用性
  - `provider_type: ModelProviderType`: 返回提供商类型
- [ ] 定义接口文档和类型注解

**验收标准**:
- [ ] 接口定义清晰，支持多种 Provider
- [ ] 包含完整的类型注解
- [ ] 通过类型检查（mypy）

---

### Task 2.2: 实现 Ollama Provider

**文件**: `src/infrastructure/ai/providers/ollama_provider.py` (新建)

**任务**:
- [ ] 创建 `OllamaProvider` 类
- [ ] 实现 `IModelProvider` 接口
- [ ] 使用 LangChain Ollama 集成（参考现有的 `OllamaAnalysisModel`）
- [ ] 实现服务可用性检查（参考现有的 `_check_ollama_available` 方法）
- [ ] 实现错误处理和重试机制
- [ ] 实现超时控制

**验收标准**:
- [ ] Provider 实现正确
- [ ] 错误处理完善
- [ ] 包含单元测试
- [ ] 服务可用性检查准确

**参考代码**:
- 现有的 `src/infrastructure/ai/ollama_analysis_model.py` 可以作为参考

---

### Task 2.3: 实现 vLLM Provider（可选）

**文件**: `src/infrastructure/ai/providers/vllm_provider.py` (新建)

**任务**:
- [ ] 创建 `VLLMProvider` 类
- [ ] 实现 `IModelProvider` 接口
- [ ] 实现 OpenAI 兼容 API 调用
- [ ] 实现服务可用性检查
- [ ] 实现错误处理和重试机制
- [ ] 实现超时控制

**验收标准**:
- [ ] Provider 实现正确
- [ ] 支持 OpenAI 兼容 API
- [ ] 错误处理完善
- [ ] 包含单元测试（可选，如果实现）

**注意**: 此任务为可选，如果时间有限可以延后实现。

---

### Task 2.4: 实现统一模型服务

**文件**: `src/infrastructure/ai/unified_model_service.py` (新建)

**任务**:
- [ ] 创建 `UnifiedModelService` 类
- [ ] 实现 `IAnalysisModel` 接口
- [ ] 使用 Provider 进行模型调用
- [ ] 实现 NER, KE, KT 提取（使用统一的 Prompt）
- [ ] 实现个性分析
- [ ] 实现错误处理和降级
- [ ] 实现日志记录

**验收标准**:
- [ ] 统一服务正常工作
- [ ] 支持所有业务功能（NER, KE, KT, 个性分析）
- [ ] 错误处理完善
- [ ] 日志记录详细

**Prompt 设计**:
- 参考现有的 `OllamaAnalysisModel` 中的 Prompt 设计
- 确保 Prompt 格式统一，便于后续优化

---

### Task 2.5: 实现 Provider 工厂

**文件**: `src/infrastructure/ai/providers/provider_factory.py` (新建)

**任务**:
- [ ] 创建 `ModelProviderFactory` 类
- [ ] 实现 `create_provider()` 静态方法
- [ ] 根据配置创建对应的 Provider
- [ ] 实现配置验证
- [ ] 实现错误处理（配置无效时抛出异常）

**验收标准**:
- [ ] 工厂模式正确实现
- [ ] 支持所有 Provider 类型（至少 Ollama）
- [ ] 配置验证完善
- [ ] 错误处理完善

---

### Task 2.6: 配置管理扩展

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
  - Ollama: `ollama_model_name`, `ollama_base_url` (已存在，可复用)
  - vLLM: `vllm_api_base_url` (可选)
  - OpenAI: `openai_api_base_url`, `openai_api_key` (可选)
- [ ] 更新 `Settings` 类，包含 `ModelServiceSettings`
- [ ] 确保配置项支持环境变量覆盖

**验收标准**:
- [ ] 所有配置项都有默认值
- [ ] 配置项有清晰的描述
- [ ] 支持环境变量覆盖
- [ ] 配置验证正确

**注意**: 现有的 `AISettings` 中已有部分 Ollama 配置，需要整合或复用。

---

### Task 2.7: 更新依赖注入

**文件**: `src/main.py`

**任务**:
- [ ] 在 `lifespan` 函数中创建 Provider
- [ ] 使用 `ModelProviderFactory` 创建 Provider
- [ ] 创建 `UnifiedModelService` 实例
- [ ] 更新 `FallbackAnalysisModel` 初始化（暂时使用 UnifiedModelService 作为 LLM 层级）
- [ ] 保持向后兼容性（如果 Provider 创建失败，使用 MockAnalysisModel）

**验收标准**:
- [ ] 依赖注入正确
- [ ] 支持配置切换 Provider
- [ ] 异常处理完善
- [ ] 应用可以正常启动

**参考代码**:
- 现有的 `lifespan` 函数中已有 `FallbackAnalysisModel` 的初始化逻辑

---

### Task 2.8: 单元测试和集成测试

**文件**: 
- `tests/unit/test_model_provider.py` (新建)
- `tests/unit/test_unified_model_service.py` (新建)
- `tests/unit/test_provider_factory.py` (新建)
- `tests/integration/test_provider_switching.py` (新建)

**任务**:
- [ ] 测试 Provider 接口
- [ ] 测试 Ollama Provider
  - [ ] 测试服务可用性检查
  - [ ] 测试文本生成
  - [ ] 测试错误处理
- [ ] 测试 vLLM Provider（如果实现）
- [ ] 测试统一模型服务
  - [ ] 测试 NER 提取
  - [ ] 测试 KE 提取
  - [ ] 测试 KT 提取
  - [ ] 测试个性分析
- [ ] 测试 Provider 工厂
  - [ ] 测试创建 Ollama Provider
  - [ ] 测试创建 vLLM Provider（如果实现）
  - [ ] 测试配置验证
- [ ] 测试配置切换（集成测试）
  - [ ] 测试通过配置切换 Provider
  - [ ] 测试 Provider 切换不影响业务逻辑

**验收标准**:
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 包含 Provider 切换测试
- [ ] 所有边界情况都有测试

---

## 验收标准总结

- [ ] 抽象模型服务接口完整实现
- [ ] Ollama Provider 正常工作
- [ ] vLLM Provider 正常工作（可选）
- [ ] 统一模型服务正常工作
- [ ] Provider 工厂正常工作
- [ ] 配置管理支持所有 Provider
- [ ] 依赖注入正确，应用可正常启动
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过
- [ ] 代码符合 AiDevelopmentGuide.md 规范
- [ ] 所有文件包含标准头部注释
- [ ] 通过 linter 检查

---

## 创建/修改的文件

### 新建文件
1. `src/core/interfaces/i_model_provider.py` - 抽象模型服务接口
2. `src/infrastructure/ai/providers/__init__.py` - Provider 模块初始化
3. `src/infrastructure/ai/providers/ollama_provider.py` - Ollama Provider
4. `src/infrastructure/ai/providers/vllm_provider.py` - vLLM Provider（可选）
5. `src/infrastructure/ai/providers/provider_factory.py` - Provider 工厂
6. `src/infrastructure/ai/unified_model_service.py` - 统一模型服务
7. `tests/unit/test_model_provider.py` - Provider 接口测试
8. `tests/unit/test_unified_model_service.py` - 统一模型服务测试
9. `tests/unit/test_provider_factory.py` - Provider 工厂测试
10. `tests/integration/test_provider_switching.py` - Provider 切换集成测试

### 修改文件
1. `src/config/settings.py` - 扩展配置管理
2. `src/main.py` - 更新依赖注入
3. `src/core/interfaces/__init__.py` - 更新导出（如果需要）

---

## 依赖关系

- **前置**: 批次一（降级策略框架与质量评估机制）已完成
- **后续**: 批次三、四依赖此批次

---

## 参考文档

- `docs/AAM Agent SD v2.md` - 系统设计规格
- `docs/plan/AAM Phase II.md` - Phase II 总体计划
- `docs/plan/PII-批次一：降级策略框架与质量评估机制实施计划.md` - 批次一实施计划
- `docs/AiDevelopmentGuide.md` - 开发规范

---

## 测试报告要求

测试完成后，需要在 `tests/reports/` 目录下创建测试报告：

**文件**: `tests/reports/PII-批次二：抽象模型服务层-測試報告.md`

**报告内容结构**:
- 测试概述
- 测试项目
- 测试结果（通过项目、失败项目、待改进项目）
- 结论与建议

---

**最后更新**: 2025-11-12

