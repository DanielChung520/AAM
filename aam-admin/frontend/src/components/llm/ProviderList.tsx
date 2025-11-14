/**
 * @purpose: LLM Provider 列表组件（左侧面板）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { Box, List, ListItem, ListItemButton, Chip, Typography, Button } from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { LLMProvider, ProviderType } from '@/types/llm';

export interface ProviderListProps {
  providers: LLMProvider[];
  selectedProvider?: ProviderType;
  onSelectProvider: (providerType: ProviderType) => void;
  onAddProvider?: () => void;
  loading?: boolean;
}

export const ProviderList: React.FC<ProviderListProps> = ({
  providers,
  selectedProvider,
  onSelectProvider,
  onAddProvider,
  loading = false,
}) => {
  const { mode } = useColorScheme();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'inactive':
        return 'neutral';
      case 'error':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '活跃';
      case 'inactive':
        return '未激活';
      case 'error':
        return '错误';
      default:
        return '未知';
    }
  };

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        bgcolor: 'background.surface',
        borderRadius: 'sm',
        border: '1px solid',
        borderColor: 'divider',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography level="title-md">Provider 列表</Typography>
      </Box>
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {loading ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              加载中...
            </Typography>
          </Box>
        ) : providers.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
              暂无 Provider
            </Typography>
          </Box>
        ) : (
          <List>
            {providers.map((provider) => (
              <ListItem key={provider.provider_type}>
                <ListItemButton
                  selected={selectedProvider === provider.provider_type}
                  onClick={() => onSelectProvider(provider.provider_type)}
                  sx={{
                    '&.Mui-selected': {
                      bgcolor: 'primary.50',
                      '&:hover': {
                        bgcolor: 'primary.100',
                      },
                    },
                  }}
                >
                  <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography level="title-sm">{provider.provider_type.toUpperCase()}</Typography>
                      <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                        {provider.models.length} 个模型
                      </Typography>
                    </Box>
                    <Chip
                      color={getStatusColor(provider.status)}
                      size="sm"
                      variant="soft"
                    >
                      {getStatusText(provider.status)}
                    </Chip>
                  </Box>
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </Box>
      {onAddProvider && (
        <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Button fullWidth variant="outlined" onClick={onAddProvider}>
            + 添加 Provider
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ProviderList;

