# AAM Admin 服务管理脚本

## 📋 脚本说明

### start-service.sh

启动 AAM Admin 服务的脚本，支持三种模式：
- `all` - 启动所有服务（数据库、后端、前端）
- `backend` - 仅启动后端服务
- `frontend` - 仅启动前端服务

**特性**:
- ✅ 自动检查并停止旧服务（端口占用和 Docker 容器）
- ✅ 自动检查数据库就绪状态
- ✅ 自动检查服务启动成功
- ✅ 自动安装依赖（如需要）
- ✅ 显示服务访问地址

### stop-service.sh

停止 AAM Admin 服务的脚本，支持四种模式：
- `all` - 停止所有服务
- `backend` - 仅停止后端服务
- `frontend` - 仅停止前端服务
- `database` - 仅停止数据库服务

### status-service.sh

查看 AAM Admin 服务状态的脚本，显示所有服务的运行状态和访问地址。

---

## 🚀 使用方法

### 启动服务

```bash
# 启动所有服务
./scripts/start-service.sh all

# 仅启动后端服务
./scripts/start-service.sh backend

# 仅启动前端服务
./scripts/start-service.sh frontend
```

### 停止服务

```bash
# 停止所有服务
./scripts/stop-service.sh all

# 仅停止后端服务
./scripts/stop-service.sh backend

# 仅停止前端服务
./scripts/stop-service.sh frontend

# 仅停止数据库服务
./scripts/stop-service.sh database
```

### 查看服务状态

```bash
# 查看所有服务状态
./scripts/status-service.sh
```

---

## 📊 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Admin Backend | 8003 | 管理后端 API |
| Admin Frontend | 3000 | 管理前端界面 |
| Admin Database | 5433 | 管理数据库 |

---

## 🔍 服务检查

脚本会自动检查以下内容：

1. **端口占用**: 检查端口是否被占用
2. **Docker 容器**: 检查 Docker 容器是否运行
3. **数据库就绪**: 等待数据库服务就绪
4. **服务健康**: 检查服务是否成功启动

---

## 📝 日志文件

服务启动后，日志文件位置：
- 后端日志: `/tmp/admin-backend.log`
- 前端日志: `/tmp/admin-frontend.log`

查看日志：
```bash
# 查看后端日志
tail -f /tmp/admin-backend.log

# 查看前端日志
tail -f /tmp/admin-frontend.log
```

---

## ⚠️ 注意事项

1. **虚拟环境**: 后端服务需要 Python 虚拟环境，确保 `backend/venv` 存在
2. **依赖安装**: 前端服务需要安装依赖，脚本会自动检查并安装
3. **Docker**: 数据库服务需要 Docker，确保 Docker 正在运行
4. **端口冲突**: 如果端口被占用，脚本会自动停止旧服务

---

## 🔧 故障排查

### 后端服务启动失败

1. 检查虚拟环境是否存在：
   ```bash
   ls -la backend/venv
   ```

2. 检查依赖是否安装：
   ```bash
   cd backend && source venv/bin/activate && pip list
   ```

3. 查看日志：
   ```bash
   tail -f /tmp/admin-backend.log
   ```

### 前端服务启动失败

1. 检查依赖是否安装：
   ```bash
   ls -la frontend/node_modules
   ```

2. 查看日志：
   ```bash
   tail -f /tmp/admin-frontend.log
   ```

### 数据库服务启动失败

1. 检查 Docker 是否运行：
   ```bash
   docker ps
   ```

2. 检查容器状态：
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```

---

**最后更新**: 2025-01-14

