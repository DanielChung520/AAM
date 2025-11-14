# AAM 系统启动说明

## 🚀 快速启动

### 推荐方式：使用统一启动脚本

```bash
cd /Users/Daniel/Documents/GitHub/AAM

# 启动所有服务（按顺序）
./scripts/start-all-services.sh all
```

### 启动顺序

1. **aam-service**（包括所有依赖服务）
2. 等待 aam-service 完全就绪（约 30 秒）
3. **aam-admin**

---

## ⚠️ 重要提示

### 避免 Docker Desktop GUI

**不要使用 Docker Desktop GUI 操作**，使用命令行：

```bash
# ✅ 正确：使用命令行
./scripts/start-all-services.sh all

# ❌ 错误：在 Docker Desktop GUI 中操作
```

### 原因

- Docker Desktop GUI 可能存在 bug
- 同时使用 GUI 和命令行会导致冲突
- 命令行提供更好的错误控制

---

## 📊 服务访问地址

启动成功后：

- **AAM Service**: http://localhost:8000
- **AAM Service API**: http://localhost:8000/docs
- **Admin Backend**: http://localhost:8003
- **Admin Backend API**: http://localhost:8003/docs
- **ChromaDB**: http://localhost:8001
- **RabbitMQ**: http://localhost:15672 (admin/admin)

---

## 🛑 停止服务

```bash
./scripts/start-all-services.sh cleanup
```

---

## 📚 详细文档

- [服务启动最佳实践](./docs/服务启动最佳实践.md)
- [Docker Compose 错误解决方案](./docs/Docker Compose 错误解决方案.md)
- [配置检查总结](./docs/配置检查总结.md)

---

**最后更新**: 2025-01-14
