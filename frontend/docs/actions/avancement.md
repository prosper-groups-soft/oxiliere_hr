# Actions — État d'avancement

> Mis à jour le 22/09/2026.

## Constat

20 fichiers `*Actions.svelte` dupliquent `DropdownMenu` par dimension (4 menus pour employés).

## Lots

- **Lot 0 — Docs** : vision, metamodel, semantics, catalogue, api, ux, avancement, migration (fait)
- **Lot 1 — Lib `hr/actions`** : `FilterMenu` (single Dropdown), `SortMenu` (séparé), `ActionBar` (Composite)
- **Lot 2 — Pilote `employees`** : remplacer 4 dropdowns par `FilterMenu` + `SortMenu` sur `employeesUi`
- **Lot 3 — Batch** : `leaves`, `payroll`, `recruitment`, `attendance`, `calendar`
