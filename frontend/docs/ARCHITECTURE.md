# Oxilière HR Frontend - Architecture & Design Guide

Ce document décrit l'architecture, les patterns de code et le système de design utilisés dans le frontend du projet Oxilière HR. Il est conçu pour aider les IA et les développeurs à comprendre et maintenir le codebase.

## Table des matières

1. [Architecture Générale](#architecture-générale)
2. [Structure des Dossiers](#structure-des-dossiers)
3. [Patterns de Code](#patterns-de-code)
4. [Design System](#design-system)
5. [Composants & Réutilisabilité](#composants--réutilisabilité)
6. [Gestion d'État](#gestion-détat)
7. [Guidelines pour IA](#guidelines-pour-ia)

---

## Architecture Générale

### Stack Technologique

- **Framework**: SvelteKit 2.48+ (Svelte 5.43+)
- **Styling**: Tailwind CSS 4.1+ avec des variables CSS personnalisées
- **State Management**: Svelte Stores avec réactivité `$state` et `$derived`
- **UI Components**: Bits UI + composants personnalisés (inspirés de shadcn)
- **Type Safety**: TypeScript
- **Dev Tools**: Vite, ESLint, Prettier

### Architecture Globale

```
Frontend
├── src/lib/          (Code partagé réutilisable)
├── src/routes/       (Pages & structure navigation)
└── src/components/   (Composants UI & layout)
```

Le projet suit une architecture **modulaire par feature** où chaque domaine métier (employees, jobs, payroll, etc.) est une feature indépendante avec ses propres composants, stores, types et services.

---

## Structure des Dossiers

### `/src/lib/` - Code Partagé

```
lib/
├── api/              # Clients API, requêtes HTTP (base.ts, endpoints)
├── components/       # Composants réutilisables
│   ├── ui/          # Composants UI basiques (Button, Card, Badge, etc.)
│   ├── shared/       # Composants métier partagés (Modal, Empty, Tooltip)
│   └── layout/       # Composants de layout (Header, Sidebar, AppIcon)
├── constants/        # Constantes globales (enum, config statiques)
├── css/              # Styles globaux (app.css)
├── events/           # Événements personnalisés
├── features/         # Code spécifique par feature/domaine
│   ├── {feature}/
│   │   ├── components/      # Composants spécifiques à la feature
│   │   ├── services/        # Logique métier & appels API
│   │   ├── stores/          # Stores Svelte pour l'état
│   │   ├── types/           # Types & interfaces TypeScript
│   │   └── schemas/         # Schémas de validation (Zod, etc.)
├── hooks/            # Hooks réactifs personnalisés
├── stores/           # Stores globaux (auth, notification, settings, ui)
├── types/            # Types globaux & partagés
└── utilities/        # Fonctions utilitaires (date, string, array, ui)
```

### `/src/routes/` - Pages & Navigation

La structure suit la convention de fichiers de SvelteKit :

```
routes/
├── +layout.svelte           # Layout racine
├── +page.svelte             # Page d'accueil
├── {feature}/               # Pages par feature
│   ├── +layout.svelte       # Layout feature
│   ├── +page.svelte         # Page principale
│   └── {subroute}/          # Sous-routes
```

---

## Patterns de Code

### 1. Composants Svelte

#### Convention de Script

```svelte
<script lang="ts">
  // 1. Imports (type d'abord, puis runtime)
  import type { Snippet } from 'svelte';
  import { Button } from '@/components/ui/button';
  import { myStore } from '@/stores/myStore.svelte';

  // 2. Props avec types explicites
  let {
    title,
    description = "Default",
    onSubmit
  } = $props<{
    title: string;
    description?: string;
    onSubmit: (data: any) => void;
  }>();

  // 3. État local
  let isLoading = $state(false);
  let formData = $state({ /* ... */ });

  // 4. État dérivé
  const isValid = $derived(formData.title.length > 0);
  const error = $derived.by(() => {
    if (!formData.email.includes('@')) return 'Email invalide';
    return null;
  });

  // 5. Handlers (groupés par thème)
  function handleClick() { /* ... */ }
  function handleSubmit() { /* ... */ }

  // 6. Lifecycle (si nécessaire)
  import { onMount } from 'svelte';
  onMount(() => { /* ... */ });
</script>
```

#### Snippets pour Composition

Les **snippets** remplacent les slots pour plus de flexibilité :

```svelte
{#snippet badge()}
  <Badge>Content</Badge>
{/snippet}

{#snippet actionButton(icon, label)}
  <Button {icon}>{label}</Button>
{/snippet}

<MyComponent {badge} {actionButton} />
```

### 2. Gestion d'État avec Stores

Tous les stores utilisent la réactivité Svelte 5. Deux patterns :

#### Store Basique

```typescript
// stores/myStore.svelte.ts
export const myStore = (() => {
	let state = $state({ count: 0 });

	return {
		get value() {
			return state.count;
		},
		increment: () => state.count++,
		reset: () => (state.count = 0)
	};
})();
```

#### Store Classe (Recommandé pour Features)

```typescript
// features/employees/stores/employeeStore.svelte.ts
class EmployeeStore {
	employees = $state<Employee[]>([]);
	selectedId = $state<string | null>(null);

	get selected() {
		return this.employees.find((e) => e.id === this.selectedId);
	}

	async add(employee: Employee) {
		this.employees = [...this.employees, employee];
	}

	async update(id: string, updates: Partial<Employee>) {
		this.employees = this.employees.map((e) => (e.id === id ? { ...e, ...updates } : e));
	}

	delete(id: string) {
		this.employees = this.employees.filter((e) => e.id !== id);
	}
}

export const employeeStore = new EmployeeStore();
```

### 3. Appels API & Services

#### Service Pattern

```typescript
// features/employees/services/employeeService.ts
import { api } from '@/api/base';

export const employeeService = {
	async list(filters?: any) {
		const response = await api.get('/employees', { params: filters });
		return response.data;
	},

	async get(id: string) {
		return api.get(`/employees/${id}`);
	},

	async create(data: CreateEmployeeInput) {
		return api.post('/employees', data);
	},

	async update(id: string, data: Partial<Employee>) {
		return api.patch(`/employees/${id}`, data);
	},

	async delete(id: string) {
		return api.delete(`/employees/${id}`);
	}
};
```

#### Utilisation dans Store

```typescript
class EmployeeStore {
	employees = $state<Employee[]>([]);
	isLoading = $state(false);
	error = $state<string | null>(null);

	async loadEmployees() {
		this.isLoading = true;
		this.error = null;
		try {
			this.employees = await employeeService.list();
		} catch (err) {
			this.error = err.message;
		} finally {
			this.isLoading = false;
		}
	}
}
```

### 4. Types & Validation

#### Types TypeScript

```typescript
// features/employees/types/types.ts
export interface Employee {
	id: string;
	firstName: string;
	lastName: string;
	email: string;
	position: string;
	department: string;
	joinDate: Date;
	status: 'active' | 'inactive' | 'on_leave';
	// ...
}

export interface CreateEmployeeInput {
	firstName: string;
	lastName: string;
	email: string;
	// ...
}
```

#### Schémas de Validation (Zod)

```typescript
// features/employees/schemas/employeeSchema.ts
import { z } from 'zod';

export const createEmployeeSchema = z.object({
	firstName: z.string().min(2, 'Min 2 caractères'),
	lastName: z.string().min(2, 'Min 2 caractères'),
	email: z.string().email('Email invalide')
	// ...
});

export type CreateEmployeeForm = z.infer<typeof createEmployeeSchema>;
```

### 5. Gestion des Modifications (Edit/Create Pattern)

Pattern courant pour les listes avec ajout/modification :

```svelte
<script lang="ts">
  let editingItem = $state<Item | null>(null);
  let isSheetOpen = $state(false);

  function handleAdd() {
    editingItem = null;  // Nouveau
    isSheetOpen = true;
  }

  function handleEdit(item: Item) {
    editingItem = item;  // Mode édition
    isSheetOpen = true;
  }

  function handleSave(data: any) {
    if (editingItem) {
      // Update
      store.update(editingItem.id, data);
    } else {
      // Create
      store.add(data);
    }
    isSheetOpen = false;
  }
</script>

<h1>{editingItem ? 'Modifier' : 'Ajouter'}</h1>
<MyForm onSave={handleSave} initialData={editingItem} />
```

---

## Design System

### 1. Palette de Couleurs

Les couleurs sont définies en variables CSS (HSL) dans `src/lib/css/app.css` :

#### Couleurs Principales

- **Primary**: Bleu (`hsl(239, 89%, 64%)`) - Actions principales, boutons CTA
- **Red**: Actions destructives, alertes de suppression
- **Emerald**: Succès, badges validés
- **Amber**: Avertissements
- **Slate**: Texte, backgrounds neutres

#### Palette Étendue

```
Slate (Gris):      #64748b (500), #e2e8f0 (100), #f1f5f9 (50)
Red (Danger):      #dc2626 (600), #fee2e2 (50)
Emerald (Success): #059669 (600), #ecfdf5 (50)
Pink (Accent):     #ec4899 (500), #fce7f3 (50)
Amber (Warning):   #d97706 (600), #fef3c7 (50)
Indigo (Link):     #6366f1 (500)
```

### 2. Typographie

- **Font**: Inter (principale), Ubuntu Mono (code), Geist (sans-serif)
- **Hiérarchie**:
  - `text-[1.1rem] font-extrabold` - Titres principaux
  - `text-[0.9rem] font-bold` - Sous-titres
  - `text-[0.8rem] font-medium` - Corps standard
  - `text-[0.75rem] tracking-tight` - Labels, badges

### 3. Spacing & Layout

Utilisation de Tailwind avec une grille `4px` :

- Padding/Margin: `p-2`, `p-3`, `p-4`, `p-6` (8px, 12px, 16px, 24px)
- Gaps: `gap-2`, `gap-3`, `gap-4`
- Height: `h-11` (44px), `h-10` (40px), `h-8` (32px) pour inputs/boutons

### 4. Bordures & Ombres

#### Bordures

- **Borderline**: `border border-slate-200` (gris clair)
- **Bordures de séparation**: `border-b border-slate-100` ou `border-t border-b`
- **Bordures arrondies**: `rounded-lg` (8px), `rounded-xl` (12px), `rounded-full` (50%)
- **Bordures tiretées**: `border-dashed` pour zones vides

#### Ombres

```
shadow-fine        # Ombre légère
hover:shadow-md    # Ombre au survol
shadow-sm          # Ombre très légère
shadow-xl          # Ombre grande (modales)
```

### 5. États & Transitions

#### Hover

```
hover:bg-slate-50/50      # Background léger
hover:text-primary        # Changement couleur texte
hover:border-primary/20   # Bordure subtile
transition-all            # Animation douce
```

#### Focus / Active

```
focus-visible:outline-2          # Accessibilité
focus-visible:outline-offset-2
text-primary data-[state=open]:bg-slate-100
```

### 6. Composants Courants & Leur Styling

#### Boutons

```svelte
<!-- Primary CTA -->
<Button class="bg-primary! shadow-fine">Action</Button>

<!-- Secondary / Outline -->
<Button variant="outline" size="sm">Label</Button>

<!-- Ghost / Minimal -->
<Button variant="ghost" size="icon" class="rounded-full">
  <AppIcon name="icon" size={20} />
</Button>
```

#### Cards

```svelte
<Card class="shadow-none! border-b border-slate-100 rounded-none">
  <CardHeader class="pb-4 border-b border-slate-50">
    <CardTitle>Titre</CardTitle>
  </CardHeader>
  <CardContent class="p-4">Contenu</CardContent>
</Card>
```

#### Badges

```svelte
<!-- Success -->
<Badge class="bg-emerald-50 text-emerald-600 border-none">OK</Badge>

<!-- Warning -->
<Badge class="bg-amber-50 text-amber-700 border-none">Alert</Badge>

<!-- Danger -->
<Badge class="bg-red-50 text-red-600 border-none">Error</Badge>

<!-- Secondary -->
<Badge variant="secondary">Secondary</Badge>
```

#### Listes avec Bordures

Pattern pour listes d'éléments avec bordures entre eux (pas de superposition) :

```svelte
{#each items as item, index}
  <FamilyMemberRow
    {item}
    isLast={index === items.length - 1}
  />
{/each}

<!-- Dans FamilyMemberRow -->
<div class="{!isLast ? 'border-b border-slate-100' : ''}">...</div>
```

### 7. Composants Spécialisés

#### Empty State

Pour les listes vides, utiliser le composant `Empty` :

```svelte
<Empty
  title="Aucun enfant enregistré"
  description="Ajoutez les enfants de cet employé à son profil."
  icon="users"
  iconClass="text-slate-300"
>
  <Button variant="outline" size="sm" onclick={handleAdd} class="gap-2 mt-4">
    <AppIcon name="plus" size={18} />
    Ajouter
  </Button>
</Empty>
```

#### Action Sheets (Modales latérales)

```svelte
<EmployeeActionSheet
  bind:open={isSheetOpen}
  title={editingItem ? "Modifier" : "Créer"}
>
  {#if isSheetOpen}
    <MyForm onSave={handleSave} initialData={editingItem} />
  {/if}

  {#snippet footer()}
    <Button type="submit" form="my-form">Enregistrer</Button>
  {/snippet}
</EmployeeActionSheet>
```

#### Tooltips

```svelte
<TooltipWrapper content="Aide" side="top" asChild={true}>
  {#snippet children(props)}
    <Button {...props}>Hover pour aide</Button>
  {/snippet}
</TooltipWrapper>
```

#### Confirmation Dialogs

```svelte
<script>
  import { notification } from '@/stores/notification.svelte';

  function handleDelete(id: string, name: string) {
    notification.confirm({
      title: 'Supprimer ?',
      message: `Voulez-vous vraiment supprimer "${name}" ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => store.delete(id)
    });
  }
</script>
```

---

## Composants & Réutilisabilité

### 1. Hiérarchie de Composants

```
ui/                    (Atomes - composants basiques)
├── Button
├── Input
├── Card
├── Badge
└── ...

shared/                (Molécules - composants métier)
├── Empty.svelte       (Empty state avec icône + bouton)
├── TooltipWrapper.svelte
├── AlertDialog.svelte
└── forms/

features/*/components/ (Organismes - composants feature)
├── Lists & Rows       (FamilyMemberRow, EmployeeRow...)
├── Detail Cards       (EmployeeDetails, ContractInfo...)
├── Forms              (EmployeeForm, LeaveForm...)
└── Sections           (EmployeeChildren, EmployeeEmergencyContacts...)
```

### 2. Composants Réutilisables par Feature

#### FamilyMemberRow

Composant pour afficher un membre de famille/contact dans une liste :

```svelte
<FamilyMemberRow
  icon="baby"
  iconClass="text-pink-400"
  title="Jean Dupont"
  subtitle="Enfant • 12 ans"
  onEdit={() => handleEdit(item)}
  onDelete={() => handleDelete(item.id, item.name)}
  isLast={index === items.length - 1}
>
  {#snippet badge()}
    <Badge>Badge content</Badge>
  {/snippet}
</FamilyMemberRow>
```

#### EmployeeActionSheet

Modal latérale pour ajouter/modifier des données :

```svelte
<EmployeeActionSheet
  bind:open={isOpen}
  title="Titre du formulaire"
>
  <!-- Contenu du formulaire -->

  {#snippet footer()}
    <Button type="submit" form="form-id">Soumettre</Button>
  {/snippet}
</EmployeeActionSheet>
```

### 3. Naming Convention

Les noms de composants suivent une convention claire :

- **Routes**: `+page.svelte`, `+layout.svelte`
- **Composants métier**: `EmployeeForm.svelte`, `LeaveRequestList.svelte`
- **Composants UI**: `Button.svelte`, `Card.svelte` (minuscule)
- **Composants conteneurs**: `Empty.svelte`, `TooltipWrapper.svelte`
- **Sous-composants**: `features/{feature}/components/{section}/{Component}.svelte`

---

## Gestion d'État

### 1. Stores Globaux

Véhicular l'état global via `/stores/` :

- `auth.ts` - État de l'utilisateur
- `notification.svelte.ts` - Confirmations & toasts
- `settings.svelte.ts` - Préférences utilisateur
- `ui.svelte.ts` - État UI (sidebar open, etc.)

### 2. Stores Locaux par Feature

Chaque feature a son store dans `features/{feature}/stores/` :

- `employeeStore.svelte.ts`
- `leaveStore.svelte.ts`
- `payrollStore.svelte.ts`

### 3. Communication État

```
Component A
    ↓ (dispatch event ou appelle store)
Store
    ↓ (update state ou fetch data)
API
    ↓
Store updates
    ↓
Component B (abonne à store)
```

### 4. Avoids Anti-Patterns

❌ **À Éviter** :

- Prop drilling excessif (passer les props sur 5+ niveaux)
- Logique métier dans les composants
- États dupliqués entre store et composant
- Pas de type pour les données

✅ **À Faire** :

- Utiliser les stores pour l'état partagé
- Garder les composants simples & présentationels
- Un seule source de vérité par entité
- Types TypeScript strictes

---

## Guidelines pour IA

### 1. Avant de Coder

1. **Comprendre la feature**: Lire la structure `features/{feature}/`
2. **Chercher la réutilisabilité**: Est-ce qu'un composant similaire existe ?
3. **Identifier le scope**: Composant métier ou UI basique ?
4. **Vérifier les types**: Les types sont-ils définis dans `types/`?

### 2. Créer un Nouveau Composant

1. **Déterminer la catégorie**: UI (`components/ui`), Métier (`features/{feature}/components`)?
2. **Inspecter les similaires**: Copier le pattern d'un composant proche
3. **Typer les props**: Utiliser `$props<{}>` avec types explicites
4. **Utiliser les snippets**: Pour la composition plutôt que les slots
5. **Ajouter des commentaires**: Sur la logique complexe

### 3. Ajouter une Feature

Structure minimale pour une nouvelle feature `features/{feature}/`:

```
├── components/         # Composants spécifiques
│   ├── forms/
│   ├── lists/
│   └── detail/
├── services/           # API & logique métier
├── stores/             # État (*.svelte.ts)
├── types/              # Types TypeScript
└── schemas/            # Validation (si besoin)
```

### 4. Intégration Formulaires

Pattern standard :

```svelte
<script>
  // 1. Validation
  import { createEmployeeSchema } from '@/features/employees/schemas';

  // 2. Service
  import { employeeService } from '@/features/employees/services';

  // 3. State
  let formData = $state<typeof createEmployeeSchema>({...});
  let errors = $state<Record<string, string>>({});

  // 4. Handler
  async function handleSubmit() {
    const result = createEmployeeSchema.safeParse(formData);
    if (!result.success) {
      errors = result.error.flatten().fieldErrors;
      return;
    }
    await employeeService.create(result.data);
  }
</script>

<form onsubmit|preventDefault={handleSubmit}>
  <input bind:value={formData.name} />
  {#if errors.name}
    <span class="text-red-600">{errors.name}</span>
  {/if}
</form>
```

### 5. Patterns Courants

#### Lire des données avec Store

```svelte
<script>
  import { employeeStore } from '@/features/employees/stores/employee.svelte';

  onMount(() => employeeStore.loadEmployees());
</script>

{#if employeeStore.isLoading}
  <Spinner />
{:else if employeeStore.error}
  <Alert type="error">{employeeStore.error}</Alert>
{:else}
  {#each employeeStore.employees as emp (emp.id)}
    <EmployeeCard {emp} />
  {/each}
{/if}
```

#### Édition avec Confirmation

```svelte
<script>
  let editingItem = $state<Item | null>(null);

  function handleDelete(id: string, name: string) {
    notification.confirm({
      title: 'Supprimer ?',
      message: `Êtes-vous sûr de supprimer "${name}" ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => store.delete(id)
    });
  }
</script>
```

#### Listes avec Pagination/Filtrage

```svelte
<script>
  let filters = $state({ search: '', status: 'all' });
  let page = $state(1);

  const results = $derived.by(async () => {
    return await service.list({ ...filters, page });
  });
</script>

<input bind:value={filters.search} placeholder="Chercher..." />
{#await results}
  <Spinner />
{:then data}
  {#each data.items as item}...{/each}
{/await}
```

### 6. Débogage

- Ouvrir la console du navigateur (F12)
- Vérifier l'état du store: `console.log(employeeStore)`
- Vérifier les requêtes API: Network tab
- Valider les types: `pnpm run check`

### 7. Performance

- Éviter les données inutiles dans les templates (`{#if condition}`)
- Utiliser `$derived` pour les calculs récursifs
- Mémoriser les API calls dans les stores
- Utiliser `:key` dans les boucles

### 8. Accessibilité

- Tous les boutons cliquables doivent être des `<button>` ou `<Button>`
- Image/icône sans label → `aria-label` ou `sr-only`
- Formulaires → labels `<label for="id">`
- Keyboard navigation → `(focus-visible:outline...)`

---

## Directives Finales

1. **TOUJOURS** vérifier les types et structures existants
2. **TOUJOURS** réutiliser les composants existants
3. **Garder les composants petits** (< 200 lignes)
4. **Nommer clairement** (éviter `Item`, `Data`, préférer `Employee`, `Leave`)
5. **Documenter le code complexe** (logique métier, calculs)
6. **Tester les changements** (`npm run check`, browser)
7. **Suivre les patterns** du codebase (cohérence > perfection)
