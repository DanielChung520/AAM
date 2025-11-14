/**
 * @purpose: 服务管理 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  ServiceStatus,
  ServiceDetail,
  ServiceStats,
  ServiceHealth,
  ServiceOperationRequest,
  ServiceOperationResponse,
  ServiceName,
} from '@/types/service';

export const serviceApi = {
  /**
   * 获取服务列表
   */
  getServices: async (): Promise<ServiceStatus[]> => {
    const response = await apiClient.get<ServiceStatus[]>(
      API_ENDPOINTS.service.list
    );
    return response.data;
  },

  /**
   * 获取服务详情
   */
  getServiceDetail: async (serviceName: ServiceName): Promise<ServiceDetail> => {
    const response = await apiClient.get<ServiceDetail>(
      API_ENDPOINTS.service.detail(serviceName)
    );
    return response.data;
  },

  /**
   * 启动服务
   */
  startService: async (
    serviceName: ServiceName,
    request: ServiceOperationRequest
  ): Promise<ServiceOperationResponse> => {
    const response = await apiClient.post<ServiceOperationResponse>(
      API_ENDPOINTS.service.start(serviceName),
      request
    );
    return response.data;
  },

  /**
   * 停止服务
   */
  stopService: async (
    serviceName: ServiceName,
    request: ServiceOperationRequest
  ): Promise<ServiceOperationResponse> => {
    const response = await apiClient.post<ServiceOperationResponse>(
      API_ENDPOINTS.service.stop(serviceName),
      request
    );
    return response.data;
  },

  /**
   * 重启服务
   */
  restartService: async (
    serviceName: ServiceName,
    request: ServiceOperationRequest
  ): Promise<ServiceOperationResponse> => {
    const response = await apiClient.post<ServiceOperationResponse>(
      API_ENDPOINTS.service.restart(serviceName),
      request
    );
    return response.data;
  },

  /**
   * 获取服务资源统计
   */
  getServiceStats: async (serviceName: ServiceName): Promise<ServiceStats> => {
    const response = await apiClient.get<ServiceStats>(
      API_ENDPOINTS.service.stats(serviceName)
    );
    return response.data;
  },

  /**
   * 获取服务健康状态
   */
  getServiceHealth: async (serviceName: ServiceName): Promise<ServiceHealth> => {
    const response = await apiClient.get<ServiceHealth>(
      API_ENDPOINTS.service.health(serviceName)
    );
    return response.data;
  },
};

