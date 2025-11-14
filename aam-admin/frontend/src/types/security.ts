/**
 * @purpose: 安全管理相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

// ==================== Token 管理相关类型 ====================

export type TokenStatus = 'active' | 'revoked' | 'expired';

export interface Token {
  id: number;
  token_hash: string;
  user_id?: number;
  name?: string;
  status: TokenStatus;
  issued_at: string;
  expires_at?: string;
  revoked_at?: string;
  last_used_at?: string;
  extra_data?: Record<string, unknown>;
}

export interface TokenCreateRequest {
  user_id?: number;
  name?: string;
  expires_hours?: number;
  extra_data?: Record<string, unknown>;
}

export interface TokenIssueResponse {
  token: string;
  token_record: Token;
}

export interface TokenRevokeRequest {
  reason?: string;
}

// ==================== 企业认证配置相关类型 ====================

export interface EnterpriseAuthConfig {
  enabled: boolean;
  secret_key?: string;
  secret_key_set: boolean;
}

export interface EnterpriseAuthConfigUpdate {
  enabled: boolean;
  secret_key?: string;
}

export interface EnterpriseAuthTestRequest {
  user_id: string;
  token?: string;
}

export interface EnterpriseAuthTestResponse {
  success: boolean;
  signature?: string;
  message: string;
}

// ==================== 审计日志相关类型 ====================

export type AuditAction =
  | 'create'
  | 'update'
  | 'delete'
  | 'login'
  | 'logout'
  | 'deploy'
  | 'rollback'
  | 'start_service'
  | 'stop_service'
  | 'restart_service';

export interface AuditLog {
  id: number;
  user_id?: number;
  username?: string;
  action: AuditAction;
  resource_type: string;
  resource_id?: string;
  description?: string;
  ip_address?: string;
  user_agent?: string;
  request_data?: Record<string, unknown>;
  response_data?: Record<string, unknown>;
  before_state?: Record<string, unknown>;
  after_state?: Record<string, unknown>;
  status?: string;
  error_message?: string;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
  page: number;
  page_size: number;
}

export interface AuditLogFilter {
  user_id?: number;
  action?: AuditAction;
  resource_type?: string;
  resource_id?: string;
  status?: string;
  start_time?: string;
  end_time?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface AuditLogDetail extends AuditLog {
  request_data?: Record<string, unknown>;
  response_data?: Record<string, unknown>;
  before_state?: Record<string, unknown>;
  after_state?: Record<string, unknown>;
}

export interface AuditLogStats {
  total_operations: number;
  success_count: number;
  failed_count: number;
  action_stats: Record<string, number>;
  user_stats: Array<{
    user_id: number;
    username: string;
    operation_count: number;
  }>;
}

export interface AuditLogTrend {
  trends: Array<{
    time: string;
    count: number;
    success_count: number;
    failed_count: number;
  }>;
  group_by: 'hour' | 'day' | 'week' | 'month';
}

export type ResourceType =
  | 'service'
  | 'config'
  | 'deployment'
  | 'token'
  | 'llm_provider'
  | 'user'
  | 'settings';

