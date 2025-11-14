# Ollama 本地模型集成指南

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: ✅ 已实现

---

## 📋 概述

本指南说明如何在 AAM Service 中集成和使用 Ollama 本地模型进行语义分析。

### 为什么选择 Ollama？

1. **完全本地化**: 不需要外部 API，数据隐私更好
2. **零成本**: 除了硬件成本，无 API 调用费用
3. **离线运行**: 可以完全离线工作
4. **易于部署**: 简单的 Docker 容器或本地安装
5. **模型丰富**: 支持多种开源模型（Llama 3, Mistral, Qwen 等）

---

## 🚀 快速开始

### 1. 安装 Ollama

#### macOS / Linux

```bash
# 使用官方安装脚本
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows

下载并安装：https://ollama.com/download/windows

#### Docker（推荐用于生产环境）

```bash
# 拉取 Ollama Docker 镜像
docker pull ollama/ollama

# 运行 Ollama 容器
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### 2. 下载模型

```bash
# 下载 Llama 3（推荐，约 4.7GB）
ollama pull llama3

# 或下载其他模型
ollama pull mistral      # Mistral 7B
ollama pull qwen2.5      # Qwen 2.5
ollama pull gemma2       # Gemma 2
```

### 3. 验证安装

```bash
# 测试 Ollama 是否运行
curl http://localhost:11434/api/tags

# 测试模型
ollama run llama3 "Hello, how are you?"
```

---

## ⚙️ 配置 AAM Service

### 1. 更新环境变量

编辑 `.env` 文件，添加以下配置：

```bash
# ============================================
# Ollama 配置
# ============================================
OLLAMA_ENABLED=true
OLLAMA_MODEL_NAME=llama3
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# 如果 Ollama 运行在 Docker 容器中，使用容器名称
# OLLAMA_BASE_URL=http://ollama:11434
```

### 2. 更新 Docker Compose（可选）

如果要在 Docker Compose 中运行 Ollama，更新 `docker-compose.dev.yml`：

```yaml
services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - aam-network-dev
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  aam-service:
    # ... 其他配置 ...
    depends_on:
      ollama:
        condition: service_healthy
      # ... 其他依赖 ...

volumes:
  ollama_data:
  # ... 其他卷 ...

networks:
  aam-network-dev:
    driver: bridge
```

### 3. 安装依赖

```bash
# 安装 LangChain Ollama 支持
pip install langchain-community
```

更新 `requirements.txt`：

```txt
# AI/ML 相關
transformers>=4.35.0,<5.0.0
torch>=2.1.0
sentence-transformers>=2.2.2,<3.0.0
peft>=0.7.0
numpy>=1.24.0,<2.0.0

# LangChain 支持
langchain>=0.1.0
langchain-community>=0.0.20
langchain-core>=0.1.0
```

---

## 🔧 使用方式

### 方式一：作为降级策略的 LLM 层

在 `FallbackAnalysisModel` 中，Ollama 可以作为优先级 3（最后保障）的 LLM 层：

```python
from src.infrastructure.ai.ollama_analysis_model import OllamaAnalysisModel
from src.infrastructure.ai.fallback_analysis_model import FallbackAnalysisModel

# 创建 Ollama 模型实例
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

### 方式二：直接使用（开发阶段）

在开发阶段，可以直接使用 Ollama 替换 Mock 模型：

```python
from src.infrastructure.ai.ollama_analysis_model import OllamaAnalysisModel

# 在 main.py 中
ollama_model = OllamaAnalysisModel(
    model_name=settings.ai.ollama_model_name,
    base_url=settings.ai.ollama_base_url,
)

