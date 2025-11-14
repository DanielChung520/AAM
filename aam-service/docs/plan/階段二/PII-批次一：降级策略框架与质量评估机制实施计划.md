# 批次一：降级策略框架与质量评估机制实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 已完成  
**基准文档**: `AAM Phase II.md`  
**前置条件**: Phase I (MVP) 已完成  
**最后更新**: 2025-11-12

---

## 📋 批次概述

### 目标

建立降级策略框架，实现质量评估机制，为后续模型集成奠定基础。

### 核心任务

1. **扩展 IAnalysisModel 接口** - 添加质量评估方法和可用性检查
2. **实现质量评估机制** - 创建 QualityEvaluator 类
3. **实现降级策略管理器** - 创建 FallbackAnalysisModel 类
4. **配置管理扩展** - 扩展 AISettings 类
5. **更新依赖注入** - 更新 main.py 中的 lifespan 函数
6. **单元测试和集成测试** - 创建完整的测试套件

---

## 📝 任务清单

### Task 1.1: 扩展 IAnalysisModel 接口

**文件**: `src/core/interfaces/i_analysis_model.py`

**任务**:
- [x] 扩展 `IAnalysisModel` 接口，添加质量评估方法
- [x] 添加模型可用性检查方法
- [x] 定义质量评估结果模型

**验收标准**:
- [x] 接口定义清晰，支持质量评估
- [x] 包含完整的类型注解
- [x] 通过类型检查（mypy）

**实现详情**:
- 创建了 `QualityEvaluationResult` 模型 (`src/models/domain/quality.py`)
- 添加了 `check_available()` 方法（默认实现返回 True）
- 添加了 `evaluate_quality()` 方法（默认实现返回 None）

---

### Task 1.2: 实现质量评估机制

**文件**: `src/infrastructure/ai/quality_evaluator.py` (新建)

**任务**:
- [x] 创建 `QualityEvaluator` 类
- [x] 实现实体提取质量评估
  - [x] 评估实体数量
  - [x] 评估实体类型多样性
  - [x] 评估实体置信度（预留）
- [x] 实现三元组质量评估
  - [x] 评估三元组数量
  - [x] 评估三元组完整性（subject, predicate, object）
  - [x] 评估三元组合理性
- [x] 实现综合质量评分（0.0 - 1.0）
- [x] 实现质量阈值配置

**验收标准**:
- [x] 质量评估算法合理
- [x] 支持可配置的质量阈值
- [x] 包含单元测试（覆盖率 > 80%）

**实现详情**:
- 实体提取质量评估（0-0.5分）
  - 实体数量评分：0-0.2分（每个实体 0.05 分，最多 4 个实体）
  - 实体多样性评分：0-0.2分（基于唯一性比率）
- 三元组质量评估（0-0.5分）
  - 三元组数量评分：0-0.2分（每个三元组 0.05 分，最多 4 个三元组）
  - 三元组完整性评分：0-0.2分（完整三元组比例）
  - 三元组合理性评分：0-0.1分（非空字符串检查）

---

### Task 1.3: 实现降级策略管理器

**文件**: `src/infrastructure/ai/fallback_analysis_model.py` (新建)

**任务**:
- [x] 创建 `FallbackAnalysisModel` 类
- [x] 实现模型优先级管理
- [x] 实现降级逻辑
  - [x] 尝试 Eb-MM → 评估质量 → 不达标则降级
  - [x] 尝试 LangChain Embedding → 评估质量 → 不达标则降级
  - [x] 尝试 LLM → 直接使用（最后保障）
- [x] 实现异常处理和降级
- [x] 实现日志记录（记录使用的模型和降级原因）
- [x] 实现模型可用性检查

**验收标准**:
- [x] 降级逻辑正确
- [x] 异常处理完善
- [x] 日志记录详细
- [x] 包含单元测试和集成测试

**实现详情**:
- 三层级降级策略：
  1. **优先级 1**: Eb-MM (Enterprise Bot mini-Model)
  2. **优先级 2**: LangChain Embedding Model
  3. **优先级 3**: LLM (大模型，最后保障)
- 质量评估触发降级：如果质量不达标，自动降级到下一层级
- 异常处理：模型不可用或失败时，自动降级
- 结构化日志：记录所有降级决策和原因

---

### Task 1.4: 配置管理扩展

**文件**: `src/config/settings.py`

