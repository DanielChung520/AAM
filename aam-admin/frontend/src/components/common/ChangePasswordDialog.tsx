/**
 * @purpose: 修改密码对话框组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-15
 * @lastModified: 2025-01-15
 */
import React, { useState } from 'react';
import {
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
  Box,
  FormControl,
  FormLabel,
  Input,
  Button,
  Alert,
  Typography,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import { authApi } from '@/services/api/auth';
import LockIcon from '@mui/icons-material/Lock';

interface ChangePasswordDialogProps {
  open: boolean;
  onClose: () => void;
}

export const ChangePasswordDialog: React.FC<ChangePasswordDialogProps> = ({
  open,
  onClose,
}) => {
  const { mode } = useColorScheme();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleClose = () => {
    // 重置表单
    setOldPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setError(null);
    setSuccess(null);
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // 验证新密码
    if (newPassword.length < 6) {
      setError('新密码长度至少为6个字符');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    if (oldPassword === newPassword) {
      setError('新密码不能与旧密码相同');
      return;
    }

    setLoading(true);

    try {
      await authApi.changePassword(oldPassword, newPassword);
      setSuccess('密码修改成功！');
      // 3秒后自动关闭
      setTimeout(() => {
        handleClose();
      }, 2000);
    } catch (err: unknown) {
      const axiosError = err as {
        response?: {
          status?: number;
          data?: { detail?: string; message?: string };
        };
        message?: string;
      };

      let errorMessage = '密码修改失败';
      if (axiosError.response?.data?.detail) {
        errorMessage = axiosError.response.data.detail;
      } else if (axiosError.message) {
        errorMessage = `错误: ${axiosError.message}`;
      }

      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog sx={{ maxWidth: 500, width: '100%' }}>
        <ModalClose />
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LockIcon />
            <Typography level="title-lg">修改密码</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {success && (
                <Alert color="success" variant="soft">
                  {success}
                </Alert>
              )}

              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              <FormControl required>
                <FormLabel>当前密码</FormLabel>
                <Input
                  type="password"
                  placeholder="请输入当前密码"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  required
                  disabled={loading}
                />
              </FormControl>

              <FormControl required>
                <FormLabel>新密码</FormLabel>
                <Input
                  type="password"
                  placeholder="请输入新密码（至少6个字符）"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  minLength={6}
                  disabled={loading}
                />
                <Typography level="body-xs" sx={{ color: 'text.tertiary', mt: 0.5 }}>
                  密码长度至少为6个字符
                </Typography>
              </FormControl>

              <FormControl required>
                <FormLabel>确认新密码</FormLabel>
                <Input
                  type="password"
                  placeholder="请再次输入新密码"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                  disabled={loading}
                />
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                <Button variant="outlined" onClick={handleClose} disabled={loading}>
                  取消
                </Button>
                <Button type="submit" loading={loading} disabled={!oldPassword || !newPassword || !confirmPassword}>
                  修改密码
                </Button>
              </Box>
            </Box>
          </form>
        </DialogContent>
      </ModalDialog>
    </Modal>
  );
};

export default ChangePasswordDialog;

