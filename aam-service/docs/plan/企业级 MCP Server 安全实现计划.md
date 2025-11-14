<!-- eb58245b-70a7-4af2-be46-830157d29184 992e6dd4-bae8-44d0-84f7-34d1caa33d1e -->
# 企业级 MCP Server 安全实现计划

## 目标

1. 安装 MCP SDK
2. 实现 JWT token 发行机制（AAM 发行）
3. 实现 token 验证机制（验证 user_id 和 token 绑定）
4. 实现 MCP Server 安全验证
5. 确保不同员工 user_id 的严格管制

## 安全设计原则

- **简化原则**：用户权限管理在外部，AAM 只负责 token 验证
- **Token 发行**：AAM 发行 JWT token，包含 user_id 信息
- **验证逻辑**：验证 user_id 存在且 token 是 AAM 发行的有效 token
- **严格管制**：确保 user_id 和 token 的绑定关系，防止越权访问

## 实施步骤

### 阶段一：安装 MCP SDK 和 JWT 依赖

**文件**: `requirements.txt`

添加依赖：

- `mcp` - MCP SDK
- `PyJWT` - JWT token 处理（如果还没有）
- `cryptography` - JWT 签名支持

**任务**:

1. 检查当前 requirements.txt 是否已有 PyJWT
2. 添加 MCP SDK 依赖
3. 添加 JWT 相关依赖（如果缺失）

### 阶段二：实现 JWT Token 服务

**文件**: `src/core/services/token_service.py` (新建)

**功能**:

1. **发行 Token** (`issue_token`)

   - 输入：user_id
   - 输出：JWT token（包含 user_id, exp, iat）
   - 使用 SECRET_KEY 签名

2. **验证 Token** (`verify_token`)

   - 输入：token, user_id
   - 验证：
     - Token 格式有效
     - Token 未过期
     - Token 签名正确（AAM 发行）
     - Token 中的 user_id 与请求的 user_id 匹配

3. **提取 user_id** (`extract_user_id`)

   - 从 token 中提取 user_id（用于验证）

**安全要点**:

- 使用 HS256 算法
- Token 有效期可配置（默认 24 小时）
- 包含 user_id 在 payload 中
- 使用 SECRET_KEY 签名

### 阶段三：扩展 SecuritySettings

**文件**: `src/config/settings.py`

**扩展 SecuritySettings**:

- `token_expire_hours: int = 24` - Token 有效期（小时）
- `token_issuer: str = "aam-agent"` - Token 发行者标识
- `enable_user_id_validation: bool = True` - 是否启用 user_id 验证

### 阶段四：实现 MCP Server 安全中间件

**文件**: `src/mcp_server/auth_middleware.py` (新建)

**功能**:

1. **Token 验证中间件**

   - 从 MCP 请求中提取 token
   - 验证 token 有效性
   - 验证 user_id 和 token 的绑定关系
   - 如果验证失败，返回错误

2. **User ID 验证**

   - 验证请求中的 user_id 与 token 中的 user_id 匹配
   - 防止越权访问（用户 A 的 token 不能访问用户 B 的数据）

### 阶段五：实现 MCP Server

**文件**: `src/mcp_server/server.py` (新建)

**核心功能**:

1. **初始化**

   - 依赖注入：memory_service, token_service
   - 注册 Tools 和 Resources
   - 集成安全中间件

2. **Tools 实现**

   - `enrich_context` - 检索 ChromaDB（需要 token 验证）
   - `archive_dialogue` - 归档对话（需要 token 验证）
   - `issue_token` - 发行 token（可选，用于测试或管理）

3. **安全验证流程**
   ```
   MCP 请求
     ↓
   提取 token 和 user_id
     ↓
   验证 token（TokenService.verify_token）
     ↓
   验证 user_id 匹配（防止越权）
     ↓
   执行业务逻辑
   ```


### 阶段六：更新 MCP 数据模型

**文件**: `src/models/api/mcp.py`

**扩展 PartialMCP**:

- 添加 `token: Optional[str]` 字段（可选，用于 MCP Server）
- 或者通过 MCP 请求的 metadata 传递 token

**注意**: MCP 协议可能需要在请求头或 metadata 中传递 token

### 阶段七：更新 MemoryService 安全验证

**文件**: `src/core/services/memory_service.py`

**在 enrich 和 archive 方法中添加**:

- Token 验证（如果提供）
- User ID 验证（确保 user_id 与 token 匹配）
- 日志记录（安全审计）

### 阶段八：创建 Token 管理 API（可选）

**文件**: `src/api/controllers/token_controller.py` (新建)

**功能**:

- `POST /v1/tokens/issue` - 发行 token（需要管理员权限或外部系统调用）
- `POST /v1/tokens/verify` - 验证 token（用于测试）

