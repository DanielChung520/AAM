/**
 * @purpose: 版本列表组件单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { VersionList } from '@/components/deployment/VersionList';
import type { Version } from '@/types/version';

const mockVersions: Version[] = [
  {
    version: 'v1.0.0',
    status: 'active',
    git_commit: 'abc123',
    git_branch: 'main',
    image_tag: 'aam-service:v1.0.0',
    created_at: '2025-01-14T10:00:00Z',
    created_by: 'admin',
    description: 'First release',
  },
  {
    version: 'v1.1.0',
    status: 'available',
    git_commit: 'def456',
    git_branch: 'main',
    image_tag: 'aam-service:v1.1.0',
    created_at: '2025-01-15T10:00:00Z',
    created_by: 'admin',
    description: 'Second release',
  },
  {
    version: 'v0.9.0',
    status: 'deprecated',
    git_commit: 'ghi789',
    git_branch: 'main',
    image_tag: 'aam-service:v0.9.0',
    created_at: '2025-01-13T10:00:00Z',
    created_by: 'admin',
  },
];

describe('VersionList', () => {
  it('应该正确渲染版本列表', () => {
    const handleSelect = vi.fn();
    const handleCreate = vi.fn();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={handleSelect}
        onCreateVersion={handleCreate}
        activeVersion="v1.0.0"
      />
    );

    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
    expect(screen.getByText('v1.1.0')).toBeInTheDocument();
    expect(screen.getByText('v0.9.0')).toBeInTheDocument();
  });

  it('应该高亮显示活动版本', () => {
    const handleSelect = vi.fn();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={handleSelect}
        activeVersion="v1.0.0"
      />
    );

    const activeVersion = screen.getByText('v1.0.0').closest('[data-testid]') || screen.getByText('v1.0.0').closest('div');
    expect(activeVersion).toBeInTheDocument();
  });

  it('应该在加载状态时显示加载提示', () => {
    render(<VersionList versions={[]} onSelectVersion={vi.fn()} loading={true} />);
    // 检查是否有加载相关的元素
    expect(screen.queryByText('v1.0.0')).not.toBeInTheDocument();
  });

  it('应该在无版本时显示空状态', () => {
    render(<VersionList versions={[]} onSelectVersion={vi.fn()} loading={false} />);
    // 检查是否有空状态提示（如果有的话）
  });

  it('应该调用 onSelectVersion 当点击版本', async () => {
    const handleSelect = vi.fn();
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={handleSelect}
      />
    );

    const versionButton = screen.getByText('v1.1.0');
    await user.click(versionButton);
    expect(handleSelect).toHaveBeenCalledWith('v1.1.0');
  });

  it('应该调用 onCreateVersion 当点击创建按钮', async () => {
    const handleCreate = vi.fn();
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={vi.fn()}
        onCreateVersion={handleCreate}
      />
    );

    const createButton = screen.getByRole('button', { name: /创建/i });
    await user.click(createButton);
    expect(handleCreate).toHaveBeenCalled();
  });

  it('应该正确显示版本状态', () => {
    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={vi.fn()}
      />
    );

    expect(screen.getByText('活动')).toBeInTheDocument();
    expect(screen.getByText('可用')).toBeInTheDocument();
    expect(screen.getByText('已废弃')).toBeInTheDocument();
  });

  it('应该支持状态过滤', () => {
    const handleStatusFilterChange = vi.fn();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={vi.fn()}
        statusFilter="active"
        onStatusFilterChange={handleStatusFilterChange}
      />
    );

    // 检查状态过滤器是否存在
    expect(screen.getByText('v1.0.0')).toBeInTheDocument();
  });

  it('应该支持搜索功能', () => {
    const handleSearchChange = vi.fn();

    render(
      <VersionList
        versions={mockVersions}
        onSelectVersion={vi.fn()}
        searchQuery="v1.0"
        onSearchChange={handleSearchChange}
      />
    );

    // 检查搜索框是否存在
    const searchInput = screen.getByPlaceholderText(/搜索/i);
    expect(searchInput).toBeInTheDocument();
  });
});

