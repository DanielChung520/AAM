/**
 * @purpose: 仪表盘 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  DashboardStats,
  ServiceStatus,
  SystemMetrics,
  RecentOperation,
} from '@/types/dashboard';

export const dashboardApi = {
  /**
   * 获取仪表盘统计概览
   */
  getStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>(
      API_ENDPOINTS.dashboard.stats
    );
    return response.data;
  },

  /**
   * 获取服务状态列表
   */
  getServices: async (): Promise<ServiceStatus[]> => {
    const response = await apiClient.get<ServiceStatus[]>(
      API_ENDPOINTS.dashboard.services
    );
    return response.data;
  },

  /**
   * 获取系统资源指标
   */
  getMetrics: async (): Promise<SystemMetrics> => {
    const response = await apiClient.get<SystemMetrics>(
      API_ENDPOINTS.dashboard.metrics
    );
    return response.data;
  },

  /**
   * 获取最近操作记录
   */
  getRecentOperations: async (
    limit: number = 10,
    hours: number = 24
  ): Promise<RecentOperation[]> => {
    const response = await apiClient.get<RecentOperation[]>(
      API_ENDPOINTS.dashboard.recentOperations,
      {
        params: { limit, hours },
      }
    );
    return response.data;
  },
};

