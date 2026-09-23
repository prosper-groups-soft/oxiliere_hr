# API — Comment l'utiliser au quotidien ?

L'idée est de remplacer, dans chaque module, une trentaine de lignes dupliquées par une seule déclaration d'onglets.

## Exemples de code

```svelte
<!-- On décrit les onglets de ce module -->
<script>
  const tabs = [
    { id: 'campaigns', label: 'Campagnes', icon: 'flag', path: hr('/performance/campaigns') },
    { id: 'reviews', label: 'Évaluations', icon: 'star', path: hr('/performance/reviews'), count: 3 }
  ];
</script>

<!-- On les affiche avec un seul composant générique -->
<NavTabs {tabs} activeId={activeTabId} variant="underline" onChange={(id) => goto(tabs.find(t => t.id === id)?.path)} />
```

Ainsi, ajouter un onglet revient à ajouter une ligne dans le tableau `tabs`, sans toucher à l'animation ou aux styles.
