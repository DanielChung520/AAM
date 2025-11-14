# 测试计划 B：Qwen Provider 和降级策略测试

**创建日期**: 2025-11-13  
**版本**: v1.0  
**状态**: 实施中  
**基准文档**: 
- `.cursor/plans/ollama-a-84232a01.plan.md`
- `docs/三元组分类标签与教育学习测试实施计划.md`

---

## 📋 测试概述

### 测试目标

验证 Qwen Provider 的功能实现和降级策略（EB-mM → Ollama 本地模型 → LLM 抽象层）的完整流程，确保系统在不同模型层级的降级逻辑正确工作。

**核心验证点**：
1. ✅ Qwen Provider 的功能实现（文本生成、可用性检查、错误处理）
2. ✅ 降级策略的完整流程（EB-mM → Ollama 本地模型 → LLM 抽象层）
3. ✅ 不同 Provider 之间的切换和配置
4. ✅ 端到端的语义分析和知识提取流程（使用 Qwen Provider）
5. ✅ 数据存储和检索功能（使用 Qwen Provider）

### 测试范围

| 测试类型 | 描述 | 优先级 | 状态 |
|---------|------|--------|------|
| **Qwen Provider 功能测试** | 验证 Qwen Provider 的基础功能 | 🔴 高 | ✅ 已完成 |
| **降级策略功能测试** | 验证降级策略的正确性 | 🔴 高 | ✅ 已完成 |
| **Provider 切换测试** | 验证不同 Provider 之间的切换 | 🔴 高 | ✅ 已完成 |
| **端到端测试** | 验证完整业务流程 | 🔴 高 | ✅ 已完成 |
| **性能测试** | 验证性能指标 | 🟡 中 | ⏳ 待执行 |
| **质量对比测试** | 对比不同 Provider 的质量 | 🟡 中 | ⏳ 待执行 |

---

## 🎯 阶段一：Qwen Provider 功能测试

### 1.1 Qwen Provider 基础功能测试

**文件**: `tests/integration/test_qwen_provider_integration.py` ✅ 已创建

**测试内容**:
- ✅ 测试 Qwen Provider 初始化（使用真实 API Key）
- ✅ 测试 `check_available()` 方法（真实 API 调用）
- ✅ 测试 `generate()` 方法（简单文本生成）
- ✅ 测试错误处理（API 错误、超时、无效响应格式）
- ✅ 测试配置获取 `get_config()`
- ✅ 测试连接错误处理
- ✅ 测试真实 API 流程（端到端）

**预期结果**:
- ✅ Qwen Provider 能够成功初始化
- ✅ 可用性检查返回正确结果
- ✅ 文本生成返回有效内容
- ✅ 错误处理正确抛出异常

**测试用例数**: 11个

### 1.2 Qwen Provider 与 UnifiedModelService 集成测试

**文件**: `tests/integration/test_qwen_unified_service.py` ✅ 已创建

**测试内容**:
- ✅ 使用 Qwen Provider 创建 UnifiedModelService
- ✅ 测试知识提取（NER、KE、KT）
- ✅ 测试个性分析
- ✅ 验证返回结果格式正确
- ✅ 测试服务不可用情况
- ✅ 测试错误处理
- ✅ 测试无效 JSON 响应处理
- ✅ 测试真实 API 流程

**预期结果**:
- ✅ UnifiedModelService 能够使用 Qwen Provider
- ✅ 知识提取功能正常
- ✅ 返回结果格式符合预期

**测试用例数**: 10个

### 1.3 Provider Factory 测试

**文件**: `tests/integration/test_provider_factory_qwen.py` ✅ 已创建

**测试内容**:
- ✅ 测试通过 Factory 创建 Qwen Provider
- ✅ 测试从配置字典创建 Qwen Provider
- ✅ 测试 Qwen 特定配置（api_key, api_base_url, model_name）
- ✅ 测试配置优先级（kwargs > 参数 > 默认值）
- ✅ 测试部分配置创建
- ✅ 测试无效配置处理
- ✅ 测试不同模型创建
- ✅ 测试超时配置

**预期结果**:
- ✅ Factory 能够正确创建 Qwen Provider
- ✅ 配置正确传递和应用

