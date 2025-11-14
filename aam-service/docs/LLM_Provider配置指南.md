# LLM Provider 配置指南

**版本**: v2.0  
**最后更新**: 2025-11-13

---

## 📋 概述

AAM 系统使用抽象的 LLM Provider 架构，支持多种 LLM 服务提供商。目前支持 Qwen、Gemini、Ollama 等 Provider，未来将支持更多 Provider（如 OpenAI、Anthropic 等）以及 MoE（Mixture of Experts）架构。

**重要**: 
- 所有 API Key 和敏感信息必须通过环境变量或 `.env` 文件配置，**不要硬编码在代码中**
- 模型配置（模型名称、max_tokens、temperature 等）通过 `config/models.json` 文件管理，**不要硬编码在代码中**

---

## 🔧 配置方式

### 模型配置文件（config/models.json）

模型配置通过 `config/models.json` 文件管理，支持：
- 每个模型独立配置 `max_tokens`（默认 8192）和 `temperature`（默认 0.5）
- 启用/禁用模型（`enabled` 字段）
- 设置模型优先级（`priority` 字段，数字越小优先级越高）
- 模型描述和显示名称

**配置文件格式**：

```json
{
  "gemini": {
    "models": [
      {
        "model_name": "gemini-2.5-flash",
        "display_name": "Gemini 2.5 Flash",
        "max_tokens": 8192,
        "temperature": 0.5,
        "enabled": true,
        "priority": 1,
        "description": "快速响应的 Gemini 模型，适合一般任务"
      }
    ]
  },
  "qwen": {
    "models": [
      {
        "model_name": "qwen-turbo",
        "display_name": "Qwen Turbo",
        "max_tokens": 8192,
        "temperature": 0.5,
        "enabled": true,
        "priority": 1,
        "description": "快速响应的 Qwen 模型"
      }
    ]
  }
}
```

**重要**：
- 只有 `enabled: true` 的模型才会被系统使用
- 如果未指定模型名称，系统会自动选择优先级最高的启用模型
- 可以通过 `scripts/manage_models.py` 工具管理模型配置

### 使用模型管理工具

```bash
# 列出所有启用的模型
python scripts/manage_models.py list --enabled-only

# 列出指定 Provider 的模型
python scripts/manage_models.py list --provider gemini

# 验证配置文件
python scripts/manage_models.py validate

# 启用模型
python scripts/manage_models.py enable gemini gemini-2.5-pro

# 禁用模型
python scripts/manage_models.py disable gemini gemini-2.5-pro

# 设置模型优先级
python scripts/manage_models.py priority gemini gemini-2.5-flash 1
```

---

## 🔧 API Key 配置方式

### 方式一：使用 .env 文件（推荐）

1. **复制配置模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**，填入实际的配置值：
   ```env
   # LLM层Provider类型
   LLM_LAYER_PROVIDER_TYPE=qwen
   
   # Qwen配置
   QWEN_API_KEY=your-actual-api-key-here
   QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
   QWEN_MODEL_NAME=qwen-turbo
   QWEN_TIMEOUT=120
   ```

3. **确保 .env 文件不被提交到 Git**（已在 .gitignore 中配置）

### 方式二：使用环境变量

```bash
export QWEN_API_KEY=your-actual-api-key-here
export QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
export QWEN_MODEL_NAME=qwen-turbo
export QWEN_TIMEOUT=120
export LLM_LAYER_PROVIDER_TYPE=qwen
```

### 方式三：Docker 环境变量

在 `docker-compose.yml` 中设置：

```yaml
environment:
  - QWEN_API_KEY=your-actual-api-key-here
  - QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
  - QWEN_MODEL_NAME=qwen-turbo
  - LLM_LAYER_PROVIDER_TYPE=qwen
```

---

## 📝 配置项说明

### LLM 层 Provider 类型

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|---------|--------|------|
| Provider类型 | `LLM_LAYER_PROVIDER_TYPE` | `qwen` | 当前使用的LLM Provider类型 |

**可选值**:
- `qwen` - 阿里云 Qwen API（当前支持）
- `ollama` - Ollama 本地模型（未来支持）
- `openai` - OpenAI API（未来支持）
- `anthropic` - Anthropic Claude API（未来支持）
- `custom` - 自定义 Provider（未来支持）

### Qwen Provider 配置

| 配置项 | 环境变量 | 默认值 | 必填 | 说明 |
|--------|---------|--------|------|------|
| API Key | `QWEN_API_KEY` | - | ✅ 是 | Qwen API 密钥（必须设置） |
| API Base URL | `QWEN_API_BASE_URL` | `https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation` | 否 | Qwen API 基础 URL |
| 模型名称 | `QWEN_MODEL_NAME` | - | 否 | Qwen 模型名称（可选，如果未指定则从 `config/models.json` 获取默认模型） |
| 超时时间 | `QWEN_TIMEOUT` | `120` | 否 | 请求超时时间（秒） |

**注意**：模型名称、max_tokens、temperature 等参数现在从 `config/models.json` 配置文件获取，不再从环境变量读取。

### Gemini Provider 配置

| 配置项 | 环境变量 | 默认值 | 必填 | 说明 |
|--------|---------|--------|------|------|
| API Key | `GEMINI_API_KEY` | - | ✅ 是 | Gemini API 密钥（必须设置） |
| API Base URL | `GEMINI_API_BASE_URL` | `https://generativelanguage.googleapis.com/v1beta` | 否 | Gemini API 基础 URL |
| 模型名称 | `GEMINI_MODEL_NAME` | - | 否 | Gemini 模型名称（可选，如果未指定则从 `config/models.json` 获取默认模型） |
| 超时时间 | `GEMINI_TIMEOUT` | `120` | 否 | 请求超时时间（秒） |

