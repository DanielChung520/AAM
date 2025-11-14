# Ollama 集成实施计划

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: ✅ 已实现基础功能  
**关联文档**: `AAM Phase II.md`

---

## 📋 概述

本计划详细说明如何将 Ollama 本地模型集成到 AAM Service 的语义分析降级策略中。

### 为什么选择 Ollama？

1. **完全本地化**: 不需要外部 API，数据隐私更好
2. **零成本**: 除了硬件成本，无 API 调用费用
3. **离线运行**: 可以完全离线工作
4. **易于部署**: 简单的 Docker 容器或本地安装
5. **模型丰富**: 支持多种开源模型（Llama 3, Mistral, Qwen 等）

---

## 🎯 实施目标

### 功能目标

1. ✅ **实现 Ollama 分析模型**
   - 替换 Mock 模型或作为降级策略的 LLM 层
   - 实现 NER, KE, KT 提取
   - 实现个性分析

2. ✅ **集成到降级策略**
   - 作为优先级 3（最后保障）的 LLM 层
   - 支持质量评估和自动降级

3. ✅ **配置管理**
   - 支持环境变量配置
   - 支持 Docker Compose 集成

### 非功能目标

1. **性能目标**
   - 响应时间: < 2000ms (P95)
   - 支持并发请求

2. **可用性目标**
   - 自动检测 Ollama 服务可用性
   - 优雅降级（如果 Ollama 不可用）

---

## 📦 任务清单

### Task 1: 创建 Ollama 分析模型 ✅

**文件**: `src/infrastructure/ai/ollama_analysis_model.py`

**状态**: ✅ 已完成

**实现内容**:
- [x] 创建 `OllamaAnalysisModel` 类
- [x] 实现 `IAnalysisModel` 接口
- [x] 使用 LangChain Ollama 集成
- [x] 实现 NER 提取
- [x] 实现 KT 提取
- [x] 实现个性分析
- [x] 实现服务可用性检查
- [x] 实现错误处理

**验收标准**:
- ✅ 代码实现完成
- ⏳ 单元测试（待完成）
- ⏳ 集成测试（待完成）

---

### Task 2: 更新配置管理 ✅

**文件**: `src/config/settings.py`

**状态**: ✅ 已完成

**实现内容**:
- [x] 添加 Ollama 配置项
  - `ollama_enabled: bool`
  - `ollama_model_name: str`
  - `ollama_base_url: str`
  - `ollama_timeout: int`
- [x] 添加 LLM 降级配置项（可选）
- [x] 添加质量评估配置项

**验收标准**:
- ✅ 配置项已添加
- ✅ 支持环境变量覆盖

---

### Task 3: 更新依赖 ⏳

**文件**: `requirements.txt`

**状态**: ✅ 已完成

**实现内容**:
- [x] 添加 `langchain>=0.1.0`
- [x] 添加 `langchain-community>=0.0.20`
- [x] 添加 `langchain-core>=0.1.0`

**验收标准**:
- ✅ 依赖已添加
- ⏳ 需要测试安装

---

### Task 4: 集成到主应用 ⏳

**文件**: `src/main.py`

**状态**: ⏳ 待实现

**任务**:
- [ ] 在 `lifespan` 函数中创建 Ollama 模型实例
- [ ] 根据配置决定是否启用 Ollama
- [ ] 集成到 `FallbackAnalysisModel`（如果已实现）
- [ ] 或直接替换 `MockAnalysisModel`

**验收标准**:
- 集成正确
- 支持配置开关
- 异常处理完善

---

### Task 5: Docker Compose 集成 ⏳

**文件**: `docker-compose.dev.yml`

**状态**: ⏳ 待实现

**任务**:
- [ ] 添加 Ollama 服务容器
- [ ] 配置网络和卷
- [ ] 添加健康检查
- [ ] 更新 `aam-service` 依赖

**验收标准**:
- Ollama 容器正常启动
- 网络连接正常
- 健康检查通过

---

### Task 6: 单元测试 ⏳

**文件**: `tests/unit/test_ollama_analysis_model.py`

**状态**: ⏳ 待实现

**任务**:
- [ ] 测试模型初始化
- [ ] 测试 NER 提取
- [ ] 测试 KT 提取
- [ ] 测试个性分析
- [ ] 测试错误处理
- [ ] 测试服务可用性检查

