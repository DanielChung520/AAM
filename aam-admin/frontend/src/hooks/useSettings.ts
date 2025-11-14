/**
 * @purpose: 系统设置相关的 Hooks
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { settingsApi } from '@/services/api/settings';
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

/**
 * 系统配置 Hook
 */
export const useSettings = () => {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsApi.getSystemSettings();
      setSettings(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取系统配置失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const updateSettings = useCallback(async (updates: SystemSettingsUpdate) => {
    try {
      setError(null);
      const data = await settingsApi.updateSystemSettings(updates);
      setSettings(data);
      return data;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('更新系统配置失败');
      setError(error);
      throw error;
    }
  }, []);

  return {
    settings,
    loading,
    error,
    fetchSettings,
    updateSettings,
  };
};

/**
 * 环境变量 Hook
 */
export const useEnvironmentVariables = () => {
  const [envVars, setEnvVars] = useState<EnvironmentVariableList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchEnvVars = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsApi.getEnvironmentVariables();
      setEnvVars(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取环境变量列表失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEnvVars();
  }, [fetchEnvVars]);

  const updateEnvVar = useCallback(
    async (key: string, request: EnvironmentVariableUpdate) => {
      try {
        setError(null);
        await settingsApi.updateEnvironmentVariable(key, request);
        // 刷新列表
        await fetchEnvVars();
      } catch (err) {
        const error = err instanceof Error ? err : new Error('更新环境变量失败');
        setError(error);
        throw error;
      }
    },
    [fetchEnvVars]
  );

  return {
    envVars,
    loading,
    error,
    fetchEnvVars,
    updateEnvVar,
  };
};

/**
 * 系统健康状态 Hook
 */
export const useSystemHealth = () => {
  const [health, setHealth] = useState<SystemHealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsApi.getSystemHealth();
      setHealth(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取系统健康状态失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return {
    health,
    loading,
    error,
    fetchHealth,
  };
};

/**
 * 备份管理 Hook
 */
export const useBackups = () => {
  const [backups, setBackups] = useState<BackupList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchBackups = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsApi.getBackups();
      setBackups(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取备份列表失败'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBackups();
  }, [fetchBackups]);

  const createBackup = useCallback(async (request: BackupRequest) => {
    try {
      setError(null);
      const backup = await settingsApi.createBackup(request);
      // 刷新列表
      await fetchBackups();
      return backup;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('创建备份失败');
      setError(error);
      throw error;
    }
  }, [fetchBackups]);

  const restoreBackup = useCallback(
    async (backupId: string, request: BackupRestoreRequest) => {
      try {
        setError(null);
        await settingsApi.restoreBackup(backupId, request);
        // 刷新列表
        await fetchBackups();
      } catch (err) {
        const error = err instanceof Error ? err : new Error('恢复备份失败');
        setError(error);
        throw error;
      }
    },
    [fetchBackups]
  );

  const downloadBackup = useCallback(async (backupId: string) => {
    try {
      setError(null);
      const blob = await settingsApi.downloadBackup(backupId);
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${backupId}.tar.gz`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('下载备份失败');
      setError(error);
      throw error;
    }
  }, []);

  return {
    backups,
    loading,
    error,
    fetchBackups,
    createBackup,
    restoreBackup,
    downloadBackup,
  };
};