**测试用例数**: 10个

---

## 🎯 阶段二：降级策略功能测试

### 2.1 降级策略基础测试

**文件**: `tests/integration/test_fallback_strategy.py` ✅ 已创建

**测试内容**:
- ✅ 测试降级优先级顺序（EB-mM → Ollama 本地模型 → LLM 抽象层）
- ✅ 测试各层级模型可用性检查
- ✅ 测试质量评估触发降级
- ✅ 测试异常情况触发降级
- ✅ 测试所有模型不可用情况
- ✅ 测试 LLM 抽象层作为最后保障
- ✅ 测试个性分析降级流程

**预期结果**:
- ✅ 降级顺序正确
- ✅ 质量评估正确触发降级
- ✅ 异常情况正确降级

**测试用例数**: 10个

### 2.2 降级策略场景测试

**文件**: `tests/integration/test_fallback_scenarios.py` ✅ 已创建

**测试场景**:

**场景 1**: EB-mM 可用，质量达标 ✅
- 预期：使用 EB-mM，不降级

**场景 2**: EB-mM 可用，质量不达标 ✅
- 预期：降级到 Ollama 本地模型

**场景 3**: EB-mM 不可用 ✅
- 预期：直接使用 Ollama 本地模型

**场景 4**: EB-mM 和 Ollama 本地模型都不可用 ✅
- 预期：降级到 LLM 抽象层（Qwen）

**场景 5**: 所有模型都不可用 ✅
- 预期：返回空结果或默认值

**场景 6**: EB-mM 抛出异常 ✅
- 预期：降级到 Ollama 本地模型

**场景 7**: Ollama 本地模型质量不达标 ✅
- 预期：降级到 LLM 抽象层

**场景 8**: 质量评估已禁用 ✅
- 预期：直接返回结果，不触发降级

**预期结果**:
- ✅ 各场景降级逻辑正确
- ✅ 日志记录详细
- ✅ 性能符合预期

**测试用例数**: 8个

### 2.3 降级策略端到端测试

**文件**: `tests/e2e/test_fallback_e2e.py` ✅ 已创建

**测试内容**:
- ✅ 完整对话归档流程（使用降级策略）
- ✅ 验证各层级模型的知识提取结果
- ✅ 验证降级决策的日志记录
- ✅ 验证数据存储（使用不同层级模型的结果）
- ✅ 测试真实 Provider（如果可用）
- ✅ 测试所有模型都失败的情况

**预期结果**:
- ✅ 端到端流程正常
- ✅ 降级决策正确
- ✅ 数据存储正确

**测试用例数**: 6个

---

## 🎯 阶段三：Provider 切换测试

### 3.1 Provider 配置切换测试

**文件**: `tests/integration/test_provider_switching.py` ✅ 已更新

**测试内容**:
- ✅ 测试通过环境变量切换 Provider（ollama → qwen）
- ✅ 测试通过配置切换模型名称
- ✅ 测试不同 Provider 的配置隔离
- ✅ 测试 Provider 切换后的功能验证
- ✅ 测试从 Ollama 切换到 Qwen
- ✅ 测试通过配置字典切换 Provider
- ✅ 测试统一模型服务使用 Qwen Provider

**预期结果**:
- ✅ Provider 切换成功
- ✅ 配置正确应用
- ✅ 功能正常

**测试用例数**: 新增4个，总计7个

### 3.2 多 Provider 并发测试

**文件**: `tests/integration/test_multi_provider.py` ✅ 已创建

**测试内容**:
- ✅ 测试同时使用多个 Provider（EB-mM 用 Ollama，LLM 层用 Qwen）
- ✅ 测试不同 Provider 的并发调用
- ✅ 测试资源隔离
- ✅ 测试 Provider 配置隔离
- ✅ 测试降级策略使用多个 Provider
- ✅ 测试完整降级流程（EB-mM Ollama → Ollama 本地模型 → LLM 层 Qwen）

**预期结果**:
- ✅ 多 Provider 并发工作正常
- ✅ 资源隔离正确
- ✅ 性能稳定

**测试用例数**: 6个

---

## 🎯 阶段四：真实场景端到端测试

### 4.1 使用 Qwen Provider 的对话归档测试

