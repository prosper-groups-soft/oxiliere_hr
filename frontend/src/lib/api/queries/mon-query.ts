// src/lib/api/queries/mon-query.ts
import { queryOptions } from '@tanstack/svelte-query';
import { MonEndpoint } from '../endpoints/MonEndpoint';


export const monQueryOptions = {
  list: () => queryOptions({
    queryKey: ['items'],
    queryFn: () => MonEndpoint.items.list(),
  }),
};

