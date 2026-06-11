import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getEvalExportUrl, getToken, setToken, clearToken } from './client';

const mockLocalStorage = localStorage as unknown as {
  getItem: ReturnType<typeof vi.fn>;
  setItem: ReturnType<typeof vi.fn>;
  removeItem: ReturnType<typeof vi.fn>;
  clear: ReturnType<typeof vi.fn>;
};

describe('client utilities', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    mockLocalStorage.clear();
  });

  describe('getEvalExportUrl', () => {
    it('constructs correct JSON export URL with default base', () => {
      const url = getEvalExportUrl('run-123', 'json');
      expect(url).toBe('http://localhost:8000/eval/runs/run-123/export?format=json');
    });

    it('constructs correct CSV export URL with default base', () => {
      const url = getEvalExportUrl('run-123', 'csv');
      expect(url).toBe('http://localhost:8000/eval/runs/run-123/export?format=csv');
    });
  });

  describe('token management', () => {
    it('returns null when no token stored', () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      expect(getToken()).toBeNull();
    });

    it('stores and retrieves token', () => {
      mockLocalStorage.getItem.mockReturnValue('test-token-123');
      expect(getToken()).toBe('test-token-123');
    });

    it('clears token', () => {
      mockLocalStorage.getItem.mockReturnValue(null);
      clearToken();
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('resolveops_token');
    });

    it('overwrites existing token', () => {
      setToken('first-token');
      setToken('second-token');
      expect(mockLocalStorage.setItem).toHaveBeenLastCalledWith('resolveops_token', 'second-token');
    });
  });
});