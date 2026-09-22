import { createQuery } from '@tanstack/svelte-query';
import { get } from 'svelte/store';
import { toResource, type ResourceAsync } from './asyncState.svelte.js';

export function useAsyncResource<T, M = T>(
  queryFactory: () => { queryKey: unknown[]; queryFn: () => Promise<T> },
  opts?: { mapData?: (data: T) => M; staleTime?: number }
): ResourceAsync<M> & { refetch: () => void; query: any } {
  const q: any = createQuery({
    get queryKey() { return queryFactory().queryKey; },
    queryFn: async () => {
      const raw = await queryFactory().queryFn();
      return opts?.mapData ? (opts.mapData(raw) as unknown as T) : raw;
    },
    staleTime: opts?.staleTime ?? 5 * 60 * 1000
  } as any);

  let qVal: any = $state(null);
  $effect(() => { const unsub = q.subscribe((v: any) => qVal = v); return () => unsub(); });
  const res = $derived(toResource<M>({ data: qVal?.data as M | undefined, isLoading: !!qVal?.isLoading, isFetching: !!qVal?.isFetching, error: qVal?.error ?? null, status: qVal?.status ?? 'idle' }));

  return {
    get data() { return res.data; },
    get status() { return res.status; },
    get error() { return res.error; },
    get isStale() { return res.isStale; },
    get isLoading() { return res.isLoading; },
    get isFetching() { return res.isFetching; },
    refetch: () => (get(q) as any)?.refetch?.(),
    query: q
  } as any;
}
