/**
 * @purpose: 日志管理 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  LogSearchRequest,
  LogSearchResponse,
  LogExportRequest,
} from '@/types/logs';

export const logsApi = {
  /**
   * 搜索日志
   */
  searchLogs: async (request: LogSearchRequest): Promise<LogSearchResponse> => {
    const response = await apiClient.post<LogSearchResponse>(
      API_ENDPOINTS.logs.search,
      request
    );
    return response.data;
  },

  /**
   * 搜索日志（GET 方法）
   */
  searchLogsGet: async (params: LogSearchRequest): Promise<LogSearchResponse> => {
    const response = await apiClient.get<LogSearchResponse>(
      API_ENDPOINTS.logs.search,
      { params }
    );
    return response.data;
  },

  /**
   * 导出日志
   */
  exportLogs: async (
    request: LogExportRequest
  ): Promise<Blob> => {
    const response = await apiClient.post(
      API_ENDPOINTS.logs.export,
      request,
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },
};

