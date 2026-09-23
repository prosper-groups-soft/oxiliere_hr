# Migration — Onglets vers `hr/navigation`

## Avant

```svelte
<Tabs.Root><Tabs.List><Tabs.Trigger>...</Tabs.Trigger></Tabs.List></Tabs.Root>
<!-- + 40 lignes de indicatorStyle, tabElements, cn, AppIcon dupliquées -->
```

## Après

```svelte
<script>
  const tabs = [{ id: 'campaigns', label: 'Campagnes', icon: 'flag', path: hr('/performance/campaigns') }];
</script>
<NavTabs {tabs} activeId={activeTabId} variant="underline" onChange={(id) => goto(tabs.find(t => t.id === id)?.path)} />
```

## Check-list

1. Déclarer `tabs: TabDef[]` (id, label, icon, path?, count?)
2. Remplacer `Tabs.Root/List/Trigger` + `indicatorStyle` par `<NavTabs>`
3. Supprimer `cn`, `AppIcon`, `tabElements` dupliqués
