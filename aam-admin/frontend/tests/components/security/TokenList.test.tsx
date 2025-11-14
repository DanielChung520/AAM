/**
 * @purpose: Token 列表组件单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/tests/utils/test-utils';
import { TokenList } from '@/components/security/TokenList';
import type { Token } from '@/types/security';

const mockTokens: Token[] = [
  {
    id: 1,
    token_hash: 'abc12345***',
    user_id: 1,
    name: 'Test Token 1',
    status: 'active',
    issued_at: '2025-01-14T10:00:00Z',
    expires_at: '2025-01-15T10:00:00Z',
    last_used_at: '2025-01-14T12:00:00Z',
  },
  {
    id: 2,
    token_hash: 'def67890***',
    user_id: 2,
    name: 'Test Token 2',
    status: 'revoked',
    issued_at: '2025-01-13T10:00:00Z',
    revoked_at: '2025-01-14T08:00:00Z',
  },
];

describe('TokenList', () => {
  it('应该正确渲染 Token 列表', () => {
    const handleRevoke = vi.fn();
    const handleViewDetail = vi.fn();

    render(
      <TokenList
        tokens={mockTokens}
        onRevoke={handleRevoke}
        onViewDetail={handleViewDetail}
      />
    );

    expect(screen.getByText('Test Token 1')).toBeInTheDocument();
    expect(screen.getByText('Test Token 2')).toBeInTheDocument();
    expect(screen.getByText('有效')).toBeInTheDocument();
    expect(screen.getByText('已撤销')).toBeInTheDocument();
  });

  it('应该在加载状态时显示加载提示', () => {
    render(<TokenList tokens={[]} loading={true} />);
    expect(screen.getByText('加载中...')).toBeInTheDocument();
  });

  it('应该在无 Token 时显示空状态', () => {
    render(<TokenList tokens={[]} loading={false} />);
    expect(screen.getByText('暂无 Token 记录')).toBeInTheDocument();
  });

  it('应该调用 onRevoke 当点击撤销按钮', async () => {
    const handleRevoke = vi.fn();
    const { userEvent } = await import('@testing-library/user-event');
    const user = userEvent.setup();

    render(
      <TokenList
        tokens={mockTokens}
        onRevoke={handleRevoke}
      />
    );

    const revokeButtons = screen.getAllByRole('button');
    const revokeButton = revokeButtons.find((btn) =>
      btn.querySelector('svg')
    );

    if (revokeButton) {
      await user.click(revokeButton);
      expect(handleRevoke).toHaveBeenCalledWith(1);
    }
  });
});

