/**
 * @purpose: 服务管理数据管理 Hook
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { serviceApi } from '@/services/api/service';
import type {
  ServiceStatus,
  ServiceDetail,
  ServiceStats,
  ServiceHealth,
  ServiceOperationRequest,
  ServiceOperationResponse,
  ServiceName,
  ServiceOperationType,
} from '@/types/service';

const REFRESH_INTERVAL = 30000; // 30 秒

export const useServices = (autoRefresh: boolean = true) => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await serviceApi.getServices();
      setServices(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();

    if (autoRefresh) {
      const interval = setInterval(fetchServices, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchServices, autoRefresh]);

  return { services, loading, error, refresh: fetchServices };
};

export const useService = (
  serviceName: ServiceName | null,
  autoRefresh: boolean = true
) => {
  const [service, setService] = useState<ServiceDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchService = useCallback(async () => {
    if (!serviceName) {
      setService(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await serviceApi.getServiceDetail(serviceName);
      setService(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [serviceName]);

  useEffect(() => {
    fetchService();

    if (autoRefresh && serviceName) {
      const interval = setInterval(fetchService, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchService, autoRefresh, serviceName]);

  return { service, loading, error, refresh: fetchService };
};

export const useServiceStats = (
  serviceName: ServiceName | null,
  autoRefresh: boolean = true
) => {
  const [stats, setStats] = useState<ServiceStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = useCallback(async () => {
    if (!serviceName) {
      setStats(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await serviceApi.getServiceStats(serviceName);
      setStats(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [serviceName]);

  useEffect(() => {
    fetchStats();

    if (autoRefresh && serviceName) {
      const interval = setInterval(fetchStats, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchStats, autoRefresh, serviceName]);

  return { stats, loading, error, refresh: fetchStats };
};

export const useServiceHealth = (
  serviceName: ServiceName | null,
  autoRefresh: boolean = true
) => {
  const [health, setHealth] = useState<ServiceHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchHealth = useCallback(async () => {
    if (!serviceName) {
      setHealth(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await serviceApi.getServiceHealth(serviceName);
      setHealth(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [serviceName]);

  useEffect(() => {
    fetchHealth();

    if (autoRefresh && serviceName) {
      const interval = setInterval(fetchHealth, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchHealth, autoRefresh, serviceName]);

  return { health, loading, error, refresh: fetchHealth };
};

export const useServiceOperation = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const operateService = useCallback(
    async (
      serviceName: ServiceName,
      operation: ServiceOperationType,
      request: ServiceOperationRequest
    ): Promise<ServiceOperationResponse | null> => {
      try {
        setLoading(true);
        setError(null);

        let response: ServiceOperationResponse;

        switch (operation) {
          case 'start':
            response = await serviceApi.startService(serviceName, request);
            break;
          case 'stop':
            response = await serviceApi.stopService(serviceName, request);
            break;
          case 'restart':
            response = await serviceApi.restartService(serviceName, request);
            break;
          default:
            throw new Error(`不支持的操作类型: ${operation}`);
        }

        return response;
      } catch (err) {
        setError(err as Error);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { operateService, loading, error };
};

