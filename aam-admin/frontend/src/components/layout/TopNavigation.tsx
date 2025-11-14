/**
 * @purpose: 顶部导航栏组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-15
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  IconButton,
  Dropdown,
  Menu,
  MenuButton,
  MenuItem,
  Avatar,
  Sheet,
} from '@mui/joy';
import { useColorScheme } from '@mui/joy/styles';
import { useAuthStore } from '@/stores/authStore';
import { useThemeStore } from '@/stores/themeStore';
import { authApi } from '@/services/api/auth';
import { ChangePasswordDialog } from '@/components/common/ChangePasswordDialog';
import LightModeIcon from '@mui/icons-material/LightMode';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import LockIcon from '@mui/icons-material/Lock';

export const TopNavigation: React.FC = () => {
  const navigate = useNavigate();
  const { mode, setMode } = useColorScheme();
  const { toggleMode } = useThemeStore();
  const { user, logout } = useAuthStore();
  const [changePasswordOpen, setChangePasswordOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      navigate('/login');
    }
  };

  const handleThemeToggle = () => {
    const newMode = mode === 'dark' ? 'light' : 'dark';
    setMode(newMode);
    toggleMode();
  };

  return (
    <Sheet
      sx={{
        height: 64,
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1100,
        bgcolor: 'background.surface',
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 2,
      }}
    >
      {/* Logo 和系统名称 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography level="h4" fontWeight="bold" sx={{ color: 'primary.500' }}>
          AAM 管理系统
        </Typography>
      </Box>

      {/* 右侧操作区 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {/* 主题切换 */}
        <IconButton
          variant="plain"
          size="sm"
          onClick={handleThemeToggle}
          sx={{
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'background.level1',
            },
          }}
        >
          {mode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
        </IconButton>

        {/* 通知中心 */}
        <IconButton
          variant="plain"
          size="sm"
          sx={{
            color: 'text.secondary',
            '&:hover': {
              bgcolor: 'background.level1',
            },
          }}
        >
          <NotificationsIcon />
        </IconButton>

        {/* 用户菜单 */}
        <Dropdown>
          <MenuButton
            slots={{ root: IconButton }}
            slotProps={{ root: { variant: 'plain', size: 'sm' } }}
            sx={{
              color: 'text.secondary',
              '&:hover': {
                bgcolor: 'background.level1',
              },
            }}
          >
            <Avatar size="sm" sx={{ bgcolor: 'primary.500' }}>
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </Avatar>
          </MenuButton>
          <Menu placement="bottom-end">
            <MenuItem disabled>
              <Box>
                <Typography level="body-sm" fontWeight="bold">
                  {user?.username || '用户'}
                </Typography>
                <Typography level="body-xs" sx={{ color: 'text.tertiary' }}>
                  {user?.email || ''}
                </Typography>
              </Box>
            </MenuItem>
            <MenuItem onClick={() => setChangePasswordOpen(true)}>
              <LockIcon sx={{ mr: 1 }} />
              修改密码
            </MenuItem>
            <MenuItem onClick={() => navigate('/settings')}>
              <SettingsIcon sx={{ mr: 1 }} />
              设置
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              <LogoutIcon sx={{ mr: 1 }} />
              登出
            </MenuItem>
          </Menu>
        </Dropdown>
      </Box>

      {/* 修改密码对话框 */}
      <ChangePasswordDialog
        open={changePasswordOpen}
        onClose={() => setChangePasswordOpen(false)}
      />
    </Sheet>
  );
};

export default TopNavigation;

