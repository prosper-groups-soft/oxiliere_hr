# API — Comment l'utiliser au quotidien ?

L'idée est de décrire le tableau de bord comme on décrit un formulaire : on liste les widgets souhaités, la bibliothèque s'occupe de les afficher au bon rôle.

## Exemples de code

```ts
// On décrit le tableau de bord pour le rôle en cours
const dashboard = createDashboard({
  role: auth.role, // 'admin' | 'hr' | 'employee'
  widgets: [headcount(), leavesPending(), recruitmentOpen(), payrollMass()],
  layout: { type: 'grid', columns: 4 },
  refresh: { policy: 'poll', interval: 5 * 60 * 1000 }
});

// Un widget sait d'où vient sa donnée, pas comment il s'affiche
const headcount = kpi({
  metric: { source: 'employees', formula: 'count' },
  period: 'month',
  visibleIf: (role) => role === 'admin' || role === 'hr'
});
```

```svelte
<!-- On affiche le tableau de bord, chaque widget interroge sa source via hr/async -->
<DashboardView {dashboard} />
```

Ainsi, ajouter un widget revient à ajouter une ligne dans la liste des widgets, sans toucher à la page d'accueil elle-même.
