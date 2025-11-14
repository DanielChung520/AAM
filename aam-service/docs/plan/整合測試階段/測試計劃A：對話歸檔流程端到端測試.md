# 测试计划 A：对话归档流程端到端测试

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 规划中  
**基准文档**: 
- `AAM (AI-Augmented Memory) SA v1.md`
- `AAM Phase II.md`

---

## 📋 测试概述

### 测试目标

验证对话归档流程的完整端到端功能，包括：
1. **多轮对话模拟**: 设置几轮真实对话场景
2. **语义分析**: 验证语义分析功能（NER、KE、KT）
3. **知识存储**: 验证知识资产存储到 ChromaDB
4. **个人偏好存储**: 验证用户画像存储到 PostgreSQL
5. **数据一致性**: 验证存储的数据正确性和完整性

### 测试范围

| 测试项 | 描述 | 优先级 |
|--------|------|--------|
| **对话归档流程** | 完整的对话归档处理流程 | 🔴 高 |
| **语义分析** | NER、KE、KT 提取验证 | 🔴 高 |
| **知识存储** | ChromaDB 存储验证 | 🔴 高 |
| **个人偏好存储** | PostgreSQL 存储验证 | 🔴 高 |
| **数据检索** | 存储后的数据检索验证 | 🟡 中 |

---

## 🎯 测试场景设计

### 场景一：技术咨询对话（3轮）

**对话内容**:
```
轮次 1:
用户: "什么是 Python？"
AI: "Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年创建。它以其简洁的语法和强大的功能而闻名。"

轮次 2:
用户: "Python 可以用来做什么？"
AI: "Python 可以用于多种用途，包括 Web 开发（Django、Flask）、数据科学（Pandas、NumPy）、机器学习（TensorFlow、PyTorch）和自动化脚本。"

轮次 3:
用户: "我想学习 Python，有什么推荐的学习资源吗？"
AI: "推荐的学习资源包括：1) Python 官方文档 2) 《Python 编程：从入门到实践》3) Codecademy 的 Python 课程 4) Real Python 网站。"
```

**预期提取结果**:
- **NER**: Python, Guido van Rossum, Django, Flask, Pandas, NumPy, TensorFlow, PyTorch, Codecademy, Real Python
- **KE**: Python 是编程语言、Python 用于 Web 开发、Python 用于数据科学
- **KT**: 
  - (Python, 创建者, Guido van Rossum)
  - (Python, 用于, Web 开发)
  - (Python, 用于, 数据科学)
  - (Django, 是, Web 框架)
  - (TensorFlow, 是, 机器学习库)
- **个人偏好**: 技术导向、学习型、正式风格

---

### 场景二：业务咨询对话（4轮）

**对话内容**:
```
轮次 1:
用户: "我们公司想实施 AI 项目，有什么建议吗？"
AI: "实施 AI 项目需要考虑几个关键因素：1) 明确业务目标 2) 数据准备 3) 技术选型 4) 团队建设 5) 预算规划。"

轮次 2:
用户: "我们的数据量很大，担心处理速度问题。"
AI: "对于大数据量，建议考虑：1) 使用分布式计算框架（如 Spark）2) 数据预处理和清洗 3) 选择合适的存储方案（如 Hadoop HDFS）4) 优化算法和模型。"

轮次 3:
用户: "预算大概需要多少？"
AI: "AI 项目预算通常包括：1) 硬件成本（GPU 服务器、存储）2) 软件许可（如需要）3) 人力成本（数据科学家、工程师）4) 云服务费用。根据项目规模，预算可能在 10 万到 100 万之间。"

轮次 4:
用户: "谢谢，我们会考虑这些建议。"
AI: "不客气！如果后续有任何问题，随时可以咨询。"
```

