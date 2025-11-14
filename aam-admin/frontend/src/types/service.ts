/**
 * @purpose: 服务管理相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export type ServiceStatusType = 'running' | 'stopped' | 'error';

export type ServiceOperationType = 'start' | 'stop' | 'restart';

export type ServiceName =
  | 'aam-service'
  | 'chromadb'
  | 'postgres'
  | 'rabbitmq';

export interface ServiceStatus {
  name: ServiceName;
  status: ServiceStatusType;
  version?: string;
  cpu_usage: number;
  memory_usage: number;
  uptime?: number;
}

export interface ServiceDetail {
  name: ServiceName;
  status: string;
  version?: string;
  container_id?: string;
  image?: string;
  ports: string[];
  cpu_usage: number;
  memory_usage: {
    used: number;
    limit: number;
    percent: number;
  };
  uptime?: number;
  created_at?: string;
  updated_at?: string;
}

export interface ServiceStats {
  service_name: ServiceName;
  cpu_usage: number;
  memory_usage: {
    used: number;
    limit: number;
    percent: number;
  };
  network_io?: {
    rx_bytes?: number;
    tx_bytes?: number;
  };
  disk_io?: {
    read_bytes?: number;
    write_bytes?: number;
  };
  timestamp: string;
}

export interface ServiceHealth {
  service_name: ServiceName;
  status: 'healthy' | 'unhealthy' | 'unknown';
  last_check: string;
  details?: {
    container_status?: string;
    cpu_usage?: number;
    memory_usage?: {
      used: number;
      limit: number;
      percent: number;
    };
    error?: string;
  };
}

export interface ServiceOperationRequest {
  confirm: boolean;
  reason?: string;
}

export interface ServiceOperationResponse {
  success: boolean;
  message: string;
  service_name: ServiceName;
  operation: ServiceOperationType;
  timestamp: string;
}

