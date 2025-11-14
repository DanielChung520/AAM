/**
 * @purpose: 审计日志详情组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useMemo } from 'react';
import {
  Box,
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerOverlay,
  Typography,
  Sheet,
  Chip,
  Divider,
  Stack,
  Table,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { AuditLogDetail as AuditLogDetailType } from '@/types/security';

export interface AuditLogDetailProps {
  log: AuditLogDetailType | null;
  open: boolean;
  onClose: () => void;
}

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

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const formatJSON = (obj: unknown): string => {
  if (!obj) return '';
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
};

const DiffView: React.FC<{ before?: Record<string, unknown>; after?: Record<string, unknown> }> = ({
  before,
  after,
}) => {
  const { mode } = useColorScheme();

  const diffEntries = useMemo(() => {
    if (!before && !after) return [];
    const allKeys = new Set([
      ...(before ? Object.keys(before) : []),
      ...(after ? Object.keys(after) : []),
    ]);

    return Array.from(allKeys).map((key) => {
      const beforeValue = before?.[key];
      const afterValue = after?.[key];
      const beforeStr = formatJSON(beforeValue);
      const afterStr = formatJSON(afterValue);

      let changeType: 'added' | 'removed' | 'modified' | 'unchanged' = 'unchanged';
      if (beforeValue === undefined && afterValue !== undefined) {
        changeType = 'added';
      } else if (beforeValue !== undefined && afterValue === undefined) {
        changeType = 'removed';
      } else if (beforeStr !== afterStr) {
        changeType = 'modified';
      }

      return { key, beforeValue, afterValue, beforeStr, afterStr, changeType };
    });
  }, [before, after]);

  if (diffEntries.length === 0) {
    return (
      <Typography level="body-sm" color="neutral">
        无状态变化
      </Typography>
    );
  }

  return (
    <Box sx={{ overflow: 'auto' }}>
      <Table
        aria-label="状态对比表"
        sx={{
          '& th': {
            fontWeight: 'bold',
            bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
          },
          '& td': {
            fontFamily: 'monospace',
            fontSize: '0.875rem',
          },
        }}
      >
        <thead>
          <tr>
            <th style={{ width: '150px' }}>字段</th>
            <th style={{ width: '40%' }}>操作前</th>
            <th style={{ width: '40%' }}>操作后</th>
            <th style={{ width: '100px' }}>变化</th>
          </tr>
        </thead>
        <tbody>
          {diffEntries.map((entry) => (
            <tr key={entry.key}>
              <td>
                <Typography level="body-sm" fontWeight="md">
                  {entry.key}
                </Typography>
              </td>
              <td>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 'sm',
                    bgcolor:
                      entry.changeType === 'removed' || entry.changeType === 'modified'
                        ? mode === 'dark'
                          ? 'danger.900'
                          : 'danger.50'
                        : 'transparent',
                    color:
                      entry.changeType === 'removed' || entry.changeType === 'modified'
                        ? mode === 'dark'
                          ? 'danger.300'
                          : 'danger.700'
                        : 'text.primary',
                  }}
                >
                  {entry.beforeStr || '-'}
                </Box>
              </td>
              <td>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 'sm',
                    bgcolor:
                      entry.changeType === 'added' || entry.changeType === 'modified'
                        ? mode === 'dark'
                          ? 'success.900'
                          : 'success.50'
                        : 'transparent',
                    color:
                      entry.changeType === 'added' || entry.changeType === 'modified'
                        ? mode === 'dark'
                          ? 'success.300'
                          : 'success.700'
                        : 'text.primary',
                  }}
                >
                  {entry.afterStr || '-'}
                </Box>
              </td>
              <td>
                {entry.changeType === 'added' && (
                  <Chip size="sm" color="success" variant="soft">
                    新增
                  </Chip>
                )}
                {entry.changeType === 'removed' && (
                  <Chip size="sm" color="danger" variant="soft">
                    删除
                  </Chip>
                )}
                {entry.changeType === 'modified' && (
                  <Chip size="sm" color="warning" variant="soft">
                    修改
                  </Chip>
                )}
                {entry.changeType === 'unchanged' && (
                  <Chip size="sm" color="neutral" variant="soft">
                    未变
                  </Chip>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Box>
  );
};

export const AuditLogDetail: React.FC<AuditLogDetailProps> = ({ log, open, onClose }) => {
  const { mode } = useColorScheme();

  if (!log) {
    return null;
  }

  return (
    <Drawer open={open} onClose={onClose} anchor="right" size="lg">
      <DrawerOverlay />
      <DrawerContent>
        <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography level="h3">审计日志详情</Typography>
            <DrawerClose />
          </Box>

          <Divider sx={{ my: 2 }} />

          <Stack spacing={3}>
            {/* 基本信息 */}
            <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
              <Typography level="title-md" sx={{ mb: 2 }}>
                基本信息
              </Typography>
              <Stack spacing={1.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    日志 ID
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {log.id}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    操作时间
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {formatDate(log.created_at)}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    操作者
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {log.username || log.user_id || '-'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    操作类型
                  </Typography>
                  <Chip size="sm" variant="soft">
                    {getActionText(log.action)}
                  </Chip>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    资源类型
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {log.resource_type}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    资源 ID
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {log.resource_id || '-'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    操作状态
                  </Typography>
                  {log.status && (
                    <Chip size="sm" color={getStatusColor(log.status)}>
                      {log.status === 'success' ? '成功' : '失败'}
                    </Chip>
                  )}
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography level="body-sm" color="neutral">
                    IP 地址
                  </Typography>
                  <Typography level="body-sm" fontWeight="md">
                    {log.ip_address || '-'}
                  </Typography>
                </Box>
                {log.user_agent && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography level="body-sm" color="neutral">
                      用户代理
                    </Typography>
                    <Typography level="body-sm" fontWeight="md" sx={{ maxWidth: '60%', textAlign: 'right' }}>
                      {log.user_agent}
                    </Typography>
                  </Box>
                )}
                {log.description && (
                  <Box>
                    <Typography level="body-sm" color="neutral" sx={{ mb: 0.5 }}>
                      描述
                    </Typography>
                    <Typography level="body-sm">{log.description}</Typography>
                  </Box>
                )}
                {log.error_message && (
                  <Box>
                    <Typography level="body-sm" color="danger" sx={{ mb: 0.5 }}>
                      错误信息
                    </Typography>
                    <Typography level="body-sm" color="danger">
                      {log.error_message}
                    </Typography>
                  </Box>
                )}
              </Stack>
            </Sheet>

            {/* 操作前后状态对比 */}
            {(log.before_state || log.after_state) && (
              <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
                <Typography level="title-md" sx={{ mb: 2 }}>
                  状态对比
                </Typography>
                <DiffView before={log.before_state} after={log.after_state} />
              </Sheet>
            )}

            {/* 请求数据 */}
            {log.request_data && (
              <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
                <Typography level="title-md" sx={{ mb: 2 }}>
                  请求数据
                </Typography>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 'sm',
                    bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    overflow: 'auto',
                    maxHeight: '300px',
                  }}
                >
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {formatJSON(log.request_data)}
                  </pre>
                </Box>
              </Sheet>
            )}

            {/* 响应数据 */}
            {log.response_data && (
              <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
                <Typography level="title-md" sx={{ mb: 2 }}>
                  响应数据
                </Typography>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 'sm',
                    bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    overflow: 'auto',
                    maxHeight: '300px',
                  }}
                >
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {formatJSON(log.response_data)}
                  </pre>
                </Box>
              </Sheet>
            )}
          </Stack>
        </Box>
      </DrawerContent>
    </Drawer>
  );
};

export default AuditLogDetail;

