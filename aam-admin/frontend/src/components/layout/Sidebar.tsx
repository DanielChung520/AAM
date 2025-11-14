/**
 * @purpose: 侧边栏导航组件
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemContent,
  ListItemDecorator,
  Typography,
  Sheet,
  IconButton,
} from '@mui/joy';
// import { useColorScheme } from '@mui/joy/styles'; // 暂时未使用，保留以备将来使用
import DashboardIcon from '@mui/icons-material/Dashboard';
import PsychologyIcon from '@mui/icons-material/Psychology';
import ComputerIcon from '@mui/icons-material/Computer';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import DescriptionIcon from '@mui/icons-material/Description';
import SecurityIcon from '@mui/icons-material/Security';
import SettingsIcon from '@mui/icons-material/Settings';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
}

const menuItems: MenuItem[] = [
  { id: 'dashboard', label: '儀表盤', icon: <DashboardIcon />, path: '/dashboard' },
  { id: 'llm-provider', label: 'LLM Provider', icon: <PsychologyIcon />, path: '/llm-provider' },
  { id: 'service-monitor', label: '服務管理', icon: <ComputerIcon />, path: '/service-monitor' },
  { id: 'deployment', label: '版本部署', icon: <RocketLaunchIcon />, path: '/deployment' },
  { id: 'logs', label: '日誌管理', icon: <DescriptionIcon />, path: '/logs' },
  { id: 'security', label: '安全管理', icon: <SecurityIcon />, path: '/security' },
  { id: 'settings', label: '系統設置', icon: <SettingsIcon />, path: '/settings' },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed = false, onToggle }) => {
  const navigate = useNavigate();
  const location = useLocation();
  // const { mode } = useColorScheme(); // 暂时未使用，保留以备将来使用

  const handleNavigation = (path: string) => {
    console.log('Sidebar navigation clicked:', path);
    console.log('Current location:', location.pathname);
    try {
      navigate(path);
      console.log('Navigation successful');
    } catch (error) {
      console.error('Navigation error:', error);
    }
  };

  return (
    <Sheet
      sx={{
        width: collapsed ? 64 : 240,
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bgcolor: 'background.surface',
        borderRight: '1px solid',
        borderColor: 'divider',
        transition: 'width 0.3s ease',
        zIndex: 1000,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
        }}
      >
        {/* 折叠按钮 */}
        {onToggle && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'flex-end',
              p: 1,
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <IconButton
              variant="plain"
              size="sm"
              onClick={onToggle}
              sx={{
                color: 'text.secondary',
                '&:hover': {
                  bgcolor: 'background.level1',
                },
              }}
            >
              {collapsed ? <MenuIcon /> : <ChevronLeftIcon />}
            </IconButton>
          </Box>
        )}

        {/* 菜单列表 */}
        <List
          sx={{
            flex: 1,
            p: 1,
            gap: 0.5,
          }}
        >
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <ListItem key={item.id}>
                <ListItemButton
                  selected={isActive}
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: 'sm',
                    '&.Mui-selected': {
                      bgcolor: 'primary.softBg',
                      color: 'primary.softColor',
                      '&:hover': {
                        bgcolor: 'primary.softHoverBg',
                      },
                    },
                    '&:hover': {
                      bgcolor: 'background.level1',
                    },
                  }}
                >
                  <ListItemDecorator
                    sx={{
                      minWidth: collapsed ? 0 : 40,
                      justifyContent: 'center',
                      color: isActive ? 'primary.500' : 'text.secondary',
                    }}
                  >
                    {item.icon}
                  </ListItemDecorator>
                  {!collapsed && (
                    <ListItemContent>
                      <Typography level="body-sm" fontWeight={isActive ? 600 : 400}>
                        {item.label}
                      </Typography>
                    </ListItemContent>
                  )}
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>
    </Sheet>
  );
};

export default Sidebar;

