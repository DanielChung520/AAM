/**
 * @purpose: 资源使用图表组件，使用 ECharts 显示 CPU、内存、磁盘使用情况
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useMemo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Box, Typography } from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { SystemMetrics } from '@/types/dashboard';

export interface ResourceChartProps {
  metrics: SystemMetrics | null;
  loading?: boolean;
  height?: number | string;
}

export const ResourceChart: React.FC<ResourceChartProps> = ({
  metrics,
  loading = false,
  height = 300,
}) => {
  const { mode } = useColorScheme();
  const isDark = mode === 'dark';

  const option = useMemo(() => {
    if (!metrics) {
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

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        backgroundColor: isDark ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.9)',
        borderColor: isDark ? '#333' : '#ddd',
        textStyle: {
          color: isDark ? '#fff' : '#000',
        },
      },
      legend: {
        data: ['CPU', '内存', '磁盘'],
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
        data: ['使用率 (%)'],
        axisLabel: {
          color: isDark ? '#fff' : '#000',
        },
        axisLine: {
          lineStyle: {
            color: isDark ? '#555' : '#ddd',
          },
        },
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: {
          color: isDark ? '#fff' : '#000',
          formatter: '{value}%',
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
          name: 'CPU',
          type: 'bar',
          data: [metrics.cpu_usage.toFixed(2)],
          itemStyle: {
            color: '#1976d2',
          },
        },
        {
          name: '内存',
          type: 'bar',
          data: [metrics.memory_usage.toFixed(2)],
          itemStyle: {
            color: '#388e3c',
          },
        },
        {
          name: '磁盘',
          type: 'bar',
          data: [metrics.disk_usage.toFixed(2)],
          itemStyle: {
            color: '#f57c00',
          },
        },
      ],
    };
  }, [metrics, isDark]);

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height,
          bgcolor: 'background.surface',
          borderRadius: 'sm',
        }}
      >
        <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
          加载中...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: '100%',
        height,
        bgcolor: 'background.surface',
        borderRadius: 'sm',
        p: 1,
      }}
    >
      <ReactECharts
        option={option}
        style={{ width: '100%', height: '100%' }}
        opts={{ renderer: 'canvas' }}
      />
    </Box>
  );
};

export default ResourceChart;

