export type FilterRecord = Record<string, string[]>;

export function createFilterState<F extends FilterRecord>(initial: F) {
  let search = $state('');
  let filters = $state<F>({ ...initial } as F);
  let page = $state(1);
  let perPage = $state(10);
  let sortBy = $state('');
  let sortOrder = $state<'asc' | 'desc'>('asc');
  let viewMode = $state<'list' | 'grid'>('list');

  const activeFiltersCount = $derived(Object.values(filters as Record<string, string[]>).flat().length);

  function toggleFilter<K extends keyof F>(key: K, value: string) {
    const arr = (filters[key] as string[]) ?? [];
    const next = arr.includes(value) ? arr.filter(v => v !== value) : [...arr, value];
    filters = { ...filters, [key]: next } as F;
    page = 1;
  }
  function setSearch(v: string) { search = v; page = 1; }
  function resetFilters() { filters = { ...initial } as F; search = ''; page = 1; }
  function setPage(p: number) { page = p; }
  function setPerPage(p: number) { perPage = p; page = 1; }
  function setSort(by: string, order: 'asc' | 'desc') { sortBy = by; sortOrder = order; }
  function toggleViewMode() { viewMode = viewMode === 'list' ? 'grid' : 'list'; }

  return {
    get search() { return search; }, set search(v: string) { search = v; page = 1; },
    get filters() { return filters; }, set filters(v: F) { filters = v; },
    get page() { return page; }, set page(v: number) { page = v; },
    get perPage() { return perPage; }, set perPage(v: number) { perPage = v; },
    get sortBy() { return sortBy; }, set sortBy(v: string) { sortBy = v; },
    get sortOrder() { return sortOrder; }, set sortOrder(v: 'asc' | 'desc') { sortOrder = v; },
    get viewMode() { return viewMode; }, set viewMode(v: 'list' | 'grid') { viewMode = v; },
    get activeFiltersCount() { return activeFiltersCount; },
    toggleFilter, resetFilters, setSearch, setPage, setPerPage, setSort, toggleViewMode,
    nextPage() { page = page + 1; },
    prevPage() { page = Math.max(1, page - 1); }
  };
}
