# AAM Admin Docker 开发环境说明

**创建日期**: 2025-01-14  
**状态**: ✅ Docker 配置已就绪

---

## 📋 开发模式说明

AAM Admin 支持两种开发模式：

### 1. 本地开发模式（当前默认）

**特点**:
- 后端：使用本地 Python 虚拟环境
- 前端：使用本地 Node.js
- 数据库：使用 Docker（admin-db）

**优点**:
- 启动快速
- 调试方便
- 热重载响应快

**缺点**:
- 需要本地安装 Python 和 Node.js
- 环境配置可能不一致

### 2. Docker 开发模式（推荐用于生产环境一致性）

**特点**:
- 后端：使用 Docker 容器
- 前端：使用 Docker 容器（可选）
- 数据库：使用 Docker

**优点**:
- 环境一致性
- 无需本地安装 Python/Node.js
- 更接近生产环境

**缺点**:
- 启动稍慢
- 需要 Docker 环境

---

## 🐳 Docker 开发环境配置

### 已配置的服务

#### 1. Admin Database (PostgreSQL)

```yaml
admin-db:
  image: postgres:15-alpine
  container_name: admin-db-dev
  ports:
    - "5433:5432"
```

#### 2. Admin Backend (FastAPI)

```yaml
admin-backend:
  build:
    context: ./backend
    dockerfile: Dockerfile.dev
  container_name: admin-backend-dev
  ports:
    - "8003:8003"
  volumes:
    - ./backend/src:/app/src  # 代码热重载
    - ./backend/tests:/app/tests
  command: uvicorn src.main:app --host 0.0.0.0 --port 8003 --reload
```

**特性**:
- ✅ 代码卷挂载（热重载）
- ✅ 自动重载（`--reload`）
- ✅ 健康检查
- ✅ 依赖数据库服务

---

## 🚀 Docker 开发模式使用方法

### 启动所有服务（Docker）

```bash
cd /Users/Daniel/Documents/GitHub/AAM/aam-admin

# 启动数据库和后端
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f admin-backend
```

### 仅启动数据库（Docker）

```bash
docker-compose -f docker-compose.dev.yml up admin-db -d
```

### 仅启动后端（Docker）

```bash
docker-compose -f docker-compose.dev.yml up admin-backend -d
```

### 停止服务（Docker）

```bash
# 停止所有服务
docker-compose -f docker-compose.dev.yml down

# 停止特定服务
docker-compose -f docker-compose.dev.yml stop admin-backend
```

---

## 🔄 混合模式（推荐）

**当前推荐配置**:
- **数据库**: Docker（确保数据持久化）
- **后端**: 本地开发（快速调试）
- **前端**: 本地开发（快速热重载）

**使用场景**:
- 日常开发：使用混合模式
- 环境测试：使用 Docker 模式
- 生产部署：使用 Docker 模式

---

## 📊 开发模式对比

| 特性 | 本地开发 | Docker 开发 |
|------|---------|------------|
| 启动速度 | ⚡ 快 | 🐢 较慢 |
| 调试便利性 | ✅ 方便 | ⚠️ 需要进入容器 |
| 环境一致性 | ⚠️ 依赖本地环境 | ✅ 完全一致 |
| 热重载 | ✅ 支持 | ✅ 支持（卷挂载） |
| 依赖管理 | ⚠️ 需手动安装 | ✅ 自动安装 |
| 生产环境匹配 | ⚠️ 可能不一致 | ✅ 完全匹配 |

---

## 🎯 建议

### 日常开发

**推荐使用混合模式**:
- 数据库：Docker（`docker-compose -f docker-compose.dev.yml up admin-db -d`）
- 后端：本地（`./scripts/start-service.sh backend`）
- 前端：本地（`./scripts/start-service.sh frontend`）

**优点**:
- 启动快速
- 调试方便
- 热重载响应快

### 环境测试

**推荐使用 Docker 模式**:
- 所有服务：Docker（`docker-compose -f docker-compose.dev.yml up -d`）

**优点**:
- 环境一致性
- 更接近生产环境

---

## 🔧 Docker 开发模式配置详情

### 后端服务配置

**Dockerfile.dev**:
- 基于 `python:3.11-slim`
- 安装系统依赖（curl, gcc, postgresql-client）
- 安装 Python 依赖
- 暴露端口 8003
- 支持热重载

**docker-compose.dev.yml**:
- 代码卷挂载：`./backend/src:/app/src`
- 测试卷挂载：`./backend/tests:/app/tests`
- 环境变量配置
- 健康检查配置
- 依赖数据库服务

### 前端服务配置

**注意**: 当前 `docker-compose.dev.yml` 中**未包含前端服务**，因为：
- 前端开发通常使用本地 Vite 开发服务器
- Vite 的热重载在本地更快速
- 前端构建产物可以独立部署

**如需前端 Docker 开发**，可以添加：

```yaml
admin-frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.dev
  container_name: admin-frontend-dev
  ports:
    - "3000:3000"
  volumes:
    - ./frontend/src:/app/src
    - ./frontend/public:/app/public
  environment:
    - VITE_API_BASE_URL=http://localhost:8003
  command: npm run dev
```

---

## 📝 使用建议

### 开发阶段

1. **快速迭代开发**: 使用本地开发模式
   ```bash
   ./scripts/start-service.sh all
   ```

2. **环境一致性测试**: 使用 Docker 模式
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

### 部署阶段

1. **生产环境**: 使用 Docker 模式
2. **CI/CD**: 使用 Docker 模式
3. **团队协作**: 使用 Docker 模式（确保环境一致）

---

## ✅ 总结

**AAM Admin 支持 Docker 开发，配置已就绪！**

- ✅ Docker Compose 配置已创建
- ✅ Dockerfile.dev 已创建
- ✅ 支持代码热重载
- ✅ 支持健康检查
- ✅ 支持环境变量配置

**当前推荐**:
- 日常开发：使用混合模式（数据库 Docker + 后端/前端本地）
- 环境测试：使用 Docker 模式（所有服务 Docker）

---

**最后更新**: 2025-01-14

