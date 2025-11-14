/**
 * @purpose: 仪表盘数据管理 Hook
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '@/services/api/dashboard';
import type {
  DashboardStats,
  ServiceStatus,
  SystemMetrics,
  RecentOperation,
} from '@/types/dashboard';

const REFRESH_INTERVAL = 30000; // 30 秒

export const useDashboardStats = (autoRefresh: boolean = true) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();

    if (autoRefresh) {
      const interval = setInterval(fetchStats, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchStats, autoRefresh]);

  return { stats, loading, error, refresh: fetchStats };
};

export const useServiceStatus = (autoRefresh: boolean = true) => {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchServices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardApi.getServices();
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

export const useSystemMetrics = (autoRefresh: boolean = true) => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardApi.getMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();

    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchMetrics, autoRefresh]);

  return { metrics, loading, error, refresh: fetchMetrics };
};

export const useRecentOperations = (
  limit: number = 10,
  hours: number = 24,
  autoRefresh: boolean = true
) => {
  const [operations, setOperations] = useState<RecentOperation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchOperations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardApi.getRecentOperations(limit, hours);
      setOperations(data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [limit, hours]);

  useEffect(() => {
    fetchOperations();

    if (autoRefresh) {
      const interval = setInterval(fetchOperations, REFRESH_INTERVAL);
      return () => clearInterval(interval);
    }
  }, [fetchOperations, autoRefresh]);

  return { operations, loading, error, refresh: fetchOperations };
};

