/**
 * @purpose: 日志管理相关的 TypeScript 类型定义
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */

import type { ServiceName } from './service';

export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  service: ServiceName | string;
  message: string;
  raw?: string;
}

export interface LogSearchRequest {
  service?: ServiceName | string;
  level?: LogLevel;
  start_time?: string;
  end_time?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
}

export interface LogSearchResponse {
  items: LogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LogFilter {
  service?: ServiceName | string;
  level?: LogLevel;
  startTime?: Date;
  endTime?: Date;
  keyword?: string;
}

export interface LogExportRequest {
  service?: ServiceName | string;
  level?: LogLevel;
  start_time?: string;
  end_time?: string;
  keyword?: string;
  format?: 'json' | 'csv';
}

export interface WebSocketLogMessage {
  type: 'log' | 'error' | 'paused' | 'resumed';
  data?: string;
  message?: string;
}