# 注入到 MemoryService
memory_service = MemoryServiceImpl(
    knowledge_store=knowledge_store,
    persona_store=persona_store,
    analysis_model=ollama_model,  # 使用 Ollama 模型
)
```

---

## 📊 性能优化

### 1. 模型选择

| 模型 | 大小 | 速度 | 质量 | 推荐场景 |
|------|------|------|------|----------|
| llama3:8b | ~4.7GB | 快 | 高 | 推荐，平衡性能和质量 |
| llama3:70b | ~40GB | 慢 | 很高 | 高质量要求 |
| mistral | ~4.1GB | 快 | 高 | 快速响应 |
| qwen2.5 | ~4.4GB | 快 | 高 | 中文优化 |
| gemma2 | ~5.4GB | 快 | 中高 | 轻量级 |

### 2. 硬件要求

**最低要求**:
- CPU: 4 核
- RAM: 8GB
- 存储: 10GB（用于模型）

**推荐配置**:
- CPU: 8 核+
- RAM: 16GB+
- GPU: NVIDIA GPU（可选，显著提升性能）
- 存储: 50GB+（用于多个模型）

### 3. 性能调优

```bash
# 使用 GPU（如果可用）
export OLLAMA_NUM_GPU=1

# 设置并发数
export OLLAMA_NUM_PARALLEL=4

# 设置上下文窗口大小
export OLLAMA_CONTEXT_SIZE=4096
```

---

## 🐛 故障排查

### 问题 1: Ollama 服务不可用

**症状**: `RuntimeError: Ollama 服務不可用`

**解决方案**:
```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果未运行，启动 Ollama
ollama serve

# 或使用 Docker
docker start ollama
```

### 问题 2: 模型未找到

**症状**: `Model not found`

**解决方案**:
```bash
# 列出已安装的模型
ollama list

# 下载模型
ollama pull llama3
```

### 问题 3: 响应超时

**症状**: `Timeout` 错误

**解决方案**:
1. 增加超时时间（`.env` 中设置 `OLLAMA_TIMEOUT=300`）
2. 使用更小的模型（如 `llama3:8b` 而不是 `llama3:70b`）
3. 检查硬件资源（CPU/RAM）

### 问题 4: Docker 网络问题

**症状**: 无法连接到 `http://ollama:11434`

**解决方案**:
1. 确保 Ollama 容器在同一网络中
2. 检查 `docker-compose.dev.yml` 中的网络配置
3. 使用容器名称而不是 `localhost`

---

## 📝 示例代码

### 完整集成示例

```python
# src/main.py
from src.infrastructure.ai.ollama_analysis_model import OllamaAnalysisModel
from src.config.settings import get_settings

async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 创建 Ollama 模型（如果启用）
    if settings.ai.ollama_enabled:
        ollama_model = OllamaAnalysisModel(
            model_name=settings.ai.ollama_model_name,
            base_url=settings.ai.ollama_base_url,
            timeout=settings.ai.ollama_timeout,
        )
        
        # 注入到依赖
        app.state.ollama_model = ollama_model
        app.state.analysis_model = ollama_model
    
    yield
    
    # 清理资源
    if hasattr(app.state, 'ollama_model'):
        del app.state.ollama_model
```

---

## 🔄 与 Phase II 计划的集成

### 更新降级策略

在 Phase II 的批次三（LLM 降级层）中，Ollama 可以作为本地 LLM 选项：

```
降级链：
1. Eb-MM (优先级 1)
2. LangChain Embedding (优先级 2)
3. Ollama (优先级 3a - 本地) 或 外部 LLM API (优先级 3b - 云端)
```

### 配置示例

```bash
# .env
# 优先使用 Ollama（本地）
OLLAMA_ENABLED=true
OLLAMA_MODEL_NAME=llama3
OLLAMA_BASE_URL=http://ollama:11434

# 可选：外部 LLM API（作为最后保障）
LLM_FALLBACK_ENABLED=false  # 如果 Ollama 可用，可以禁用外部 API
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-3.5-turbo
```

---

## 📚 参考资源

- **Ollama 官方文档**: https://ollama.com/docs
- **LangChain Ollama 集成**: https://python.langchain.com/docs/integrations/llms/ollama
- **模型列表**: https://ollama.com/library

---

## ✅ 检查清单

- [ ] Ollama 已安装并运行
- [ ] 模型已下载（如 `llama3`）
- [ ] 环境变量已配置（`.env`）
- [ ] 依赖已安装（`langchain-community`）
- [ ] Docker Compose 已更新（如使用 Docker）
- [ ] 测试连接成功（`curl http://localhost:11434/api/tags`）
- [ ] 单元测试通过
- [ ] 集成测试通过

---

**最后更新**: 2025-11-12

