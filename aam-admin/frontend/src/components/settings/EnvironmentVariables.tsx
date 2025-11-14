/**
 * @purpose: 环境变量管理组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Sheet,
  Typography,
  Table,
  Button,
  Input,
  IconButton,
  Chip,
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
  FormControl,
  FormLabel,
  Alert,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import type { EnvironmentVariable, EnvironmentVariableUpdate } from '@/types/settings';

export interface EnvironmentVariablesProps {
  envVars: EnvironmentVariable[];
  loading?: boolean;
  onUpdate: (key: string, request: EnvironmentVariableUpdate) => Promise<void>;
}

export const EnvironmentVariables: React.FC<EnvironmentVariablesProps> = ({
  envVars,
  loading = false,
  onUpdate,
}) => {
  const { mode } = useColorScheme();
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [visibleKeys, setVisibleKeys] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const handleEdit = (envVar: EnvironmentVariable) => {
    setEditingKey(envVar.key);
    setEditValue(envVar.is_sensitive ? '' : envVar.value);
    setEditDescription(envVar.description || '');
    setError(null);
  };

  const handleSave = async () => {
    if (!editingKey) return;

    try {
      setError(null);
      await onUpdate(editingKey, {
        value: editValue,
        description: editDescription || undefined,
      });
      setEditingKey(null);
      setEditValue('');
      setEditDescription('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '更新环境变量失败');
    }
  };

  const toggleVisibility = (key: string) => {
    const newVisible = new Set(visibleKeys);
    if (newVisible.has(key)) {
      newVisible.delete(key);
    } else {
      newVisible.add(key);
    }
    setVisibleKeys(newVisible);
  };

  return (
    <Box>
      <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
        <Table>
          <thead>
            <tr>
              <th style={{ width: '200px' }}>变量名</th>
              <th style={{ width: '300px' }}>变量值</th>
              <th style={{ width: '200px' }}>描述</th>
              <th style={{ width: '100px' }}>类型</th>
              <th style={{ width: '100px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {envVars.map((envVar) => (
              <tr key={envVar.key}>
                <td>
                  <Typography level="body-sm" fontWeight="md">
                    {envVar.key}
                  </Typography>
                </td>
                <td>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography
                      level="body-sm"
                      sx={{
                        fontFamily: 'monospace',
                        fontSize: '0.875rem',
                        maxWidth: '250px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                    >
                      {envVar.is_sensitive && !visibleKeys.has(envVar.key)
                        ? '***FILTERED***'
                        : envVar.value}
                    </Typography>
                    {envVar.is_sensitive && (
                      <IconButton
                        size="sm"
                        variant="plain"
                        onClick={() => toggleVisibility(envVar.key)}
                      >
                        {visibleKeys.has(envVar.key) ? (
                          <VisibilityOffIcon />
                        ) : (
                          <VisibilityIcon />
                        )}
                      </IconButton>
                    )}
                  </Box>
                </td>
                <td>
                  <Typography level="body-sm" color="neutral">
                    {envVar.description || '-'}
                  </Typography>
                </td>
                <td>
                  {envVar.is_sensitive ? (
                    <Chip size="sm" color="warning" variant="soft">
                      敏感
                    </Chip>
                  ) : (
                    <Chip size="sm" color="neutral" variant="soft">
                      普通
                    </Chip>
                  )}
                </td>
                <td>
                  <IconButton
                    size="sm"
                    variant="plain"
                    onClick={() => handleEdit(envVar)}
                    disabled={loading}
                  >
                    <EditIcon />
                  </IconButton>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Sheet>

      {/* 编辑对话框 */}
      <Modal open={editingKey !== null} onClose={() => setEditingKey(null)}>
        <ModalDialog>
          <ModalClose />
          <DialogTitle>编辑环境变量</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              <FormControl>
                <FormLabel>变量名</FormLabel>
                <Input value={editingKey || ''} disabled />
              </FormControl>

              <FormControl>
                <FormLabel>变量值</FormLabel>
                <Input
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  placeholder="输入变量值"
                  type={editingKey && envVars.find((v) => v.key === editingKey)?.is_sensitive ? 'password' : 'text'}
                />
              </FormControl>

              <FormControl>
                <FormLabel>描述（可选）</FormLabel>
                <Input
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="输入描述"
                />
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => setEditingKey(null)}>
                  取消
                </Button>
                <Button onClick={handleSave} loading={loading}>
                  保存
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </ModalDialog>
      </Modal>
    </Box>
  );
};

export default EnvironmentVariables;

