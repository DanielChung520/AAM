/**
 * @purpose: 版本管理数据管理 Hook
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { versionApi } from '@/services/api/version';
import type {
  Version,
  VersionDetail,
  VersionCreateRequest,
  VersionListResponse,
  VersionCompareResult,
  VersionListParams,
} from '@/types/version';

const REFRESH_INTERVAL = 60000; // 60 秒

/**
 * 版本列表 Hook
 */
export const useVersions = (
  params?: VersionListParams,
  autoRefresh: boolean = false
) => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(params?.page || 1);
  const [pageSize, setPageSize] = useState(params?.page_size || 20);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchVersions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await versionApi.getVersions({
        ...params,
        page,
        page_size: pageSize,
      });
      setVersions(data.items);
      setTotal(data.total);
      setPage(data.page);
      setPageSize(data.page_size);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取版本列表失败'));
    } finally {
      setLoading(false);
    }
  }, [params, page, pageSize]);

  useEffect(() => {
    fetchVersions();

    if (autoRefresh) {
      const interval = setInterval(fetchVersions, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchVersions, autoRefresh]);

  return {
    versions,
    total,
    page,
    pageSize,
    totalPages,
    loading,
    error,
    refresh: fetchVersions,
    setPage,
    setPageSize,
  };
};

/**
 * 单个版本详情 Hook
 */
export const useVersion = (
  version: string | null,
  autoRefresh: boolean = false
) => {
  const [versionDetail, setVersionDetail] = useState<VersionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchVersion = useCallback(async () => {
    if (!version) {
      setVersionDetail(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await versionApi.getVersion(version);
      setVersionDetail(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('获取版本详情失败'));
    } finally {
      setLoading(false);
    }
  }, [version]);

  useEffect(() => {
    fetchVersion();

    if (autoRefresh && version) {
      const interval = setInterval(fetchVersion, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchVersion, autoRefresh, version]);

  return {
    version: versionDetail,
    loading,
    error,
    refresh: fetchVersion,
  };
};

/**
 * 活动版本 Hook
 */
export const useActiveVersion = (autoRefresh: boolean = true) => {
  const [activeVersion, setActiveVersion] = useState<Version | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchActiveVersion = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await versionApi.getActiveVersion();
      setActiveVersion(data);
    } catch (err) {
      // 如果没有活动版本，不视为错误
      if (err instanceof Error && err.message.includes('404')) {
        setActiveVersion(null);
      } else {
        setError(err instanceof Error ? err : new Error('获取活动版本失败'));
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchActiveVersion();

    if (autoRefresh) {
      const interval = setInterval(fetchActiveVersion, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchActiveVersion, autoRefresh]);

  return {
    activeVersion,
    loading,
    error,
    refresh: fetchActiveVersion,
  };
};

/**
 * 版本操作 Hook
 */
export const useVersionOperations = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const createVersion = useCallback(async (request: VersionCreateRequest): Promise<Version> => {
    try {
      setLoading(true);
      setError(null);
      const version = await versionApi.createVersion(request);
      return version;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('创建版本失败');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteVersion = useCallback(async (version: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      await versionApi.deleteVersion(version);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('删除版本失败');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const compareVersions = useCallback(
    async (v1: string, v2: string): Promise<VersionCompareResult> => {
      try {
        setLoading(true);
        setError(null);
        const result = await versionApi.compareVersions(v1, v2);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('比较版本失败');
        setError(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    loading,
    error,
    createVersion,
    deleteVersion,
    compareVersions,
  };
};

