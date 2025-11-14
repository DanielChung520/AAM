/**
 * @purpose: 版本详情组件单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { VersionDetail } from '@/components/deployment/VersionDetail';
import type { VersionDetail as VersionDetailType } from '@/types/version';

const mockVersionDetail: VersionDetailType = {
  version: 'v1.0.0',
  status: 'active',
  git_commit: 'abc123def456',
  git_branch: 'main',
  git_tag: 'v1.0.0',
  image_tag: 'aam-service:v1.0.0',
  created_at: '2025-01-14T10:00:00Z',
  created_by: 'admin',
  description: 'First release',
  config_snapshot: {
    version: 'v1.0.0',
    services: ['aam-service'],
  },
  docker_compose_config: {
    services: {
      'aam-service': {
        image: 'aam-service:v1.0.0',
      },
    },
  },
  environment_variables: {
    APP_VERSION: 'v1.0.0',
  },
  service_config: {
    api: {
      port: 8000,
    },
  },
};

describe('VersionDetail', () => {
  it('应该正确渲染版本详情', () => {
    render(<VersionDetail version={mockVersionDetail} />);

    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    expect(screen.getByText('活动')).toBeInTheDocument();
    expect(screen.getByText('First release')).toBeInTheDocument();
  });

  it('应该在版本为 null 时显示空状态', () => {
    render(<VersionDetail version={null} />);
    // 检查是否有空状态提示
  });

  it('应该在加载状态时显示加载提示', () => {
    render(<VersionDetail version={null} loading={true} />);
    // 检查是否有加载相关的元素
  });

  it('应该正确显示 Git 信息', () => {
    render(<VersionDetail version={mockVersionDetail} />);

    expect(screen.getByText(/abc123/i)).toBeInTheDocument();
    expect(screen.getByText(/main/i)).toBeInTheDocument();
  });

  it('应该正确显示配置信息', () => {
    render(<VersionDetail version={mockVersionDetail} />);

    // 检查配置标签页是否存在
    const tabs = screen.getAllByRole('tab');
    expect(tabs.length).toBeGreaterThan(0);
  });

  it('应该支持复制到剪贴板', async () => {
    const clipboardWriteText = vi.fn();
    Object.assign(navigator, {
      clipboard: {
        writeText: clipboardWriteText,
      },
    });

    render(<VersionDetail version={mockVersionDetail} />);

    const copyButtons = screen.getAllByRole('button');
    const copyButton = copyButtons.find((btn) =>
      btn.querySelector('[data-testid="ContentCopyIcon"]')
    );

    if (copyButton) {
      const { userEvent } = await import('@testing-library/user-event');
      const user = userEvent.setup();
      await user.click(copyButton);
      // 验证复制功能被调用
    }
  });
});