**预期提取结果**:
- **NER**: AI 项目, Spark, Hadoop HDFS, GPU, 数据科学家
- **KE**: AI 项目实施步骤、大数据处理方案、AI 项目预算构成
- **KT**:
  - (AI 项目, 需要, 明确业务目标)
  - (大数据量, 处理方案, 分布式计算)
  - (Spark, 是, 分布式计算框架)
  - (AI 项目, 预算范围, 10-100万)
- **个人偏好**: 业务导向、决策型、正式风格、积极情感

---

### 场景三：日常对话（2轮）

**对话内容**:
```
轮次 1:
用户: "今天天气真好！"
AI: "是的，今天天气确实不错！适合外出活动。您有什么计划吗？"

轮次 2:
用户: "我想去公园走走。"
AI: "那是个不错的选择！公园里空气清新，可以放松心情。祝您玩得愉快！"
```

**预期提取结果**:
- **NER**: 今天, 公园
- **KE**: 天气好、去公园
- **KT**:
  - (用户, 计划, 去公园)
- **个人偏好**: 轻松风格、友好、积极情感

---

## 📝 测试步骤

### 步骤 1: 准备测试环境

1. [ ] 启动测试数据库（ChromaDB、PostgreSQL）
2. [ ] 初始化测试数据（清空测试数据库）
3. [ ] 配置测试用的分析模型（可以使用 Mock 或真实模型）
4. [ ] 准备测试用的 MemoryService 实例

### 步骤 2: 执行对话归档

对于每个测试场景：

1. [ ] **创建对话归档消息**
   - 构造 `DialogueArchiveMessage` 对象
   - 包含 user_id, dialog_id, turn, user_query, ai_response

2. [ ] **调用 archive 方法**
   - 调用 `MemoryServiceImpl.archive(message)`
   - 验证方法执行成功（无异常）

3. [ ] **验证语义分析执行**
   - 验证分析模型被调用（extract_knowledge, analyze_personality）
   - 验证 NER 提取结果
   - 验证 KE 提取结果
   - 验证 KT 提取结果
   - 验证个性分析结果

4. [ ] **验证知识存储到 ChromaDB**
   - 查询 ChromaDB，验证知识资产已存储
   - 验证存储的元数据正确（user_id, session_id, entities, triples_json）
   - 验证向量已生成
   - 验证文档内容正确

5. [ ] **验证个人偏好存储到 PostgreSQL**
   - 查询 PostgreSQL，验证用户画像已存储/更新
   - 验证 style_tags 正确
   - 验证 sentiment 正确
   - 验证 language_patterns 正确
   - 验证 last_updated 已更新

### 步骤 3: 验证数据检索

1. [ ] **验证知识检索**
   - 使用 `knowledge_store.search()` 检索知识
   - 验证检索结果包含存储的知识
   - 验证向量搜索正常工作

2. [ ] **验证用户画像检索**
   - 使用 `persona_store.get()` 检索用户画像
   - 验证检索结果正确
   - 验证多轮对话后的画像累积更新

### 步骤 4: 验证数据一致性

1. [ ] **验证多轮对话数据累积**
   - 验证每轮对话的知识都正确存储
   - 验证用户画像在多轮对话后正确更新
   - 验证实体和三元组正确累积

2. [ ] **验证数据完整性**
   - 验证所有必需字段都存在
   - 验证数据格式正确（JSON、时间戳等）
   - 验证数据关联正确（user_id、session_id）

---

## 🧪 测试实现

### 测试文件结构

```
tests/e2e/
├── test_dialogue_archive_flow.py    # 主要测试文件
├── fixtures/
│   ├── dialogue_scenarios.py       # 对话场景数据
│   └── test_data.py                # 测试数据准备
└── conftest.py                      # E2E 测试配置
```

### 测试用例设计

#### 测试用例 1: 技术咨询对话完整流程

