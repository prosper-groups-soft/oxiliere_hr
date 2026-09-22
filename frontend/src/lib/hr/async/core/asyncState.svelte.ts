export type AsyncStatus = 'idle' | 'pending' | 'fulfilled' | 'rejected';

export interface ResourceAsync<T> {
  data: T | null;
  status: AsyncStatus;
  error: unknown | null;
  isStale: boolean;
  isLoading: boolean;  // pending && !data
  isFetching: boolean; // pending && !!data (stale)
}

export function toResource<T>(query: { data: T | undefined; isLoading: boolean; isFetching: boolean; error: unknown | null; status: string }): ResourceAsync<T> {
  const status = query.error ? 'rejected' as const : query.data !== undefined ? 'fulfilled' as const : query.isLoading ? 'pending' as const : 'idle' as const;
  const pending = query.isFetching || query.isLoading;
  return {
    data: query.data ?? null,
    status: pending ? 'pending' : status,
    error: query.error ?? null,
    isStale: pending && !!query.data,
    isLoading: pending && !query.data,
    isFetching: pending && !!query.data
  };
}
