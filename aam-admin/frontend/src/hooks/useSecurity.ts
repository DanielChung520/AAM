/**
 * @purpose: 安全管理相关的 Hooks
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { securityApi } from '@/services/api/security';
import type {
  Token,
  TokenCreateRequest,
  TokenIssueResponse,
  TokenRevokeRequest,
  EnterpriseAuthConfig,
  EnterpriseAuthConfigUpdate,
  EnterpriseAuthTestRequest,
  AuditLog,
  AuditLogDetail,
  AuditLogListResponse,
  AuditLogFilter,
  AuditLogStats,
  AuditLogTrend,
} from '@/types/security';

/**
 * Token 管理 Hook
 */
export const useTokens = () => {
  const [tokens, setTokens] = useState<Token[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTokens = useCallback(async (params?: {
    user_id?: number;
    status?: string;
    limit?: number;
    offset?: number;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const data = await securityApi.getTokens(params);
      setTokens(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取 Token 列表失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTokens();
  }, [fetchTokens]);

  const issueToken = useCallback(async (request: TokenCreateRequest): Promise<TokenIssueResponse> => {
    try {
      setError(null);
      const response = await securityApi.issueToken(request);
      // 刷新列表
      await fetchTokens();
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('发行 Token 失败');
      setError(error);
      throw error;
    }
  }, [fetchTokens]);

  const revokeToken = useCallback(async (tokenId: number, request: TokenRevokeRequest = {}) => {
    try {
      setError(null);
      await securityApi.revokeToken(tokenId, request);
      // 刷新列表
      await fetchTokens();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('撤销 Token 失败');
      setError(error);
      throw error;
    }
  }, [fetchTokens]);

  return {
    tokens,
    loading,
    error,
    fetchTokens,
    issueToken,
    revokeToken,
  };
};

/**
 * 企业认证配置 Hook
 */
export const useEnterpriseAuth = () => {
  const [config, setConfig] = useState<EnterpriseAuthConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await securityApi.getEnterpriseAuthConfig();
      setConfig(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取企业认证配置失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const updateConfig = useCallback(async (request: EnterpriseAuthConfigUpdate) => {
    try {
      setError(null);
      const data = await securityApi.updateEnterpriseAuthConfig(request);
      setConfig(data);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('更新企业认证配置失败');
      setError(error);
      throw error;
    }
  }, []);

  const testAuth = useCallback(async (request: EnterpriseAuthTestRequest) => {
    try {
      setError(null);
      return await securityApi.testEnterpriseAuth(request);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('测试企业认证失败');
      setError(error);
      throw error;
    }
  }, []);

  return {
    config,
    loading,
    error,
    fetchConfig,
    updateConfig,
    testAuth,
  };
};

/**
 * 审计日志 Hook
 */
export const useAuditLogs = (filter?: AuditLogFilter) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(filter?.page || 1);
  const [pageSize, setPageSize] = useState(filter?.page_size || 20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchLogs = useCallback(async (currentFilter?: AuditLogFilter) => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        ...currentFilter,
        page: currentFilter?.page || page,
        page_size: currentFilter?.page_size || pageSize,
      };
      const data = await securityApi.getAuditLogs(params);
      setLogs(data.items);
      setTotal(data.total);
      setPage(data.page);
      setPageSize(data.page_size);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取审计日志失败'));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize]);

  useEffect(() => {
    fetchLogs(filter);
  }, [fetchLogs, filter]);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    fetchLogs({ ...filter, page: newPage });
  }, [filter, fetchLogs]);

  return {
    logs,
    total,
    page,
    pageSize,
    loading,
    error,
    fetchLogs,
    handlePageChange,
  };
};

/**
 * 审计日志详情 Hook
 */
export const useAuditLogDetail = () => {
  const [log, setLog] = useState<AuditLogDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchLogDetail = useCallback(async (logId: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await securityApi.getAuditLogDetail(logId);
      setLog(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取审计日志详情失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  const clearLog = useCallback(() => {
    setLog(null);
    setError(null);
  }, []);

  return {
    log,
    loading,
    error,
    fetchLogDetail,
    clearLog,
  };
};

/**
 * 审计统计 Hook
 */
export const useAuditStats = (timeRange?: { start_time?: string; end_time?: string }) => {
  const [stats, setStats] = useState<AuditLogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = useCallback(async (range?: { start_time?: string; end_time?: string }) => {
    try {
      setLoading(true);
      setError(null);
      const data = await securityApi.getAuditStats(range || timeRange);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取审计统计失败'));
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    fetchStats,
  };
};

/**
 * 审计趋势 Hook
 */
export const useAuditTrends = (params?: {
  start_time?: string;
  end_time?: string;
  group_by?: 'hour' | 'day' | 'week' | 'month';
  action?: string;
}) => {
  const [trends, setTrends] = useState<AuditLogTrend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchTrends = useCallback(async (trendParams?: {
    start_time?: string;
    end_time?: string;
    group_by?: 'hour' | 'day' | 'week' | 'month';
    action?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);
      const data = await securityApi.getAuditTrends(trendParams || params);
      setTrends(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取操作趋势失败'));
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    fetchTrends();
  }, [fetchTrends]);

  return {
    trends,
    loading,
    error,
    fetchTrends,
  };
};

/**
 * 审计日志导出 Hook
 */
export const useAuditLogExport = () => {
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const exportLogs = useCallback(async (
    filter?: AuditLogFilter & { format?: 'csv' | 'json' }
  ) => {
    try {
      setExporting(true);
      setError(null);
      const blob = await securityApi.exportAuditLogs(filter);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.${filter?.format || 'csv'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('导出审计日志失败');
      setError(error);
      throw error;
    } finally {
      setExporting(false);
    }
  }, []);

  return {
    exporting,
    error,
    exportLogs,
  };
};

