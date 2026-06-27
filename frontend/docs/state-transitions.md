# Gestion des Transitions d'État sans Flash

## Problème

Lors du changement d'état dans une liste avec recherche/filtres, on observe :
- **Flash** : alternance brutale entre états (loading → vide → contenu)
- **Clignotement** : l'icône "aucun résultat" apparaît brièvement avant la liste
- **Transitions abruptes** : disparition brutale des éléments (FilterChips, etc.)

## Solution Architecture

### 1. Store Pattern

```typescript
export class DataStore {
  // --- État de base ---
  items = $state<Item[]>([]);
  isLoading = $state(false);
  hasLoaded = $state(false);  // Premier chargement terminé ?
  hasEverSeenData = $state(false);  // Au moins un item chargé un jour ?
  
  // --- État dérivé pour les transitions ---
  viewState = $derived(
    !this.hasLoaded && this.isLoading ? 'initial-loading' :
    this.items.length > 0 ? 'content' :
    'empty'
  );
  
  async fetchItems() {
    this.isLoading = true;
    // NOTE: NE PAS reset hasLoaded ici pour garder l'état précédent visible
    
    try {
      const response = await api.fetch(...);
      this.items = response.results;
      if (response.results.length > 0) {
        this.hasEverSeenData = true;  // Persiste pour toute la session
      }
    } finally {
      this.isLoading = false;
      this.hasLoaded = true;
    }
  }
}
```

**Points clés :**
- `hasLoaded` : évite l'état vide pendant le chargement initial
- `hasEverSeenData` : empêche l'icône "vide système" quand on sait qu'il y a des données
- `viewState` dérivé : logique centralisée, pas de conditions complexes dans le composant

### 2. Composant Pattern

```svelte
<script>
  import { fade } from 'svelte/transition';
</script>

{#snippet EmptyState()}
  {@const icon = store.activeFiltersCount > 0 || store.hasEverSeenData ? "search" : "folder"}
  {@const description = store.activeFiltersCount > 0 || store.hasEverSeenData
    ? "Essayez d'ajuster vos filtres"
    : "Aucun élément dans le système"}
  <div class="absolute inset-0 flex items-center justify-center" 
       in:fade={{ duration: 200, delay: 50 }}>
    <Empty {icon} title="Aucun résultat" {description} />
  </div>
{/snippet}

<div class="relative">
  {#if store.viewState === 'initial-loading'}
    <!-- Spinner seulement au premier chargement -->
    <div in:fade out:fade>
      <Spinner />
    </div>
    
  {:else if store.viewState === 'content'}
    <!-- Liste avec fade-in -->
    <div in:fade={{ duration: 200 }}>
      {#each store.items as item}
        <ItemRow {item} />
      {/each}
    </div>
    
  {:else}
    <!-- État vide -->
    {@render EmptyState()}
  {/if}
</div>
```

**Points clés :**
- 3 états uniquement : `'initial-loading' | 'content' | 'empty'`
- Pas de `{:else if ... && ... && ...}` complexes
- `fade` avec `delay` pour éviter le flash sur les transitions rapides
- Snippet `EmptyState` pour encapsuler la logique d'icône/message

### 3. Recherche avec Debounce

Le composant `SearchBar` gère son propre état de debounce :

```svelte
<!-- SearchBar.svelte -->
<script>
  let { 
    value = $bindable(),
    debounceMs = 300,
    onSearch = (q: string) => {}
  } = $props();
  
  let isSearching = $state(false);
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  function handleInput() {
    isSearching = true;
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => {
      isSearching = false;
      onSearch(value);
    }, debounceMs);
  }
</script>

<!-- Icône search ↔ spinner selon isSearching -->
{#if isSearching}
  <Spinner />
{:else}
  <SearchIcon />
{/if}
```

**Avantages :**
- Réutilisable partout sans dépendance au store
- Feedback immédiat à l'utilisateur (spinner dès la frappe)
- API simple : `onSearch` appelé après le délai

### 4. Transitions Douces des Filtres

Pour éviter la disparition brutale des `FilterChips` :

```svelte
<!-- FilterChips.svelte -->
<script>
  import { slide } from 'svelte/transition';
</script>

{#if activeFiltersCount > 0}
  <div transition:slide={{ duration: 200 }}>
    <!-- chips -->
  </div>
{/if}
```

