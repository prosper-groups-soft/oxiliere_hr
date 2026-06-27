# Contraintes et Contexte Technique - Oxiliere HR

> **Document de référence obligatoire** - Ce fichier définit les contraintes architecturales et technologiques du projet. Toute intervention doit respecter ces contraintes.

---

## Stack Technique Globale

### Frontend
| Catégorie | Technologie | Contrainte |
|-----------|-------------|------------|
| Framework | **SvelteKit** | Obligatoire - pas de React/Vue/Angular |
| Langage | **Svelte 5** | Utiliser les runes (`$state`, `$derived`, `$effect`, `$props`) |
| Styling | **Tailwind CSS** | Uniquement - pas de CSS modules ou styled-components |
| UI Primitives | **bits-ui** | Composants headless basés sur Melt UI |
| Icons | **Lucide** | Via `lucide-svelte` |
| State Server | **TanStack Query** | (`@tanstack/svelte-query`) pour toute donnée serveur |
| State Client | **Svelte 5 Stores** | Classes avec état réactif (`$state`), pas de Redux/Zustand |
| HTTP Client | **Axios** | Avec intercepteurs pour auth et tenant |
| Validation | **Zod** | Schémas de validation côté client |
| Package Manager | **pnpm** | Commande: `pnpm add` (pas npm/yarn) |

### Backend
| Catégorie | Technologie | Contrainte |
|-----------|-------------|------------|
| Framework | **Django + Ninja Extra** | API REST uniquement, pas de Django REST Framework |
| Langage | **Python 3.12+** | Type hints obligatoires avec `from __future__ import annotations` |
| ORM | **Django ORM** | Avec `django-safedelete` pour soft delete |
| Database | **PostgreSQL 15+** | Contraintes d'unicité au niveau DB |
| Migrations | **Django Migrations** | Jamais de raw SQL dans le code métier |
| Soft Delete | **django-safedelete** | `SOFT_DELETE_CASCADE` par défaut, `HARD_DELETE` explicite |
| Package Manager | **uv** | (`astral-sh/uv`) - commandes: `uv pip install`, `uv run` |
| Environment | **python-dotenv** | Variables dans `.env` à la racine backend |

### DevOps & Outils
| Catégorie | Technologie | Contrainte |
|-----------|-------------|------------|
| Version Control | **Git** | Conventional commits recommandés |
| Formatting | **Prettier** (frontend) / **Ruff** (backend) | Auto-format on save |
| Linting | **ESLint** (frontend) / **Ruff** (backend) | Zéro warning toléré |
| Tenant | **Multi-tenant** | Toutes les requêtes filtrées par `tenant_id` |

---

## Contraintes Frontend Détaillées

### Svelte 5 - Runes Obligatoires

**❌ INTERDIT (ancien Svelte 4)**:
```svelte
<script>
  let count = 0;  // Mauvais: pas réactif
  $: doubled = count * 2;  // Mauvais: ancienne syntaxe
</script>
```

**✅ OBLIGATOIRE (Svelte 5)**:
```svelte
<script>
  let count = $state(0);  // Bon: état réactif
  let doubled = $derived(count * 2);  // Bon: dérivé
</script>
```

### Pattern Store avec État Privé

**Structure obligatoire**:
```typescript
class FeatureStore {
  // État public réactif
  data = $state<T | null>(null);
  loading = $state(false);
  
  // État privé (tracking, cache)
  #cache = $state<Map<string, T>>(new Map());
  #originalValue: string | null = null;
  
  // Méthodes publiques
  async load() { }
  
  // Méthodes privées
  #reset() { }
}

export const featureStore = new FeatureStore();
```

### TanStack Query - Pattern Requis

```typescript
// Queries: lecture serveur
const query = createQuery({
  queryKey: ['feature', id],
  queryFn: () => api.getData(id),
  staleTime: 1000 * 60 * 5,
});

// Mutations: écriture serveur
const mutation = createMutation({
  mutationFn: (data) => api.saveData(data),
  onSuccess: async () => {
    await queryClient.invalidateQueries({ queryKey: ['feature'] });
    await queryClient.refetchQueries({ queryKey: ['feature'] });
  },
});
```

### UI - Contraintes bits-ui

- Toujours utiliser les primitives bits-ui (Dialog, AlertDialog, Sheet, etc.)
- **Jamais de `{#if isOpen}`** pour les modals - utiliser `bind:open` et animations CSS
- **Pointer-events**: `pointer-events-none` sur wrapper, `pointer-events-auto` sur contenu
- Animations via `data-state` (CSS) pas de transitions Svelte sur composants

---

## Contraintes Backend Détaillées

### Django Ninja Extra - Structure API

```python
from ninja_extra import api_controller, route
from ninja import Field, Schema

@api_controller('/feature', tags=['Feature'])
class FeatureController:
    service = FeatureService()  # Injection service
    
    @route.get('/{id}', response=FeatureSchema)
    def get_feature(self, id: UUID) -> Feature:
        return self.service.get(id)
    
    @route.patch('/{id}', response=FeatureSchema)
    def update_feature(self, id: UUID, payload: FeatureUpdateSchema) -> Feature:
        return self.service.update(id, payload)
```

### Services - Pattern CRUD

**Fichier**: `backend/<module>/services/<feature>.py`

```python
from core.services import BaseCRUDService

class FeatureService(BaseCRUDService):
    model = FeatureModel
    allowed_update_fields = ['field1', 'field2']  # Whitelist
    
    def update(self, instance, data):
        # Logique métier ici
        return super().update(instance=instance, data=data)
```

### SafeDelete - Contraintes

