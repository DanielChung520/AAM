/**
 * @purpose: 审计统计组件，显示审计统计信息和操作趋势图表
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import {
  Box,
  Sheet,
  Typography,
  Grid,
  Card,
  CardContent,
  Stack,
  Select,
  Option,
  FormControl,
  FormLabel,
  Chip,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { AuditLogStats, AuditLogTrend } from '@/types/security';

export interface AuditStatsProps {
  stats: AuditLogStats | null;
  trends: AuditLogTrend | null;
  loading?: boolean;
  onGroupByChange?: (groupBy: 'hour' | 'day' | 'week' | 'month') => void;
  onActionFilterChange?: (action: string | null) => void;
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

export const AuditStats: React.FC<AuditStatsProps> = ({
  stats,
  trends,
  loading = false,
  onGroupByChange,
  onActionFilterChange,
}) => {
  const { mode } = useColorScheme();
  const isDark = mode === 'dark';
  const [groupBy, setGroupBy] = React.useState<'hour' | 'day' | 'week' | 'month'>('day');
  const [actionFilter, setActionFilter] = React.useState<string | null>(null);

  const handleGroupByChange = (value: 'hour' | 'day' | 'week' | 'month' | null) => {
    if (value) {
      setGroupBy(value);
      onGroupByChange?.(value);
    }
  };

  const handleActionFilterChange = (value: string | null) => {
    setActionFilter(value);
    onActionFilterChange?.(value);
  };

  const trendChartOption = useMemo(() => {
    if (!trends || trends.trends.length === 0) {
      return {
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'middle',
          textStyle: {
            color: isDark ? '#fff' : '#000',
          },
        },
      };
    }

    const timeLabels = trends.trends.map((t) => {
      const date = new Date(t.time);
      if (trends.group_by === 'hour') {
        return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit' });
      } else if (trends.group_by === 'day') {
        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
      } else if (trends.group_by === 'week') {
        return `第${Math.ceil(date.getDate() / 7)}周`;
      } else {
        return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit' });
      }
    });

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        borderColor: isDark ? '#333' : '#ddd',
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      legend: {
        data: ['总操作数', '成功', '失败'],
        top: 10,
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: timeLabels,
        axisLabel: {
          color: isDark ? '#fff' : '#000',
          rotate: trends.group_by === 'hour' ? 45 : 0,
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#555' : '#ddd',
          },
        },
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          color: isDark ? '#fff' : '#000',
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#555' : '#ddd',
          },
        },
        splitLine: {
          lineStyle: {
            color: isDark ? '#333' : '#eee',
          },
        },
      },
      series: [
        {
          name: '总操作数',
          type: 'line',
          data: trends.trends.map((t) => t.count),
          itemStyle: {
            color: '#1976d2',
          },
          smooth: true,
        },
        {
          name: '成功',
          type: 'line',
          data: trends.trends.map((t) => t.success_count),
          itemStyle: {
            color: '#388e3c',
          },
          smooth: true,
        },
        {
          name: '失败',
          type: 'line',
          data: trends.trends.map((t) => t.failed_count),
          itemStyle: {
            color: '#d32f2f',
          },
          smooth: true,
        },
      ],
    };
  }, [trends, isDark]);

  const actionStatsChartOption = useMemo(() => {
    if (!stats || !stats.action_stats || Object.keys(stats.action_stats).length === 0) {
      return {
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'middle',
          textStyle: {
            color: isDark ? '#fff' : '#000',
          },
        },
      };
    }

    const actionEntries = Object.entries(stats.action_stats).sort((a, b) => b[1] - a[1]);

    return {
      tooltip: {
        trigger: 'item',
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        borderColor: isDark ? '#333' : '#ddd',
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'middle',
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      series: [
        {
          name: '操作类型',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: isDark ? '#1a1a1a' : '#fff',
            borderWidth: 2,
          },
          label: {
            show: true,
            formatter: '{b}: {c}',
            color: isDark ? '#fff' : '#000',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
            },
          },
          data: actionEntries.map(([action, count]) => ({
            value: count,
            name: getActionText(action),
          })),
        },
      ],
    };
  }, [stats, isDark]);

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography level="body-sm" color="neutral">
          加载中...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* 统计卡片 */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                总操作数
              </Typography>
              <Typography level="h2" sx={{ color: 'primary.500' }}>
                {stats?.total_operations || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                成功操作
              </Typography>
              <Typography level="h2" sx={{ color: 'success.500' }}>
                {stats?.success_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                失败操作
              </Typography>
              <Typography level="h2" sx={{ color: 'danger.500' }}>
                {stats?.failed_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                成功率
              </Typography>
              <Typography level="h2" sx={{ color: 'primary.500' }}>
                {stats && stats.total_operations > 0
                  ? ((stats.success_count / stats.total_operations) * 100).toFixed(1)
                  : '0.0'}
                %
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 操作趋势图表 */}
      <Sheet variant="outlined" sx={{ p: 2, mb: 3, borderRadius: 'sm' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography level="title-md">操作趋势</Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControl size="sm" sx={{ minWidth: 120 }}>
              <FormLabel>分组方式</FormLabel>
              <Select value={groupBy} onChange={(_, value) => handleGroupByChange(value)}>
                <Option value="hour">按小时</Option>
                <Option value="day">按天</Option>
                <Option value="week">按周</Option>
                <Option value="month">按月</Option>
              </Select>
            </FormControl>
            <FormControl size="sm" sx={{ minWidth: 150 }}>
              <FormLabel>操作类型</FormLabel>
              <Select
                value={actionFilter}
                onChange={(_, value) => handleActionFilterChange(value)}
                placeholder="全部"
              >
                <Option value={null}>全部</Option>
                {stats?.action_stats &&
                  Object.keys(stats.action_stats).map((action) => (
                    <Option key={action} value={action}>
                      {getActionText(action)}
                    </Option>
                  ))}
              </Select>
            </FormControl>
          </Box>
        </Box>
        <ReactECharts
          option={trendChartOption}
          style={{ width: '100%', height: '300px' }}
          opts={{ renderer: 'canvas' }}
        />
      </Sheet>

      {/* 操作类型统计 */}
      <Grid container spacing={2}>
        <Grid xs={12} md={6}>
          <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
            <Typography level="title-md" sx={{ mb: 2 }}>
              操作类型统计
            </Typography>
            <ReactECharts
              option={actionStatsChartOption}
              style={{ width: '100%', height: '300px' }}
              opts={{ renderer: 'canvas' }}
            />
          </Sheet>
        </Grid>
        <Grid xs={12} md={6}>
          <Sheet variant="outlined" sx={{ p: 2, borderRadius: 'sm' }}>
            <Typography level="title-md" sx={{ mb: 2 }}>
              操作者统计（Top 10）
            </Typography>
            {stats?.user_stats && stats.user_stats.length > 0 ? (
              <Stack spacing={1}>
                {stats.user_stats.slice(0, 10).map((user, index) => (
                  <Box
                    key={user.user_id}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      p: 1,
                      borderRadius: 'sm',
                      bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip size="sm" color="primary" variant="soft">
                        #{index + 1}
                      </Chip>
                      <Typography level="body-sm" fontWeight="md">
                        {user.username || `用户 ${user.user_id}`}
                      </Typography>
                    </Box>
                    <Typography level="body-sm" color="neutral">
                      {user.operation_count} 次操作
                    </Typography>
                  </Box>
                ))}
              </Stack>
            ) : (
              <Typography level="body-sm" color="neutral" sx={{ textAlign: 'center', py: 4 }}>
                暂无数据
              </Typography>
            )}
          </Sheet>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AuditStats;

