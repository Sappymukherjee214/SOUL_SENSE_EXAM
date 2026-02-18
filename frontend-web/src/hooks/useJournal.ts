'use client';

import { useState, useCallback, useMemo } from 'react';
import { useApi } from './useApi';
import { journalApi, JournalEntry, JournalFilters } from '@/lib/api/journal';

interface UseJournalOptions {
  page?: number;
  limit?: number;
  filters?: JournalFilters;
}

interface UseJournalReturn {
  entries: JournalEntry[];
  total: number;
  loading: boolean;
  error: string | null;
  page: number;
  totalPages: number;
  hasNextPage: boolean;
  hasPrevPage: boolean;
  setPage: (page: number) => void;
  setFilters: (filters: JournalFilters) => void;
  filters: JournalFilters;
  refetch: () => void;
  loadMore: () => void; // for infinite scroll
}

export function useJournal(options: UseJournalOptions = {}): UseJournalReturn {
  const [page, setPage] = useState(options.page || 1);
  const [filters, setFilters] = useState<JournalFilters>(options.filters || {});
  const limit = options.limit || 10;

  const {
    data,
    loading,
    error,
    refetch,
  } = useApi({
    apiFn: () => journalApi.listEntries(page, limit, filters),
    deps: [page, filters],
  });

  const entries = data?.entries || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / limit);

  const hasNextPage = page < totalPages;
  const hasPrevPage = page > 1;

  const handleSetPage = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  const handleSetFilters = useCallback((newFilters: JournalFilters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  }, []);

  const loadMore = useCallback(() => {
    if (hasNextPage && !loading) {
      setPage(prev => prev + 1);
    }
  }, [hasNextPage, loading]);

  return {
    entries,
    total,
    loading,
    error,
    page,
    totalPages,
    hasNextPage,
    hasPrevPage,
    setPage: handleSetPage,
    setFilters: handleSetFilters,
    filters,
    refetch,
    loadMore,
  };
}