```python
from safedelete.config import HARD_DELETE

# Soft delete (par défaut) - garde en DB
instance.delete()  # deleted_at = now()

# Hard delete (suppression physique) - requis pour contraintes uniques
instance.delete(force_policy=HARD_DELETE)  # DELETE FROM table

# Query avec soft-deleted
Model.objects.all_with_deleted().filter(...)  # Inclut deleted
```

### Multi-tenancy - Contraintes

Tous les modèles doivent hériter de `TenantAwareModel` ou filtrer explicitement:

```python
class MyModel(TenantAwareModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # ...

# Dans les services/controllers
items = MyModel.objects.filter(tenant=request.tenant)
```

---

## Contraintes de Code

### TypeScript - Frontend

- **Strict mode**: Activé (`strict: true` dans tsconfig)
- **Types explicites**: Sur les fonctions exportées et props
- **Never `any`**: Sauf cas extrêmes avec commentaire
- **Interface vs Type**: Préférer `interface` pour les objets, `type` pour unions

```typescript
// Bon
interface UserProps {
  id: string;
  name: string;
}

function getUser(id: string): Promise<User> { }

// Mauvais
function getUser(id: any): any { }
```

### Python - Backend

- **Type hints**: Obligatoires sur toutes les fonctions
- **Docstrings**: Google style pour les classes et méthodes publiques
- **f-strings**: Uniquement pour le formatage
- **Pas de `print`**: Utiliser le logger Django (`import structlog`)

```python
from __future__ import annotations
import structlog

logger = structlog.get_logger(__name__)

def get_user(user_id: UUID) -> User | None:
    """Récupère un utilisateur par son ID.
    
    Args:
        user_id: L'UUID de l'utilisateur
        
    Returns:
        L'utilisateur ou None si non trouvé
    """
    logger.info("Fetching user", user_id=user_id)
    return User.objects.filter(id=user_id).first()
```

---

## Structure des Dossiers

### Frontend
```
frontend/src/
├── lib/
│   ├── components/           # Composants réutilisables
│   │   ├── ui/              # bits-ui wrappers
│   │   ├── shared/          # Composants métier génériques
│   │   └── layout/          # Layout (header, sidebar, etc.)
│   ├── features/            # Modules métier (par domaine)
│   │   └── admin/
│   │       └── settings/
│   │           ├── components/
│   │           ├── queries/     # TanStack Query
│   │           ├── services/    # API calls
│   │           ├── stores/      # Svelte 5 stores
│   │           └── types/       # TypeScript types
│   ├── stores/              # Stores globaux (ui, notification, auth)
│   ├── utilities/           # Utils (cn, formatting, etc.)
│   └── constants/           # Constantes globales
├── routes/                  # SvelteKit file-based routing
└── app.html                 # Template HTML
```

### Backend
```
backend/
├── core/                    # Code partagé
│   ├── services/           # BaseCRUDService
│   ├── models.py           # Base models (TenantAwareModel)
│   └── exceptions.py       # Custom exceptions
├── hr/                      # Module RH
│   ├── leaves/             # Congés
│   │   ├── controllers/    # API controllers (Ninja Extra)
│   │   ├── services/       # Business logic
│   │   ├── models.py       # Django models
│   │   └── schemas.py      # Ninja schemas
│   └── employees/          # Employés
├── config/                  # Django settings
└── manage.py
```

---

## Commandes Courantes

### Frontend (pnpm)
```bash
# Installation
cd frontend && pnpm install

# Dev server
pnpm dev

# Build
pnpm build

# Lint
pnpm lint

# Add dependency
pnpm add <package>
```

### Backend (uv)
```bash
# Installation
cd backend && uv pip install -r requirements.txt

# Dev server
uv run python manage.py runserver

# Migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Shell
uv run python manage.py shell
```

---

## Points de Vigilance

### ❌ INTERDICTIONS ABSOLUES

1. **Pas de npm/yarn** dans le frontend (pnpm uniquement)
2. **Pas de pip** direct dans le backend (uv uniquement)
3. **Pas de Svelte 4** (`$:` reactive statements)
4. **Pas de Redux/Vuex/MobX** (Svelte 5 stores natifs)
5. **Pas de Django REST Framework** (Ninja Extra obligatoire)
6. **Pas de raw SQL** dans le code métier (ORM uniquement)
7. **Pas de `any`** en TypeScript sans justification commentée
8. **Pas de `print()`** en Python (logging structuré)

### ⚠️ ATTENTION

1. **Soft delete par défaut**: Toujours vérifier si `HARD_DELETE` est nécessaire
2. **Multi-tenant**: Toujours filtrer par tenant dans les requêtes
3. **Queries TanStack**: Toujours invalider le cache après mutation
4. **Store reload**: Toujours appeler `#resetTrackingState()` avant `loadFromData()`
5. **Modal animations**: Jamais de `{#if}` sur les modals avec transitions

---

## Debugging

### Frontend
```typescript
// Store state
console.log($state.snapshot(store.data));

// TanStack Query devtools
// Activer dans +layout.ts: `devtools: { enabled: true }`
```

### Backend
```python
# Logger structuré
logger.debug("Debug info", variable=value)

# SQL queries
# Setting LOGGING -> django.db.backends -> level DEBUG
```

---

## Ressources

- **Svelte 5 Docs**: https://svelte.dev/docs/svelte/what-is-svelte-5
- **TanStack Query**: https://tanstack.com/query/latest/docs/framework/svelte/overview
- **bits-ui**: https://bits-ui.com/docs
- **Django Ninja Extra**: https://django-ninja.dev/
- **django-safedelete**: https://django-safedelete.readthedocs.io/

---

## Dernière Mise à Jour

- **Date**: Avril 2026
- **Version**: 1.0
- **Responsable**: Développeur principal Oxiliere HR

*Ce document est la source de vérité pour toute intervention sur le projet.*
