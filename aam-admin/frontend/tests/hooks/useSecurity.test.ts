/**
 * @purpose: useSecurity Hooks 单元测试
 * @author: Daniel Chung
 * @createdAt: 2025-01-14
 * @lastModified: 2025-01-14
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useTokens } from '@/hooks/useSecurity';
import { securityApi } from '@/services/api/security';

// Mock API
vi.mock('@/services/api/security');

describe('useSecurity Hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('useTokens', () => {
    it('应该正确获取 Token 列表', async () => {
      const mockTokens = [
        {
          id: 1,
          token_hash: 'abc12345***',
          user_id: 1,
          name: 'Test Token',
          status: 'active' as const,
          issued_at: '2025-01-14T10:00:00Z',
        },
      ];

      vi.mocked(securityApi.getTokens).mockResolvedValue(mockTokens);

      const { result } = renderHook(() => useTokens());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.tokens).toEqual(mockTokens);
      expect(result.current.error).toBeNull();
    });

    it('应该处理 API 错误', async () => {
      const mockError = new Error('API Error');
      vi.mocked(securityApi.getTokens).mockRejectedValue(mockError);

      const { result } = renderHook(() => useTokens());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBeTruthy();
      expect(result.current.tokens).toEqual([]);
    });

    it('应该正确发行 Token', async () => {
      const mockIssueResponse = {
        token: 'test_token_string',
        token_record: {
          id: 1,
          token_hash: 'abc12345***',
          user_id: 1,
          name: 'New Token',
          status: 'active' as const,
          issued_at: '2025-01-14T10:00:00Z',
        },
      };

      vi.mocked(securityApi.issueToken).mockResolvedValue(mockIssueResponse);
      vi.mocked(securityApi.getTokens).mockResolvedValue([]);

      const { result } = renderHook(() => useTokens());

      const issueResult = await result.current.issueToken({
        name: 'New Token',
        expires_hours: 24,
      });

      expect(issueResult).toEqual(mockIssueResponse);
      expect(securityApi.getTokens).toHaveBeenCalled();
    });

    it('应该正确撤销 Token', async () => {
      const mockToken = {
        id: 1,
        token_hash: 'abc12345***',
        user_id: 1,
        name: 'Test Token',
        status: 'revoked' as const,
        issued_at: '2025-01-14T10:00:00Z',
        revoked_at: '2025-01-14T12:00:00Z',
      };

      vi.mocked(securityApi.revokeToken).mockResolvedValue(mockToken);
      vi.mocked(securityApi.getTokens).mockResolvedValue([]);

      const { result } = renderHook(() => useTokens());

      await result.current.revokeToken(1, { reason: 'Test' });

      expect(securityApi.revokeToken).toHaveBeenCalledWith(1, { reason: 'Test' });
      expect(securityApi.getTokens).toHaveBeenCalled();
    });
  });
});

