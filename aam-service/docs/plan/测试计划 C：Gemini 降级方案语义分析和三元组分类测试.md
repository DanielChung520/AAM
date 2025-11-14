<!-- b53cbfdc-d01e-411d-aaee-3b7cf359468c b0623b87-7edc-499c-b0e5-797976f504dc -->
# 测试计划 C：Gemini 降级方案语义分析和三元组分类测试

**创建日期**: 2025-11-13

**版本**: v1.0

**状态**: 规划中

**基准文档**:

- `测试计划A：對話歸檔流程端到端測試.md`
- `测试计划B：Qwen Provider和降級策略測試.md`
- `LLM_Provider配置指南.md`

---

## 📋 测试概述

### 测试目标

验证使用 Gemini Provider 作为降级方案进行语义分析和三元组分类的完整功能，包括：

1. **Gemini Provider 降级使用**: 验证 Gemini 作为 LLM 抽象层（优先级 3）的降级功能
2. **语义分析**: 验证使用 Gemini 进行 NER、KE、KT 提取
3. **三元组分类**: 验证使用 Gemini 进行三元组分类标签
4. **知识存储**: 验证使用 Gemini 提取的知识资产存储到 ChromaDB
5. **个人偏好存储**: 验证使用 Gemini 分析的用户画像存储到 PostgreSQL
6. **数据质量**: 验证 Gemini 提取结果的质量和完整性

### 测试范围

| 测试项 | 描述 | 优先级 |

|--------|------|--------|

| **Gemini Provider 降级功能** | 验证 Gemini 作为降级方案的正确性 | 🔴 高 |

| **语义分析（NER、KE、KT）** | 验证使用 Gemini 进行语义提取 | 🔴 高 |

| **三元组分类** | 验证使用 Gemini 进行三元组分类标签 | 🔴 高 |

| **知识存储** | ChromaDB 存储验证 | 🔴 高 |

| **个人偏好存储** | PostgreSQL 存储验证 | 🔴 高 |

| **数据质量评估** | 验证 Gemini 提取结果的质量 | 🟡 中 |

| **性能测试** | 验证 Gemini 响应时间和性能 | 🟡 中 |

---

## 🎯 测试场景设计

### 场景一：Gemini 作为唯一可用模型（直接使用）

**场景描述**: EB-mM 和 Ollama 本地模型都不可用，直接使用 Gemini 作为 LLM 抽象层

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
- **三元组分类**: 技术类、教育类、工具类
- **个人偏好**: 技术导向、学习型、正式风格

---

### 场景二：Gemini 作为降级方案（质量不达标降级）

