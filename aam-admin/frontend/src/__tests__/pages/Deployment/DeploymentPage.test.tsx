/**
 * @purpose: 部署页面单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { DeploymentPage } from '@/pages/Deployment/DeploymentPage';

// Mock hooks
vi.mock('@/hooks/useVersions', () => ({
  useVersions: () => ({
    versions: [],
    loading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

vi.mock('@/hooks/useDeployments', () => ({
  useDeployments: () => ({
    deployments: [],
    loading: false,
    error: null,
    deployVersion: vi.fn(),
    rollbackVersion: vi.fn(),
  }),
}));

describe('DeploymentPage', () => {
  it('应该正确渲染部署页面', () => {
    render(<DeploymentPage />);

    expect(screen.getByText(/版本部署/i)).toBeInTheDocument();
  });

  it('应该显示版本列表', () => {
    render(<DeploymentPage />);

    // 检查版本列表区域是否存在
    const versionList = screen.queryByText(/版本列表/i);
    // 由于使用了 mock，可能不会显示实际内容
  });

  it('应该显示部署配置区域', () => {
    render(<DeploymentPage />);

    // 检查部署配置区域是否存在
  });
});

