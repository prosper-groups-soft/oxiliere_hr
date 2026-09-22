# API — Comment l'utiliser au quotidien ?

L'idée est de remplacer, dans chaque page, une vingtaine de lignes répétées par trois éléments simples :

1. **Un gestionnaire de filtres** qui centralise la recherche, les filtres choisis, la pagination et le tri. Il sait combien de filtres sont actifs, comment en retirer un, et comment revenir à la première page quand un critère change.

2. **Une ressource asynchrone** qui s'occupe d'appeler le serveur dès que les filtres changent, et qui expose clairement son état : est-ce en train de charger ? Est-ce que ce sont les premières données ou une mise à jour ? Y a-t-il une erreur ?

3. **Une vue unifiée** qui, à partir de cette ressource, affiche automatiquement le bon écran : le chargement initial, le message d'erreur avec un bouton pour réessayer, le message de liste vide, ou enfin la liste elle-même. La page n'a plus qu'à décrire à quoi ressemble le cas où tout va bien.

Ainsi, ajouter une nouvelle page revient à dire "voici mes filtres et comment interroger le serveur", le reste étant pris en charge de manière cohérente dans toute l'application.

## Exemples de code

```ts
// 1. Filtres — on déclare ce qui existe pour cette page
const ui = createFilterState<{ orgUnit: string[], status: string[] }>({
  orgUnit: [], status: []
});
// ui.search, ui.filters, ui.page, ui.toggleFilter(), ui.resetFilters(), etc.

// 2. Ressource — le serveur est interrogé dès que les filtres changent
const employees = useAsyncResource(
  () => employeesService.listEmployees({ page: ui.page, search: ui.search, filters: ui.filters }),
  { mapData: d => ({ items: d.results, total: d.count }) }
);
// employees.data, employees.isLoading, employees.isFetching, employees.error

// 3. Vue — un seul composant affiche le bon état
<AsyncView state={employees} emptyWhen={d => d.total === 0}>
  {#snippet success(data)}
    <EmployeeList employees={data.items} />
  {/snippet}
</AsyncView>
<DataPagination totalCount={employees.data?.total} currentPage={ui.page} onPageChange={ui.setPage} />
```
