# Docker 配置文件目录

本目录包含 AAM 服务在不同环境下的 Docker 配置文件。

## 📁 目录结构

```
docker/
├── Dockerfile.dev          # 开发环境 Dockerfile
├── Dockerfile.staging      # 沙盒环境 Dockerfile（待创建）
└── Dockerfile.prod         # 生产环境 Dockerfile（待创建）
```

## 🚀 使用方式

### 开发环境

```bash
# 使用开发环境配置启动
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f aam-service

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

### 默认配置（向后兼容）

```bash
# 使用默认 docker-compose.yml（指向开发环境）
docker-compose up -d
```

## 📋 环境说明

### 开发环境 (Development)
- **文件**: `Dockerfile.dev`, `docker-compose.dev.yml`
- **特点**:
  - 启用热重载 (`--reload`)
  - 代码卷挂载 (`./src:/app/src`)
  - DEBUG 模式开启
  - 详细的日志输出
  - 容器名称后缀: `-dev`

### 沙盒环境 (Staging)
- **文件**: `Dockerfile.staging`, `docker-compose.staging.yml`（待创建）
- **特点**:
  - 接近生产环境的配置
  - 性能优化
  - 日志级别: INFO
  - 容器名称后缀: `-staging`

### 生产环境 (Production)
- **文件**: `Dockerfile.prod`, `docker-compose.prod.yml`（待创建）
- **特点**:
  - 最小化镜像体积
  - 安全加固
  - 性能优化
  - 日志级别: WARNING
  - 容器名称后缀: `-prod`

## 🔧 配置差异

| 特性 | Dev | Staging | Prod |
|------|-----|---------|------|
| 热重载 | ✅ | ❌ | ❌ |
| 代码挂载 | ✅ | ❌ | ❌ |
| DEBUG 模式 | ✅ | ❌ | ❌ |
| 日志级别 | DEBUG | INFO | WARNING |
| 镜像优化 | 基础 | 中等 | 最大化 |
| 安全加固 | 基础 | 中等 | 严格 |

## 📝 注意事项

1. **数据卷隔离**: 不同环境使用不同的数据卷（如 `chromadb_data_dev`, `chromadb_data_staging`）
2. **网络隔离**: 不同环境使用不同的网络（如 `aam-network-dev`, `aam-network-staging`）
3. **容器命名**: 不同环境的容器名称包含环境后缀，避免冲突
4. **端口映射**: 开发环境使用标准端口，其他环境可能需要调整

## 🔄 迁移说明

原有的 `Dockerfile` 已迁移到 `docker/Dockerfile.dev`，`docker-compose.yml` 已更新为指向新的路径，保持向后兼容。

---

**最后更新**: 2025-11-12