### Ollama Provider 配置

| 配置项 | 环境变量 | 默认值 | 必填 | 说明 |
|--------|---------|--------|------|------|
| API Base URL | `MODEL_API_BASE_URL` 或 `OLLAMA_BASE_URL` | `http://localhost:11434` | 否 | Ollama API 基础 URL |
| 模型名称 | `MODEL_NAME` | - | 否 | Ollama 模型名称（可选，如果未指定则从 `config/models.json` 获取默认模型） |
| 超时时间 | `MODEL_TIMEOUT` | `120` | 否 | 请求超时时间（秒） |

**注意**：Ollama 不需要 API Key。

---

## ⚠️ 安全注意事项

1. **不要硬编码 API Key**
   - ✅ 正确：使用环境变量或 `.env` 文件
   - ❌ 错误：在代码中直接写入 API Key

2. **不要提交 .env 文件到 Git**
   - `.env` 文件已在 `.gitignore` 中配置
   - 只提交 `.env.example` 模板文件

3. **使用不同的 API Key**
   - 开发环境、测试环境、生产环境应使用不同的 API Key
   - 定期轮换 API Key

---

## 🔍 验证配置

### 检查环境变量是否设置

```bash
# 检查 Qwen API Key
echo $QWEN_API_KEY

# 检查所有 LLM Provider 相关环境变量
env | grep -E "(QWEN_|LLM_LAYER_PROVIDER_TYPE)"
```

### 测试 Provider 创建

```python
from src.infrastructure.ai.providers.provider_factory import ModelProviderFactory
from src.core.interfaces.i_model_provider import ModelProviderType

# 如果配置正确，应该能成功创建
provider = ModelProviderFactory.create_provider(
    provider_type=ModelProviderType.QWEN,
    model_name="qwen-turbo"
)

# 如果配置错误，会抛出清晰的错误信息
```

---

## 📝 模型配置管理

### 添加新模型

1. 编辑 `config/models.json` 文件
2. 在对应的 Provider 下添加新模型配置：

```json
{
  "gemini": {
    "models": [
      {
        "model_name": "gemini-2.5-pro",
        "display_name": "Gemini 2.5 Pro",
        "max_tokens": 8192,
        "temperature": 0.5,
        "enabled": true,
        "priority": 2,
        "description": "高性能 Gemini 模型"
      }
    ]
  }
}
```

3. 验证配置：
```bash
python scripts/manage_models.py validate
```

### 启用/禁用模型

**方式一：使用管理工具（推荐）**
```bash
# 启用模型
python scripts/manage_models.py enable gemini gemini-2.5-pro

# 禁用模型
python scripts/manage_models.py disable gemini gemini-2.5-pro
```

**方式二：直接编辑配置文件**
编辑 `config/models.json`，将模型的 `enabled` 字段设置为 `true` 或 `false`。

### 设置模型优先级

优先级用于确定默认模型（当未指定模型名称时）。数字越小，优先级越高。

```bash
python scripts/manage_models.py priority gemini gemini-2.5-flash 1
```

### 模型参数说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_name` | string | - | 模型名称（必需） |
| `display_name` | string | 同 model_name | 显示名称 |
| `max_tokens` | integer | 8192 | 最大 token 数 |
| `temperature` | float | 0.5 | 温度参数（0.0-2.0） |
| `enabled` | boolean | true | 是否启用 |
| `priority` | integer | 999 | 优先级（数字越小优先级越高） |
| `description` | string | - | 模型描述 |

## 🚀 未来扩展

### MoE（Mixture of Experts）配置

未来支持 MoE 时，可以在 `.env` 文件中配置：

```env
# 启用 MoE
MOE_ENABLED=true
MOE_PROVIDERS=qwen,ollama,openai
MOE_ROUTING_STRATEGY=quality_based

# 每个 Provider 的权重（可选）
QWEN_WEIGHT=0.5
OLLAMA_WEIGHT=0.3
OPENAI_WEIGHT=0.2
```

### 自动获取模型列表

未来版本将支持从各 Provider API 自动获取可用模型列表并更新配置文件。

### 多 Provider 配置

```env
# 主 Provider
LLM_LAYER_PROVIDER_TYPE=qwen

# 备用 Provider（用于降级）
FALLBACK_PROVIDER_TYPE=ollama
FALLBACK_PROVIDER_2_TYPE=openai
```

---

## 📚 相关文档

- [测试计划 B：Qwen Provider 和降级策略测试](../plan/整合測試階段/測試計劃B-Qwen Provider和降級策略測試.md)
- [配置 LLM 层使用阿里 Qwen API 工作计划](../../.cursor/plans/ollama-a-84232a01.plan.md)
- [环境设置指南](./環境設置.md)

---

## ❓ 常见问题

### Q: 如何获取 Qwen API Key？

A: 访问阿里云 DashScope 控制台，创建 API Key。

### Q: 如果忘记设置 API Key 会怎样？

A: 系统会抛出清晰的错误信息，提示你设置 `QWEN_API_KEY` 环境变量。

### Q: 可以在代码中直接设置 API Key 吗？

A: **不建议**。虽然技术上可以，但会带来安全风险。推荐使用环境变量或 `.env` 文件。

### Q: 如何在不同环境使用不同的配置？

A: 使用不同的 `.env` 文件（如 `.env.development`、`.env.production`），或使用环境变量覆盖。

---

**最后更新**: 2025-11-13  
**维护者**: AAM 开发团队

