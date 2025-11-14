# 测试计划 A：对话归档流程端到端测试执行指南

**版本**: v1.0  
**最后更新**: 2025-11-12

---

## 📋 测试概述

本测试计划验证对话归档流程的完整端到端功能，包括：

1. ✅ **多轮对话模拟**: 设置几轮真实对话场景
2. ✅ **语义分析**: 验证语义分析功能（NER、KE、KT）
3. ✅ **知识存储**: 验证知识资产存储到 ChromaDB
4. ✅ **个人偏好存储**: 验证用户画像存储到 PostgreSQL

---

## 🚀 快速开始

### 前置要求

1. **Docker & Docker Compose** (必需)
2. **Python 3.11+** (仅在宿主机运行测试时需要)

### 运行测试

#### 方式 1：在 Docker 容器内运行（推荐）✅

**优点**：
- ✅ 环境一致：测试环境 = 运行环境
- ✅ 无端口冲突：使用 Docker 网络连接数据库
- ✅ 完全隔离：不影响宿主机环境
- ✅ 依赖统一：只需维护 Docker 环境

**步骤**：

```bash
# 1. 启动所有服务（包括数据库）
docker-compose -f docker-compose.dev.yml up -d

# 2. 等待服务就绪（约 30-60 秒）
docker-compose -f docker-compose.dev.yml ps

# 3. 在容器内运行测试
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/ -v

# 或者运行特定测试
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/test_gemini_fallback_semantic_analysis.py -v

# 或者进入容器后运行
docker-compose -f docker-compose.dev.yml exec aam-service bash
pytest tests/e2e/ -v
```

**注意**：首次运行前需要在容器内安装 pytest：
```bash
docker-compose -f docker-compose.dev.yml exec aam-service pip install pytest pytest-asyncio pytest-cov
```

#### 方式 2：在宿主机运行（不推荐）⚠️

**缺点**：
- ⚠️ 需要停止本地 PostgreSQL（避免端口冲突）
- ⚠️ 需要维护两套环境（venv 和 Docker）
- ⚠️ 环境不一致可能导致测试结果不准确

**步骤**：

```bash
# 1. 停止本地 PostgreSQL（如果运行中）
brew services stop postgresql  # macOS
# 或
sudo systemctl stop postgresql  # Linux

# 2. 启动 Docker 服务
docker-compose -f docker-compose.dev.yml up -d

# 3. 安装测试依赖（如果还没有）
source venv/bin/activate
pip install pytest pytest-asyncio pytest-cov

# 4. 运行测试
pytest tests/e2e/ -v
```

### 测试命令示例

```bash
# 运行所有 E2E 测试
pytest tests/e2e/ -v

# 运行特定测试场景
pytest tests/e2e/test_dialogue_archive_flow.py::TestDialogueArchiveFlow::test_technical_consultation_dialogue_flow -v

# 运行并显示详细输出
pytest tests/e2e/ -v -s

# 运行并生成覆盖率报告
pytest tests/e2e/ --cov=src --cov-report=html

# 运行 Gemini 相关测试
pytest tests/e2e/test_gemini_fallback_semantic_analysis.py -v -m gemini
```

---

## 📝 测试场景

### 场景一：技术咨询对话（3轮）

**对话内容**:
- 轮次 1: "什么是 Python？"
- 轮次 2: "Python 可以用来做什么？"
- 轮次 3: "我想学习 Python，有什么推荐的学习资源吗？"

**验证点**:
- ✅ 提取实体: Python, Guido van Rossum, Django, Flask 等
- ✅ 提取知识要点: Python 是编程语言、Python 用于 Web 开发等
- ✅ 提取三元组: (Python, 创建者, Guido van Rossum) 等
- ✅ 存储到 ChromaDB: 3 条知识资产
- ✅ 更新用户画像: 技术导向、学习型

### 场景二：业务咨询对话（4轮）

**对话内容**:
- 轮次 1: "我们公司想实施 AI 项目，有什么建议吗？"
- 轮次 2: "我们的数据量很大，担心处理速度问题。"
- 轮次 3: "预算大概需要多少？"
- 轮次 4: "谢谢，我们会考虑这些建议。"

**验证点**:
- ✅ 提取实体: AI 项目, Apache Spark, Hadoop 等
- ✅ 提取知识要点: AI 项目实施步骤、预算构成等
- ✅ 提取三元组: (AI 项目, 需要, 数据准备) 等
- ✅ 存储到 ChromaDB: 4 条知识资产
- ✅ 更新用户画像: 业务导向、决策型

