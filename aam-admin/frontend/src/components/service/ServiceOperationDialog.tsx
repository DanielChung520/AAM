/**
 * @purpose: 服务操作确认对话框组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Modal,
  ModalDialog,
  ModalClose,
  Typography,
  Button,
  Textarea,
  Alert,
  Box,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import WarningIcon from '@mui/icons-material/Warning';
import type { ServiceName, ServiceOperationType } from '@/types/service';

export interface ServiceOperationDialogProps {
  open: boolean;
  serviceName: ServiceName;
  operation: ServiceOperationType;
  onConfirm: (reason?: string) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export const ServiceOperationDialog: React.FC<ServiceOperationDialogProps> = ({
  open,
  serviceName,
  operation,
  onConfirm,
  onCancel,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);

  const getOperationText = () => {
    switch (operation) {
      case 'start':
        return '启动';
      case 'stop':
        return '停止';
      case 'restart':
        return '重启';
      default:
        return '操作';
    }
  };

  const getWarningMessage = () => {
    switch (operation) {
      case 'start':
        return `确定要启动服务 "${serviceName}" 吗？`;
      case 'stop':
        return `确定要停止服务 "${serviceName}" 吗？此操作可能会影响系统正常运行。`;
      case 'restart':
        return `确定要重启服务 "${serviceName}" 吗？此操作会导致服务短暂中断。`;
      default:
        return `确定要对服务 "${serviceName}" 执行此操作吗？`;
    }
  };

  const getWarningColor = () => {
    switch (operation) {
      case 'stop':
        return 'danger';
      case 'restart':
        return 'warning';
      default:
        return 'warning';
    }
  };

  const handleConfirm = async () => {
    try {
      setError(null);
      await onConfirm(reason || undefined);
      setReason('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '操作失败');
    }
  };

  const handleCancel = () => {
    setReason('');
    setError(null);
    onCancel();
  };

  return (
    <Modal open={open} onClose={handleCancel}>
      <ModalDialog
        sx={{
          maxWidth: 500,
          width: '100%',
        }}
      >
        <ModalClose />
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <WarningIcon
            sx={{
              color: getWarningColor() === 'danger' ? 'danger.500' : 'warning.500',
              mr: 1,
            }}
          />
          <Typography level="title-lg">{getOperationText()}服务</Typography>
        </Box>

        <Alert color={getWarningColor()} sx={{ mb: 2 }}>
          {getWarningMessage()}
        </Alert>

        <Box sx={{ mb: 2 }}>
          <Typography level="body-sm" sx={{ mb: 1 }}>
            操作原因（可选）
          </Typography>
          <Textarea
            placeholder="请输入操作原因..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            minRows={3}
            maxRows={5}
            sx={{ width: '100%' }}
          />
        </Box>

        {error && (
          <Alert color="danger" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
          <Button variant="outlined" onClick={handleCancel} disabled={loading}>
            取消
          </Button>
          <Button
            color={getWarningColor() === 'danger' ? 'danger' : 'primary'}
            onClick={handleConfirm}
            loading={loading}
          >
            确认{getOperationText()}
          </Button>
        </Box>
      </ModalDialog>
    </Modal>
  );
};

export default ServiceOperationDialog;

