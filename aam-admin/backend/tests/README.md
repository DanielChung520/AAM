# 后端测试说明

## 测试框架

- **pytest**: Python 测试框架
- **pytest-asyncio**: 异步测试支持
- **TestClient**: FastAPI 测试客户端

## 运行测试

### 运行所有测试

```bash
cd backend
pytest
```

### 运行特定测试文件

```bash
pytest tests/test_security_routes.py
```

### 运行特定测试类

```bash
pytest tests/test_security_routes.py::TestSecurityRoutes
```

### 运行特定测试方法

```bash
pytest tests/test_security_routes.py::TestSecurityRoutes::test_list_tokens
```

### 显示详细输出

```bash
pytest -v
```

### 显示覆盖率

```bash
pytest --cov=src --cov-report=html
```

## 测试结构

```
tests/
├── __init__.py
├── conftest.py              # pytest 配置和 fixtures
├── test_token_management_service.py  # Token 管理服务测试
├── test_security_routes.py  # 安全管理路由测试
├── test_dashboard_routes.py # 仪表盘路由测试
├── test_llm_provider_routes.py  # LLM Provider 路由测试
├── test_service_routes.py  # 服务管理路由测试
└── test_logs_routes.py     # 日志管理路由测试
```

## Fixtures

- `db_session`: 测试数据库会话
- `client`: FastAPI 测试客户端
- `test_user`: 测试用户
- `test_token`: 测试 JWT Token
- `authenticated_client`: 已认证的测试客户端
- `mock_docker_client`: 模拟的 Docker 客户端

## 注意事项

1. 测试使用 SQLite 内存数据库，不会影响实际数据库
2. 每个测试函数都会创建新的数据库会话
3. 测试完成后会自动清理数据库

