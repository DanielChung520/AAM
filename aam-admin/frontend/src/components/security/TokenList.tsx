/**
 * @purpose: Token 列表组件
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
  IconButton,
  Typography,
  Button,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import type { Token } from '@/types/security';

export interface TokenListProps {
  tokens: Token[];
  loading?: boolean;
  onRevoke?: (tokenId: number) => void;
  onViewDetail?: (tokenId: number) => void;
}

export const TokenList: React.FC<TokenListProps> = ({
  tokens,
  loading = false,
  onRevoke,
  onViewDetail,
}) => {
  const { mode } = useColorScheme();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'revoked':
        return 'danger';
      case 'expired':
        return 'neutral';
      default:
        return 'neutral';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '有效';
      case 'revoked':
        return '已撤销';
      case 'expired':
        return '已过期';
      default:
        return '未知';
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('zh-CN');
  };

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography>加载中...</Typography>
      </Box>
    );
  }

  if (tokens.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography level="body-md" color="neutral">
          暂无 Token 记录
        </Typography>
      </Box>
    );
  }

  return (
    <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
      <Table
        aria-label="Token 列表"
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
            <th style={{ width: '150px' }}>Token Hash</th>
            <th style={{ width: '100px' }}>用户 ID</th>
            <th style={{ width: '150px' }}>名称</th>
            <th style={{ width: '100px' }}>状态</th>
            <th style={{ width: '180px' }}>发行时间</th>
            <th style={{ width: '180px' }}>过期时间</th>
            <th style={{ width: '180px' }}>最后使用</th>
            <th style={{ width: '120px' }}>操作</th>
          </tr>
        </thead>
        <tbody>
          {tokens.map((token) => (
            <tr key={token.id}>
              <td>{token.id}</td>
              <td>
                <Typography level="body-sm" fontFamily="monospace">
                  {token.token_hash}
                </Typography>
              </td>
              <td>{token.user_id || '-'}</td>
              <td>{token.name || '-'}</td>
              <td>
                <Chip size="sm" color={getStatusColor(token.status)}>
                  {getStatusText(token.status)}
                </Chip>
              </td>
              <td>
                <Typography level="body-sm">{formatDate(token.issued_at)}</Typography>
              </td>
              <td>
                <Typography level="body-sm">{formatDate(token.expires_at)}</Typography>
              </td>
              <td>
                <Typography level="body-sm">{formatDate(token.last_used_at)}</Typography>
              </td>
              <td>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {onViewDetail && (
                    <IconButton
                      size="sm"
                      variant="plain"
                      color="neutral"
                      onClick={() => onViewDetail(token.id)}
                    >
                      <VisibilityIcon />
                    </IconButton>
                  )}
                  {onRevoke && token.status === 'active' && (
                    <IconButton
                      size="sm"
                      variant="plain"
                      color="danger"
                      onClick={() => onRevoke(token.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  )}
                </Box>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Sheet>
  );
};

