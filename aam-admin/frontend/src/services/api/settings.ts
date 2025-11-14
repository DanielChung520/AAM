/**
 * @purpose: 系统设置 API 服务
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import apiClient from './client';
import { API_ENDPOINTS } from '@/config/api';
import type {
  SystemSettings,
  SystemSettingsUpdate,
  EnvironmentVariableList,
  EnvironmentVariableUpdate,
  SystemHealthStatus,
  BackupList,
  BackupRequest,
  BackupRestoreRequest,
} from '@/types/settings';

export const settingsApi = {
  /**
   * 获取系统配置
   */
  getSystemSettings: async (): Promise<SystemSettings> => {
    const response = await apiClient.get<SystemSettings>(
      API_ENDPOINTS.settings.systemSettings
    );
    return response.data;
  },

  /**
   * 更新系统配置
   */
  updateSystemSettings: async (
    request: SystemSettingsUpdate
  ): Promise<SystemSettings> => {
    const response = await apiClient.put<SystemSettings>(
      API_ENDPOINTS.settings.systemSettings,
      request
    );
    return response.data;
  },

  /**
   * 获取环境变量列表
   */
  getEnvironmentVariables: async (): Promise<EnvironmentVariableList> => {
    const response = await apiClient.get<EnvironmentVariableList>(
      API_ENDPOINTS.settings.environmentVariables
    );
    return response.data;
  },

  /**
   * 更新环境变量
   */
  updateEnvironmentVariable: async (
    key: string,
    request: EnvironmentVariableUpdate
  ): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.put<{ success: boolean; message: string }>(
      API_ENDPOINTS.settings.updateEnvironmentVariable(key),
      request
    );
    return response.data;
  },

  /**
   * 获取系统健康状态
   */
  getSystemHealth: async (): Promise<SystemHealthStatus> => {
    const response = await apiClient.get<SystemHealthStatus>(
      API_ENDPOINTS.settings.systemHealth
    );
    return response.data;
  },

  /**
   * 创建备份
   */
  createBackup: async (request: BackupRequest): Promise<BackupRecord> => {
    const response = await apiClient.post<BackupRecord>(
      API_ENDPOINTS.settings.createBackup,
      request
    );
    return response.data;
  },

  /**
   * 获取备份列表
   */
  getBackups: async (): Promise<BackupList> => {
    const response = await apiClient.get<BackupList>(
      API_ENDPOINTS.settings.backups
    );
    return response.data;
  },

  /**
   * 恢复备份
   */
  restoreBackup: async (
    backupId: string,
    request: BackupRestoreRequest
  ): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      API_ENDPOINTS.settings.restoreBackup(backupId),
      request
    );
    return response.data;
  },

  /**
   * 下载备份
   */
  downloadBackup: async (backupId: string): Promise<Blob> => {
    const response = await apiClient.get(
      API_ENDPOINTS.settings.downloadBackup(backupId),
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },
};

