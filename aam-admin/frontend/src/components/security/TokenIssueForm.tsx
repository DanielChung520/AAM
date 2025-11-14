/**
 * @purpose: Token 发行表单组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Sheet,
  FormControl,
  FormLabel,
  Input,
  Button,
  Typography,
  Textarea,
  Alert,
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import type { TokenCreateRequest, TokenIssueResponse } from '@/types/security';

export interface TokenIssueFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (request: TokenCreateRequest) => Promise<TokenIssueResponse>;
  loading?: boolean;
}

export const TokenIssueForm: React.FC<TokenIssueFormProps> = ({
  open,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [formData, setFormData] = useState<TokenCreateRequest>({
    user_id: undefined,
    name: '',
    expires_hours: 24,
    extra_data: undefined,
  });
  const [issuedToken, setIssuedToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIssuedToken(null);

    try {
      const response = await onSubmit(formData);
      setIssuedToken(response.token);
      // 重置表单
      setFormData({
        user_id: undefined,
        name: '',
        expires_hours: 24,
        extra_data: undefined,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : '发行 Token 失败');
    }
  };

  const handleCopyToken = () => {
    if (issuedToken) {
      navigator.clipboard.writeText(issuedToken);
    }
  };

  const handleClose = () => {
    setFormData({
      user_id: undefined,
      name: '',
      expires_hours: 24,
      extra_data: undefined,
    });
    setIssuedToken(null);
    setError(null);
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog sx={{ maxWidth: 500, width: '100%' }}>
        <ModalClose />
        <DialogTitle>发行 Token</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              {issuedToken && (
                <Alert color="success" variant="soft">
                  <Typography level="body-sm" sx={{ mb: 1 }}>
                    Token 发行成功！请妥善保管，此 Token 仅显示一次。
                  </Typography>
                  <Box
                    sx={{
                      display: 'flex',
                      gap: 1,
                      alignItems: 'center',
                      bgcolor: mode === 'dark' ? 'background.level1' : 'background.surface',
                      p: 1,
                      borderRadius: 'sm',
                    }}
                  >
                    <Typography
                      level="body-sm"
                      fontFamily="monospace"
                      sx={{ flex: 1, wordBreak: 'break-all' }}
                    >
                      {issuedToken}
                    </Typography>
                    <Button
                      size="sm"
                      variant="plain"
                      onClick={handleCopyToken}
                      startDecorator={<ContentCopyIcon />}
                    >
                      复制
                    </Button>
                  </Box>
                </Alert>
              )}

              <FormControl>
                <FormLabel>用户 ID（可选）</FormLabel>
                <Input
                  type="number"
                  value={formData.user_id || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      user_id: e.target.value ? parseInt(e.target.value, 10) : undefined,
                    })
                  }
                  placeholder="留空则创建通用 Token"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Token 名称</FormLabel>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="例如：API Token for Integration"
                />
              </FormControl>

              <FormControl>
                <FormLabel>有效期（小时）</FormLabel>
                <Input
                  type="number"
                  value={formData.expires_hours || 24}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      expires_hours: e.target.value ? parseInt(e.target.value, 10) : 24,
                    })
                  }
                  min={1}
                  max={8760}
                />
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                <Button variant="outlined" onClick={handleClose} disabled={loading}>
                  取消
                </Button>
                <Button type="submit" loading={loading}>
                  发行 Token
                </Button>
              </Box>
            </Box>
          </form>
        </DialogContent>
      </ModalDialog>
    </Modal>
  );
};

