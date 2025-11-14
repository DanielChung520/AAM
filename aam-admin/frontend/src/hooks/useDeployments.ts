/**
 * @purpose: 部署管理数据管理 Hook
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { deploymentApi } from '@/services/api/deployment';
import type {
  DeploymentRecord,
  DeploymentRequest,
  DeploymentPreviewResponse,
  DeploymentStatusResponse,
  RollbackRequest,
  DeploymentListParams,
} from '@/types/deployment';

const REFRESH_INTERVAL = 5000; // 5 秒（部署状态需要频繁更新）
const STATUS_POLL_INTERVAL = 2000; // 2 秒（进行中的部署状态轮询）

/**
 * 部署历史列表 Hook
 */
export const useDeployments = (
  params?: DeploymentListParams,
  autoRefresh: boolean = false
) => {
  const [deployments, setDeployments] = useState<DeploymentRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(params?.page || 1);
  const [pageSize, setPageSize] = useState(params?.page_size || 20);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchDeployments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await deploymentApi.getDeployments({
        ...params,
        page,
        page_size: pageSize,
      });
      setDeployments(data.items);
      setTotal(data.total);
      setPage(data.page);
      setPageSize(data.page_size);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取部署列表失败'));
    } finally {
      setLoading(false);
    }
  }, [params, page, pageSize]);

  useEffect(() => {
    fetchDeployments();

    if (autoRefresh) {
      const interval = setInterval(fetchDeployments, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchDeployments, autoRefresh]);

  return {
    deployments,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    refresh: fetchDeployments,
    setPage,
    setPageSize,
  };
};

/**
 * 单个部署详情 Hook
 */
export const useDeployment = (
  id: number | null,
  autoRefresh: boolean = false
) => {
  const [deployment, setDeployment] = useState<DeploymentRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchDeployment = useCallback(async () => {
    if (!id) {
      setDeployment(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await deploymentApi.getDeployment(id);
      setDeployment(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取部署详情失败'));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDeployment();

    if (autoRefresh && id) {
      const interval = setInterval(fetchDeployment, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchDeployment, autoRefresh, id]);

  return {
    deployment,
    loading,
    error,
    refresh: fetchDeployment,
  };
};

/**
 * 部署状态 Hook（支持轮询）
 */
export const useDeploymentStatus = (
  id: number | null,
  autoPoll: boolean = true
) => {
  const [status, setStatus] = useState<DeploymentStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStatus = useCallback(async () => {
    if (!id) {
      setStatus(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await deploymentApi.getDeploymentStatus(id);
      setStatus(data);

      // 如果部署已完成或失败，停止轮询
      if (
        data.status === 'success' ||
        data.status === 'failed' ||
        data.status === 'rolled_back'
      ) {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取部署状态失败'));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchStatus();

    if (autoPoll && id) {
      // 开始轮询
      pollingRef.current = setInterval(fetchStatus, STATUS_POLL_INTERVAL);

      return () => {
        if (pollingRef.current) {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
      };
    }
  }, [fetchStatus, autoPoll, id]);

  return {
    status,
    loading,
    error,
    refresh: fetchStatus,
  };
};

/**
 * 部署操作 Hook
 */
export const useDeploymentOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const deployVersion = useCallback(
    async (version: string, request: DeploymentRequest): Promise<number> => {
      try {
        setLoading(true);
        setError(null);
        const response = await deploymentApi.deployVersion(version, request);
        return response.deployment_id;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('部署失败');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const previewDeployment = useCallback(
    async (
      version: string,
      request: DeploymentRequest
    ): Promise<DeploymentPreviewResponse> => {
      try {
        setLoading(true);
        setError(null);
        const preview = await deploymentApi.previewDeployment(version, request);
        return preview;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('预览部署失败');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const rollbackVersion = useCallback(
    async (version: string, request: RollbackRequest): Promise<number> => {
      try {
        setLoading(true);
        setError(null);
        const response = await deploymentApi.rollbackVersion(version, request);
        return response.deployment_id;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('回滚失败');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const switchActiveVersion = useCallback(async (version: string): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      const response = await deploymentApi.switchActiveVersion(version);
      return response.success;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('切换活动版本失败');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getDeploymentLogs = useCallback(async (id: number, tail: number = 1000): Promise<string> => {
    try {
      setLoading(true);
      setError(null);
      const response = await deploymentApi.getDeploymentLogs(id, tail);
      return response.logs;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('获取部署日志失败');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    deployVersion,
    previewDeployment,
    rollbackVersion,
    switchActiveVersion,
    getDeploymentLogs,
  };
};

