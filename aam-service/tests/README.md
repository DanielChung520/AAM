# AAM 系统测试指南

**版本**: v1.0  
**最后更新**: 2025-11-12

---

## 📋 测试概述

AAM 系统的测试分为以下几个层次：

1. **单元测试 (Unit Tests)**: 测试单个组件/函数
2. **整合测试 (Integration Tests)**: 测试组件之间的集成
3. **端到端测试 (E2E Tests)**: 测试完整业务流程
4. **性能测试 (Performance Tests)**: 测试系统性能
5. **压力测试 (Stress Tests)**: 测试系统在高负载下的表现
6. **容错测试 (Resilience Tests)**: 测试系统容错能力

---

## 🚀 快速开始

### 前置要求

1. **Python 3.11+**
2. **Docker & Docker Compose** (用于整合测试)
3. **测试依赖**:
   ```bash
   pip install -r requirements-test.txt
   ```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行并显示覆盖率
pytest --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

---

## 📁 测试目录结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_mcp_controller.py
│   ├── test_memory_service.py
│   └── ...
├── integration/             # 整合测试
│   ├── test_mcp_api.py
│   ├── test_smartq_integration.py
│   ├── test_eb_mm_integration.py
│   └── ...
├── e2e/                     # 端到端测试（待创建）
│   └── test_user_query_flow.py
├── performance/             # 性能测试（待创建）
│   └── test_api_performance.py
├── stress/                  # 压力测试（待创建）
│   └── test_high_load.py
├── resilience/              # 容错测试（待创建）
│   └── test_service_unavailable.py
├── conftest.py             # 测试配置和 Fixture
└── README.md               # 本文件
```

---

## 🧪 测试类型详解

### 1. 单元测试

**位置**: `tests/unit/`

**目的**: 测试单个组件/函数的正确性

**特点**:
- 快速执行
- 不依赖外部服务
- 使用 Mock 隔离依赖

**运行方式**:
```bash
# 运行所有单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_memory_service.py

# 运行特定测试用例
pytest tests/unit/test_memory_service.py::TestMemoryService::test_enrich
```

**示例**:
```python
# tests/unit/test_memory_service.py
def test_enrich_with_knowledge(mock_knowledge_store, mock_persona_store):
    """测试记忆丰富化功能"""
    service = MemoryServiceImpl(...)
    result = await service.enrich(mcp)
    assert result.retrieved_knowledge.docs is not None
```

---

### 2. 整合测试

**位置**: `tests/integration/`

**目的**: 测试组件之间的集成

**特点**:
- 可能需要外部服务（数据库、消息队列等）
- 使用真实服务或 Mock
- 测试组件间的交互

**运行方式**:
```bash
# 运行所有整合测试
pytest -m integration

# 运行需要数据库的整合测试
pytest -m "integration and database"

# 运行需要真实服务的整合测试
pytest -m "integration and real_service"
```

**测试标记**:
- `@pytest.mark.integration` - 整合测试
- `@pytest.mark.database` - 需要数据库
- `@pytest.mark.model_service` - 需要模型服务
- `@pytest.mark.external` - 需要外部服务
- `@pytest.mark.real_service` - 需要真实服务（非 Mock）

**示例**:
```python
# tests/integration/test_mcp_api.py
@pytest.mark.integration
class TestMCPAPIIntegration:
    def test_enrich_endpoint_success(self, client):
        """测试 MCP API 端点"""
        response = client.post("/v1/mcp/enrich", ...)
        assert response.status_code == 200
```

---

### 3. 端到端测试 (E2E)

**位置**: `tests/e2e/` (待创建)

**目的**: 测试完整业务流程

**特点**:
- 需要完整的测试环境（所有服务运行）
- 测试真实业务流程
- 执行时间较长

**运行方式**:
```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行 E2E 测试
pytest -m e2e

# 清理测试环境
docker-compose -f docker-compose.test.yml down
```

**示例**:
```python
# tests/e2e/test_user_query_flow.py
@pytest.mark.e2e
class TestUserQueryFlow:
    async def test_user_query_with_memory_retrieval(self, test_environment):
        """测试用户查询流程"""
        # 1. 准备测试数据
        # 2. 发送用户查询
        # 3. 验证响应
        pass
```

---

### 4. 性能测试

**位置**: `tests/performance/` (待创建)

**目的**: 测试系统性能指标

**特点**:
- 测试响应时间、吞吐量等
- 可能需要长时间运行
- 生成性能报告

**运行方式**:
```bash
# 运行性能测试
pytest -m performance

# 运行性能测试并生成报告
pytest -m performance --benchmark-only
```

**示例**:
```python
# tests/performance/test_api_performance.py
@pytest.mark.performance
class TestAPIPerformance:
    async def test_enrich_api_response_time(self, client):
        """测试 API 响应时间"""
        times = []
        for _ in range(100):
            start = time.time()
            response = client.post("/v1/mcp/enrich", ...)
            times.append(time.time() - start)
        
        p95 = np.percentile(times, 95)
        assert p95 < 0.5  # P95 < 500ms
```

---

### 5. 压力测试

**位置**: `tests/stress/` (待创建)

**目的**: 测试系统在高负载下的表现

**特点**:
- 高并发请求
- 长时间运行
- 监控资源使用

**运行方式**:
```bash
# 运行压力测试
pytest -m stress

