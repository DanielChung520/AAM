/**
 * @purpose: 主题状态管理（Zustand）
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ColorScheme = 'light' | 'dark' | 'system';

interface ThemeState {
  mode: ColorScheme;
  setMode: (mode: ColorScheme) => void;
  toggleMode: () => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      mode: 'system',
      setMode: (mode) => set({ mode }),
      toggleMode: () =>
        set((state) => {
          if (state.mode === 'light') {
            return { mode: 'dark' };
          } else if (state.mode === 'dark') {
            return { mode: 'light' };
          } else {
            // system mode, toggle to light
            return { mode: 'light' };
          }
        }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

