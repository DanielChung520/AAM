/**
 * @purpose: 创建版本对话框组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
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
  RadioGroup,
  Radio,
  Checkbox,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import type { VersionCreateRequest } from '@/types/version';

export interface CreateVersionDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (request: VersionCreateRequest) => Promise<void>;
  loading?: boolean;
}

export const CreateVersionDialog: React.FC<CreateVersionDialogProps> = ({
  open,
  onClose,
  onSubmit,
  loading = false,
}) => {
  const { mode } = useColorScheme();
  const [formData, setFormData] = useState<VersionCreateRequest>({
    version: '',
    git_tag: undefined,
    description: '',
    image_tag: undefined,
  });
  const [createMode, setCreateMode] = useState<'manual' | 'git'>('manual');
  const [error, setError] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateVersion = (version: string): boolean => {
    if (!version) {
      setValidationError('版本号不能为空');
      return false;
    }

    if (!version.startsWith('v')) {
      setValidationError('版本号必须以 "v" 开头');
      return false;
    }

    const parts = version.substring(1).split('.');
    if (parts.length !== 3) {
      setValidationError('版本号格式应为 vMAJOR.MINOR.PATCH（如 v1.0.0）');
      return false;
    }

    try {
      const major = parseInt(parts[0], 10);
      const minor = parseInt(parts[1], 10);
      const patch = parseInt(parts[2], 10);

      if (isNaN(major) || isNaN(minor) || isNaN(patch)) {
        setValidationError('版本号各部分必须为数字');
        return false;
      }

      if (major < 0 || minor < 0 || patch < 0) {
        setValidationError('版本号各部分必须为非负整数');
        return false;
      }
    } catch {
      setValidationError('版本号格式无效');
      return false;
    }

    setValidationError(null);
    return true;
  };

  const handleVersionChange = (value: string) => {
    setFormData({ ...formData, version: value });
    if (value) {
      validateVersion(value);
    } else {
      setValidationError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!validateVersion(formData.version)) {
      return;
    }

    try {
      const request: VersionCreateRequest = {
        version: formData.version,
        description: formData.description || undefined,
        image_tag: formData.image_tag || undefined,
        git_tag: createMode === 'git' && formData.git_tag ? formData.git_tag : undefined,
      };

      await onSubmit(request);
      handleClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建版本失败');
    }
  };

  const handleClose = () => {
    setFormData({
      version: '',
      git_tag: undefined,
      description: '',
      image_tag: undefined,
    });
    setCreateMode('manual');
    setError(null);
    setValidationError(null);
    onClose();
  };

  return (
    <Modal open={open} onClose={handleClose}>
      <ModalDialog sx={{ maxWidth: 600, width: '100%' }}>
        <ModalClose />
        <DialogTitle>创建新版本</DialogTitle>
        <DialogContent>
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              {/* 创建模式选择 */}
              <FormControl>
                <FormLabel>创建模式</FormLabel>
                <RadioGroup
                  value={createMode}
                  onChange={(e) => setCreateMode(e.target.value as 'manual' | 'git')}
                  orientation="horizontal"
                >
                  <Radio value="manual" label="手动创建" />
                  <Radio value="git" label="基于 Git Tag" />
                </RadioGroup>
              </FormControl>

              {/* 版本号 */}
              <FormControl required error={!!validationError}>
                <FormLabel>版本号 *</FormLabel>
                <Input
                  placeholder="例如: v1.0.0"
                  value={formData.version}
                  onChange={(e) => handleVersionChange(e.target.value)}
                  disabled={loading}
                  error={!!validationError}
                />
                {validationError && (
                  <Typography level="body-xs" sx={{ color: 'danger.500', mt: 0.5 }}>
                    {validationError}
                  </Typography>
                )}
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  格式: vMAJOR.MINOR.PATCH（如 v1.0.0）
                </Typography>
              </FormControl>

              {/* Git Tag（仅在 Git 模式下显示） */}
              {createMode === 'git' && (
                <FormControl>
                  <FormLabel>Git Tag</FormLabel>
                  <Input
                    placeholder="例如: v1.0.0"
                    value={formData.git_tag || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, git_tag: e.target.value })
                    }
                    disabled={loading}
                  />
                  <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                    如果提供 Git Tag，将从 Git 获取相关信息
                  </Typography>
                </FormControl>
              )}

              {/* 镜像标签 */}
              <FormControl>
                <FormLabel>Docker 镜像标签</FormLabel>
                <Input
                  placeholder="例如: v1.0.0"
                  value={formData.image_tag || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, image_tag: e.target.value })
                  }
                  disabled={loading}
                />
                <Typography level="body-xs" sx={{ color: 'text.secondary', mt: 0.5 }}>
                  可选，如果不提供则使用版本号
                </Typography>
              </FormControl>

              {/* 描述 */}
              <FormControl>
                <FormLabel>版本描述</FormLabel>
                <Textarea
                  placeholder="输入版本描述..."
                  value={formData.description || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  disabled={loading}
                  minRows={3}
                />
              </FormControl>

              {/* 提交按钮 */}
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                <Button variant="outlined" onClick={handleClose} disabled={loading}>
                  取消
                </Button>
                <Button type="submit" disabled={loading || !!validationError}>
                  {loading ? '创建中...' : '创建版本'}
                </Button>
              </Box>
            </Box>
          </form>
        </DialogContent>
      </ModalDialog>
    </Modal>
  );
};

export default CreateVersionDialog;

