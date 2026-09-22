# Async Resource — État d'avancement

> Fichier de suivi : une nouvelle session doit pouvoir reprendre à partir de ce seul fichier.
> Mis à jour le 22/09/2026.

## Constat (audit 22/09/2026)

8+ pages dupliquent le même cycle : `use*Query → sync*Store → 2 $effect (refetch)` + UI `LoadingBar + AnimateSpin + Empty + SearchBar + FilterChips + DataPagination`.
Le store mélange état UI (filtres, pagination) et état fetch (données, chargement, erreur), ce qui rend la maintenance coûteuse.

**Lib créée** : `src/lib/hr/async/` (hors `forms/` — agnostique, cf. `forms-bindings` pour les types métier).
**Pilote** : `routes/hr/employees/+page.svelte` migré vers `createFilterState + useAsyncResource + AsyncView`.

## Lots

### Lot 0 — Fondations — TERMINÉ (22/09/2026)
- `hr/async/core/asyncState.svelte.ts` : `ResourceAsync<T>`, `toResource()`
- `hr/async/core/useAsyncResource.svelte.ts` : wrapper TanStack `createQuery` (staleTime 5m)
- `hr/async/filters/filterState.svelte.ts` : factory générique `createFilterState<F>()`
- `hr/async/components/AsyncView.svelte` : LoadingBar + AnimateSpin + Empty + Réessayer
- Docs `frontend/docs/async-state/` : vision, metamodel, semantics, catalogue, api (format explicatif, pas code brut)

### Lot 1 — Pilote employees — TERMINÉ (22/09/2026)
- `routes/hr/employees/+page.svelte` : remplacé `employeeStore`/`syncEmployeesStore`/`2 $effect` par `ui = createFilterState(...)` + `employees = useAsyncResource(...)` + `<AsyncView state={employees}>`
- Filtres génériques : `{ orgUnit, status, location, contractType }` — plus de store monolithe
- `tsc --skipLibCheck` : 0 erreur sur `hr/async` + pilote (34 erreurs pré-existantes ailleurs)

### À faire (généralisation)
- Lot 2 : `recruitment` (même pattern paginé, test transverse)
- Lot 3 : `performance`, `jobs`, `payroll`, `banking` (batch)
- Optionnel : `hr/async/filters/queryParams.svelte.ts` (sync filtres ↔ URL)
