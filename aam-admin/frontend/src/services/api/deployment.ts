/**
 * @purpose: 部署管理 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  DeploymentRecord,
  DeploymentRequest,
  DeploymentPreviewResponse,
  DeploymentListResponse,
  DeploymentStatusResponse,
  RollbackRequest,
  DeploymentListParams,
} from '@/types/deployment';

export const deploymentApi = {
  /**
   * 获取部署历史列表
   */
  getDeployments: async (params?: DeploymentListParams): Promise<DeploymentListResponse> => {
    const response = await apiClient.get<DeploymentListResponse>(
      API_ENDPOINTS.deployment.list,
      {
        params: {
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          version: params?.version,
          status: params?.status,
          operator_id: params?.operator_id,
          start_time: params?.start_time,
          end_time: params?.end_time,
          sort_by: params?.sort_by || 'deployment_time',
          sort_order: params?.sort_order || 'desc',
        },
      }
    );
    return response.data;
  },

  /**
   * 获取部署详情
   */
  getDeployment: async (id: number): Promise<DeploymentRecord> => {
    const response = await apiClient.get<DeploymentRecord>(
      API_ENDPOINTS.deployment.detail(id)
    );
    return response.data;
  },

  /**
   * 部署指定版本
   */
  deployVersion: async (
    version: string,
    request: DeploymentRequest
  ): Promise<{ deployment_id: number; message: string }> => {
    const response = await apiClient.post<{ deployment_id: number; message: string }>(
      API_ENDPOINTS.deployment.deploy(version),
      request
    );
    return response.data;
  },

  /**
   * 预览部署
   */
  previewDeployment: async (
    version: string,
    request: DeploymentRequest
  ): Promise<DeploymentPreviewResponse> => {
    const previewRequest = { ...request, preview: true };
    const response = await apiClient.post<DeploymentPreviewResponse>(
      API_ENDPOINTS.deployment.deploy(version),
      previewRequest
    );
    return response.data;
  },

  /**
   * 回滚到指定版本
   */
  rollbackVersion: async (
    version: string,
    request: RollbackRequest
  ): Promise<{ deployment_id: number; message: string }> => {
    const response = await apiClient.post<{ deployment_id: number; message: string }>(
      API_ENDPOINTS.deployment.rollback(version),
      request
    );
    return response.data;
  },

  /**
   * 切换活动版本
   */
  switchActiveVersion: async (version: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      API_ENDPOINTS.deployment.switchActive,
      null,
      {
        params: { version },
      }
    );
    return response.data;
  },

  /**
   * 获取部署状态
   */
  getDeploymentStatus: async (id: number): Promise<DeploymentStatusResponse> => {
    const response = await apiClient.get<DeploymentStatusResponse>(
      API_ENDPOINTS.deployment.status(id)
    );
    return response.data;
  },

  /**
   * 获取部署日志
   */
  getDeploymentLogs: async (id: number, tail: number = 1000): Promise<{ deployment_id: number; logs: string }> => {
    const response = await apiClient.get<{ deployment_id: number; logs: string }>(
      API_ENDPOINTS.deployment.logs(id),
      {
        params: { tail },
      }
    );
    return response.data;
  },
};

