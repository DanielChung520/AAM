/**
 * @purpose: 版本管理 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  Version,
  VersionDetail,
  VersionCreateRequest,
  VersionListResponse,
  VersionCompareResult,
  VersionListParams,
} from '@/types/version';

export const versionApi = {
  /**
   * 获取版本列表
   */
  getVersions: async (params?: VersionListParams): Promise<VersionListResponse> => {
    const response = await apiClient.get<VersionListResponse>(
      API_ENDPOINTS.version.list,
      {
        params: {
          page: params?.page || 1,
          page_size: params?.page_size || 20,
          status: params?.status,
          search: params?.search,
          created_after: params?.created_after,
          created_before: params?.created_before,
          sort_by: params?.sort_by || 'created_at',
          sort_order: params?.sort_order || 'desc',
        },
      }
    );
    return response.data;
  },

  /**
   * 获取版本详情
   */
  getVersion: async (version: string): Promise<VersionDetail> => {
    const response = await apiClient.get<VersionDetail>(
      API_ENDPOINTS.version.detail(version)
    );
    return response.data;
  },

  /**
   * 创建新版本
   */
  createVersion: async (request: VersionCreateRequest): Promise<Version> => {
    const response = await apiClient.post<Version>(
      API_ENDPOINTS.version.create,
      request
    );
    return response.data;
  },

  /**
   * 删除版本
   */
  deleteVersion: async (version: string): Promise<void> => {
    await apiClient.delete(API_ENDPOINTS.version.delete(version));
  },

  /**
   * 比较两个版本
   */
  compareVersions: async (v1: string, v2: string): Promise<VersionCompareResult> => {
    const response = await apiClient.get<VersionCompareResult>(
      API_ENDPOINTS.version.compare(v1, v2)
    );
    return response.data;
  },

  /**
   * 获取当前活动版本
   */
  getActiveVersion: async (): Promise<Version> => {
    const response = await apiClient.get<Version>(API_ENDPOINTS.version.active);
    return response.data;
  },
};

