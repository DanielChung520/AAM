/**
 * @purpose: 版本管理相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export type VersionStatus = 'active' | 'available' | 'deprecated';

export interface Version {
  version: string;
  status: VersionStatus;
  git_commit?: string;
  git_branch?: string;
  git_tag?: string;
  image_tag?: string;
  created_at: string;
  created_by?: string;
  description?: string;
}

export interface VersionDetail extends Version {
  config_snapshot?: Record<string, unknown>;
  docker_compose_config?: Record<string, unknown>;
  environment_variables?: Record<string, string>;
  service_config?: Record<string, unknown>;
}

export interface VersionCreateRequest {
  version: string;
  git_tag?: string;
  description?: string;
  image_tag?: string;
}

export interface VersionListResponse {
  items: Version[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface VersionCompareResult {
  version1: string;
  version2: string;
  differences: Record<string, {
    added: string[];
    removed: string[];
    modified: string[];
  }>;
  summary: {
    added: number;
    removed: number;
    modified: number;
  };
}

export interface VersionFilter {
  status?: VersionStatus;
  search?: string;
  created_after?: string;
  created_before?: string;
}

export interface VersionListParams {
  page?: number;
  page_size?: number;
  status?: VersionStatus;
  search?: string;
  created_after?: string;
  created_before?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

