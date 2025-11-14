/**
 * @purpose: 审计日志页面，集成审计日志列表、过滤器、统计和详情
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  Stack,
  Sheet,
  Tabs,
  TabList,
  Tab,
  TabPanel,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import DownloadIcon from '@mui/icons-material/Download';
import { AuditLogTable } from '@/components/security/AuditLogTable';
import { AuditLogFilter } from '@/components/audit/AuditLogFilter';
import { AuditLogDetail } from '@/components/audit/AuditLogDetail';
import { AuditStats } from '@/components/audit/AuditStats';
import {
  useAuditLogs,
  useAuditLogDetail,
  useAuditStats,
  useAuditTrends,
  useAuditLogExport,
} from '@/hooks/useSecurity';
import type { AuditLogFilter as AuditLogFilterType } from '@/types/security';

export const AuditLogPage: React.FC = () => {
  const { mode } = useColorScheme();
  const [activeTab, setActiveTab] = useState(0);
  const [filter, setFilter] = useState<AuditLogFilterType>({
    page: 1,
    page_size: 20,
    sort_by: 'created_at',
    sort_order: 'desc',
  });
  const [selectedLogId, setSelectedLogId] = useState<number | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);

  // 计算时间范围（用于统计和趋势）
  const timeRange = useMemo(() => {
    return {
      start_time: filter.start_time,
      end_time: filter.end_time,
    };
  }, [filter.start_time, filter.end_time]);

  // Hooks
  const {
    logs,
    total,
    page,
    pageSize,
    loading: logsLoading,
    error: logsError,
    fetchLogs,
    handlePageChange,
  } = useAuditLogs(filter);

  const {
    log: logDetail,
    loading: detailLoading,
    error: detailError,
    fetchLogDetail,
    clearLog,
  } = useAuditLogDetail();

  const {
    stats,
    loading: statsLoading,
    error: statsError,
    fetchStats,
  } = useAuditStats(timeRange);

  const {
    trends,
    loading: trendsLoading,
    error: trendsError,
    fetchTrends,
  } = useAuditTrends({
    ...timeRange,
    group_by: 'day',
  });

  const { exporting, exportLogs } = useAuditLogExport();

  // 处理过滤器变化
  const handleFilterChange = useCallback(
    (newFilter: AuditLogFilterType) => {
      setFilter(newFilter);
      fetchLogs(newFilter);
    },
    [fetchLogs]
  );

  // 处理重置过滤器
  const handleResetFilter = useCallback(() => {
    const resetFilter: AuditLogFilterType = {
      page: 1,
      page_size: 20,
      sort_by: 'created_at',
      sort_order: 'desc',
    };
    setFilter(resetFilter);
    fetchLogs(resetFilter);
  }, [fetchLogs]);

  // 处理查看详情
  const handleViewDetail = useCallback(
    (logId: number) => {
      setSelectedLogId(logId);
      setDetailOpen(true);
      fetchLogDetail(logId);
    },
    [fetchLogDetail]
  );

  // 处理关闭详情
  const handleCloseDetail = useCallback(() => {
    setDetailOpen(false);
    setSelectedLogId(null);
    clearLog();
  }, [clearLog]);

  // 处理导出
  const handleExport = useCallback(async () => {
    try {
      await exportLogs({
        ...filter,
        format: 'csv',
      });
    } catch (err) {
      // 错误已在 Hook 中处理
    }
  }, [filter, exportLogs]);

  // 处理趋势分组变化
  const handleGroupByChange = useCallback(
    (groupBy: 'hour' | 'day' | 'week' | 'month') => {
      fetchTrends({
        ...timeRange,
        group_by: groupBy,
      });
    },
    [timeRange, fetchTrends]
  );

  // 处理操作类型过滤变化
  const handleActionFilterChange = useCallback(
    (action: string | null) => {
      fetchTrends({
        ...timeRange,
        group_by: 'day',
        action: action || undefined,
      });
    },
    [timeRange, fetchTrends]
  );

  // 更新表格以支持点击查看详情
  const handleTableRowClick = useCallback(
    (logId: number) => {
      handleViewDetail(logId);
    },
    [handleViewDetail]
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography level="h2">操作审计</Typography>
        <Button
          startDecorator={<DownloadIcon />}
          onClick={handleExport}
          loading={exporting}
          variant="outlined"
        >
          导出日志
        </Button>
      </Box>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value as number)}>
        <TabList>
          <Tab>审计日志</Tab>
          <Tab>统计分析</Tab>
        </TabList>

        {/* 审计日志 Tab */}
        <TabPanel value={0}>
          <Stack spacing={2}>
            {logsError && (
              <Alert color="danger" variant="soft">
                {logsError.message}
              </Alert>
            )}

            {/* 过滤器 */}
            <AuditLogFilter
              filter={filter}
              onFilterChange={handleFilterChange}
              onReset={handleResetFilter}
            />

            {/* 审计日志表格 */}
            <AuditLogTable
              logs={logs}
              total={total}
              page={page}
              pageSize={pageSize}
              loading={logsLoading}
              onPageChange={handlePageChange}
              onRowClick={handleTableRowClick}
            />
          </Stack>
        </TabPanel>

        {/* 统计分析 Tab */}
        <TabPanel value={1}>
          <Stack spacing={2}>
            {(statsError || trendsError) && (
              <Alert color="danger" variant="soft">
                {statsError?.message || trendsError?.message || '获取统计数据失败'}
              </Alert>
            )}

            {/* 统计和趋势 */}
            <AuditStats
              stats={stats}
              trends={trends}
              loading={statsLoading || trendsLoading}
              onGroupByChange={handleGroupByChange}
              onActionFilterChange={handleActionFilterChange}
            />
          </Stack>
        </TabPanel>
      </Tabs>

      {/* 审计日志详情抽屉 */}
      <AuditLogDetail
        log={logDetail}
        open={detailOpen}
        onClose={handleCloseDetail}
      />
    </Box>
  );
};

export default AuditLogPage;

