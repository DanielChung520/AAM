/**
 * @purpose: 版本部署主页面 - 左右分栏布局，集成版本列表和部署配置
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState, useCallback } from 'react';
import {
  Box,
  Grid,
  Typography,
  Sheet,
  Alert,
  Button,
  Modal,
  ModalDialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import { VersionList } from '@/components/deployment/VersionList';
import { VersionDetail } from '@/components/deployment/VersionDetail';
import { DeploymentConfig } from '@/components/deployment/DeploymentConfig';
import { CreateVersionDialog } from '@/components/deployment/CreateVersionDialog';
import {
  useVersions,
  useVersion,
  useActiveVersion,
  useVersionOperations,
} from '@/hooks/useVersions';
import { useDeployments, useDeploymentOperations } from '@/hooks/useDeployments';
import type { VersionStatus } from '@/types/version';
import type { DeploymentRequest } from '@/types/deployment';

export const DeploymentPage: React.FC = () => {
  const { mode } = useColorScheme();
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<VersionStatus | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [deployDialogOpen, setDeployDialogOpen] = useState(false);
  const [deployRequest, setDeployRequest] = useState<DeploymentRequest | null>(null);

  // 获取版本列表
  const {
    versions,
    loading: versionsLoading,
    error: versionsError,
    refresh: refreshVersions,
  } = useVersions(
    {
      status: statusFilter || undefined,
      search: searchQuery || undefined,
    },
    true
  );

  // 获取活动版本
  const { activeVersion } = useActiveVersion(true);

  // 版本操作
  const { createVersion, deleteVersion } = useVersionOperations();

  // 部署操作
  const { deployVersion } = useDeploymentOperations();

  // 获取选中版本的详情
  const {
    version: versionDetail,
    loading: detailLoading,
    error: detailError,
  } = useVersion(selectedVersion || undefined);

  // 获取部署历史（用于刷新）
  const { refresh: refreshDeployments } = useDeployments({}, false);

  // 处理版本选择
  const handleSelectVersion = useCallback((version: string) => {
    setSelectedVersion(version);
  }, []);

  // 处理创建版本
  const handleCreateVersion = useCallback(() => {
    setCreateDialogOpen(true);
  }, []);

  // 处理创建版本提交
  const handleCreateVersionSubmit = useCallback(
    async (request: Parameters<typeof createVersion>[0]) => {
      try {
        await createVersion(request);
        setCreateDialogOpen(false);
        await refreshVersions();
        // 如果创建成功，自动选中新创建的版本
        if (request.version) {
          setSelectedVersion(request.version);
        }
      } catch (error) {
        console.error('创建版本失败:', error);
        throw error;
      }
    },
    [createVersion, refreshVersions]
  );

  // 处理删除版本
  const handleDeleteVersion = useCallback(
    async (version: string) => {
      if (window.confirm(`确定要删除版本 ${version} 吗？`)) {
        try {
          await deleteVersion(version);
          await refreshVersions();
          // 如果删除的是当前选中的版本，清空选择
          if (selectedVersion === version) {
            setSelectedVersion(null);
          }
        } catch (error) {
          console.error('删除版本失败:', error);
          alert('删除版本失败: ' + (error instanceof Error ? error.message : '未知错误'));
        }
      }
    },
    [deleteVersion, refreshVersions, selectedVersion]
  );

  // 处理部署
  const handleDeploy = useCallback(
    async (request: DeploymentRequest) => {
      try {
        await deployVersion(request.version, request);
        setDeployDialogOpen(false);
        setDeployRequest(null);
        await refreshVersions();
        await refreshDeployments();
      } catch (error) {
        console.error('部署失败:', error);
        throw error;
      }
    },
    [deployVersion, refreshVersions, refreshDeployments]
  );

  // 处理部署预览
  const handlePreview = useCallback(async (request: DeploymentRequest) => {
    setDeployRequest(request);
    setDeployDialogOpen(true);
  }, []);

  return (
    <Box
      sx={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        p: 2,
      }}
    >
      {/* 页面标题 */}
      <Box>
        <Typography level="h2" sx={{ mb: 1 }}>
          版本部署
        </Typography>
        <Typography level="body-md" sx={{ color: 'text.secondary' }}>
          管理服务版本并进行部署操作
        </Typography>
      </Box>

      {/* 错误提示 */}
      {versionsError && (
        <Alert color="danger" sx={{ mb: 2 }}>
          {versionsError.message}
        </Alert>
      )}

      {/* 主内容区域 - 左右分栏 */}
      <Grid
        container
        spacing={2}
        sx={{
          flex: 1,
          minHeight: 0,
        }}
      >
        {/* 左侧：版本列表（40%） */}
        <Grid xs={12} md={4.8}>
          <Sheet
            variant="outlined"
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 'sm',
              overflow: 'hidden',
            }}
          >
            <VersionList
              versions={versions}
              selectedVersion={selectedVersion || undefined}
              activeVersion={activeVersion || undefined}
              onSelectVersion={handleSelectVersion}
              onCreateVersion={handleCreateVersion}
              onDeleteVersion={handleDeleteVersion}
              loading={versionsLoading}
              statusFilter={statusFilter}
              onStatusFilterChange={setStatusFilter}
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />
          </Sheet>
        </Grid>

        {/* 右侧：版本详情和部署配置（60%） */}
        <Grid xs={12} md={7.2}>
          <Sheet
            variant="outlined"
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 'sm',
              overflow: 'hidden',
            }}
          >
            {selectedVersion ? (
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  height: '100%',
                  overflow: 'auto',
                }}
              >
                {/* 版本详情 */}
                <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                  <VersionDetail version={versionDetail} loading={detailLoading} />
                </Box>

                {/* 部署配置 */}
                <Box sx={{ p: 2, flex: 1, overflow: 'auto' }}>
                  <DeploymentConfig
                    version={selectedVersion}
                    onDeploy={handleDeploy}
                    onPreview={handlePreview}
                  />
                </Box>
              </Box>
            ) : (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '100%',
                  color: 'text.secondary',
                }}
              >
                <Typography level="body-lg">
                  请从左侧选择一个版本以查看详情和进行部署
                </Typography>
              </Box>
            )}
          </Sheet>
        </Grid>
      </Grid>

      {/* 创建版本对话框 */}
      <CreateVersionDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateVersionSubmit}
      />

      {/* 部署确认对话框 */}
      <Modal open={deployDialogOpen} onClose={() => setDeployDialogOpen(false)}>
        <ModalDialog>
          <DialogTitle>确认部署</DialogTitle>
          <DialogContent>
            {deployRequest && (
              <Box>
                <Typography level="body-md" sx={{ mb: 2 }}>
                  确定要部署版本 <strong>{deployRequest.version}</strong> 吗？
                </Typography>
                <Typography level="body-sm" sx={{ color: 'text.secondary' }}>
                  部署策略: {deployRequest.strategy}
                </Typography>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button
              variant="outlined"
              color="neutral"
              onClick={() => setDeployDialogOpen(false)}
            >
              取消
            </Button>
            <Button
              variant="solid"
              color="primary"
              onClick={async () => {
                if (deployRequest) {
                  await handleDeploy(deployRequest);
                }
              }}
            >
              确认部署
            </Button>
          </DialogActions>
        </ModalDialog>
      </Modal>
    </Box>
  );
};

export default DeploymentPage;

