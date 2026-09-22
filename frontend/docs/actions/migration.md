# Migration — Barre d'actions vers `hr/actions`

## Avant

```svelte
<DropdownMenu.Root> <!-- Tri -->
<DropdownMenu.Root> <!-- Unité -->
<DropdownMenu.Root> <!-- Statut -->
<DropdownMenu.Root> <!-- Contrat -->
```

## Après

```svelte
<ActionBar>
  <FilterMenu {filterDefs} bind:filterState={ui} />
  <SortMenu {sortDefs} bind:filterState={ui} />
</ActionBar>
```

## Check-list

1. Déclarer `filterDefs: FilterDef[]` (key, label, icon, mode, options)
2. Déclarer `sortDefs: SortDef` (options, value, order)
3. Remplacer N `DropdownMenu.Root` par `FilterMenu` + `SortMenu`
4. Brancher sur `filterState` (`hr/async` `createFilterState`)
5. Supprimer `store.toggleFilter` direct, badges manuels