```python
@pytest.mark.e2e
async def test_technical_consultation_dialogue_flow(
    memory_service,
    knowledge_store,
    persona_store,
    analysis_model,
):
    """测试技术咨询对话的完整归档流程"""
    # 1. 准备对话数据
    dialogues = [
        {
            "turn": 1,
            "user_query": "什么是 Python？",
            "ai_response": "Python 是一种高级编程语言...",
        },
        # ... 更多轮次
    ]
    
    # 2. 执行归档
    for dialogue in dialogues:
        message = DialogueArchiveMessage(
            dialog_id="test_dialog_001",
            user_id="test_user_001",
            turn=dialogue["turn"],
            user_query=dialogue["user_query"],
            ai_response=dialogue["ai_response"],
            timestamp=datetime.now(),
        )
        await memory_service.archive(message)
    
    # 3. 验证知识存储
    # 4. 验证个人偏好存储
    # 5. 验证数据检索
```

#### 测试用例 2: 多轮对话数据累积

```python
@pytest.mark.e2e
async def test_multi_turn_dialogue_accumulation(
    memory_service,
    knowledge_store,
    persona_store,
):
    """测试多轮对话的数据累积"""
    # 执行多轮对话归档
    # 验证每轮对话的知识都存储
    # 验证用户画像累积更新
```

#### 测试用例 3: 语义分析结果验证

```python
@pytest.mark.e2e
async def test_semantic_analysis_results(
    memory_service,
    analysis_model,
):
    """测试语义分析结果"""
    # 执行归档
    # 验证 NER 提取
    # 验证 KE 提取
    # 验证 KT 提取
    # 验证个性分析
```

---

## 📊 验证点清单

### 语义分析验证

- [ ] **NER 提取验证**
  - 实体数量 > 0
  - 实体类型正确（人名、地名、组织名、产品名等）
  - 实体内容准确

- [ ] **KE 提取验证**
  - 知识要点数量 > 0
  - 知识要点内容相关
  - 知识要点格式正确

- [ ] **KT 提取验证**
  - 三元组数量 > 0
  - 三元组完整性（subject, predicate, object）
  - 三元组合理性
  - 三元组 JSON 格式正确

- [ ] **个性分析验证**
  - style_tags 存在
  - sentiment 存在
  - language_patterns 存在
  - confidence_score 在 0-1 之间

### 知识存储验证

- [ ] **ChromaDB 存储验证**
  - 知识资产已存储
  - 向量已生成
  - 元数据正确（user_id, session_id, entities, triples_json）
  - 文档内容正确
  - 时间戳正确

- [ ] **数据检索验证**
  - 可以检索到存储的知识
  - 向量搜索正常工作
  - 元数据过滤正常工作

### 个人偏好存储验证

- [ ] **PostgreSQL 存储验证**
  - 用户画像已存储/更新
  - style_tags 正确（JSON 格式）
  - sentiment 正确
  - language_patterns 正确
  - last_updated 已更新

- [ ] **数据累积验证**
  - 多轮对话后，用户画像正确累积
  - style_tags 正确合并
  - sentiment_history 正确更新

---

## 🔧 测试环境要求

### 必需服务

1. **ChromaDB**
   - 测试数据库实例
   - 独立的 collection（测试隔离）

2. **PostgreSQL**
   - 测试数据库实例
   - 独立的 schema（测试隔离）

3. **分析模型**
   - Mock 模型（快速测试）
   - 或真实模型（完整验证）

### 可选服务

1. **RabbitMQ**（如果测试消息队列集成）
2. **Ollama/vLLM**（如果使用真实模型）

---

## 📈 测试数据准备

### 对话场景数据

**文件**: `tests/e2e/fixtures/dialogue_scenarios.py`

```python
TECHNICAL_CONSULTATION_DIALOGUES = [
    {
        "dialog_id": "tech_dialog_001",
        "user_id": "user_tech_001",
        "turn": 1,
        "user_query": "什么是 Python？",
        "ai_response": "Python 是一种高级编程语言，由 Guido van Rossum 在 1991 年创建。",
    },
    # ... 更多轮次
]

BUSINESS_CONSULTATION_DIALOGUES = [
    # ... 业务咨询对话
]

CASUAL_DIALOGUES = [
    # ... 日常对话
]
```

