# Migration — Page d'accueil vers `hr/dashboard`

## Avant

```svelte
<Card><CardTitle>Total Employés</CardTitle><p>1,284</p></Card> <!-- en dur -->
```

## Après

```svelte
<script>
  const dashboard = createDashboard({ role: auth.role, widgets: [headcount(), leavesPending()] });
</script>
<DashboardView {dashboard} />
```

## Check-list

1. Créer `dashboard` avec `role` et `widgets` souhaités
2. Brancher `period` sur `FilterMenu` (`hr/actions`) si besoin
3. Remplacer les `Card` en dur par `DashboardView`
