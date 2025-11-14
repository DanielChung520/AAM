# AAM 管理系统 API 文档

**版本**: v1.0  
**最后更新**: 2025-01-14  
**基础 URL**: `http://localhost:8003/api/v1`

---

## 目录

1. [认证](#认证)
2. [版本管理 API](#版本管理-api)
3. [部署管理 API](#部署管理-api)
4. [错误处理](#错误处理)

---

## 认证

所有 API 请求都需要在请求头中包含认证 Token：

```
Authorization: Bearer <token>
```

### 获取 Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 版本管理 API

### 获取版本列表

```http
GET /api/v1/admin/versions
```

**查询参数**:
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页数量，默认 20，最大 100
- `status` (string, 可选): 版本状态过滤 (`active`, `available`, `deprecated`)
- `search` (string, 可选): 搜索关键词
- `created_after` (string, 可选): 创建时间起始（ISO 格式）
- `created_before` (string, 可选): 创建时间结束（ISO 格式）
- `sort_by` (string, 可选): 排序字段，默认 `created_at`
- `sort_order` (string, 可选): 排序顺序 (`asc`/`desc`)，默认 `desc`

**响应**:
```json
{
  "items": [
    {
      "version": "v1.0.0",
      "status": "active",
      "git_commit": "abc123",
      "git_branch": "main",
      "image_tag": "aam-service:v1.0.0",
      "created_at": "2025-01-14T10:00:00Z",
      "created_by": "admin",
      "description": "First release"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 创建版本

```http
POST /api/v1/admin/versions
Content-Type: application/json

{
  "version": "v1.0.0",
  "git_tag": "v1.0.0",
  "description": "First release",
  "image_tag": "aam-service:v1.0.0"
}
```

**响应**: 201 Created
```json
{
  "version": "v1.0.0",
  "status": "available",
  "git_commit": "abc123",
  "git_branch": "main",
  "image_tag": "aam-service:v1.0.0",
  "created_at": "2025-01-14T10:00:00Z",
  "created_by": "admin"
}
```

### 获取版本详情

```http
GET /api/v1/admin/versions/{version}
```

**响应**:
```json
{
  "version": "v1.0.0",
  "status": "active",
  "git_commit": "abc123",
  "git_branch": "main",
  "git_tag": "v1.0.0",
  "image_tag": "aam-service:v1.0.0",
  "created_at": "2025-01-14T10:00:00Z",
  "created_by": "admin",
  "description": "First release",
  "config_snapshot": {...},
  "docker_compose_config": {...},
  "environment_variables": {...},
  "service_config": {...}
}
```

### 比较版本

```http
GET /api/v1/admin/versions/{v1}/compare/{v2}
```

**响应**:
```json
{
  "v1": "v1.0.0",
  "v2": "v1.1.0",
  "differences": {
    "docker_compose_config": {...},
    "environment_variables": {...},
    "service_config": {...}
  },
  "summary": {
    "total_changes": 5,
    "added": 2,
    "modified": 2,
    "deleted": 1
  }
}
```

### 获取活动版本

```http
GET /api/v1/admin/versions/active
```

**响应**:
```json
{
  "version": "v1.0.0",
  "status": "active",
  ...
}
```

### 删除版本

```http
DELETE /api/v1/admin/versions/{version}
```

**响应**: 204 No Content

---

## 部署管理 API

### 获取部署列表

```http
GET /api/v1/admin/deployments
```

**查询参数**:
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页数量，默认 20
- `version` (string, 可选): 版本号过滤
- `status` (string, 可选): 状态过滤 (`pending`, `in_progress`, `success`, `failed`, `rolled_back`)
- `operator_id` (int, 可选): 操作者 ID 过滤
- `start_time` (string, 可选): 开始时间（ISO 格式）
- `end_time` (string, 可选): 结束时间（ISO 格式）
- `sort_by` (string, 可选): 排序字段，默认 `deployment_time`
- `sort_order` (string, 可选): 排序顺序 (`asc`/`desc`)，默认 `desc`

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "version": "v1.0.0",
      "status": "success",
      "operator_id": 1,
      "operator_name": "admin",
      "deployment_time": "2025-01-14T10:00:00Z",
      "completed_time": "2025-01-14T10:05:00Z",
      "deployment_strategy": "blue_green",
      "config_snapshot": {...}
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### 获取部署详情

```http
GET /api/v1/admin/deployments/{deployment_id}
```

**响应**:
```json
{
  "id": 1,
  "version": "v1.0.0",
  "status": "success",
  "operator_id": 1,
  "operator_name": "admin",
  "deployment_time": "2025-01-14T10:00:00Z",
  "completed_time": "2025-01-14T10:05:00Z",
  "deployment_strategy": "blue_green",
  "config_snapshot": {...},
  "logs": "...",
  "error_message": null
}
```

### 部署版本

```http
POST /api/v1/admin/deployments/versions/{version}/deploy
Content-Type: application/json

{
  "version": "v1.0.0",
  "strategy": "blue_green",
  "config": {
    "health_check_timeout": 300,
    "traffic_switch_delay": 10
  },
  "preview": false
}
```

**部署策略**:
- `blue_green`: 蓝绿部署
- `rolling`: 滚动更新
- `canary`: 金丝雀部署

**响应**: 201 Created
```json
{
  "deployment_id": 1,
  "message": "部署已启动"
}
```

### 回滚版本

```http
POST /api/v1/admin/deployments/versions/{version}/rollback
Content-Type: application/json

{
  "target_version": "v0.9.0",
  "reason": "Rollback due to errors"
}
```

**响应**: 201 Created
```json
{
  "deployment_id": 2,
  "message": "回滚已启动"
}
```

### 切换活动版本

```http
POST /api/v1/admin/deployments/versions/active/switch?version=v1.0.0
```

**响应**: 200 OK
```json
{
  "message": "活动版本已切换"
}
```

### 获取部署状态

```http
GET /api/v1/admin/deployments/{deployment_id}/status
```

**响应**:
```json
{
  "id": 1,
  "status": "in_progress",
  "progress": 50.0,
  "current_step": "Deploying containers",
  "steps": [
    {"name": "Prepare", "status": "completed"},
    {"name": "Deploy", "status": "in_progress"},
    {"name": "Verify", "status": "pending"}
  ],
  "error_message": null
}
```

### 获取部署日志

```http
GET /api/v1/admin/deployments/{deployment_id}/logs?tail=1000
```

**查询参数**:
- `tail` (int, 可选): 返回最后 N 行日志，默认 1000，最大 10000

**响应**:
```json
{
  "deployment_id": 1,
  "logs": "Deployment started\nDeploying containers...\nDeployment completed"
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

### HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功，无返回内容
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权
- `403 Forbidden`: 无权限
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

**最后更新**: 2025-01-14