**场景描述**: EB-mM 质量不达标，降级到 Gemini

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
```

**预期提取结果**:

- **NER**: AI 项目, Spark, Hadoop HDFS, GPU, 数据科学家
- **KE**: AI 项目实施步骤、大数据处理方案、AI 项目预算构成
- **KT**:
  - (AI 项目, 需要, 明确业务目标)
  - (大数据量, 处理方案, 分布式计算)
  - (Spark, 是, 分布式计算框架)
  - (AI 项目, 预算范围, 10-100万)
- **三元组分类**: 业务类、技术类、管理类
- **个人偏好**: 业务导向、决策型、正式风格、积极情感

---

### 场景三：Gemini 三元组分类专项测试

**场景描述**: 重点测试 Gemini 进行三元组分类的准确性和完整性

**测试数据**: 包含多种类型的三元组

- 技术类: (Python, 是, 编程语言)
- 教育类: (Python, 用于, 学习编程)
- 工具类: (Django, 是, Web 框架)
- 人物类: (Guido van Rossum, 创建, Python)
- 关系类: (Python, 支持, 机器学习)

**预期结果**:

- 所有三元组都能正确分类
- 分类标签符合预定义分类体系
- 分类准确率 > 80%

---

## 📝 测试步骤

### 步骤 1: 准备测试环境

1. [ ] 配置 Gemini Provider（设置 GEMINI_API_KEY）
2. [ ] 配置降级策略（禁用 EB-mM 和 Ollama 本地模型，只使用 Gemini）
3. [ ] 启动测试数据库（ChromaDB、PostgreSQL）
4. [ ] 初始化测试数据（清空测试数据库）
5. [ ] 验证 Gemini Provider 可用性

### 步骤 2: 测试 Gemini Provider 基础功能

1. [ ] **测试 Gemini Provider 初始化**

   - 验证使用模型配置文件中的配置
   - 验证默认 max_tokens 和 temperature 参数

2. [ ] **测试 Gemini Provider 文本生成**

   - 验证简单文本生成
   - 验证使用配置中的默认参数

3. [ ] **测试 Gemini Provider 可用性检查**

   - 验证 check_available() 方法

### 步骤 3: 测试语义分析（使用 Gemini）

对于每个测试场景：

1. [ ] **执行知识提取**

   - 调用 `UnifiedModelService.extract_knowledge()`（使用 Gemini Provider）
   - 验证方法执行成功（无异常）

2. [ ] **验证 NER 提取**

   - 验证实体数量 > 0
   - 验证实体类型正确
   - 验证实体内容准确

3. [ ] **验证 KE 提取**

   - 验证知识要点数量 > 0
   - 验证知识要点内容相关

4. [ ] **验证 KT 提取**

   - 验证三元组数量 > 0
   - 验证三元组完整性（subject, predicate, object）
   - 验证三元组合理性

### 步骤 4: 测试三元组分类（使用 Gemini）

1. [ ] **执行三元组分类**

   - 调用 `TripleClassifier.classify_triples()`（使用 Gemini Provider）
   - 验证分类执行成功

2. [ ] **验证分类结果**

   - 验证每个三元组都有 category 字段
   - 验证分类标签符合预定义分类体系
   - 验证分类准确率

3. [ ] **验证分类质量**

   - 验证技术类三元组正确分类
   - 验证教育类三元组正确分类
   - 验证其他类别三元组正确分类

### 步骤 5: 测试降级策略（使用 Gemini）

1. [ ] **测试直接使用 Gemini**

   - 配置：EB-mM 禁用，Ollama 本地模型禁用
   - 验证直接使用 Gemini 作为 LLM 抽象层

2. [ ] **测试质量不达标降级到 Gemini**

   - 配置：EB-mM 质量不达标（Mock 低质量结果）
   - 验证降级到 Gemini
   - 验证 Gemini 提取结果质量

3. [ ] **测试异常情况降级到 Gemini**

   - 配置：EB-mM 抛出异常
   - 验证降级到 Gemini
   - 验证 Gemini 正常处理

### 步骤 6: 验证知识存储

1. [ ] **验证知识存储到 ChromaDB**

   - 查询 ChromaDB，验证知识资产已存储
   - 验证存储的元数据正确（user_id, session_id, entities, triples_json）
   - 验证向量已生成
   - 验证文档内容正确
   - 验证三元组分类标签已存储

2. [ ] **验证个人偏好存储到 PostgreSQL**

   - 查询 PostgreSQL，验证用户画像已存储/更新
   - 验证 style_tags 正确
   - 验证 sentiment 正确
   - 验证 language_patterns 正确

### 步骤 7: 验证数据质量

1. [ ] **验证 NER 提取质量**

   - 计算 NER 提取准确率
   - 验证实体类型多样性
   - 验证实体置信度

2. [ ] **验证 KT 提取质量**

   - 计算 KT 提取准确率
   - 验证三元组完整性
   - 验证三元组合理性

3. [ ] **验证三元组分类质量**

   - 计算分类准确率
   - 验证分类标签正确性
   - 验证分类覆盖率

---

## 🧪 测试实现

### 测试文件结构

```
tests/e2e/
├── test_gemini_fallback_semantic_analysis.py    # 主要测试文件
├── fixtures/
│   ├── dialogue_scenarios.py                    # 对话场景数据
│   └── expected_results_gemini.py              # Gemini 预期结果
└── conftest.py                                  # E2E 测试配置
```

### 测试用例设计

#### 测试用例 1: Gemini 直接使用场景

```python
@pytest.mark.e2e
@pytest.mark.gemini
async def test_gemini_direct_usage_semantic_analysis(
    memory_service_with_gemini,
    knowledge_store,
    persona_store,
):
    """测试直接使用 Gemini 进行语义分析"""
    # 1. 配置：只使用 Gemini（禁用其他模型）
    # 2. 执行对话归档
    # 3. 验证语义分析结果
    # 4. 验证三元组分类
    # 5. 验证数据存储
```

#### 测试用例 2: Gemini 降级场景

```python
@pytest.mark.e2e
@pytest.mark.gemini
async def test_gemini_fallback_scenario(
    memory_service_with_fallback,
    knowledge_store,
):
    """测试 Gemini 作为降级方案"""
    # 1. 配置：EB-mM 质量不达标
    # 2. 验证降级到 Gemini
    # 3. 验证 Gemini 提取结果
    # 4. 验证数据质量
```

#### 测试用例 3: Gemini 三元组分类专项测试

```python
@pytest.mark.e2e
@pytest.mark.gemini
async def test_gemini_triple_classification(
    gemini_provider,
    triple_classifier,
):
    """测试 Gemini 进行三元组分类"""
    # 1. 准备测试三元组
    # 2. 执行分类
    # 3. 验证分类结果
    # 4. 验证分类准确率
