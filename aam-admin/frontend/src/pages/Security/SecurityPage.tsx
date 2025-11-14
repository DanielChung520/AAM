/**
 * @purpose: 安全管理页面
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  Button,
  Alert,
  Modal,
  ModalDialog,
  ModalClose,
  DialogTitle,
  DialogContent,
  Input,
  FormControl,
  FormLabel,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import AddIcon from '@mui/icons-material/Add';
import { TokenList } from '@/components/security/TokenList';
import { TokenIssueForm } from '@/components/security/TokenIssueForm';
import { EnterpriseAuthForm } from '@/components/security/EnterpriseAuthForm';
import { AuditLogPage } from './AuditLogPage';
import { useTokens, useEnterpriseAuth } from '@/hooks/useSecurity';
import { securityApi } from '@/services/api/security';
import type { TokenCreateRequest, TokenIssueResponse } from '@/types/security';

export const SecurityPage: React.FC = () => {
  const { mode } = useColorScheme();
  const [activeTab, setActiveTab] = useState(0);
  const [tokenIssueModalOpen, setTokenIssueModalOpen] = useState(false);
  const [revokeTokenId, setRevokeTokenId] = useState<number | null>(null);
  const [revokeReason, setRevokeReason] = useState('');
  const [revokeModalOpen, setRevokeModalOpen] = useState(false);

  const {
    tokens,
    loading: tokensLoading,
    error: tokensError,
    fetchTokens,
    issueToken,
    revokeToken,
  } = useTokens();

  const {
    config: enterpriseAuthConfig,
    loading: enterpriseAuthLoading,
    error: enterpriseAuthError,
    updateConfig: updateEnterpriseAuth,
    testAuth: testEnterpriseAuth,
  } = useEnterpriseAuth();


  const handleIssueToken = async (request: TokenCreateRequest): Promise<TokenIssueResponse> => {
    return await issueToken(request);
  };

  const handleRevokeToken = async () => {
    if (!revokeTokenId) return;

    try {
      await revokeToken(revokeTokenId, { reason: revokeReason });
      setRevokeModalOpen(false);
      setRevokeTokenId(null);
      setRevokeReason('');
    } catch (err) {
      // 错误已在 Hook 中处理
    }
  };

  const handleTestEnterpriseAuth = async (userId: string, token?: string) => {
    await testEnterpriseAuth({ user_id: userId, token });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography level="h2">安全管理</Typography>
      </Box>

      <Tabs value={activeTab} onChange={(_, value) => setActiveTab(value as number)}>
        <TabList>
          <Tab>Token 管理</Tab>
          <Tab>企业认证</Tab>
          <Tab>审计日志</Tab>
        </TabList>

        {/* Token 管理 Tab */}
        <TabPanel value={0}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {tokensError && (
              <Alert color="danger" variant="soft">
                {tokensError.message}
              </Alert>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                startDecorator={<AddIcon />}
                onClick={() => setTokenIssueModalOpen(true)}
              >
                发行 Token
              </Button>
            </Box>

            <TokenList
              tokens={tokens}
              loading={tokensLoading}
              onRevoke={(tokenId) => {
                setRevokeTokenId(tokenId);
                setRevokeModalOpen(true);
              }}
            />
          </Box>
        </TabPanel>

        {/* 企业认证 Tab */}
        <TabPanel value={1}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {enterpriseAuthError && (
              <Alert color="danger" variant="soft">
                {enterpriseAuthError.message}
              </Alert>
            )}

            {enterpriseAuthConfig && (
              <EnterpriseAuthForm
                config={enterpriseAuthConfig}
                loading={enterpriseAuthLoading}
                onUpdate={updateEnterpriseAuth}
                onTest={handleTestEnterpriseAuth}
              />
            )}
          </Box>
        </TabPanel>

        {/* 审计日志 Tab */}
        <TabPanel value={2}>
          <AuditLogPage />
        </TabPanel>
      </Tabs>

      {/* Token 发行 Modal */}
      <TokenIssueForm
        open={tokenIssueModalOpen}
        onClose={() => {
          setTokenIssueModalOpen(false);
        }}
        onSubmit={handleIssueToken}
        loading={tokensLoading}
      />

      {/* Token 撤销确认 Modal */}
      <Modal open={revokeModalOpen} onClose={() => setRevokeModalOpen(false)}>
        <ModalDialog>
          <ModalClose />
          <DialogTitle>撤销 Token</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography level="body-md">
                确定要撤销 Token ID {revokeTokenId} 吗？此操作不可恢复。
              </Typography>
              <FormControl>
                <FormLabel>撤销原因（可选）</FormLabel>
                <Input
                  value={revokeReason}
                  onChange={(e) => setRevokeReason(e.target.value)}
                  placeholder="请输入撤销原因"
                />
              </FormControl>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => setRevokeModalOpen(false)}>
                  取消
                </Button>
                <Button color="danger" onClick={handleRevokeToken}>
                  确认撤销
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </ModalDialog>
      </Modal>
    </Box>
  );
};

export default SecurityPage;

