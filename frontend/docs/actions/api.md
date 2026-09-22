# API — Comment l'utiliser au quotidien ?

L'idée est de remplacer, dans chaque barre d'actions, plusieurs menus dupliqués par deux composants simples : un menu unique pour tous les filtres, et un menu à part pour le tri.

## Exemples de code

```svelte
<!-- 1. On décrit les filtres de cette page -->
<script>
  const filterDefs = [
    { key: 'orgUnit', label: 'Unité', icon: 'building', mode: 'multi', options: orgUnits },
    { key: 'status', label: 'Statut', icon: 'activity', mode: 'multi', options: statusOptions }
  ];
  const sortDefs = { options: [{ value: 'name', label: 'Nom' }], value: ui.sortBy, order: ui.sortOrder };
</script>

<!-- 2. On les affiche avec deux menus génériques -->
<ActionBar>
  <FilterMenu {filterDefs} bind:filterState={ui} />
  <SortMenu {sortDefs} bind:filterState={ui} />
  <ViewMode bind:filterState={ui} />
  <Primary label="Nouvel employé" onClick={openCreate} />
</ActionBar>
```

Ainsi, ajouter un filtre revient à ajouter une ligne dans `filterDefs`, sans toucher à l'interface.