```

#### 测试用例 4: Gemini 完整对话归档流程

```python
@pytest.mark.e2e
@pytest.mark.gemini
async def test_gemini_complete_dialogue_archive(
    memory_service_with_gemini,
    knowledge_store,
    persona_store,
):
    """测试使用 Gemini 的完整对话归档流程"""
    # 1. 执行多轮对话归档
    # 2. 验证语义分析
    # 3. 验证三元组分类
    # 4. 验证知识存储
    # 5. 验证个人偏好存储
```

---

## 📊 验证点清单

### Gemini Provider 验证

- [ ] **Provider 初始化验证**
  - 使用模型配置文件中的配置
  - 默认 max_tokens = 8192
  - 默认 temperature = 0.5

- [ ] **文本生成验证**
  - 能够成功生成文本
  - 响应格式正确
  - 错误处理正确

### 语义分析验证

- [ ] **NER 提取验证**
  - 实体数量 > 0
  - 实体类型正确（人名、地名、组织名、产品名等）
  - 实体内容准确
  - NER 提取准确率 > 70%

- [ ] **KE 提取验证**
  - 知识要点数量 > 0
  - 知识要点内容相关
  - 知识要点格式正确

- [ ] **KT 提取验证**
  - 三元组数量 > 0
  - 三元组完整性（subject, predicate, object）
  - 三元组合理性
  - 三元组 JSON 格式正确
  - KT 提取准确率 > 60%

### 三元组分类验证

- [ ] **分类执行验证**
  - 所有三元组都能分类
  - 分类过程无异常

- [ ] **分类结果验证**
  - 每个三元组都有 category 字段
  - 分类标签符合预定义分类体系
  - 分类准确率 > 80%

- [ ] **分类质量验证**
  - 技术类三元组正确分类
  - 教育类三元组正确分类
  - 工具类三元组正确分类
  - 其他类别三元组正确分类

### 降级策略验证

- [ ] **直接使用 Gemini**
  - 能够直接使用 Gemini
  - 提取结果质量符合预期

- [ ] **降级到 Gemini**
  - 降级逻辑正确
  - 降级后 Gemini 正常工作
  - 提取结果质量符合预期

### 知识存储验证

- [ ] **ChromaDB 存储验证**
  - 知识资产已存储
  - 向量已生成
  - 元数据正确（包含三元组分类标签）
  - 文档内容正确

- [ ] **PostgreSQL 存储验证**
  - 用户画像已存储/更新
  - style_tags 正确
  - sentiment 正确
  - language_patterns 正确

---

## 🔧 测试环境要求

### 必需服务

1. **Gemini API**

   - 有效的 GEMINI_API_KEY
   - 网络连接（访问 Google Gemini API）

2. **ChromaDB**

   - 测试数据库实例
   - 独立的 collection（测试隔离）

3. **PostgreSQL**

   - 测试数据库实例
   - 独立的 schema（测试隔离）

### 配置要求

```env
# .env 文件配置
LLM_LAYER_PROVIDER_TYPE=gemini
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-2.5-flash  # 或从 config/models.json 获取
GEMINI_TIMEOUT=120

# 降级策略配置（测试场景）
EB_MM_ENABLED=false  # 禁用 EB-mM
OLLAMA_LOCAL_MODEL_ENABLED=false  # 禁用 Ollama 本地模型
QUALITY_EVALUATION_ENABLED=true
QUALITY_THRESHOLD=0.7
```

---

## 📈 测试数据准备

### 对话场景数据

**文件**: `tests/e2e/fixtures/dialogue_scenarios.py`

```python
GEMINI_TECHNICAL_DIALOGUES = [
    {
        "dialog_id": "gemini_tech_dialog_001",
        "user_id": "user_gemini_001",
        "turn": 1,
        "user_query": "什么是 Python？",
        "ai_response": "Python 是一种高级编程语言...",
    },
    # ... 更多轮次
]

GEMINI_BUSINESS_DIALOGUES = [
    # ... 业务咨询对话
]

GEMINI_TRIPLE_CLASSIFICATION_TEST_DATA = [
    {
        "subject": "Python",
        "predicate": "是",
        "object": "编程语言",
        "expected_category": "技术类"
    },
    # ... 更多测试三元组
]
```

### 预期结果数据

**文件**: `tests/e2e/fixtures/expected_results_gemini.py`

```python
EXPECTED_NER_GEMINI = [
    "Python",
    "Guido van Rossum",
    "Django",
    # ...
]

EXPECTED_KT_GEMINI = [
    {"subject": "Python", "predicate": "创建者", "object": "Guido van Rossum"},
    {"subject": "Python", "predicate": "用于", "object": "Web 开发"},
    # ...
]

