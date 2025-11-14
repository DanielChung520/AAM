/**
 * @purpose: 部署管理相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export type DeploymentStatus = 'pending' | 'in_progress' | 'success' | 'failed' | 'rolled_back';

export type DeploymentStrategy = 'blue_green' | 'rolling' | 'canary';

export interface DeploymentRecord {
  id: number;
  version: string;
  status: DeploymentStatus;
  operator_id: number;
  operator_name?: string;
  deployment_time: string;
  completed_time?: string;
  rollback_version?: string;
  deployment_strategy?: DeploymentStrategy;
  config_snapshot?: Record<string, unknown>;
  error_message?: string;
  extra_data?: Record<string, unknown>;
}

export interface DeploymentRequest {
  version: string;
  strategy: DeploymentStrategy;
  config?: Record<string, unknown>;
  preview?: boolean;
}

export interface DeploymentPreviewResponse {
  version: string;
  strategy: DeploymentStrategy;
  config_valid: boolean;
  dependencies_ok: boolean;
  config_diff?: Record<string, unknown>;
  impact_analysis?: {
    affected_services?: string[];
    estimated_downtime?: number | null;
    rollback_available?: boolean;
  };
  warnings: string[];
  errors: string[];
}

export interface DeploymentListResponse {
  items: DeploymentRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DeploymentStatusResponse {
  id: number;
  status: DeploymentStatus;
  progress?: number;
  current_step?: string;
  steps: Array<{
    name: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
  }>;
  error_message?: string;
}

export interface RollbackRequest {
  version: string;
  reason?: string;
}

export interface DeploymentListParams {
  page?: number;
  page_size?: number;
  version?: string;
  status?: DeploymentStatus;
  operator_id?: number;
  start_time?: string;
  end_time?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// 部署策略配置类型
export interface BlueGreenConfig {
  health_check_timeout?: number;
  traffic_switch_delay?: number;
}

export interface RollingUpdateConfig {
  max_unavailable?: number;
  max_surge?: number;
  min_ready_seconds?: number;
}

export interface CanaryConfig {
  initial_traffic_percent?: number;
  traffic_increment_percent?: number;
  increment_interval_seconds?: number;
  max_error_rate?: number;
  max_response_time_ms?: number;
}

export type DeploymentConfig = BlueGreenConfig | RollingUpdateConfig | CanaryConfig;