**验收标准**:
- 测试覆盖率 > 80%
- 所有边界情况都有测试

---

### Task 7: 集成测试 ⏳

**文件**: `tests/integration/test_ollama_integration.py`

**状态**: ⏳ 待实现

**任务**:
- [ ] 测试与真实 Ollama 服务的集成
- [ ] 测试降级流程
- [ ] 测试端到端流程

**验收标准**:
- 集成测试通过
- 包含真实场景测试

---

### Task 8: 文档更新 ✅

**文件**: 
- `docs/Ollama集成指南.md` ✅
- `docs/plan/AAM Phase II.md` ✅
- `README.md` (可选)

**状态**: ✅ 已完成

**实现内容**:
- [x] 创建 Ollama 集成指南
- [x] 更新 Phase II 计划
- [x] 添加配置说明

---

## 🚀 快速开始

### 1. 安装 Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 或使用 Docker
docker pull ollama/ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. 下载模型

```bash
ollama pull llama3
```

### 3. 配置环境变量

```bash
# .env
OLLAMA_ENABLED=true
OLLAMA_MODEL_NAME=llama3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 测试

```bash
# 测试 Ollama 连接
curl http://localhost:11434/api/tags

# 运行单元测试
pytest tests/unit/test_ollama_analysis_model.py
```

---

## 📊 实施进度

| 任务 | 状态 | 完成度 |
|------|------|--------|
| Task 1: 创建 Ollama 分析模型 | ✅ | 100% |
| Task 2: 更新配置管理 | ✅ | 100% |
| Task 3: 更新依赖 | ✅ | 100% |
| Task 4: 集成到主应用 | ⏳ | 0% |
| Task 5: Docker Compose 集成 | ⏳ | 0% |
| Task 6: 单元测试 | ⏳ | 0% |
| Task 7: 集成测试 | ⏳ | 0% |
| Task 8: 文档更新 | ✅ | 100% |

**总体进度**: **50%** (4/8 任务完成)

---

## 🔄 下一步行动

### 立即行动（高优先级）

1. **集成到主应用** (Task 4)
   - 在 `main.py` 中创建 Ollama 模型实例
   - 替换 Mock 模型或集成到降级策略

2. **Docker Compose 集成** (Task 5)
   - 添加 Ollama 服务容器
   - 更新网络配置

### 后续行动（中优先级）

3. **单元测试** (Task 6)
   - 编写测试用例
   - 确保覆盖率 > 80%

4. **集成测试** (Task 7)
   - 测试真实场景
   - 验证降级流程

---

## 📝 使用示例

### 直接使用

```python
from src.infrastructure.ai.ollama_analysis_model import OllamaAnalysisModel

# 创建模型实例
ollama_model = OllamaAnalysisModel(
    model_name="llama3",
    base_url="http://localhost:11434",
)

# 提取知识
knowledge = await ollama_model.extract_knowledge(
    text="Apple is a technology company.",
    user_id="user123",
    session_id="session456",
)

# 分析个性
personality = await ollama_model.analyze_personality(
    text="I love programming and technology!"
)
```

### 集成到降级策略

```python
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
from src.infrastructure.ai.ollama_analysis_model import OllamaAnalysisModel

# 创建 Ollama 模型
ollama_model = OllamaAnalysisModel(
    model_name="llama3",
    base_url="http://localhost:11434",
)

# 集成到降级策略
fallback_model = FallbackAnalysisModel(
    eb_mm_model=None,  # 优先级 1
    langchain_embedding=None,  # 优先级 2
    llm_model=ollama_model,  # 优先级 3（Ollama）
)
```

---

## ✅ 检查清单

### 开发环境设置

- [ ] Ollama 已安装
- [ ] 模型已下载（如 `llama3`）
- [ ] 环境变量已配置
- [ ] 依赖已安装

### 代码实现

- [x] Ollama 分析模型已创建
- [x] 配置管理已更新
- [x] 依赖已添加
- [ ] 主应用集成完成
- [ ] Docker Compose 集成完成

### 测试

- [ ] 单元测试完成
- [ ] 集成测试完成
- [ ] 测试覆盖率 > 80%

### 文档

- [x] 集成指南已创建
- [x] Phase II 计划已更新
- [ ] README 已更新（可选）

---

**最后更新**: 2025-11-12

