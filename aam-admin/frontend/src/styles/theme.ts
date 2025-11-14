/**
 * @purpose: Joy UI 主题配置
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { extendTheme } from '@mui/joy/styles';

export const theme = extendTheme({
  colorSchemes: {
    light: {
      palette: {
        primary: {
          50: '#e3f2fd',
          100: '#bbdefb',
          200: '#90caf9',
          300: '#64b5f6',
          400: '#42a5f5',
          500: '#2196f3',
          600: '#1e88e5',
          700: '#1976d2',
          800: '#1565c0',
          900: '#0d47a1',
        },
      },
    },
    dark: {
      palette: {
        primary: {
          50: '#0d47a1',
          100: '#1565c0',
          200: '#1976d2',
          300: '#1e88e5',
          400: '#2196f3',
          500: '#42a5f5',
          600: '#64b5f6',
          700: '#90caf9',
          800: '#bbdefb',
          900: '#e3f2fd',
        },
      },
    },
  },
});