**任务**:
- [x] 扩展 `AISettings` 类
- [x] 添加 Eb-MM 配置项
  - [x] `eb_mm_enabled: bool`
  - [x] `eb_mm_model_path: str`
  - [x] `eb_mm_lora_path: str`
- [x] 添加 LangChain Embedding 配置项
  - [x] `langchain_embedding_enabled: bool`
  - [x] `langchain_embedding_model: str`
- [x] 添加 LLM 降级配置项
  - [x] `llm_fallback_enabled: bool`
  - [x] `llm_provider: str`
  - [x] `llm_model_name: str`
- [x] 添加质量评估配置项
  - [x] `quality_threshold: float` (0.0 - 1.0)
  - [x] `quality_evaluation_enabled: bool`

**验收标准**:
- [x] 所有配置项都有默认值
- [x] 配置项有清晰的描述
- [x] 支持环境变量覆盖

**实现详情**:
- 所有配置项都使用 Pydantic `Field` 和 `alias` 支持环境变量
- 配置项包含清晰的描述文档字符串
- 质量阈值包含验证（ge=0.0, le=1.0）

---

### Task 1.5: 更新依赖注入

**文件**: `src/main.py`

**任务**:
- [x] 更新 `lifespan` 函数
- [x] 创建 `FallbackAnalysisModel` 实例
- [x] 配置各层级模型（初始为 None，后续批次填充）
- [x] 更新 `MemoryServiceImpl` 初始化

**验收标准**:
- [x] 依赖注入正确
- [x] 支持模型动态加载
- [x] 异常处理完善

**实现详情**:
- 创建 `QualityEvaluator` 实例
- 创建 `FallbackAnalysisModel` 实例
- 初始时，三个层级模型都设置为 None
- 如果所有模型都不可用，使用 `MockAnalysisModel` 作为临时占位符
- 保持向后兼容性

---

### Task 1.6: 单元测试和集成测试

**文件**: 
- `tests/unit/test_quality_evaluator.py` (新建)
- `tests/unit/test_fallback_analysis_model.py` (新建)
- `tests/unit/test_interfaces.py` (更新)

**任务**:
- [x] 测试降级逻辑
- [x] 测试质量评估
- [x] 测试异常处理
- [x] 测试日志记录

**验收标准**:
- [x] 测试覆盖率 > 80%
- [x] 所有边界情况都有测试

**实现详情**:
- `test_quality_evaluator.py`: 8 个测试用例
  - 空知识资产评估
  - 实体提取质量评估
  - 三元组质量评估
  - 不完整三元组评估
  - 质量阈值判断
  - 自定义阈值
  - 无效 JSON 处理
  - 实体多样性评估
- `test_fallback_analysis_model.py`: 10 个测试用例
  - Eb-MM 成功提取
  - Eb-MM 低质量降级
  - 所有模型失败
  - Eb-MM 不可用降级
  - 个性分析测试
  - 可用性检查
  - 质量评估禁用测试
- `test_interfaces.py`: 更新以测试新的接口方法

---

## ✅ 验收标准总结

- [x] 降级策略框架完整实现
- [x] 质量评估机制正常工作
- [x] 配置管理支持所有模型层级
- [x] 依赖注入正确，应用可正常启动
- [x] 单元测试创建完成
- [x] 代码符合 AiDevelopmentGuide.md 规范
- [x] 所有文件包含标准头部注释
- [x] 通过 linter 检查

---

## 📁 创建/修改的文件

### 新建文件
1. `src/models/domain/quality.py` - 质量评估结果模型
2. `src/infrastructure/ai/quality_evaluator.py` - 质量评估器
3. `src/infrastructure/ai/fallback_analysis_model.py` - 降级策略管理器
4. `tests/unit/test_quality_evaluator.py` - 质量评估器测试
5. `tests/unit/test_fallback_analysis_model.py` - 降级策略测试

### 修改文件
1. `src/core/interfaces/i_analysis_model.py` - 扩展接口
2. `src/models/domain/__init__.py` - 更新导出
3. `src/config/settings.py` - 扩展配置
4. `src/main.py` - 更新依赖注入
5. `tests/unit/test_interfaces.py` - 更新接口测试

---

## 🔄 依赖关系

- **前置**: Phase I (MVP) 已完成
- **后续**: 批次二、三、四、五依赖此批次

---

## 📚 参考文档

- `docs/AAM Agent SD v2.md` - 系统设计规格
- `docs/plan/AAM Phase II.md` - Phase II 总体计划
- `docs/AiDevelopmentGuide.md` - 开发规范

---

**最后更新**: 2025-11-12

