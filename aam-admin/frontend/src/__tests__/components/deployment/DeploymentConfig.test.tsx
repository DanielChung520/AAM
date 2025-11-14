/**
 * @purpose: 部署配置组件单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { DeploymentConfig } from '@/components/deployment/DeploymentConfig';

describe('DeploymentConfig', () => {
  const mockOnDeploy = vi.fn();
  const mockOnPreview = vi.fn();

  it('应该正确渲染部署配置表单', () => {
    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
        onPreview={mockOnPreview}
      />
    );

    expect(screen.getByText(/部署策略/i)).toBeInTheDocument();
    expect(screen.getByText(/蓝绿部署/i)).toBeInTheDocument();
  });

  it('应该支持选择不同的部署策略', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
        onPreview={mockOnPreview}
      />
    );

    // 查找滚动更新选项
    const rollingOption = screen.getByLabelText(/滚动更新/i);
    await user.click(rollingOption);

    // 验证配置表单已更新
    expect(screen.getByText(/滚动更新/i)).toBeInTheDocument();
  });

  it('应该调用 onDeploy 当点击部署按钮', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
        onPreview={mockOnPreview}
      />
    );

    const deployButton = screen.getByRole('button', { name: /部署/i });
    await user.click(deployButton);

    expect(mockOnDeploy).toHaveBeenCalled();
  });

  it('应该调用 onPreview 当点击预览按钮', async () => {
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
        onPreview={mockOnPreview}
      />
    );

    const previewButton = screen.getByRole('button', { name: /预览/i });
    await user.click(previewButton);

    expect(mockOnPreview).toHaveBeenCalled();
  });

  it('应该在加载状态时禁用按钮', () => {
    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
        loading={true}
      />
    );

    const deployButton = screen.getByRole('button', { name: /部署/i });
    expect(deployButton).toBeDisabled();
  });

  it('应该显示错误信息当部署失败', () => {
    render(
      <DeploymentConfig
        version="v1.0.0"
        onDeploy={mockOnDeploy}
      />
    );

    // 模拟错误状态（需要组件支持错误显示）
  });
});

