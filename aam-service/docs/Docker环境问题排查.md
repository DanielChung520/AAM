# Docker 环境问题排查指南

**创建日期**: 2025-11-12  
**版本**: v1.0  
**适用场景**: Docker daemon 未运行导致的问题

---

## 🔍 问题现象

执行 Docker 命令时出现以下错误：
```
Cannot connect to the Docker daemon at unix:///Users/Daniel/.docker/run/docker.sock. 
Is the docker daemon running?
```

---

## 📋 问题原因

**Docker Desktop 未启动**

- Docker Desktop 是一个 GUI 应用程序，需要手动启动
- 即使 Docker 已安装，如果 Docker Desktop 未运行，Docker daemon 也不会启动
- 这是 macOS 上 Docker 的正常行为

---

## ✅ 解决方案

### 方法 1: 通过命令行启动（推荐）

```bash
# 启动 Docker Desktop
open -a Docker

# 等待 30-60 秒让 Docker Desktop 完全启动
# 检查状态
docker info
```

### 方法 2: 手动启动

1. 打开 **应用程序 (Applications)** 文件夹
2. 找到 **Docker** 应用程序
3. 双击启动 Docker Desktop
4. 等待 Docker Desktop 图标停止动画（表示已完全启动）

### 方法 3: 使用检查脚本

```bash
# 运行检查脚本
./scripts/check-docker.sh
```

脚本会自动：
- 检查 Docker 安装状态
- 检查 Docker daemon 状态
- 如果未运行，自动尝试启动 Docker Desktop
- 检查容器状态

---

## 🔄 验证 Docker 环境

### 1. 检查 Docker daemon 状态

```bash
docker info
```

如果成功，会显示 Docker 系统信息；如果失败，会显示连接错误。

### 2. 检查容器状态

```bash
# 检查所有容器
docker ps -a

# 检查 AAM 服务容器
docker ps -a | grep -E "(aam-service|chromadb|postgres|rabbitmq|redis)"

# 使用 docker-compose 检查
docker-compose ps
```

### 3. 启动 AAM 服务

```bash
# 进入项目目录
cd /Users/Daniel/Documents/GitHub/AAM/aam-service

# 启动所有服务
docker-compose up --build -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f aam-service
```

---

## 🎯 为什么之前测试正常，现在不行？

### 可能的原因：

1. **Docker Desktop 未自动启动**
   - macOS 重启后，Docker Desktop 不会自动启动
   - 需要手动启动或设置开机自启动

2. **Docker Desktop 被关闭**
   - 可能意外关闭了 Docker Desktop
   - 或者系统资源不足导致 Docker Desktop 退出

3. **Docker Desktop 更新**
   - 更新后可能需要重新启动

---

## 📝 开发环境说明

### Docker 环境 vs 本地环境

| 环境 | 用途 | 依赖安装位置 | 独立性 |
|------|------|------------|--------|
| **Docker 环境** | 生产环境、完整测试 | 容器内 (`/root/.local`) | ✅ 完全独立 |
| **本地环境** | 代码编辑、快速测试 | 本地虚拟环境 (`venv/`) | ⚠️ 需要隔离 |

### 重要说明：

1. **Docker 环境是独立的**
   - 容器内的 Python 环境与本地完全隔离
   - 本地安装依赖不会影响 Docker 容器
   - Docker 容器使用 `requirements.txt` 安装依赖

2. **本地环境是可选的**
   - 主要用于代码编辑和 IDE 支持
   - 如果需要本地测试，建议使用虚拟环境隔离

3. **测试应该在 Docker 环境中运行**
   - 单元测试可以在本地运行（不依赖外部服务）
   - 集成测试应该在 Docker 环境中运行（需要数据库等）

---

## 🛠️ 常用命令

### Docker 管理

```bash
# 启动 Docker Desktop
open -a Docker

# 检查 Docker 状态
docker info

# 查看所有容器
docker ps -a

# 停止所有容器
docker-compose down

# 启动所有服务
docker-compose up -d

# 重新构建并启动
docker-compose up --build -d
```

### AAM 服务管理

```bash
# 启动开发环境
./scripts/start-dev.sh

# 检查 Docker 环境
./scripts/check-docker.sh

# 查看服务日志
docker-compose logs -f aam-service

# 进入容器
docker-compose exec aam-service bash

# 在容器内运行测试
docker-compose exec aam-service pytest
```

---

## ⚠️ 注意事项

1. **Docker Desktop 需要保持运行**
   - 开发期间不要关闭 Docker Desktop
   - 如果关闭，需要重新启动

2. **端口冲突**
   - 确保端口 8000, 8001, 5432, 5672, 6379 未被占用
   - 如果端口被占用，可以修改 `docker-compose.yml` 中的端口映射

3. **资源使用**
   - Docker Desktop 会占用一定的系统资源
   - 如果系统资源不足，可能导致 Docker Desktop 运行不稳定

4. **数据持久化**
   - Docker volumes 中的数据会持久保存
   - 删除容器不会删除 volumes 中的数据
   - 需要清理数据时，使用 `docker-compose down -v`

---

## 🔧 故障排查

### 问题 1: Docker Desktop 启动失败

**解决方案：**
```bash
# 检查 Docker Desktop 进程
ps aux | grep -i "docker desktop"

# 重启 Docker Desktop
killall Docker
open -a Docker
```

### 问题 2: 容器无法启动

**解决方案：**
```bash
# 查看详细日志
docker-compose logs aam-service

# 检查容器状态
docker-compose ps

# 重新构建
docker-compose build --no-cache aam-service
docker-compose up -d
```

### 问题 3: 端口被占用

**解决方案：**
```bash
# 检查端口占用
lsof -i :8000
lsof -i :8001
lsof -i :5432

# 停止占用端口的进程，或修改 docker-compose.yml 中的端口映射
```

---

## 📚 相关文档

- [环境设置指南](./環境設置.md)
- [开发指导手册](./AiDevelopmentGuide.md)
- [README](../README.md)

---

**最后更新**: 2025-11-12