**安全**:

- Token 发行需要额外的认证（如管理员 API Key）
- 或者由外部系统调用（外部系统负责用户权限管理）

### 阶段九：更新配置和文档

**文件**:

- `.env.example` - 添加 token 相关配置示例
- `docs/plan/MCP-Server-安全实现.md` - 安全实现文档

**配置项**:

- `TOKEN_EXPIRE_HOURS=24` - Token 有效期
- `TOKEN_ISSUER=aam-agent` - Token 发行者
- `ENABLE_USER_ID_VALIDATION=true` - 启用 user_id 验证

### 阶段十：测试和验证

**测试文件**: `tests/unit/test_token_service.py` (新建)

**测试用例**:

1. Token 发行测试
2. Token 验证测试（有效 token）
3. Token 验证测试（过期 token）
4. Token 验证测试（无效签名）
5. User ID 匹配测试（正确）
6. User ID 匹配测试（不匹配 - 越权访问）

**测试文件**: `tests/integration/test_mcp_server_security.py` (新建)

**测试用例**:

1. MCP Server 启动测试
2. Token 验证中间件测试
3. 越权访问防护测试
4. Token 过期处理测试

## 安全机制设计

### Token 结构

```json
{
  "user_id": "user_123",
  "iss": "aam-agent",
  "iat": 1234567890,
  "exp": 1234654290
}
```

### 验证流程

```
1. 提取 token 和 user_id
2. 验证 token 格式
3. 验证 token 签名（使用 SECRET_KEY）
4. 验证 token 未过期
5. 验证 token 中的 user_id 与请求的 user_id 匹配
6. 执行业务逻辑
```

### 安全日志

- 记录所有 token 验证失败（包括越权访问尝试）
- 记录 token 发行事件
- 记录 user_id 验证失败

## 文件清单

### 新建文件

- `src/core/services/token_service.py` - Token 服务
- `src/mcp_server/__init__.py` - MCP Server 包初始化
- `src/mcp_server/server.py` - MCP Server 实现
- `src/mcp_server/auth_middleware.py` - 安全中间件
- `src/api/controllers/token_controller.py` - Token 管理 API（可选）
- `tests/unit/test_token_service.py` - Token 服务单元测试
- `tests/integration/test_mcp_server_security.py` - MCP Server 安全集成测试
- `docs/plan/MCP-Server-安全实现.md` - 安全实现文档

### 修改文件

- `requirements.txt` - 添加 MCP 和 JWT 依赖
- `src/config/settings.py` - 扩展 SecuritySettings
- `src/models/api/mcp.py` - 扩展 MCP 模型（如果需要）
- `src/core/services/memory_service.py` - 添加安全验证
- `.env.example` - 添加 token 配置示例

## 实施优先级

1. **高优先级**：阶段一、二、三（基础依赖和 Token 服务）
2. **高优先级**：阶段四、五（MCP Server 和安全验证）
3. **中优先级**：阶段六、七（数据模型和业务逻辑集成）
4. **低优先级**：阶段八、九、十（可选功能和测试）

## 安全最佳实践

1. **Token 存储**：不在日志中记录完整 token，只记录前 8 位
2. **Token 传输**：使用 HTTPS（生产环境）
3. **Token 刷新**：支持 token 刷新机制（可选）
4. **审计日志**：记录所有安全相关事件
5. **错误处理**：不泄露敏感信息（如 token 签名密钥）

## 注意事项

1. **MCP 协议限制**：MCP 协议可能不支持直接在请求中传递 token，需要查看 MCP SDK 文档确定最佳方式
2. **向后兼容**：保持现有 HTTP API 的兼容性
3. **性能考虑**：Token 验证不应显著影响性能
4. **测试覆盖**：确保安全测试覆盖所有边界情况

### To-dos

- [ ] 安装 MCP SDK 和 JWT 相关依赖（检查 requirements.txt，添加 mcp、PyJWT、cryptography）
- [ ] 实现 TokenService（发行 token、验证 token、提取 user_id）
- [ ] 扩展 SecuritySettings（token_expire_hours、token_issuer、enable_user_id_validation）
- [ ] 实现 MCP Server 安全中间件（token 验证、user_id 匹配验证）
- [ ] 实现 MCP Server（enrich_context、archive_dialogue tools，集成安全中间件）
- [ ] 更新 MCP 数据模型（支持 token 传递，如果需要）
- [ ] 更新 MemoryService（添加 token 和 user_id 验证）
- [ ] 创建 Token 管理 API（发行 token 端点，可选）
- [ ] 更新配置文件和文档（.env.example、安全实现文档）
- [ ] 创建安全测试（TokenService 单元测试、MCP Server 安全集成测试）