# 使用 Locust 进行压力测试
locust -f tests/stress/locustfile.py
```

---

### 6. 容错测试

**位置**: `tests/resilience/` (待创建)

**目的**: 测试系统容错和恢复能力

**特点**:
- 模拟服务故障
- 测试降级策略
- 测试恢复能力

**运行方式**:
```bash
# 运行容错测试
pytest -m resilience
```

---

## 🛠️ 测试环境设置

### 开发环境测试

**使用 Mock**: 快速执行，不依赖外部服务

```bash
# 运行使用 Mock 的测试
pytest -m "not real_service"
```

### 整合测试环境

**使用 Docker Compose**: 启动所有必要的服务

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行整合测试
pytest -m integration

# 清理测试环境
docker-compose -f docker-compose.test.yml down -v
```

### 真实服务测试

**使用真实服务**: 需要真实的服务运行

```bash
# 设置环境变量
export SMARTQ_SERVICE_URL=http://localhost:8001
export AAM_SERVICE_URL=http://localhost:8000

# 运行真实服务测试
pytest -m "integration and real_service"
```

---

## 📊 测试覆盖率

### 查看覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 查看 HTML 报告
open htmlcov/index.html

# 查看终端报告
# 覆盖率信息会显示在终端
```

### 覆盖率目标

- **单元测试**: > 85%
- **整合测试**: > 70%
- **总体覆盖率**: > 80%

---

## 🔧 测试配置

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
markers =
    unit: 单元测试
    integration: 整合测试
    e2e: 端到端测试
    performance: 性能测试
    stress: 压力测试
    resilience: 容错测试
    database: 需要数据库
    model_service: 需要模型服务
    external: 需要外部服务
    real_service: 需要真实服务
```

### conftest.py

**位置**: `tests/conftest.py`

**用途**: 定义全局 Fixture 和测试配置

**示例**:
```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def test_settings():
    """测试配置"""
    return {
        "api_key": "test-key",
        "chromadb_host": "localhost",
        "postgres_host": "localhost",
    }
```

---

## 📝 测试最佳实践

### 1. 测试命名

```python
# 好的命名
def test_enrich_with_knowledge_retrieval():
    """测试带知识检索的丰富化功能"""
    pass

# 不好的命名
def test1():
    pass
```

### 2. 测试组织

```python
# 使用类组织相关测试
class TestMemoryService:
    """记忆服务测试"""
    
    def test_enrich(self):
        """测试丰富化功能"""
        pass
    
    def test_archive(self):
        """测试归档功能"""
        pass
```

### 3. 使用 Fixture

```python
# 好的做法：使用 Fixture
def test_enrich(mock_knowledge_store, mock_persona_store):
    service = MemoryServiceImpl(mock_knowledge_store, mock_persona_store)
    result = await service.enrich(mcp)
    assert result is not None

# 不好的做法：在测试中创建依赖
def test_enrich():
    store = Mock()  # 不应该在测试中创建
    service = MemoryServiceImpl(store)
    ...
```

### 4. 测试隔离

```python
# 每个测试应该是独立的
def test_enrich_1():
    """测试 1"""
    # 不应该依赖 test_enrich_2 的执行结果
    pass

def test_enrich_2():
    """测试 2"""
    # 不应该依赖 test_enrich_1 的执行结果
    pass
```

### 5. 使用 Mock

```python
# 好的做法：使用 Mock 隔离外部依赖
@patch('src.infrastructure.ai.ollama_provider.OllamaProvider.generate')
def test_eb_mm_extraction(mock_generate):
    mock_generate.return_value = '{"entities": ["Python"]}'
    result = await eb_mm.extract_knowledge("text", "user", "session")
    assert "Python" in result.entities
```

---

## 🐛 调试测试

### 运行单个测试

```bash
# 运行特定测试
pytest tests/unit/test_memory_service.py::TestMemoryService::test_enrich

# 运行并显示详细输出
pytest -v -s tests/unit/test_memory_service.py::TestMemoryService::test_enrich
```

### 使用调试器

```python
# 在测试中使用 pdb
def test_enrich():
    import pdb; pdb.set_trace()
    result = await service.enrich(mcp)
    assert result is not None
```

### 查看测试输出

```bash
# 显示 print 输出
pytest -s

# 显示详细输出
pytest -v

# 显示最详细输出
pytest -vv
```

---

## 📈 持续集成 (CI)

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## 📚 参考文档

- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [整合测试计划](../docs/plan/整合測試計劃.md)
- [测试报告](../tests/reports/)

---

## ❓ 常见问题

### Q: 如何跳过某些测试？

A: 使用 `pytest.skip()` 或标记:

```python
@pytest.mark.skip(reason="需要真实服务")
def test_real_service():
    pass

# 或使用条件跳过
def test_real_service():
    if not os.getenv("REAL_SERVICE_URL"):
        pytest.skip("需要设置 REAL_SERVICE_URL")
```

### Q: 如何运行特定标记的测试？

A: 使用 `-m` 选项:

```bash
# 运行所有整合测试
pytest -m integration

# 运行需要数据库的测试
pytest -m database

# 运行不需要真实服务的测试
pytest -m "not real_service"
```

### Q: 测试执行太慢怎么办？

A: 
1. 使用 Mock 替代真实服务
2. 并行运行测试: `pytest -n auto`
3. 只运行相关测试: `pytest tests/unit/`

### Q: 如何测试异步代码？

A: 使用 `pytest-asyncio`:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

---

**最后更新**: 2025-11-12

