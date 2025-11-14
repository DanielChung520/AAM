# Ollama 配置指南

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: 配置指南

---

## 📋 概述

本指南说明如何在 AAM 项目中配置使用 Ollama 和 deepseek-r1:8b 模型。

---

## ✅ 验证结果

### Ollama 服务状态

- ✅ **Ollama 服务运行中**: API 可访问 (`http://localhost:11434`)
- ✅ **模型已安装**: 
  - `deepseek-r1:8b` (4.9 GB) - **推荐使用**
  - `deepseek-r1:14b` (9.0 GB) - 可选

### 测试结果

- ✅ **API 连接测试**: 通过
- ✅ **文本生成测试**: 通过
- ✅ **模型响应**: 正常（包含 reasoning 过程）

---

## ⚙️ 配置步骤

### 步骤 1: 检查当前配置

当前 `.env` 文件中的配置：
```bash
MODEL_NAME=microsoft/DialoGPT-medium  # 这不是 Ollama 模型
```

### 步骤 2: 修改 .env 文件

在 `.env` 文件中添加或修改以下配置：

```bash
# ============================================
# 统一模型服务配置（推荐使用）
# ============================================
MODEL_PROVIDER_TYPE=ollama
MODEL_NAME=deepseek-r1:8b
MODEL_API_BASE_URL=http://localhost:11434
MODEL_TIMEOUT=120

# ============================================
# Ollama 特定配置（向后兼容）
# ============================================
OLLAMA_MODEL_NAME=deepseek-r1:8b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120
```

### 步骤 3: 验证配置

运行测试脚本验证配置：

```bash
# 测试基础连接
python3 scripts/test_ollama_simple.py --model deepseek-r1:8b

# 测试完整功能（如果项目依赖已安装）
python3 scripts/test_ollama_connection.py --model deepseek-r1:8b --unified
```

---

## 🔍 项目如何调用 Ollama

### 调用流程

```
1. 应用启动 (src/main.py)
   ↓
2. 读取配置 (src/config/settings.py)
   - MODEL_PROVIDER_TYPE=ollama
   - MODEL_NAME=deepseek-r1:8b
   ↓
3. 创建 Provider (src/infrastructure/ai/providers/provider_factory.py)
   - ModelProviderFactory.create_provider()
   - 创建 OllamaProvider
   ↓
4. 创建统一模型服务 (src/infrastructure/ai/unified_model_service.py)
   - UnifiedModelService(provider=provider)
   ↓
5. 实际调用 (src/infrastructure/ai/providers/ollama_provider.py)
   - provider.generate(prompt)
   - 使用 LangChain Ollama.ainvoke()
   ↓
6. Ollama API (http://localhost:11434/api/generate)
   ↓
7. 返回结果
```

### 关键代码

**OllamaProvider** (`src/infrastructure/ai/providers/ollama_provider.py`):
```python
class OllamaProvider(IModelProvider):
    def __init__(self, model_name: str, base_url: str, timeout: int):
        self.llm = Ollama(
            model=model_name,      # deepseek-r1:8b
            base_url=base_url,     # http://localhost:11434
            timeout=timeout,       # 120
        )
    
    async def generate(self, prompt: str) -> str:
        return await self.llm.ainvoke(prompt)
```

---

## 🧪 测试验证

### 测试脚本 1: 简单测试（推荐）

**文件**: `scripts/test_ollama_simple.py`

**优点**: 
- 不依赖项目复杂依赖
- 快速验证 Ollama 连接
- 已测试通过 ✅

**使用方法**:
```bash
# 测试 API 连接
python3 scripts/test_ollama_simple.py --model deepseek-r1:8b --api-only

# 测试文本生成
python3 scripts/test_ollama_simple.py --model deepseek-r1:8b
```

### 测试脚本 2: 完整测试

**文件**: `scripts/test_ollama_connection.py`

**优点**:
- 测试完整的项目集成
- 测试统一模型服务
- 测试知识提取功能

**使用方法**:
```bash
# 基础连接测试
python3 scripts/test_ollama_connection.py --model deepseek-r1:8b

# 完整功能测试（包含知识提取）
python3 scripts/test_ollama_connection.py --model deepseek-r1:8b --unified
```

---

## 📊 配置选项