## Checklist d'Implémentation

Pour réutiliser ce pattern sur un nouveau composant :

### Store
- [ ] Ajouter `hasLoaded = $state(false)`
- [ ] Ajouter `hasEverSeenData = $state(false)`
- [ ] Créer `viewState` dérivé avec les 3 états
- [ ] Dans `fetch()`, set `hasEverSeenData = true` si données présentes
- [ ] NE PAS reset `hasLoaded` dans `fetch()`

### Composant
- [ ] Utiliser `{#if viewState === 'X'}` (pas de conditions complexes)
- [ ] Extraire `EmptyState` dans un snippet
- [ ] Utiliser `fade` avec `delay` sur l'état vide
- [ ] Pas de `out:fade` pour éviter les superpositions

### SearchBar
- [ ] Utiliser le composant `SearchBar` qui gère le debounce en interne
- [ ] Passer `onSearch` (appelé après debounce), pas `onInput`

## Exemple Complet : Liste d'Employés

```typescript
// stores/employeeStore.svelte.ts
export class EmployeeStore {
  employees = $state<Employee[]>([]);
  isLoading = $state(false);
  hasLoaded = $state(false);
  hasEverSeenEmployees = $state(false);
  
  viewState = $derived(
    !this.hasLoaded && this.isLoading ? 'initial-loading' :
    this.employees.length > 0 ? 'content' :
    'empty'
  );
  
  async fetchEmployees(filters?: Filters) {
    this.isLoading = true;
    try {
      const res = await api.getEmployees(filters);
      this.employees = res.results;
      if (res.results.length > 0) this.hasEverSeenEmployees = true;
    } finally {
      this.isLoading = false;
      this.hasLoaded = true;
    }
  }
}
```

```svelte
<!-- components/EmployeeList.svelte -->
<script>
  import { fade } from 'svelte/transition';
  import { employeeStore } from '../stores/employeeStore.svelte';
</script>

{#snippet EmptyState()}
  {@const hasFilters = employeeStore.activeFiltersCount > 0}
  {@const hasData = employeeStore.hasEverSeenEmployees}
  <div in:fade={{ duration: 200, delay: 50 }}>
    <Empty 
      icon={hasFilters || hasData ? "search" : "users"}
      description={hasFilters || hasData 
        ? "Aucun employé ne correspond" 
        : "Aucun employé dans le système"}
    />
  </div>
{/snippet}

{#if employeeStore.viewState === 'initial-loading'}
  <Spinner />
{:else if employeeStore.viewState === 'content'}
  <div in:fade>
    {#each employeeStore.employees as emp}
      <EmployeeCard {emp} />
    {/each}
  </div>
{:else}
  {@render EmptyState()}
{/if}
```

## Anti-Patterns à Éviter

❌ **Ne pas faire :**
```svelte
<!-- Conditions complexes dans le template -->
{#if items.length === 0 && !isLoading && hasLoaded && !searchQuery}
  <Empty icon="users" />
{:else if items.length === 0 && !isLoading && hasLoaded && searchQuery}
  <Empty icon="search" />
{/if}
```

❌ **Ne pas faire :**
```typescript
// Reset hasLoaded dans fetch()
async fetch() {
  this.isLoading = true;
  this.hasLoaded = false;  // ← Crée un flash!
  // ...
}
```

❌ **Ne pas faire :**
```svelte
<!-- Superposition avec z-index -->
<div class={isLoading ? 'z-10' : 'z-0'}>Spinner</div>
<div class={!isLoading && items.length > 0 ? 'z-10' : 'z-0'}>Liste</div>
```

## Pattern Moderne : TanStack Query (Svelte Query)

Pour les features complexes avec données relationnelles et mutations, utiliser **TanStack Query** avec ce pattern :

### Architecture en Couches

```
UI (Svelte Component)
    ↓ $props() / $bindable()
Store (Svelte 5 $state) ← UI State, validation, form data
    ↓ getPendingChanges()
Mutation (TanStack Query) ← Orchestration, cache, error handling
    ↓ HTTP calls
Service (TypeScript) ← API layer, error parsing
    ↓ REST API
Backend (Django)
```

