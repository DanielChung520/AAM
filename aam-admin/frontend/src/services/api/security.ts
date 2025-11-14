/**
 * @purpose: 安全管理 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  Token,
  TokenCreateRequest,
  TokenIssueResponse,
  TokenRevokeRequest,
  EnterpriseAuthConfig,
  EnterpriseAuthConfigUpdate,
  EnterpriseAuthTestRequest,
  EnterpriseAuthTestResponse,
  AuditLog,
  AuditLogDetail,
  AuditLogListResponse,
  AuditLogFilter,
  AuditLogStats,
  AuditLogTrend,
} from '@/types/security';

export const securityApi = {
  /**
   * 获取 Token 列表
   */
  getTokens: async (params?: {
    user_id?: number;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<Token[]> => {
    const response = await apiClient.get<Token[]>(API_ENDPOINTS.security.tokens.list, {
      params,
    });
    return response.data;
  },

  /**
   * 发行 Token
   */
  issueToken: async (request: TokenCreateRequest): Promise<TokenIssueResponse> => {
    const response = await apiClient.post<TokenIssueResponse>(
      API_ENDPOINTS.security.tokens.issue,
      request
    );
    return response.data;
  },

  /**
   * 撤销 Token
   */
  revokeToken: async (
    tokenId: number,
    request: TokenRevokeRequest
  ): Promise<Token> => {
    const response = await apiClient.post<Token>(
      API_ENDPOINTS.security.tokens.revoke(tokenId),
      request
    );
    return response.data;
  },

  /**
   * 获取 Token 详情
   */
  getTokenDetail: async (tokenId: number): Promise<Token> => {
    const response = await apiClient.get<Token>(
      API_ENDPOINTS.security.tokens.detail(tokenId)
    );
    return response.data;
  },

  /**
   * 获取企业认证配置
   */
  getEnterpriseAuthConfig: async (): Promise<EnterpriseAuthConfig> => {
    const response = await apiClient.get<EnterpriseAuthConfig>(
      API_ENDPOINTS.security.enterpriseAuth.get
    );
    return response.data;
  },

  /**
   * 更新企业认证配置
   */
  updateEnterpriseAuthConfig: async (
    request: EnterpriseAuthConfigUpdate
  ): Promise<EnterpriseAuthConfig> => {
    const response = await apiClient.put<EnterpriseAuthConfig>(
      API_ENDPOINTS.security.enterpriseAuth.update,
      request
    );
    return response.data;
  },

  /**
   * 测试企业认证签名
   */
  testEnterpriseAuth: async (
    request: EnterpriseAuthTestRequest
  ): Promise<EnterpriseAuthTestResponse> => {
    const response = await apiClient.post<EnterpriseAuthTestResponse>(
      API_ENDPOINTS.security.enterpriseAuth.test,
      request
    );
    return response.data;
  },

  /**
   * 获取审计日志列表
   */
  getAuditLogs: async (filter?: AuditLogFilter): Promise<AuditLogListResponse> => {
    const response = await apiClient.get<AuditLogListResponse>(
      API_ENDPOINTS.security.auditLogs.list,
      {
        params: filter,
      }
    );
    return response.data;
  },

  /**
   * 获取审计日志详情
   */
  getAuditLogDetail: async (logId: number): Promise<AuditLogDetail> => {
    const response = await apiClient.get<AuditLogDetail>(
      API_ENDPOINTS.security.auditLogs.detail(logId)
    );
    return response.data;
  },

  /**
   * 导出审计日志
   */
  exportAuditLogs: async (
    filter?: AuditLogFilter & { format?: 'csv' | 'json' }
  ): Promise<Blob> => {
    const response = await apiClient.get(API_ENDPOINTS.security.auditLogs.export, {
      params: filter,
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * 获取审计统计信息
   */
  getAuditStats: async (params?: {
    start_time?: string;
    end_time?: string;
  }): Promise<AuditLogStats> => {
    const response = await apiClient.get<AuditLogStats>(
      API_ENDPOINTS.security.auditLogs.stats,
      {
        params,
      }
    );
    return response.data;
  },

  /**
   * 获取操作趋势数据
   */
  getAuditTrends: async (params?: {
    start_time?: string;
    end_time?: string;
    group_by?: 'hour' | 'day' | 'week' | 'month';
    action?: string;
  }): Promise<AuditLogTrend> => {
    const response = await apiClient.get<AuditLogTrend>(
      API_ENDPOINTS.security.auditLogs.trends,
      {
        params,
      }
    );
    return response.data;
  },
};

