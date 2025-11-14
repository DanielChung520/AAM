/**
 * @purpose: 备份管理组件
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
  Chip,
  IconButton,
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
  FormControl,
  FormLabel,
  Input,
  Checkbox,
  Alert,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import DownloadIcon from '@mui/icons-material/Download';
import RestoreIcon from '@mui/icons-material/Restore';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import type { BackupRecord, BackupRequest, BackupRestoreRequest } from '@/types/settings';

export interface BackupManagementProps {
  backups: BackupRecord[];
  loading?: boolean;
  onCreateBackup: (request: BackupRequest) => Promise<void>;
  onRestoreBackup: (backupId: string, request: BackupRestoreRequest) => Promise<void>;
  onDownloadBackup: (backupId: string) => Promise<void>;
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
};

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN');
};

export const BackupManagement: React.FC<BackupManagementProps> = ({
  backups,
  loading = false,
  onCreateBackup,
  onRestoreBackup,
  onDownloadBackup,
}) => {
  const { mode } = useColorScheme();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [restoreModalOpen, setRestoreModalOpen] = useState(false);
  const [selectedBackupId, setSelectedBackupId] = useState<string | null>(null);
  const [backupName, setBackupName] = useState('');
  const [includeDatabase, setIncludeDatabase] = useState(true);
  const [includeConfig, setIncludeConfig] = useState(true);
  const [includeVersions, setIncludeVersions] = useState(true);
  const [restoreDatabase, setRestoreDatabase] = useState(true);
  const [restoreConfig, setRestoreConfig] = useState(true);
  const [restoreVersions, setRestoreVersions] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleCreateBackup = async () => {
    try {
      setError(null);
      await onCreateBackup({
        name: backupName || undefined,
        include_database: includeDatabase,
        include_config: includeConfig,
        include_versions: includeVersions,
      });
      setCreateModalOpen(false);
      setBackupName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建备份失败');
    }
  };

  const handleRestoreBackup = async () => {
    if (!selectedBackupId) return;

    try {
      setError(null);
      await onRestoreBackup(selectedBackupId, {
        backup_id: selectedBackupId,
        restore_database: restoreDatabase,
        restore_config: restoreConfig,
        restore_versions: restoreVersions,
      });
      setRestoreModalOpen(false);
      setSelectedBackupId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : '恢复备份失败');
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography level="title-lg">备份管理</Typography>
        <Button
          startDecorator={<AddIcon />}
          onClick={() => setCreateModalOpen(true)}
          variant="outlined"
        >
          创建备份
        </Button>
      </Box>

      <Sheet variant="outlined" sx={{ borderRadius: 'sm', overflow: 'auto' }}>
        <Table>
          <thead>
            <tr>
              <th style={{ width: '200px' }}>备份名称</th>
              <th style={{ width: '180px' }}>创建时间</th>
              <th style={{ width: '100px' }}>大小</th>
              <th style={{ width: '100px' }}>状态</th>
              <th style={{ width: '200px' }}>包含内容</th>
              <th style={{ width: '200px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {backups.map((backup) => (
              <tr key={backup.id}>
                <td>
                  <Typography level="body-sm" fontWeight="md">
                    {backup.name}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm">
                    {formatDate(backup.created_at)}
                  </Typography>
                </td>
                <td>
                  <Typography level="body-sm">
                    {formatFileSize(backup.size)}
                  </Typography>
                </td>
                <td>
                  <Chip
                    size="sm"
                    color={backup.status === 'completed' ? 'success' : backup.status === 'failed' ? 'danger' : 'warning'}
                  >
                    {backup.status === 'completed' ? '已完成' : backup.status === 'failed' ? '失败' : '进行中'}
                  </Chip>
                </td>
                <td>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {backup.includes.database && <Chip size="sm" variant="soft">数据库</Chip>}
                    {backup.includes.config && <Chip size="sm" variant="soft">配置</Chip>}
                    {backup.includes.versions && <Chip size="sm" variant="soft">版本</Chip>}
                  </Box>
                </td>
                <td>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton
                      size="sm"
                      variant="plain"
                      onClick={() => onDownloadBackup(backup.id)}
                      disabled={loading}
                    >
                      <DownloadIcon />
                    </IconButton>
                    <IconButton
                      size="sm"
                      variant="plain"
                      onClick={() => {
                        setSelectedBackupId(backup.id);
                        setRestoreModalOpen(true);
                      }}
                      disabled={loading || backup.status !== 'completed'}
                    >
                      <RestoreIcon />
                    </IconButton>
                  </Box>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Sheet>

      {/* 创建备份对话框 */}
      <Modal open={createModalOpen} onClose={() => setCreateModalOpen(false)}>
        <ModalDialog>
          <ModalClose />
          <DialogTitle>创建备份</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              <FormControl>
                <FormLabel>备份名称（可选）</FormLabel>
                <Input
                  value={backupName}
                  onChange={(e) => setBackupName(e.target.value)}
                  placeholder="留空则使用时间戳"
                />
              </FormControl>

              <FormControl>
                <FormLabel>包含内容</FormLabel>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Checkbox
                    label="数据库"
                    checked={includeDatabase}
                    onChange={(e) => setIncludeDatabase(e.target.checked)}
                  />
                  <Checkbox
                    label="配置文件"
                    checked={includeConfig}
                    onChange={(e) => setIncludeConfig(e.target.checked)}
                  />
                  <Checkbox
                    label="版本配置"
                    checked={includeVersions}
                    onChange={(e) => setIncludeVersions(e.target.checked)}
                  />
                </Box>
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => setCreateModalOpen(false)}>
                  取消
                </Button>
                <Button onClick={handleCreateBackup} loading={loading}>
                  创建备份
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </ModalDialog>
      </Modal>

      {/* 恢复备份对话框 */}
      <Modal open={restoreModalOpen} onClose={() => setRestoreModalOpen(false)}>
        <ModalDialog>
          <ModalClose />
          <DialogTitle>恢复备份</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {error && (
                <Alert color="danger" variant="soft">
                  {error}
                </Alert>
              )}

              <Alert color="warning" variant="soft">
                恢复备份将覆盖现有数据，请谨慎操作！
              </Alert>

              <FormControl>
                <FormLabel>恢复内容</FormLabel>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Checkbox
                    label="数据库"
                    checked={restoreDatabase}
                    onChange={(e) => setRestoreDatabase(e.target.checked)}
                  />
                  <Checkbox
                    label="配置文件"
                    checked={restoreConfig}
                    onChange={(e) => setRestoreConfig(e.target.checked)}
                  />
                  <Checkbox
                    label="版本配置"
                    checked={restoreVersions}
                    onChange={(e) => setRestoreVersions(e.target.checked)}
                  />
                </Box>
              </FormControl>

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => setRestoreModalOpen(false)}>
                  取消
                </Button>
                <Button color="danger" onClick={handleRestoreBackup} loading={loading}>
                  确认恢复
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </ModalDialog>
      </Modal>
    </Box>
  );
};

export default BackupManagement;

