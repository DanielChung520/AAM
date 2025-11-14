/**
 * @purpose: 审计日志表格组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import {
  Box,
  Sheet,
  Table,
  Chip,
  Typography,
  Pagination,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { AuditLog } from '@/types/security';

export interface AuditLogTableProps {
  logs: AuditLog[];
  total: number;
  page: number;
  pageSize: number;
  loading?: boolean;
  onPageChange?: (page: number) => void;
  onRowClick?: (logId: number) => void;
}

export const AuditLogTable: React.FC<AuditLogTableProps> = ({
  logs,
  total,
  page,
  pageSize,
  loading = false,
  onPageChange,
  onRowClick,
}) => {
  const { mode } = useColorScheme();

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'failed':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const getActionText = (action: string) => {
    const actionMap: Record<string, string> = {
      create: '创建',
      update: '更新',
      delete: '删除',
      login: '登录',
      logout: '登出',
      deploy: '部署',
      rollback: '回滚',
      start_service: '启动服务',
      stop_service: '停止服务',
      restart_service: '重启服务',
    };
    return actionMap[action] || action;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('zh-CN');
  };

  const totalPages = Math.ceil(total / pageSize);

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>加载中...</Typography>
      </Box>
    );
  }

  if (logs.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography level="body-md" color="neutral">
          暂无审计日志
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
        <Table
          aria-label="审计日志表格"
          sx={{
            '& thead th': {
              fontWeight: 'bold',
              bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
            },
          }}
        >
          <thead>
            <tr>
              <th style={{ width: '60px' }}>ID</th>
              <th style={{ width: '120px' }}>用户</th>
              <th style={{ width: '120px' }}>操作</th>
              <th style={{ width: '150px' }}>资源类型</th>
              <th style={{ width: '150px' }}>资源 ID</th>
              <th style={{ width: '200px' }}>描述</th>
              <th style={{ width: '100px' }}>状态</th>
              <th style={{ width: '150px' }}>IP 地址</th>
              <th style={{ width: '180px' }}>时间</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr
                key={log.id}
                onClick={() => onRowClick?.(log.id)}
                style={{
                  cursor: onRowClick ? 'pointer' : 'default',
                }}
                onMouseEnter={(e) => {
                  if (onRowClick) {
                    e.currentTarget.style.backgroundColor =
                      mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (onRowClick) {
                    e.currentTarget.style.backgroundColor = 'transparent';
                  }
                }}
              >
                <td>{log.id}</td>
                <td>{log.username || log.user_id || '-'}</td>
                <td>
                  <Chip size="sm" variant="soft">
                    {getActionText(log.action)}
                  </Chip>
                </td>
                <td>{log.resource_type}</td>
                <td>{log.resource_id || '-'}</td>
                <td>
                  <Typography level="body-sm" sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {log.description || '-'}
                  </Typography>
                </td>
                <td>
                  {log.status && (
                    <Chip size="sm" color={getStatusColor(log.status)}>
                      {log.status === 'success' ? '成功' : '失败'}
                    </Chip>
                  )}
                </td>
                <td>
                  <Typography level="body-sm">{log.ip_address || '-'}</Typography>
                </td>
                <td>
                  <Typography level="body-sm">{formatDate(log.created_at)}</Typography>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Sheet>

      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => onPageChange?.(newPage)}
          />
        </Box>
      )}
    </Box>
  );
};

