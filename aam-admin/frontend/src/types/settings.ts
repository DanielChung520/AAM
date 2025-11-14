/**
 * @purpose: 系统设置相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export interface SystemSettings {
  app_name: string;
  app_version: string;
  debug: boolean;
  log_level: string;
  api_host: string;
  api_port: number;
  api_prefix: string;
  cors_origins: string[];
  database_url: string; // 只读
  docker_host?: string; // 只读
  docker_base_url?: string; // 只读
}

export interface SystemSettingsUpdate {
  app_name?: string;
  app_version?: string;
  debug?: boolean;
  log_level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  api_host?: string;
  api_port?: number;
  api_prefix?: string;
  cors_origins?: string[];
}

export interface EnvironmentVariable {
  key: string;
  value: string;
  is_sensitive: boolean;
  description?: string;
}

export interface EnvironmentVariableList {
  items: EnvironmentVariable[];
  total: number;
}

export interface EnvironmentVariableUpdate {
  value: string;
  description?: string;
}

export interface SystemHealthCheck {
  status: 'healthy' | 'warning' | 'unhealthy' | 'unknown';
  message: string;
  details: Record<string, unknown>;
}

export interface SystemHealthStatus {
  overall_status: 'healthy' | 'warning' | 'unhealthy';
  checks: {
    database?: SystemHealthCheck;
    docker?: SystemHealthCheck;
    aam_service?: SystemHealthCheck;
    disk?: SystemHealthCheck;
    memory?: SystemHealthCheck;
  };
  timestamp: string;
}

export interface BackupRecord {
  id: string;
  name: string;
  created_at: string;
  size: number;
  status: 'completed' | 'failed' | 'in_progress';
  includes: {
    database: boolean;
    config: boolean;
    versions: boolean;
  };
  description?: string;
}

export interface BackupList {
  items: BackupRecord[];
  total: number;
}

export interface BackupRequest {
  name?: string;
  include_database?: boolean;
  include_config?: boolean;
  include_versions?: boolean;
  description?: string;
}

export interface BackupRestoreRequest {
  backup_id: string;
  restore_database?: boolean;
  restore_config?: boolean;
  restore_versions?: boolean;
}