### 预期结果数据

**文件**: `tests/e2e/fixtures/expected_results.py`

```python
EXPECTED_NER_TECHNICAL = [
    "Python",
    "Guido van Rossum",
    "Django",
    "Flask",
    # ...
]

EXPECTED_KT_TECHNICAL = [
    {"subject": "Python", "predicate": "创建者", "object": "Guido van Rossum"},
    {"subject": "Python", "predicate": "用于", "object": "Web 开发"},
    # ...
]

EXPECTED_PERSONALITY_TECHNICAL = {
    "style_tags": {"technical": 0.9, "formal": 0.8},
    "sentiment": "positive",
    "language_patterns": ["专业", "详细"],
}
```

---

## ✅ 验收标准

### 功能验收

- [ ] 所有测试场景通过
- [ ] 语义分析结果正确
- [ ] 知识存储正确
- [ ] 个人偏好存储正确
- [ ] 数据检索正常

### 性能验收

- [ ] 单轮对话归档时间 < 5 秒
- [ ] 多轮对话（10 轮）归档时间 < 30 秒
- [ ] 内存使用合理（无泄漏）

### 数据质量验收

- [ ] NER 提取准确率 > 70%
- [ ] KT 提取准确率 > 60%
- [ ] 三元组完整性 > 90%
- [ ] 数据存储成功率 = 100%

---

## 📝 测试报告模板

### 测试执行报告

```markdown
# 测试计划 A 执行报告

**测试日期**: YYYY-MM-DD
**测试环境**: 开发/测试
**测试人员**: XXX
**版本**: v1.0

## 测试概述

## 测试结果

### 场景一：技术咨询对话
- ✅ 对话归档: 通过
- ✅ 语义分析: 通过
- ✅ 知识存储: 通过
- ✅ 个人偏好存储: 通过

### 场景二：业务咨询对话
- ✅ 对话归档: 通过
- ✅ 语义分析: 通过
- ✅ 知识存储: 通过
- ✅ 个人偏好存储: 通过

### 场景三：日常对话
- ✅ 对话归档: 通过
- ✅ 语义分析: 通过
- ✅ 知识存储: 通过
- ✅ 个人偏好存储: 通过

## 语义分析结果验证

### NER 提取
- 场景一: 提取 10 个实体 ✅
- 场景二: 提取 8 个实体 ✅
- 场景三: 提取 2 个实体 ✅

### KE 提取
- 场景一: 提取 5 个知识要点 ✅
- 场景二: 提取 6 个知识要点 ✅
- 场景三: 提取 2 个知识要点 ✅

### KT 提取
- 场景一: 提取 8 个三元组 ✅
- 场景二: 提取 7 个三元组 ✅
- 场景三: 提取 1 个三元组 ✅

## 数据存储验证

### ChromaDB 存储
- 场景一: 3 条知识资产 ✅
- 场景二: 4 条知识资产 ✅
- 场景三: 2 条知识资产 ✅

### PostgreSQL 存储
- 场景一: 用户画像已更新 ✅
- 场景二: 用户画像已更新 ✅
- 场景三: 用户画像已更新 ✅

## 问题清单

无

## 总结

所有测试场景通过，功能正常。
```

---

## 🚀 执行计划

### 阶段一：测试环境准备（1 天）

- [ ] 创建测试数据库配置
- [ ] 准备测试数据
- [ ] 配置测试 Fixture

### 阶段二：测试实现（2-3 天）

- [ ] 实现测试用例
- [ ] 实现测试数据准备
- [ ] 实现验证逻辑

### 阶段三：测试执行（1 天）

- [ ] 执行所有测试场景
- [ ] 记录测试结果
- [ ] 生成测试报告

### 阶段四：问题修复（如需要）

- [ ] 修复发现的问题
- [ ] 重新执行测试
- [ ] 验证修复

---

**最后更新**: 2025-11-12  
**下次审查**: 测试实现完成后

