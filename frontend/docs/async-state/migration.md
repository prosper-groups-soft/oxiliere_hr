# Migration — Pages vers `hr/async`

> Guide pas à pas pour migrer une page qui utilise encore `use*Query + sync*Store + 2 $effect` vers `createFilterState + useAsyncResource + AsyncView`.

## 1. Avant (à remplacer)

```svelte
<script>
  const q = useEmployeesQuery(() => store.page, () => store.search, () => store.filters, ...);
  $effect(() => syncEmployeesStore($q));
  $effect(() => { store.filters.status; store.search; get(q).refetch(); });
</script>

<LoadingBar loading={$q.isFetching} />
{#if $q.isLoading && store.totalCount===0}<AnimateSpin />{:else if $q.error}<Empty />{:else}<List />{/if}
<DataPagination totalCount={store.totalCount} />
```

## 2. Après (cible)

```svelte
<script>
  import { createFilterState } from '@/hr/async/filters/filterState.svelte';
  import { useAsyncResource } from '@/hr/async/core/useAsyncResource.svelte';
  import AsyncView from '@/hr/async/components/AsyncView.svelte';

  const ui = createFilterState<{ status: string[] }>({ status: [] });
  const res = useAsyncResource(
    () => ({
      queryKey: ['employees', ui.page, ui.search, ui.filters],
      queryFn: () => employeesService.listEmployees({ page: ui.page, search: ui.search, filters: ui.filters })
    }),
    { mapData: d => ({ items: d.results, total: d.count }) }
  );
</script>

<SearchBar bind:value={ui.search} />
<FilterChips filters={ui.filters} onRemove={(k,v)=>ui.toggleFilter(k,v)} onReset={ui.resetFilters} />
<AsyncView state={res} emptyWhen={d=>d.total===0}>
  {#snippet success(data)}<List items={data.items} />{/snippet}
</AsyncView>
<DataPagination totalCount={res.data?.total} currentPage={ui.page} onPageChange={ui.setPage} />
```

## 3. Check-list

1. Déclarer `ui = createFilterState<Filters>(initial)` (typé par module)
2. Remplacer `use*Query + sync*Store + 2 $effect` par `useAsyncResource(() => ({ queryKey, queryFn }), { mapData })`
3. Remplacer `{#if isLoading} {:else if error}` par `<AsyncView state={res}>`
4. Brancher `SearchBar/FilterChips/DataPagination` sur `ui.*` (plus `store.*`)
5. Supprimer `setEmployees/setLoading/setError/paginatedEmployees` du store (garder que `viewMode` si besoin)
6. Vérifier `npx tsc --skipLibCheck | Select-String "async"` → 0 erreur ciblée

## 4. Ordre recommandé

- Pilote : `employees` (fait)
- Lot 2 : `recruitment` (transverse)
- Lot 3 : `performance`, `jobs`, `payroll`, `banking` (batch)
