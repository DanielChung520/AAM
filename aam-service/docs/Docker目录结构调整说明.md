# Docker 目录结构调整说明

**创建日期**: 2025-11-12  
**版本**: v1.0  
**状态**: ✅ 已完成

---

## 📋 变更概述

根据 DevOps 最佳实践和微服务架构原则，将 Docker 配置文件重新组织到 `docker/` 目录下，支持多环境配置（开发、沙盒、生产）。

---

## 🏗️ 新的目录结构

```
aam-service/
├── docker/                          # ✅ 新增：Docker 配置文件目录
│   ├── Dockerfile.dev               # ✅ 开发环境 Dockerfile（从根目录迁移）
│   ├── Dockerfile.staging           # ⏳ 待创建：沙盒环境 Dockerfile
│   ├── Dockerfile.prod             # ⏳ 待创建：生产环境 Dockerfile
│   └── README.md                    # ✅ 新增：Docker 配置说明文档
├── docker-compose.yml               # ✅ 更新：指向 docker/Dockerfile.dev（向后兼容）
├── docker-compose.dev.yml           # ✅ 新增：开发环境编排配置
├── docker-compose.staging.yml       # ⏳ 待创建：沙盒环境编排配置
├── docker-compose.prod.yml          # ⏳ 待创建：生产环境编排配置
├── src/                             # 源代码
├── tests/                           # 测试
├── scripts/                         # 脚本（已更新 start-dev.sh）
└── docs/                            # 文档
```

---

## ✅ 已完成的变更

### 1. 目录创建
- ✅ 创建 `docker/` 目录
- ✅ 移动 `Dockerfile` → `docker/Dockerfile.dev`
- ✅ 更新 `Dockerfile.dev` 注释（标注为开发环境）

### 2. 配置文件
- ✅ 创建 `docker-compose.dev.yml`（开发环境专用配置）
- ✅ 更新 `docker-compose.yml`（指向新路径，保持向后兼容）

### 3. 环境隔离
- ✅ 开发环境使用独立的数据卷（`*_dev` 后缀）
- ✅ 开发环境使用独立的网络（`aam-network-dev`）
- ✅ 开发环境容器名称使用 `-dev` 后缀

### 4. 脚本更新
- ✅ 更新 `scripts/start-dev.sh` 使用 `docker-compose.dev.yml`
- ✅ 更新脚本中的命令示例

### 5. 文档
- ✅ 创建 `docker/README.md` 说明文档
- ✅ 创建本文档记录变更

---

## 🚀 使用方法

### 开发环境（推荐）

```bash
# 使用开发环境配置
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f aam-service

# 停止服务
docker-compose -f docker-compose.dev.yml down
```

### 向后兼容（默认）

```bash
# 仍然可以使用默认配置（指向开发环境）
docker-compose up -d
```

### 使用启动脚本

```bash
# 使用更新后的启动脚本
./scripts/start-dev.sh
```

---

## 📊 环境对比

| 特性 | 开发环境 (Dev) | 沙盒环境 (Staging) | 生产环境 (Prod) |
|------|---------------|-------------------|----------------|
| **配置文件** | `docker/Dockerfile.dev` | `docker/Dockerfile.staging` | `docker/Dockerfile.prod` |
| **编排文件** | `docker-compose.dev.yml` | `docker-compose.staging.yml` | `docker-compose.prod.yml` |
| **容器名称** | `*-dev` | `*-staging` | `*-prod` |
| **数据卷** | `*_dev` | `*_staging` | `*_prod` |
| **网络** | `aam-network-dev` | `aam-network-staging` | `aam-network-prod` |
| **热重载** | ✅ | ❌ | ❌ |
| **代码挂载** | ✅ | ❌ | ❌ |
| **DEBUG 模式** | ✅ | ❌ | ❌ |
| **日志级别** | DEBUG | INFO | WARNING |

---

## 🔄 迁移影响

### 对现有用户的影响

1. **向后兼容**: 原有的 `docker-compose up` 命令仍然可用
2. **数据卷**: 开发环境使用新的数据卷（`*_dev`），不会影响现有数据
3. **容器名称**: 开发环境容器名称改为 `*-dev`，避免与其他环境冲突

### 需要更新的地方

- ✅ `scripts/start-dev.sh` - 已更新
- ⏳ CI/CD 脚本（如有）- 需要更新为使用 `docker-compose.dev.yml`
- ⏳ 团队文档 - 需要更新使用说明

---

## 📝 后续计划

### 待创建的文件

1. **沙盒环境**
   - `docker/Dockerfile.staging`
   - `docker-compose.staging.yml`
   - `.env.staging`

2. **生产环境**
   - `docker/Dockerfile.prod`
   - `docker-compose.prod.yml`
   - `.env.prod`

### 优化建议

1. **镜像优化**: 生产环境使用多阶段构建，最小化镜像体积
2. **安全加固**: 生产环境添加安全扫描、非 root 用户等
3. **性能优化**: 生产环境优化启动参数、资源限制等
4. **监控集成**: 添加健康检查、日志聚合等

---

## ✅ 验证清单

- [x] Docker 目录结构已创建
- [x] Dockerfile 已迁移到 `docker/Dockerfile.dev`
- [x] `docker-compose.dev.yml` 已创建并配置
- [x] `docker-compose.yml` 已更新（向后兼容）
- [x] 开发环境服务已成功启动
- [x] 所有容器状态为 healthy
- [x] 健康检查端点正常响应
- [x] 脚本已更新
- [x] 文档已创建

---

## 🔍 验证命令

```bash
# 检查目录结构
ls -la docker/

# 检查服务状态
docker-compose -f docker-compose.dev.yml ps

# 检查健康状态
curl http://localhost:8000/health

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f aam-service
```

---

## 📞 问题反馈

如有问题或建议，请：
- 创建 GitHub Issue
- 联系项目维护者
- 在团队频道讨论

---

**最后更新**: 2025-11-12

