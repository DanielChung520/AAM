# AAM Admin Docker 模式说明

**创建日期**: 2025-01-14  
**状态**: ✅ 默认使用 Docker 模式

---

## 📋 默认配置

**AAM Admin 默认使用 Docker 模式**，统一管理所有服务，避免环境混淆。

### 服务配置

- **数据库**: Docker 容器（`admin-db-dev`）
- **后端**: Docker 容器（`admin-backend-dev`）
- **前端**: 本地模式（保持 Vite 热重载速度）

---

## 🚀 快速开始

### 启动所有服务（Docker 模式）

```bash
# 启动数据库和后端（Docker）
./scripts/start-service.sh all

# 或使用 Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

### 启动前端服务（本地模式）

```bash
# 前端使用本地模式以保持热重载速度
./scripts/start-service.sh frontend
```

---

## 📊 服务端口

| 服务 | 端口 | 访问地址 | 运行方式 |
|------|------|----------|---------|
| Admin Backend | 8003 | http://localhost:8003 | Docker |
| Admin Frontend | 3000 | http://localhost:3000 | 本地 |
| Admin Database | 5433 | localhost:5433 | Docker |

---

## 🔧 Docker 服务管理

### 查看服务状态

```bash
# 使用脚本查看
./scripts/status-service.sh

# 或使用 Docker Compose
docker-compose -f docker-compose.dev.yml ps
```

### 查看日志

```bash
# 后端日志
docker-compose -f docker-compose.dev.yml logs -f admin-backend

# 数据库日志
docker-compose -f docker-compose.dev.yml logs -f admin-db

# 所有服务日志
docker-compose -f docker-compose.dev.yml logs -f
```

### 停止服务

```bash
# 使用脚本停止
./scripts/stop-service.sh all

# 或使用 Docker Compose
docker-compose -f docker-compose.dev.yml down
```

### 重启服务

```bash
# 重启后端
docker-compose -f docker-compose.dev.yml restart admin-backend

# 重启所有服务
docker-compose -f docker-compose.dev.yml restart
```

---

## 🔍 资源监控

### 查看资源占用

```bash
# 使用资源检查脚本
./scripts/check-resources.sh

# 或使用 Docker 命令
docker stats admin-db-dev admin-backend-dev
```

---

## 🛠️ 开发调试

### 进入后端容器

```bash
# 进入容器
docker exec -it admin-backend-dev bash

# 查看容器内文件
docker exec -it admin-backend-dev ls -la /app/src
```

### 查看容器环境变量

```bash
docker exec admin-backend-dev env
```

### 执行数据库迁移

```bash
# 进入容器执行迁移
docker exec -it admin-backend-dev alembic upgrade head

# 或从本地执行（需要配置数据库连接）
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## 📝 配置说明

### Docker Compose 配置

**文件**: `docker-compose.dev.yml`

**服务**:
- `admin-db`: PostgreSQL 数据库
- `admin-backend`: FastAPI 后端服务

**特性**:
- ✅ 代码热重载（卷挂载）
- ✅ 自动重载（`--reload`）
- ✅ 健康检查
- ✅ 环境变量配置

### 环境变量

后端服务环境变量（在 `docker-compose.dev.yml` 中配置）:
- `DEBUG=true`
- `LOG_LEVEL=DEBUG`
- `DB_DATABASE_URL=postgresql://admin:admin@admin-db:5432/aam_admin`
- `API_HOST=0.0.0.0`
- `API_PORT=8003`
- `API_CORS_ORIGINS=http://localhost:3000`
- `AUTH_SECRET_KEY=dev-secret-key-change-in-production`
- `AUTH_AAM_SERVICE_URL=http://host.docker.internal:8000`

---

## ⚠️ 注意事项

### 1. 数据持久化

数据库数据存储在 Docker 卷中：
- 卷名: `admin_db_data_dev`
- 数据位置: Docker 管理的卷

**备份数据**:
```bash
# 导出数据库
docker exec admin-db-dev pg_dump -U admin aam_admin > backup.sql

# 导入数据库
docker exec -i admin-db-dev psql -U admin aam_admin < backup.sql
```

### 2. 端口冲突

确保以下端口未被占用：
- `8003`: 后端 API
- `5433`: 数据库
- `3000`: 前端（本地）

**检查端口占用**:
```bash
lsof -i :8003
lsof -i :5433
lsof -i :3000
```

### 3. 代码热重载

后端代码通过卷挂载实现热重载：
- 本地路径: `./backend/src`
- 容器路径: `/app/src`

修改本地代码后，容器内的代码会自动更新，Uvicorn 会自动重载。

---

## 🔄 切换到本地模式

如果需要使用本地模式（不推荐，会造成环境混淆）：

```bash
# 使用本地模式启动
./scripts/start-service.sh all --local

# 或单独启动后端（本地模式）
./scripts/start-service.sh backend --local
```

**注意**: 本地模式需要：
- Python 3.11+ 和虚拟环境
- 已安装所有依赖

---

## 📚 相关文档

- [开发模式选择指南](开发模式选择指南.md)
- [服务管理脚本](../scripts/README.md)
- [Docker 开发环境说明](Docker开发环境说明.md)

---

**最后更新**: 2025-01-14