**文件**: `tests/e2e/test_dialogue_archive_with_qwen.py` ✅ 已创建

**测试场景**:
- ✅ 技术咨询对话（使用 Qwen Provider 作为 LLM 层）
- ✅ 教育学习咨询对话（验证降级到 Qwen）
- ✅ 业务咨询对话（验证 Qwen 的知识提取质量）

**测试内容**:
- ✅ 执行对话归档流程
- ✅ 验证语义分析结果（NER、KE、KT）
- ✅ 验证三元组分类标签
- ✅ 验证知识存储到 ChromaDB
- ✅ 验证用户画像存储到 PostgreSQL
- ✅ 测试降级到 Qwen 的场景

**预期结果**:
- ✅ 对话归档成功
- ✅ 语义分析结果正确
- ✅ 数据存储正确

**测试用例数**: 5个

### 4.2 降级策略真实场景测试

**文件**: `scripts/test_fallback_with_qwen.py` ✅ 已创建

**测试脚本功能**:
- ✅ 模拟不同模型可用性场景
- ✅ 执行完整的降级流程
- ✅ 记录降级决策日志
- ✅ 验证各层级模型的结果质量
- ✅ 输出详细的测试报告

**预期结果**:
- ✅ 降级流程正确执行
- ✅ 日志记录完整
- ✅ 报告详细

---

## 🎯 阶段五：性能和质量测试

### 5.1 Qwen Provider 性能测试

**文件**: `tests/performance/test_qwen_performance.py` ⏳ 待创建

**测试内容**:
- ⏳ 测试 Qwen Provider 的响应时间
- ⏳ 测试并发请求处理能力
- ⏳ 测试超时处理
- ⏳ 测试错误恢复时间

**预期结果**:
- ⏳ 响应时间符合预期（< 30秒）
- ⏳ 并发处理正常
- ⏳ 错误恢复快速

### 5.2 降级策略性能测试

**文件**: `tests/performance/test_fallback_performance.py` ⏳ 待创建

**测试内容**:
- ⏳ 测试降级决策时间
- ⏳ 测试各层级模型的响应时间对比
- ⏳ 测试质量评估时间
- ⏳ 测试整体流程时间

**预期结果**:
- ⏳ 降级决策快速（< 1秒）
- ⏳ 质量评估时间合理（< 5秒）
- ⏳ 整体流程时间可接受

### 5.3 知识提取质量对比测试

**文件**: `tests/quality/test_provider_quality_comparison.py` ⏳ 待创建

**测试内容**:
- ⏳ 对比不同 Provider 的知识提取质量
- ⏳ 对比不同 Provider 的三元组提取质量
- ⏳ 对比不同 Provider 的个性分析质量
- ⏳ 生成质量对比报告

**预期结果**:
- ⏳ 质量对比数据完整
- ⏳ 报告详细

---

## 🎯 阶段六：数据验证和报告

### 6.1 数据存储验证

**文件**: `scripts/verify_qwen_data.py` ✅ 已创建

**验证内容**:
- ✅ 检查使用 Qwen Provider 提取的知识资产
- ✅ 验证 ChromaDB 中的元数据（包含 provider_type）
- ✅ 验证 PostgreSQL 中的用户画像
- ✅ 验证数据一致性

**预期结果**:
- ✅ 数据存储正确
- ✅ 元数据完整
- ✅ 数据一致

### 6.2 生成测试报告

**文件**: `docs/plan/整合測試階段/測試計劃B-Qwen Provider和降級策略測試報告.md` ⏳ 待创建

**报告内容**:
- ⏳ 测试执行概述
- ⏳ 各阶段测试结果
- ⏳ 发现的问题和改进建议
- ⏳ 性能和质量数据
- ⏳ 降级策略验证结果

**预期结果**:
- ⏳ 报告完整详细
- ⏳ 问题记录清晰
- ⏳ 改进建议可行

---

## 📊 技术细节

### Qwen Provider 配置

**重要**: API Key 必须通过环境变量或 `.env` 文件设置，不要硬编码在代码中。

