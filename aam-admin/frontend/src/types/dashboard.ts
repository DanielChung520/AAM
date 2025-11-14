/**
 * @purpose: 仪表盘相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export interface ServiceStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  version?: string;
  cpu_usage: number;
  memory_usage: number;
  uptime?: number;
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  memory_total: number;
  memory_used: number;
  disk_usage: number;
  disk_total: number;
  disk_used: number;
  timestamp: string;
}

export interface RecentOperation {
  id: number;
  action: string;
  resource_type: string;
  resource_id?: string;
  description?: string;
  operator: string;
  status: string;
  created_at: string;
}

export interface DashboardStats {
  total_services: number;
  running_services: number;
  total_providers: number;
  active_providers: number;
  current_version?: string;
  system_load: number;
}

