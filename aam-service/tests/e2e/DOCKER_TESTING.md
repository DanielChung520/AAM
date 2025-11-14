# 在 Docker 容器内运行测试指南

**版本**: v1.0  
**最后更新**: 2025-11-13

---

## 📋 概述

本指南说明如何在 Docker 容器内运行 E2E 测试。这是**推荐的测试方式**，因为：

- ✅ **环境一致**：测试环境 = 运行环境
- ✅ **无端口冲突**：使用 Docker 网络连接数据库（服务名：`chromadb`, `postgres`）
- ✅ **完全隔离**：不影响宿主机环境
- ✅ **依赖统一**：只需维护 Docker 环境

---

## 🚀 快速开始

### 1. 启动 Docker 服务

```bash
# 启动所有服务（包括数据库）
docker-compose -f docker-compose.dev.yml up -d

# 等待服务就绪（约 30-60 秒）
docker-compose -f docker-compose.dev.yml ps
```

### 2. 安装测试依赖（首次运行）

```bash
# 在容器内安装 pytest
docker-compose -f docker-compose.dev.yml exec aam-service pip install pytest pytest-asyncio pytest-cov
```

### 3. 运行测试

```bash
# 运行所有 E2E 测试
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/ -v

# 运行特定测试文件
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/test_gemini_fallback_semantic_analysis.py -v

# 运行特定测试用例
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/test_gemini_fallback_semantic_analysis.py::TestGeminiFallbackSemanticAnalysis::test_gemini_provider_initialization -v

# 运行并显示详细输出
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/ -v -s

# 运行并生成覆盖率报告
docker-compose -f docker-compose.dev.yml exec aam-service pytest tests/e2e/ --cov=src --cov-report=html
```

### 4. 设置环境变量

如果需要设置环境变量（如 API Key），使用 `-e` 参数：

```bash
docker-compose -f docker-compose.dev.yml exec -e GEMINI_API_KEY=your-key aam-service pytest tests/e2e/test_gemini_fallback_semantic_analysis.py -v
```

---

## 🔧 环境检测

测试配置会自动检测运行环境：

- **Docker 容器内**：使用服务名连接数据库
  - ChromaDB: `chromadb:8000`
  - PostgreSQL: `postgres:5432`

- **宿主机**：使用 localhost 和映射端口
  - ChromaDB: `localhost:8001`
  - PostgreSQL: `localhost:5432`

检测逻辑在 `tests/e2e/conftest.py` 的 `is_running_in_docker()` 函数中实现。

---

## 📝 常用命令

### 进入容器

```bash
docker-compose -f docker-compose.dev.yml exec aam-service bash
```

### 查看容器日志

```bash
docker-compose -f docker-compose.dev.yml logs -f aam-service
```

### 重启服务

```bash
docker-compose -f docker-compose.dev.yml restart aam-service
```

### 停止所有服务

```bash
docker-compose -f docker-compose.dev.yml down
```

---

## ⚠️ 注意事项

1. **首次运行**：需要在容器内安装 pytest 依赖
2. **文件同步**：`tests/` 目录已挂载到容器，修改后自动同步
3. **配置文件**：确保 `config/models.json` 在容器内可访问
4. **环境变量**：使用 `-e` 参数传递环境变量

---

## 🐛 故障排查

### 问题：找不到测试文件

**解决**：确保 `tests/` 目录已挂载
```bash
docker-compose -f docker-compose.dev.yml exec aam-service ls -la /app/tests/e2e/
```

### 问题：pytest 未安装

**解决**：安装 pytest
```bash
docker-compose -f docker-compose.dev.yml exec aam-service pip install pytest pytest-asyncio pytest-cov
```

### 问题：数据库连接失败

**解决**：检查服务是否运行
```bash
docker-compose -f docker-compose.dev.yml ps
```

### 问题：环境变量未传递

**解决**：使用 `-e` 参数
```bash
docker-compose -f docker-compose.dev.yml exec -e KEY=value aam-service pytest ...
```

---

## 📚 相关文档

- [测试计划 A 执行指南](./README.md)
- [Docker 环境问题排查](../../docs/Docker环境问题排查.md)
- [Docker 配置说明](../../docker/README.md)

---

**最后更新**: 2025-11-13

