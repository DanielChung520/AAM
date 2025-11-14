/**
 * @purpose: API 配置
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8003',
  apiPrefix: '/api/v1',
  timeout: 30000,
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8003',
} as const;

export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    me: '/auth/me',
    changePassword: '/auth/change-password',
  },
  dashboard: {
    stats: '/dashboard/stats',
    services: '/dashboard/services',
    metrics: '/dashboard/metrics',
    recentOperations: '/dashboard/recent-operations',
  },
  llm: {
    providers: '/llm-providers',
  },
  service: {
    list: '/services',
    detail: (name: string) => `/services/${name}`,
    start: (name: string) => `/services/${name}/start`,
    stop: (name: string) => `/services/${name}/stop`,
    restart: (name: string) => `/services/${name}/restart`,
    stats: (name: string) => `/services/${name}/stats`,
    health: (name: string) => `/services/${name}/health`,
  },
  logs: {
    search: '/logs/search',
    export: '/logs/export',
    ws: (containerName: string) => `/ws/logs/${containerName}`,
  },
  security: {
    tokens: {
      list: '/security/tokens',
      issue: '/security/tokens/issue',
      revoke: (tokenId: number) => `/security/tokens/${tokenId}/revoke`,
      detail: (tokenId: number) => `/security/tokens/${tokenId}`,
    },
    enterpriseAuth: {
      get: '/security/enterprise-auth',
      update: '/security/enterprise-auth',
      test: '/security/enterprise-auth/test',
    },
    auditLogs: {
      list: '/admin/audit-logs',
      detail: (logId: number) => `/admin/audit-logs/${logId}`,
      export: '/admin/audit-logs/export',
      stats: '/admin/audit-logs/stats',
      trends: '/admin/audit-logs/trends',
    },
  },
  version: {
    list: '/admin/versions',
    detail: (version: string) => `/admin/versions/${version}`,
    create: '/admin/versions',
    delete: (version: string) => `/admin/versions/${version}`,
    compare: (v1: string, v2: string) => `/admin/versions/${v1}/compare/${v2}`,
    active: '/admin/versions/active',
  },
  deployment: {
    list: '/admin/deployments',
    detail: (id: number) => `/admin/deployments/${id}`,
    deploy: (version: string) => `/admin/deployments/versions/${version}/deploy`,
    rollback: (version: string) => `/admin/deployments/versions/${version}/rollback`,
    switchActive: '/admin/deployments/versions/active/switch',
    status: (id: number) => `/admin/deployments/${id}/status`,
    logs: (id: number) => `/admin/deployments/${id}/logs`,
  },
  settings: {
    systemSettings: '/admin/settings',
    environmentVariables: '/admin/settings/environment',
    updateEnvironmentVariable: (key: string) => `/admin/settings/environment/${key}`,
    systemHealth: '/admin/settings/health',
    createBackup: '/admin/settings/backup',
    backups: '/admin/settings/backups',
    restoreBackup: (backupId: string) => `/admin/settings/restore/${backupId}`,
    downloadBackup: (backupId: string) => `/admin/settings/backups/${backupId}/download`,
  },
} as const;