EXPECTED_TRIPLE_CLASSIFICATIONS = {
    "技术类": [
        {"subject": "Python", "predicate": "是", "object": "编程语言"},
        # ...
    ],
    "教育类": [
        # ...
    ],
    # ...
}
```

---

## ✅ 验收标准

### 功能验收

- [ ] Gemini Provider 能够正常初始化和使用
- [ ] 语义分析（NER、KE、KT）功能正常
- [ ] 三元组分类功能正常
- [ ] 降级策略正确使用 Gemini
- [ ] 知识存储正确
- [ ] 个人偏好存储正确

### 质量验收

- [ ] NER 提取准确率 > 70%
- [ ] KT 提取准确率 > 60%
- [ ] 三元组分类准确率 > 80%
- [ ] 三元组完整性 > 90%
- [ ] 数据存储成功率 = 100%

### 性能验收

- [ ] 单轮对话归档时间 < 10 秒（Gemini API 响应时间）
- [ ] 多轮对话（10 轮）归档时间 < 60 秒
- [ ] 三元组分类时间 < 5 秒/个
- [ ] 内存使用合理（无泄漏）

---

## 📝 测试报告模板

### 测试执行报告

```markdown
# 测试计划 C 执行报告

**测试日期**: YYYY-MM-DD
**测试环境**: 开发/测试
**测试人员**: XXX
**版本**: v1.0

## 测试概述

## 测试结果

### 场景一：Gemini 直接使用
- ✅ Gemini Provider 初始化: 通过
- ✅ 语义分析: 通过
- ✅ 三元组分类: 通过
- ✅ 知识存储: 通过
- ✅ 个人偏好存储: 通过

### 场景二：Gemini 降级场景
- ✅ 降级逻辑: 通过
- ✅ 语义分析: 通过
- ✅ 三元组分类: 通过
- ✅ 数据质量: 通过

### 场景三：三元组分类专项测试
- ✅ 分类执行: 通过
- ✅ 分类准确率: XX%
- ✅ 分类质量: 通过

## 语义分析结果验证

### NER 提取
- 场景一: 提取 X 个实体 ✅
- 场景二: 提取 X 个实体 ✅
- 准确率: XX% ✅

### KE 提取
- 场景一: 提取 X 个知识要点 ✅
- 场景二: 提取 X 个知识要点 ✅

### KT 提取
- 场景一: 提取 X 个三元组 ✅
- 场景二: 提取 X 个三元组 ✅
- 准确率: XX% ✅

## 三元组分类结果验证

### 分类准确率
- 技术类: XX% ✅
- 教育类: XX% ✅
- 工具类: XX% ✅
- 总体准确率: XX% ✅

## 数据存储验证

### ChromaDB 存储
- 场景一: X 条知识资产 ✅
- 场景二: X 条知识资产 ✅
- 三元组分类标签: 已存储 ✅

### PostgreSQL 存储
- 场景一: 用户画像已更新 ✅
- 场景二: 用户画像已更新 ✅

## 性能数据

- 平均响应时间: X 秒
- 三元组分类时间: X 秒/个
- 内存使用: X MB

## 问题清单

无

## 总结

所有测试场景通过，Gemini 作为降级方案能够完成语义分析和三元组分类目标。
```

---

## 🚀 执行计划

### 阶段一：测试环境准备（1 天）

- [ ] 配置 Gemini Provider（API Key、模型配置）
- [ ] 配置降级策略（禁用其他模型，只使用 Gemini）
- [ ] 准备测试数据
- [ ] 配置测试 Fixture

### 阶段二：测试实现（2-3 天）

- [ ] 实现测试用例
- [ ] 实现测试数据准备
- [ ] 实现验证逻辑
- [ ] 实现质量评估逻辑

### 阶段三：测试执行（1-2 天）

- [ ] 执行所有测试场景
- [ ] 记录测试结果
- [ ] 生成测试报告

### 阶段四：问题修复（如需要）

- [ ] 修复发现的问题
- [ ] 重新执行测试
- [ ] 验证修复

---

## 📚 相关文档

- [测试计划 A：对话归档流程端到端测试](測試計劃A：對話歸檔流程端到端測試.md)
- [测试计划 B：Qwen Provider和降級策略測試](測試計劃B-Qwen Provider和降級策略測試.md)
- [LLM Provider 配置指南](../../LLM_Provider配置指南.md)
- [三元组分类标签与教育学习测试实施计划](../../三元组分类标签与教育学习测试实施计划.md)

---

**最后更新**: 2025-11-13

**下次审查**: 测试实现完成后

### To-dos

- [ ] 配置测试环境：设置 Gemini Provider 和降级策略配置
- [ ] 创建测试文件：test_gemini_fallback_semantic_analysis.py
- [ ] 准备测试数据：对话场景和预期结果数据
- [ ] 实现测试用例1：Gemini 直接使用场景的语义分析测试
- [ ] 实现测试用例2：Gemini 降级场景测试
- [ ] 实现测试用例3：Gemini 三元组分类专项测试
- [ ] 实现测试用例4：Gemini 完整对话归档流程测试
- [ ] 执行所有测试并记录结果
- [ ] 生成测试报告