### 场景三：日常对话（2轮）

**对话内容**:
- 轮次 1: "今天天气真好！"
- 轮次 2: "我想去公园走走。"

**验证点**:
- ✅ 提取实体: 今天, 公园
- ✅ 提取知识要点: 天气好、去公园
- ✅ 提取三元组: (用户, 计划, 去公园)
- ✅ 存储到 ChromaDB: 2 条知识资产
- ✅ 更新用户画像: 轻松风格、友好

---

## 🔧 测试配置

### 环境变量

```bash
# ChromaDB 配置
export CHROMADB_HOST=localhost
export CHROMADB_PORT=8000

# PostgreSQL 配置
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=aam_test
export POSTGRES_USER=test
export POSTGRES_PASSWORD=test
```

### 使用 Mock 模型（快速测试）

默认使用 Mock 模型，返回预设的分析结果。适合快速验证存储逻辑。

### 使用真实模型（完整验证）

如果需要使用真实模型进行测试，可以修改 `conftest.py`:

```python
@pytest.fixture(scope="function")
def analysis_model():
    """使用真实模型"""
    from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel
    from src.infrastructure.ai.eb_mm_analysis_model import EbMMAnalysisModel
    # ... 配置真实模型
    return FallbackAnalysisModel(...)
```

---

## 📊 测试结果验证

### 验证清单

每个测试场景都会验证：

- [ ] **对话归档执行成功**（无异常）
- [ ] **语义分析结果正确**
  - [ ] NER 提取结果存在
  - [ ] KE 提取结果存在
  - [ ] KT 提取结果存在
  - [ ] 三元组结构完整（subject, predicate, object）
- [ ] **知识存储到 ChromaDB**
  - [ ] 知识资产已存储
  - [ ] 元数据正确（user_id, session_id, entities, triples_json）
  - [ ] 向量已生成
  - [ ] 文档内容正确
- [ ] **个人偏好存储到 PostgreSQL**
  - [ ] 用户画像已存储/更新
  - [ ] style_tags 正确
  - [ ] sentiment 正确
  - [ ] language_patterns 正确
  - [ ] last_updated 已更新

---

## 🐛 调试技巧

### 查看测试输出

```bash
# 显示详细输出
pytest tests/e2e/ -v -s

# 显示最详细输出
pytest tests/e2e/ -vv -s
```

### 检查数据库内容

```python
# 在测试中使用 pdb 调试
import pdb; pdb.set_trace()

# 检查 ChromaDB
results = knowledge_store.collection.get()
print(results)

# 检查 PostgreSQL
profile = await persona_store.get("user_tech_001")
print(profile)
```

### 查看测试数据

测试数据位于 `tests/e2e/fixtures/`:
- `dialogue_scenarios.py` - 对话场景数据
- `expected_results.py` - 预期结果数据

---

## 📈 测试报告

### 生成测试报告

```bash
# 生成 HTML 报告
pytest tests/e2e/ --html=report.html --self-contained-html

# 生成 JUnit XML 报告（用于 CI/CD）
pytest tests/e2e/ --junitxml=report.xml
```

### 测试报告模板

测试报告应包含：

1. **测试概述**: 测试场景、测试数据
2. **测试结果**: 通过/失败统计
3. **语义分析结果**: NER、KE、KT 提取结果
4. **数据存储验证**: ChromaDB 和 PostgreSQL 存储验证
5. **问题清单**: 发现的问题和建议

---

## ❓ 常见问题

### Q: 测试失败，提示数据库连接错误

A: 确保测试数据库已启动：
```bash
docker-compose -f docker-compose.test.yml up -d
```

### Q: 测试数据没有清理

A: 测试会自动清理，但如果失败可能需要手动清理：
```bash
# 清理 ChromaDB（删除测试 collection）
# 清理 PostgreSQL（删除测试用户）
```

### Q: 如何验证真实模型的分析结果？

A: 修改 `conftest.py` 使用真实模型，或创建新的测试文件专门测试真实模型。

### Q: 测试执行太慢

A: 使用 Mock 模型可以大幅提升速度。真实模型测试建议单独运行。

---

## 📚 相关文档

- [测试计划 A 详细文档](../../docs/plan/測試計劃A：對話歸檔流程端到端測試.md)
- [整合测试计划](../../docs/plan/整合測試計劃.md)
- [测试执行指南](../README.md)

---

**最后更新**: 2025-11-12