### Exemple : Leave Settings avec Policy dépendante

**1. Queries avec ID réactif** (`+page.svelte`):

```typescript
// Le policyId est derived des données de la première query
const policiesQuery = useLeavePoliciesQuery();

const cdPolicy = $derived.by(() => {
  const policies = $policiesQuery.data ?? [];
  return policies.find(p => p.country_code === DEFAULT_COUNTRY_CODE);
});

const policyId = $derived(cdPolicy?.id ?? null);

// IMPORTANT: Recréer les queries quand policyId change
let circumstanceRulesQuery = $state(useCircumstanceRulesQuery(null));
let seniorityRulesQuery = $state(useSeniorityRulesQuery(null));
let lastPolicyId = $state<string | null>(null);

$effect(() => {
  const pid = policyId;
  if (pid && pid !== lastPolicyId) {
    circumstanceRulesQuery = useCircumstanceRulesQuery(pid);
    seniorityRulesQuery = useSeniorityRulesQuery(pid);
    lastPolicyId = pid;
  }
});
```

**2. Chargement dans le store** (`+page.svelte`):

```typescript
let loadedPolicyId = $state<string | null>(null);

$effect(() => {
  const policy = cdPolicy;
  const circumstances = $circumstanceRulesQuery.data;
  const seniority = $seniorityRulesQuery.data;
  
  // Charger une seule fois par policy
  if (policy && 
      Array.isArray(circumstances) && 
      Array.isArray(seniority) && 
      policy.id !== loadedPolicyId) {
    leaveSettingsStore.loadFromData(policy, circumstances, seniority);
    loadedPolicyId = policy.id;
  }
});
```

**3. Mutations orchestrées** (`leaveQueries.ts`):

```typescript
export function useSaveLeaveSettingsMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: async () => {
      const changes = leaveSettingsStore.getPendingChanges();
      
      // Appels API via le service
      if (changes.policy) {
        await leaveSettingsService.updatePolicy(...);
      }
      if (changes.seniorityRule?.type === 'update') {
        await leaveSettingsService.updateSeniorityRule(...);
      }
      // ... autres updates
    },
    
    onSuccess: () => {
      // Invalidation du cache → re-fetch automatique
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
      leaveSettingsStore.commitChanges();
    },
  });
}
```

### Checklist TanStack Query

- [ ] **Queries** : `createQuery({ queryKey, queryFn, enabled })`
- [ ] **Queries réactives** : Recréer avec `$state` + `$effect` quand l'ID change
- [ ] **Mutations** : `createMutation({ mutationFn, onSuccess })`
- [ ] **Invalidation** : `queryClient.invalidateQueries({ queryKey })` dans `onSuccess`
- [ ] **Service** : Couche HTTP pure, jamais appelé directement par l'UI
- [ ] **Store** : État local uniquement, pas de `fetch()` dans le store
- [ ] **UI** : `$derived` pour les états combinés (`isLoading`, `error`)

### Différences clés avec le pattern "vanilla"

| Aspect | Pattern Vanilla | Pattern TanStack Query |
|--------|----------------|------------------------|
| **Data fetching** | `store.fetch()` | `useQuery()` dans le composant |
| **Cache** | Manuel | Automatique (staleTime, gcTime) |
| **Re-fetch** | Manuel | Auto sur focus, reconnect, mutation |
| **Loading state** | `store.isLoading` | `$query.isLoading` |
| **Mutations** | Directe dans store | `useMutation()` + orchestration |
| **Erreurs** | `store.error` | `$query.error` + `mutation.error` |

## Résumé

| État | Condition | Affichage |
|------|-----------|-----------|
| `initial-loading` | `!hasLoaded && isLoading` | Spinner |
| `content` | `items.length > 0` | Liste avec fade-in |
| `empty` | `hasLoaded && items.length === 0` | EmptyState avec fade + delay |

**Règle d'or** : Un seul état actif à la fois, pas de superpositions. Les transitions se font par remplacement du DOM avec `{#if}` + transitions Svelte.

**Quand utiliser quel pattern ?**
- **Vanilla** : Listes simples, CRUD basique, pas de relations complexes
- **TanStack Query** : Données relationnelles, cache important, mutations multiples, état serveur complexe

