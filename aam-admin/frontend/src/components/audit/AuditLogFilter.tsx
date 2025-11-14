/**
 * @purpose: 审计日志过滤器组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useCallback } from 'react';
import {
  Box,
  Sheet,
  FormControl,
  FormLabel,
  Select,
  Option,
  Input,
  Button,
  Chip,
  Stack,
  IconButton,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
import type { AuditLogFilter, AuditAction, ResourceType } from '@/types/security';

export interface AuditLogFilterProps {
  filter: AuditLogFilter;
  onFilterChange: (filter: AuditLogFilter) => void;
  onReset?: () => void;
}

const ACTION_OPTIONS: Array<{ value: AuditAction; label: string }> = [
  { value: 'create', label: '创建' },
  { value: 'update', label: '更新' },
  { value: 'delete', label: '删除' },
  { value: 'login', label: '登录' },
  { value: 'logout', label: '登出' },
  { value: 'deploy', label: '部署' },
  { value: 'rollback', label: '回滚' },
  { value: 'start_service', label: '启动服务' },
  { value: 'stop_service', label: '停止服务' },
  { value: 'restart_service', label: '重启服务' },
];

const RESOURCE_TYPE_OPTIONS: Array<{ value: ResourceType; label: string }> = [
  { value: 'service', label: '服务' },
  { value: 'config', label: '配置' },
  { value: 'deployment', label: '部署' },
  { value: 'token', label: 'Token' },
  { value: 'llm_provider', label: 'LLM Provider' },
  { value: 'user', label: '用户' },
  { value: 'settings', label: '设置' },
];

const STATUS_OPTIONS = [
  { value: 'success', label: '成功' },
  { value: 'failed', label: '失败' },
];

export const AuditLogFilter: React.FC<AuditLogFilterProps> = ({
  filter,
  onFilterChange,
  onReset,
}) => {
  const { mode } = useColorScheme();
  const [expanded, setExpanded] = useState(false);
  const [localFilter, setLocalFilter] = useState<AuditLogFilter>(filter);

  const handleFilterChange = useCallback(
    (key: keyof AuditLogFilter, value: unknown) => {
      const newFilter = { ...localFilter, [key]: value, page: 1 }; // 重置页码
      setLocalFilter(newFilter);
      onFilterChange(newFilter);
    },
    [localFilter, onFilterChange]
  );

  const handleReset = useCallback(() => {
    const resetFilter: AuditLogFilter = {
      page: 1,
      page_size: 20,
    };
    setLocalFilter(resetFilter);
    onFilterChange(resetFilter);
    onReset?.();
  }, [onFilterChange, onReset]);

  const hasActiveFilters = useCallback(() => {
    return !!(
      localFilter.action ||
      localFilter.resource_type ||
      localFilter.status ||
      localFilter.user_id ||
      localFilter.resource_id ||
      localFilter.keyword ||
      localFilter.start_time ||
      localFilter.end_time
    );
  }, [localFilter]);

  const activeFilterCount = hasActiveFilters() ? 1 : 0;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <Button
          variant={expanded ? 'solid' : 'outlined'}
          startDecorator={<FilterListIcon />}
          onClick={() => setExpanded(!expanded)}
          color={activeFilterCount > 0 ? 'primary' : 'neutral'}
        >
          过滤器
          {activeFilterCount > 0 && (
            <Chip size="sm" color="primary" sx={{ ml: 1 }}>
              {activeFilterCount}
            </Chip>
          )}
        </Button>

        {hasActiveFilters() && (
          <Button variant="outlined" color="neutral" onClick={handleReset} size="sm">
            <ClearIcon sx={{ mr: 0.5 }} />
            重置
          </Button>
        )}
      </Box>

      {expanded && (
        <Sheet
          variant="outlined"
          sx={{
            p: 2,
            borderRadius: 'sm',
            bgcolor: mode === 'dark' ? 'background.surface' : 'background.level1',
          }}
        >
          <Stack spacing={2}>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              {/* 操作类型 */}
              <FormControl>
                <FormLabel>操作类型</FormLabel>
                <Select
                  value={localFilter.action || null}
                  onChange={(_, value) => handleFilterChange('action', value)}
                  placeholder="全部"
                >
                  {ACTION_OPTIONS.map((option) => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </FormControl>

              {/* 资源类型 */}
              <FormControl>
                <FormLabel>资源类型</FormLabel>
                <Select
                  value={localFilter.resource_type || null}
                  onChange={(_, value) => handleFilterChange('resource_type', value)}
                  placeholder="全部"
                >
                  {RESOURCE_TYPE_OPTIONS.map((option) => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </FormControl>

              {/* 操作状态 */}
              <FormControl>
                <FormLabel>操作状态</FormLabel>
                <Select
                  value={localFilter.status || null}
                  onChange={(_, value) => handleFilterChange('status', value)}
                  placeholder="全部"
                >
                  {STATUS_OPTIONS.map((option) => (
                    <Option key={option.value} value={option.value}>
                      {option.label}
                    </Option>
                  ))}
                </Select>
              </FormControl>

              {/* 用户 ID */}
              <FormControl>
                <FormLabel>用户 ID</FormLabel>
                <Input
                  type="number"
                  value={localFilter.user_id || ''}
                  onChange={(e) =>
                    handleFilterChange('user_id', e.target.value ? parseInt(e.target.value, 10) : undefined)
                  }
                  placeholder="输入用户 ID"
                />
              </FormControl>

              {/* 资源 ID */}
              <FormControl>
                <FormLabel>资源 ID</FormLabel>
                <Input
                  value={localFilter.resource_id || ''}
                  onChange={(e) => handleFilterChange('resource_id', e.target.value || undefined)}
                  placeholder="输入资源 ID"
                />
              </FormControl>
            </Box>

            {/* 关键词搜索 */}
            <FormControl>
              <FormLabel>关键词搜索</FormLabel>
              <Input
                value={localFilter.keyword || ''}
                onChange={(e) => handleFilterChange('keyword', e.target.value || undefined)}
                placeholder="搜索描述或资源 ID"
                startDecorator={<SearchIcon />}
              />
            </FormControl>

            {/* 时间范围 */}
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
              <FormControl>
                <FormLabel>开始时间</FormLabel>
                <Input
                  type="datetime-local"
                  value={
                    localFilter.start_time
                      ? new Date(localFilter.start_time).toISOString().slice(0, 16)
                      : ''
                  }
                  onChange={(e) =>
                    handleFilterChange(
                      'start_time',
                      e.target.value ? new Date(e.target.value).toISOString() : undefined
                    )
                  }
                />
              </FormControl>

              <FormControl>
                <FormLabel>结束时间</FormLabel>
                <Input
                  type="datetime-local"
                  value={
                    localFilter.end_time
                      ? new Date(localFilter.end_time).toISOString().slice(0, 16)
                      : ''
                  }
                  onChange={(e) =>
                    handleFilterChange(
                      'end_time',
                      e.target.value ? new Date(e.target.value).toISOString() : undefined
                    )
                  }
                />
              </FormControl>
            </Box>
          </Stack>
        </Sheet>
      )}
    </Box>
  );
};

export default AuditLogFilter;