### 选项 1: 使用 deepseek-r1:8b（推荐）

```bash
MODEL_PROVIDER_TYPE=ollama
MODEL_NAME=deepseek-r1:8b
MODEL_API_BASE_URL=http://localhost:11434
MODEL_TIMEOUT=120
```

**优点**:
- 模型较小（4.9 GB），加载快
- 响应时间较短（10-30 秒）
- 资源消耗较低

### 选项 2: 使用 deepseek-r1:14b

```bash
MODEL_PROVIDER_TYPE=ollama
MODEL_NAME=deepseek-r1:14b
MODEL_API_BASE_URL=http://localhost:11434
MODEL_TIMEOUT=300  # 增加超时时间
```

**优点**:
- 模型更大（9.0 GB），准确度更高
- 适合复杂任务

**缺点**:
- 响应时间较长（30-60 秒）
- 资源消耗较高

---

## 🔧 故障排查

### 问题 1: 模型名称不匹配

**症状**: 初始化失败，提示模型不存在

**解决**:
```bash
# 检查已安装的模型
ollama list

# 如果模型不存在，下载模型
ollama pull deepseek-r1:8b

# 验证模型已下载
ollama list | grep deepseek-r1:8b
```

### 问题 2: API 连接失败

**症状**: `check_available()` 返回 False

**解决**:
```bash
# 检查 Ollama 服务是否运行
curl http://localhost:11434/api/tags

# 如果失败，启动 Ollama 服务
ollama serve

# 或检查进程
ps aux | grep ollama
```

### 问题 3: 超时错误

**症状**: 生成文本时超时

**解决**:
```bash
# 增加超时时间（在 .env 中）
MODEL_TIMEOUT=300  # 增加到 300 秒

# 或使用更小的模型
MODEL_NAME=deepseek-r1:8b  # 而不是 14b
```

---

## ✅ 配置验证清单

### 环境验证

- [x] Ollama 服务运行中
- [x] 模型已下载（deepseek-r1:8b, deepseek-r1:14b）
- [x] API 可访问

### 项目配置

- [ ] `.env` 文件已配置 `MODEL_NAME=deepseek-r1:8b`
- [ ] `.env` 文件已配置 `MODEL_PROVIDER_TYPE=ollama`
- [ ] `.env` 文件已配置 `MODEL_API_BASE_URL=http://localhost:11434`

### 功能验证

- [x] 基础连接测试通过
- [x] 文本生成测试通过
- [ ] 统一模型服务测试通过（需要项目依赖）
- [ ] 知识提取测试通过（需要项目依赖）

---

## 📝 配置示例

### 完整 .env 配置示例

```bash
# ============================================
# 应用配置
# ============================================
APP_NAME=AAM Service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# ============================================
# 统一模型服务配置（Ollama）
# ============================================
MODEL_PROVIDER_TYPE=ollama
MODEL_NAME=deepseek-r1:8b
MODEL_API_BASE_URL=http://localhost:11434
MODEL_TIMEOUT=120

# ============================================
# Ollama 特定配置（向后兼容）
# ============================================
OLLAMA_ENABLED=true
OLLAMA_MODEL_NAME=deepseek-r1:8b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# ============================================
# 数据库配置
# ============================================
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=aam
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ============================================
# 其他配置...
# ============================================
```

---

## 🚀 下一步

### 立即行动

1. **修改 .env 文件**
   ```bash
   # 添加或修改以下配置
   MODEL_PROVIDER_TYPE=ollama
   MODEL_NAME=deepseek-r1:8b
   MODEL_API_BASE_URL=http://localhost:11434
   ```

2. **重启 AAM 服务**
   ```bash
   # 如果服务正在运行，重启以加载新配置
   docker-compose restart aam-service
   # 或
   # 停止并重新启动服务
   ```

3. **验证配置生效**
   - 检查启动日志，确认 Ollama Provider 初始化成功
   - 运行测试计划 A，使用真实模型进行测试

---

## 📚 相关文档

- [Ollama 调用验证报告](Ollama調用驗證報告.md)
- [测试计划 A](測試計劃A：對話歸檔流程端到端測試.md)
- [整合测试计划](整合測試計劃.md)

---

**最后更新**: 2025-11-12  
**状态**: ✅ Ollama 可以正常使用，需要配置模型名称