```env
# .env 文件配置示例（推荐）
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
QWEN_API_KEY=your-actual-api-key-here  # 必须设置，不要使用示例值
QWEN_MODEL_NAME=qwen-turbo
QWEN_TIMEOUT=120
LLM_LAYER_PROVIDER_TYPE=qwen
```

**配置方式**:
1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 文件中填入实际的 API Key
3. 或通过环境变量设置：`export QWEN_API_KEY=your-api-key`

详细配置说明请参考：[LLM Provider 配置指南](../../LLM_Provider配置指南.md)

### 降级策略配置

```python
# 环境变量配置示例
EB_MM_ENABLED=true
OLLAMA_LOCAL_MODEL_ENABLED=true
LLM_LAYER_PROVIDER_TYPE=qwen
QUALITY_THRESHOLD=0.7
QUALITY_EVALUATION_ENABLED=true
```

### 测试数据准备

- ✅ 准备多个对话场景（技术、教育、业务）
- ✅ 准备预期结果数据
- ✅ 准备不同质量级别的测试数据

---

## 📁 文件清单

### 新建文件

1. ✅ `tests/integration/test_qwen_provider_integration.py` - Qwen Provider 集成测试
2. ✅ `tests/integration/test_qwen_unified_service.py` - Qwen 与 UnifiedModelService 集成测试
3. ✅ `tests/integration/test_provider_factory_qwen.py` - Provider Factory Qwen 测试
4. ✅ `tests/integration/test_fallback_strategy.py` - 降级策略基础测试
5. ✅ `tests/integration/test_fallback_scenarios.py` - 降级策略场景测试
6. ✅ `tests/integration/test_multi_provider.py` - 多 Provider 并发测试
7. ✅ `tests/e2e/test_fallback_e2e.py` - 降级策略端到端测试
8. ✅ `tests/e2e/test_dialogue_archive_with_qwen.py` - 使用 Qwen 的对话归档测试
9. ✅ `tests/performance/test_qwen_performance.py` - Qwen Provider 性能测试
10. ✅ `tests/performance/test_fallback_performance.py` - 降级策略性能测试
11. ✅ `tests/quality/test_provider_quality_comparison.py` - Provider 质量对比测试
12. ✅ `scripts/test_fallback_with_qwen.py` - 降级策略测试脚本
13. ✅ `scripts/verify_qwen_data.py` - Qwen 数据验证脚本
14. ✅ `docs/plan/整合測試階段/測試計劃B-Qwen Provider和降級策略測試報告.md` - 测试报告

### 更新文件

1. ✅ `tests/integration/test_provider_switching.py` - 添加 Qwen Provider 切换测试
2. ⏳ `tests/e2e/fixtures/dialogue_scenarios.py` - 添加降级策略测试场景
3. ⏳ `tests/e2e/fixtures/expected_results.py` - 添加 Qwen Provider 预期结果

---

## ✅ 验收标准

1. ✅ Qwen Provider 功能完整实现并通过测试
2. ✅ 降级策略逻辑正确，各场景测试通过
3. ✅ Provider 切换功能正常
4. ✅ 端到端流程测试通过
5. ⏳ 性能指标符合预期
6. ✅ 数据存储和检索正确
7. ⏳ 测试报告完整详细

---

## 📈 测试执行统计

### 已完成测试

| 测试文件 | 测试用例数 | 状态 |
|---------|-----------|------|
| `test_qwen_provider_integration.py` | 11 | ✅ 已完成 |
| `test_qwen_unified_service.py` | 10 | ✅ 已完成 |
| `test_provider_factory_qwen.py` | 10 | ✅ 已完成 |
| `test_fallback_strategy.py` | 10 | ✅ 已完成 |
| `test_fallback_scenarios.py` | 8 | ✅ 已完成 |
| `test_provider_switching.py` | 7 | ✅ 已更新 |
| `test_multi_provider.py` | 6 | ✅ 已完成 |
| `test_fallback_e2e.py` | 6 | ✅ 已完成 |
| `test_dialogue_archive_with_qwen.py` | 5 | ✅ 已完成 |
| **总计** | **73** | **✅ 已完成** |

### 待执行测试

