# AAM Admin 管理系统

**版本**: 1.0.0  
**状态**: 阶段一基础设施搭建已完成  
**最后更新**: 2025-01-14

---

## 📋 项目简介

AAM Admin 管理系统是 AAM 系统的管理后台，提供 Web 界面用于管理 AAM 服务、监控系统状态、查看日志等功能。

### 核心功能

- **服务监控**: 监控 AAM 服务及其依赖服务的运行状态
- **日志管理**: 实时查看和管理服务日志
- **用户管理**: 管理员用户和权限管理
- **系统配置**: 系统参数和配置管理
- **部署管理**: 版本部署和历史记录

---

## 🚀 快速开始

### 使用启动脚本（推荐）

```bash
# 启动所有服务（默认 Docker 模式）
./scripts/start-service.sh all

# 仅启动后端服务（默认 Docker 模式）
./scripts/start-service.sh backend

# 仅启动前端服务（本地模式，保持热重载速度）
./scripts/start-service.sh frontend

# 查看服务状态
./scripts/status-service.sh

# 查看资源占用
./scripts/check-resources.sh

# 停止服务
./scripts/stop-service.sh all
```

**注意**: 默认使用 Docker 模式，统一管理，避免环境混淆。如需本地模式，使用 `--local` 参数。

### 手动启动（Docker 模式）

#### 使用 Docker Compose（推荐）

```bash
# 启动所有服务（数据库 + 后端）
docker-compose -f docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f admin-backend

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

#### 启动前端服务（本地模式，保持热重载速度）

```bash
cd frontend
npm run dev
```

**注意**: 前端建议使用本地模式，以保持 Vite 热重载的最佳性能。

---

## 📊 服务端口

| 服务 | 端口 | 访问地址 |
|------|------|----------|
| Admin Backend | 8003 | http://localhost:8003 |
| Admin Frontend | 3000 | http://localhost:3000 |
| Admin Database | 5433 | localhost:5433 |

---

## 🔧 开发环境

### 前置要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### 安装依赖

#### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 前端

```bash
cd frontend
npm install
```

---

## 📝 数据库初始化

### 执行迁移

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 创建初始管理员用户

```bash
cd backend
source venv/bin/activate
python scripts/init_admin_user.py
```

默认管理员账户：
- 用户名: `admin`
- 密码: `admin`
- 邮箱: `admin@example.com`

**⚠️ 重要**: 首次登录后请立即修改密码！

---

## 🧪 测试

### 测试后端 API

```bash
# 健康检查
curl http://localhost:8003/health

# 登录
curl -X POST http://localhost:8003/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### 访问前端

打开浏览器访问: http://localhost:3000

### 访问 API 文档

打开浏览器访问: http://localhost:8003/docs

---

## 📁 项目结构

```
aam-admin/
├── backend/              # 后端服务
│   ├── src/             # 源代码
│   ├── alembic/         # 数据库迁移
│   ├── scripts/         # 脚本文件
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端服务
│   ├── src/            # 源代码
│   └── package.json    # Node.js 依赖
├── scripts/             # 服务管理脚本
│   ├── start-service.sh # 启动脚本
│   ├── stop-service.sh  # 停止脚本
│   └── status-service.sh # 状态脚本
└── docker-compose.dev.yml # Docker Compose 配置
```

---

## 🔗 相关文档

- [系统设计文档](docs/AAM管理系統-SD.md)
- [页面布局设计](docs/AAM管理系統-頁面佈局設計.md)
- [开发计划](docs/plan/阶段一：基础设施搭建.md)
- [服务管理脚本](scripts/README.md)

---

**最后更新**: 2025-01-14