## Pattern: Filtres Réactifs avec TanStack Query

### Problème
Avec TanStack Query, la fonction `useUsersQuery(() => filters)` crée la query une seule fois au montage. Quand les filtres changent (recherche, pagination, filtres actifs), la query n'est pas automatiquement invalidée et les données restent stale.

### Solution
Utiliser `useQueryClient` + `$effect` pour invalider la query quand les filtres changent :

```svelte
<!-- UsersManagement.svelte -->
<script lang="ts">
  import { useUsersQuery } from "../../queries/accessQueries.svelte";
  import { useQueryClient } from '@tanstack/svelte-query';
  import { accessUserStore } from "../../stores/accessUserStore.svelte";

  // TanStack Query hooks
  const queryClient = useQueryClient();
  const usersQuery = useUsersQuery(() => accessUserStore.queryFilters);
  
  // Refetch automatique quand les filtres changent
  $effect(() => {
    const filters = accessUserStore.queryFilters;
    queryClient.invalidateQueries({ queryKey: ['access', 'users', 'list'] });
  });
</script>
```

### Points clés

1. **Récupérer `queryClient`** : Importez-le depuis `@tanstack/svelte-query` (pas depuis vos queries locales)
2. **Observer les filtres** : L'`$effect` track automatiquement `accessUserStore.queryFilters` car c'est un `$derived`
3. **Invalider par queryKey** : Utilisez le préfixe de la queryKey (ex: `['access', 'users', 'list']`) pour invalider toutes les variations

### Store Pattern

Le store expose un `queryFilters` dérivé qui regroupe tous les filtres UI :

```typescript
// stores/accessUserStore.svelte.ts
export class AccessUserStore {
  searchQuery = $state('');
  selectedGroups = $state<string[]>([]);
  selectedRoles = $state<string[]>([]);
  isActiveFilter = $state<boolean | null>(null);
  currentPage = $state(1);
  perPage = $state(8);

  // Tous les filtres exposés en un seul objet réactif
  queryFilters = $derived({
    search: this.searchQuery || undefined,
    page: this.currentPage,
    page_size: this.perPage,
    groups: this.selectedGroups.length > 0 ? this.selectedGroups : undefined,
    roles: this.selectedRoles.length > 0 ? this.selectedRoles : undefined,
    is_active: this.isActiveFilter !== null ? this.isActiveFilter : undefined
  });
}
```

### Query Pattern

La query utilise un getter pour le `queryKey` pour être réactive :

```typescript
// queries/accessQueries.svelte.ts
export function useUsersQuery(filtersGetter: () => UserFilters) {
  return createQuery({
    get queryKey() {
      const filters = filtersGetter();
      return ['access', 'users', 'list', filters];
    },
    queryFn: () => {
      const filters = filtersGetter();
      return accessUserService.listUsers(filters);
    },
  });
}
```

**Pourquoi un getter ?** TanStack Query détecte les changements de `queryKey`. Avec un getter, le `queryKey` est recalculé à chaque fois que les filtres changent, mais il faut quand même appeler `invalidateQueries()` pour forcer le refetch immédiat.

### Avantages
- **Réactivité immédiate** : Les filtres s'appliquent instantanément sans navigation
- **Cache intelligent** : TanStack Query gère le cache et les requêtes en doublon
- **Dépendances claires** : L'`$effect` montre explicitement la relation filtres → refetch

### Anti-pattern à éviter

❌ **Ne pas faire** : Recréer la query manuellement
```svelte
<!-- Mauvais: Crée une nouvelle query instance à chaque changement -->
$effect(() => {
  const slug = group.slug;
  if (slug && slug !== lastGroupSlug) {
    membersQuery = useGroupMembersQuery(slug);  // ← Crée des fuites !
    lastGroupSlug = slug;
  }
});
```

✅ **Faire** : Invalider la query existante
```svelte
<!-- Bon: Invalide le cache, la query se refetch avec la nouvelle key -->
$effect(() => {
  const filters = accessUserStore.queryFilters;
  queryClient.invalidateQueries({ queryKey: ['access', 'users', 'list'] });
});
```