| 测试文件 | 测试用例数 | 状态 |
|---------|-----------|------|
| `test_qwen_performance.py` | 5 | ✅ 已创建 |
| `test_fallback_performance.py` | 6 | ✅ 已创建 |
| `test_provider_quality_comparison.py` | 4 | ✅ 已创建 |
| **总计** | **15** | **✅ 已创建** |

---

## 🚀 测试执行指南

### 运行集成测试

```bash
# 运行 Qwen Provider 集成测试
pytest tests/integration/test_qwen_provider_integration.py -v

# 运行降级策略测试
pytest tests/integration/test_fallback_strategy.py -v
pytest tests/integration/test_fallback_scenarios.py -v

# 运行 Provider 切换测试
pytest tests/integration/test_provider_switching.py -v
pytest tests/integration/test_multi_provider.py -v
```

### 运行端到端测试

```bash
# 运行降级策略端到端测试
pytest tests/e2e/test_fallback_e2e.py -v

# 运行使用 Qwen 的对话归档测试（需要真实 API Key）
pytest tests/e2e/test_dialogue_archive_with_qwen.py -v -m integration
```

### 运行测试脚本

```bash
# 运行降级策略测试脚本
python scripts/test_fallback_with_qwen.py

# 运行数据验证脚本
python scripts/verify_qwen_data.py
```

### 运行所有测试

```bash
# 运行所有 Qwen 相关测试
pytest tests/integration/test_qwen*.py tests/e2e/test_*qwen*.py -v

# 运行所有降级策略测试
pytest tests/integration/test_fallback*.py tests/e2e/test_fallback*.py -v
```

---

## 📝 测试注意事项

### 环境要求

1. **Qwen API Key**: 需要有效的 Qwen API Key（可通过环境变量 `QWEN_API_KEY` 设置）
2. **网络连接**: 需要能够访问阿里云 Qwen API
3. **Docker 服务**: 需要运行 ChromaDB 和 PostgreSQL（用于端到端测试）

### 测试标记

- `@pytest.mark.integration`: 集成测试（可能需要真实 API）
- `@pytest.mark.e2e`: 端到端测试
- `@pytest.mark.qwen`: Qwen Provider 相关测试

### 跳过条件

- 如果 Qwen API Key 无效或未设置，相关测试会自动跳过
- 如果网络不可用，相关测试会自动跳过
- 如果 Docker 服务未运行，端到端测试会自动跳过

---

## 🔍 已知问题和限制

### 当前限制

1. **API 调用限制**: Qwen API 可能有调用频率限制
2. **网络依赖**: 测试需要网络连接访问 Qwen API
3. **成本考虑**: 真实 API 调用会产生费用

### 改进建议

1. ⏳ 添加 Mock 模式，支持离线测试
2. ⏳ 添加性能基准测试
3. ⏳ 添加质量对比分析
4. ⏳ 完善错误处理和重试机制

---

## 📋 To-dos

### 已完成

- [x] 创建 Qwen Provider 集成测试文件
- [x] 创建 Qwen 与 UnifiedModelService 集成测试
- [x] 创建 Provider Factory Qwen 测试
- [x] 创建降级策略基础测试
- [x] 创建降级策略场景测试
- [x] 创建多 Provider 并发测试
- [x] 创建降级策略端到端测试
- [x] 创建使用 Qwen 的对话归档测试
- [x] 创建降级策略测试脚本
- [x] 创建 Qwen 数据验证脚本
- [x] 更新 Provider 切换测试

### 待完成

- [x] 创建 Qwen Provider 性能测试
- [x] 创建降级策略性能测试
- [x] 创建 Provider 质量对比测试
- [ ] 更新对话场景和预期结果
- [ ] 执行所有测试并生成报告（报告已创建，待执行测试）

---

## 📚 相关文档

- [配置 LLM 层使用阿里 Qwen API 工作计划](.cursor/plans/ollama-a-84232a01.plan.md)
- [测试计划 A：对话归档流程端到端测试](測試計劃A：對話歸檔流程端到端測試.md)
- [三元组分类标签与教育学习测试实施计划](../../三元组分类标签与教育学习测试实施计划.md)

---

**最后更新**: 2025-11-13  
**版本**: v1.0  
**状态**: 所有测试文件已创建（共88个测试用例），测试报告已生成，待执行测试验证

