# AAM 管理系统部署指南

**版本**: v1.0  
**最后更新**: 2025-01-14

---

## 目录

1. [概述](#概述)
2. [部署前准备](#部署前准备)
3. [版本管理](#版本管理)
4. [部署策略](#部署策略)
5. [部署流程](#部署流程)
6. [回滚操作](#回滚操作)
7. [故障排查](#故障排查)

---

## 概述

AAM 管理系统支持三种零中断部署策略：

1. **蓝绿部署 (Blue-Green Deployment)**: 创建新环境，切换流量，适合主要版本更新
2. **滚动更新 (Rolling Update)**: 逐步替换实例，适合小版本更新
3. **金丝雀部署 (Canary Deployment)**: 小流量测试，逐步扩大，适合新功能验证

---

## 部署前准备

### 1. 环境要求

- Docker 和 Docker Compose 已安装
- PostgreSQL 数据库已配置
- 管理后端 API 服务运行正常
- 有足够的系统资源（CPU、内存、磁盘）

### 2. 版本准备

确保要部署的版本已经创建并包含完整的配置快照：

```bash
# 创建版本
POST /api/v1/admin/versions
{
  "version": "v1.0.0",
  "git_tag": "v1.0.0",
  "description": "First release"
}
```

### 3. 配置检查

在部署前，建议使用预览功能检查配置：

```bash
POST /api/v1/admin/deployments/versions/v1.0.0/deploy
{
  "version": "v1.0.0",
  "strategy": "blue_green",
  "preview": true
}
```

---

## 版本管理

### 创建版本

版本号应遵循语义化版本规范：`vMAJOR.MINOR.PATCH`

**示例**:
- `v1.0.0`: 主要版本
- `v1.1.0`: 次要版本
- `v1.1.1`: 补丁版本

### 版本状态

- **active**: 当前活动版本
- **available**: 可用版本（可部署）
- **deprecated**: 已废弃版本

### 版本比较

在部署前，建议比较新旧版本的配置差异：

```bash
GET /api/v1/admin/versions/v1.0.0/compare/v1.1.0
```

---

## 部署策略

### 蓝绿部署 (Blue-Green)

**适用场景**:
- 主要版本更新
- 重大功能变更
- 需要快速回滚的场景

**配置参数**:
```json
{
  "strategy": "blue_green",
  "config": {
    "health_check_timeout": 300,
    "traffic_switch_delay": 10
  }
}
```

**流程**:
1. 创建绿色环境（新版本）
2. 等待健康检查通过
3. 切换流量到绿色环境
4. 清理蓝色环境（旧版本）

### 滚动更新 (Rolling Update)

**适用场景**:
- 小版本更新
- 配置变更
- 安全补丁

**配置参数**:
```json
{
  "strategy": "rolling",
  "config": {
    "max_unavailable": 1,
    "max_surge": 1,
    "min_ready_seconds": 30
  }
}
```

**流程**:
1. 逐个停止旧实例
2. 启动新版本实例
3. 等待新实例健康检查通过
4. 重复直到所有实例更新完成

### 金丝雀部署 (Canary)

**适用场景**:
- 新功能测试
- 性能验证
- 风险控制

**配置参数**:
```json
{
  "strategy": "canary",
  "config": {
    "initial_traffic_percent": 10,
    "traffic_increment_percent": 10,
    "increment_interval_seconds": 300,
    "max_error_rate": 5,
    "max_response_time_ms": 1000
  }
}
```

**流程**:
1. 部署金丝雀实例（小流量）
2. 监控指标（错误率、响应时间）
3. 逐步增加流量
4. 如果指标异常，自动回滚
5. 如果成功，全量部署

---

## 部署流程

### 1. 选择版本和策略

在管理界面中选择要部署的版本和部署策略。

### 2. 配置部署参数

根据选择的策略配置相应的参数。

### 3. 预览部署

使用预览功能检查配置和依赖：

```bash
POST /api/v1/admin/deployments/versions/v1.0.0/deploy
{
  "version": "v1.0.0",
  "strategy": "blue_green",
  "preview": true
}
```

### 4. 执行部署

确认预览结果后，执行实际部署：

```bash
POST /api/v1/admin/deployments/versions/v1.0.0/deploy
{
  "version": "v1.0.0",
  "strategy": "blue_green",
  "config": {...}
}
```

### 5. 监控部署状态

实时监控部署进度和状态：

```bash
GET /api/v1/admin/deployments/{deployment_id}/status
```

### 6. 查看部署日志

如有问题，查看部署日志：

```bash
GET /api/v1/admin/deployments/{deployment_id}/logs
```

---

## 回滚操作

### 自动回滚

系统会在以下情况自动触发回滚：

- 健康检查失败
- 错误率超过阈值
- 响应时间超过阈值

### 手动回滚

如果需要手动回滚：

```bash
POST /api/v1/admin/deployments/versions/v1.0.0/rollback
{
  "target_version": "v0.9.0",
  "reason": "Rollback due to errors"
}
```

### 切换活动版本

快速切换到指定版本：

```bash
POST /api/v1/admin/deployments/versions/active/switch?version=v0.9.0
```

---

## 故障排查

### 部署失败

1. **检查部署日志**:
   ```bash
   GET /api/v1/admin/deployments/{deployment_id}/logs
   ```

2. **检查版本配置**:
   ```bash
   GET /api/v1/admin/versions/{version}
   ```

3. **检查系统资源**:
   - CPU 使用率
   - 内存使用率
   - 磁盘空间

### 健康检查失败

1. **检查服务是否正常启动**
2. **检查健康检查端点是否可访问**
3. **检查网络连接**
4. **增加健康检查超时时间**

### 流量切换失败

1. **检查负载均衡器配置**
2. **检查新版本服务是否正常**
3. **检查网络连接**

---

## 最佳实践

1. **部署前测试**: 在测试环境先验证部署流程
2. **使用预览功能**: 部署前预览配置和依赖
3. **监控指标**: 部署后持续监控系统指标
4. **准备回滚方案**: 提前准备好回滚计划
5. **记录操作**: 记录所有部署操作和原因
6. **版本管理**: 遵循语义化版本规范
7. **备份配置**: 部署前备份当前配置

---

**最后更新**: 2025-01-14

