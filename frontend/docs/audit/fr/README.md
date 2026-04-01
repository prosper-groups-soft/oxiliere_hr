# Module Audit — Documentation Technique

## Vue d'ensemble

Le module Audit est le **journal de traçabilité central** du système Oxiliere HR. Il enregistre et expose toutes les actions significatives effectuées dans l'application (création, modification, suppression d'entités, connexions, exports, validations...) afin de garantir la conformité, la sécurité et la transparence.

---

## Fonctionnalités prévues

| Fonctionnalité | Description |
|---|---|
| **Journal d'activité** | Liste paginée de tous les événements système |
| **Traçabilité utilisateurs** | Qui a fait quoi et quand |
| **Historique des modifications** | Avant / Après sur les données modifiées |
| **Filtres avancés** | Par utilisateur, date, module, type d'action |
| **Export** | Export CSV/PDF des logs pour conformité |

---

## Architecture du module

Le module suit le pattern standard des autres modules de l'application :

```
routes/
  admin/
    audit/
      +page.svelte          # Redirige vers l'onglet par défaut
      +layout.svelte        # Enveloppe avec navigation par onglets (AuditTabs)
      logs/
        +page.svelte        # Vue principale : journal des événements

lib/features/audit/
  types/
    types.ts                # Types et interfaces TypeScript
  stores/
    audit.svelte.ts         # Store Svelte 5 (classe avec $state / $derived)
  components/
    nav/
      AuditTabs.svelte      # Navigation entre les onglets
    logs/
      LogsView.svelte       # Vue principale du journal
      LogTable.svelte       # Tableau des événements
      LogRow.svelte         # Ligne individuelle d'un événement
      LogDetailSheet.svelte # Tiroir de détail d'un événement (avant/après)
      LogFilters.svelte     # Panel de filtres (utilisateur, date, module, action)
      LogExportButton.svelte # Bouton d'export CSV
    shared/
      ActionBadge.svelte    # Badge coloré par type d'action (CREATE, UPDATE, DELETE...)
      ModuleBadge.svelte    # Badge du module source (Employees, Leaves, Payroll...)
```

---

## Modèle de données (`types/types.ts`)

```typescript
// Type d'action effectuée
export type AuditAction = 'CREATE' | 'UPDATE' | 'DELETE' | 'LOGIN' | 'LOGOUT' | 'EXPORT' | 'APPROVE' | 'REJECT';

// Module source de l'action
export type AuditModule =
  | 'employees'
  | 'attendance'
  | 'leaves'
  | 'payroll'
  | 'recruitment'
  | 'banking'
  | 'jobs'
  | 'calendar'
  | 'settings'
  | 'auth';

// Entrée principale du journal
export interface AuditLog {
  id: string;
  timestamp: string;       // ISO date-time
  userId: number;
  userName: string;
  avatarUrl?: string;
  action: AuditAction;
  module: AuditModule;
  entityId?: string;       // ID de l'entité concernée
  entityLabel?: string;    // Libellé humain (ex: "Jean Dupont", "Fiche de paie #42")
  description: string;     // Phrase lisible (ex: "Création d'un employé")
  diff?: AuditDiff;        // Différentiel avant/après (optionnel)
  ipAddress?: string;
  userAgent?: string;
}

// Différentiel de modification
export interface AuditDiff {
  before: Record<string, unknown>;
  after: Record<string, unknown>;
}

// Filtres appliqués dans la vue
export interface AuditFilters {
  search: string;
  userIds: number[];
  modules: AuditModule[];
  actions: AuditAction[];
  dateRange: {
    from: string;   // ISO date
    to: string;     // ISO date
  };
}

// Type d'onglet de navigation
export type AuditTabId = 'logs';
```

---

## Store (`audit.svelte.ts`)

Le store est une **classe Svelte 5** utilisant les runes `$state` et `$derived`, selon le même pattern que `AttendanceStore`, `LeavesStore`, etc.

### État

| Propriété | Type | Description |
|---|---|---|
| `logs` | `AuditLog[]` | Tous les événements du journal |
| `filters` | `AuditFilters` | Filtres actifs |
| `activeTab` | `AuditTabId` | Onglet actif |

### Dérivés

| Propriété | Description |
|---|---|
| `filteredLogs` | Logs filtrés selon `filters` |
| `activeFiltersCount` | Nombre de filtres actifs (pour afficher le badge) |
| `stats` | Compteurs rapides : total, par action, par module |

### Actions

| Méthode | Description |
|---|---|
| `setSearch(query)` | Mettre à jour la recherche textuelle |
| `toggleFilter(category, value)` | Activer/désactiver un filtre |
| `resetFilters()` | Réinitialiser tous les filtres |
| `setDateRange(from, to)` | Définir la plage de dates |
| `exportLogs()` | Déclencher un export CSV des logs filtrés |

---

## Navigation (`+layout.svelte` & `AuditTabs.svelte`)

Le layout encapsule la navigation avec un seul onglet pour commencer :

| Onglet | Route | Icône |
|---|---|---|
| **Journal** | `/admin/audit/logs` | `History` |

> **Note :** Un second onglet "Statistiques" peut être envisagé ultérieurement si le besoin de reporting se précise.

---

## Vue principale : `LogsView.svelte`

La vue du journal est organisée ainsi :

```
┌─────────────────────────────────────────────────────┐
│  En-tête : Titre + bouton Export CSV                │
├─────────────────────────────────────────────────────┤
│  Barre de filtres : Recherche | Module | Action | Date│
├─────────────────────────────────────────────────────┤
│  Tableau des événements                             │
│  ┌────────────┬──────────┬──────────┬─────────────┐ │
│  │ Horodatage │ Utilisat.│ Action   │ Entité      │ │
│  ├────────────┼──────────┼──────────┼─────────────┤ │
│  │ 28/03 09h  │ J. Dupon │ UPDATE   │ Emp. #12    │ │
│  │ 28/03 08h  │ Admin    │ CREATE   │ Poste Dev   │ │
│  └────────────┴──────────┴──────────┴─────────────┘ │
│                                                     │
│  [Cliquer une ligne → Sheet détail Avant/Après]    │
└─────────────────────────────────────────────────────┘
```

### `LogDetailSheet.svelte`

Tiroir latéral (Sheet) qui s'ouvre au clic d'une ligne avec :
- Informations complètes de l'événement (utilisateur, IP, user-agent)
- Bloc **Avant / Après** si un `diff` est présent, avec mise en évidence des champs modifiés

---

## Données mock (pour le développement)

En l'absence de backend, le store génère des données simulées représentatives :
- ~50 entrées couvrant les 7 derniers jours
- Mélange de modules (`employees`, `leaves`, `payroll`...)
- Mélange d'actions (`CREATE`, `UPDATE`, `DELETE`, `LOGIN`...)
- Quelques entrées avec `diff` renseigné pour tester le détail Avant/Après

---

## Labels et couleurs

### Actions (`AuditAction`)

| Action | Label | Couleur badge |
|---|---|---|
| `CREATE` | Création | Vert (`emerald`) |
| `UPDATE` | Modification | Bleu (`blue`) |
| `DELETE` | Suppression | Rouge (`rose`) |
| `LOGIN` | Connexion | Slate |
| `LOGOUT` | Déconnexion | Slate |
| `EXPORT` | Export | Violet (`violet`) |
| `APPROVE` | Approbation | Vert (`green`) |
| `REJECT` | Rejet | Ambre (`amber`) |

### Modules (`AuditModule`)

Chaque module aura un badge avec son nom et une couleur neutre (identique pour tous pour ne pas surcharger visuellement).

---

## Plan d'implémentation (ordre suggéré)

1. **`types/types.ts`** — Définir tous les types TypeScript
2. **`stores/audit.svelte.ts`** — Créer le store avec données mock et filtres
3. **`+layout.svelte` + `AuditTabs.svelte`** — Navigation et layout de la route
4. **`+page.svelte` (redirect)** — Redirection automatique vers `/admin/audit/logs`
5. **`LogsView.svelte` + `LogTable.svelte` + `LogRow.svelte`** — Vue principale du journal
6. **`ActionBadge.svelte` / `ModuleBadge.svelte`** — Composants visuels partagés
7. **`LogFilters.svelte`** — Panel de filtres complet
8. **`LogDetailSheet.svelte`** — Tiroir de détail Avant/Après
9. **`LogExportButton.svelte`** — Export CSV

---

## Références

- Pattern de store : [`attendance.svelte.ts`](../../src/lib/features/attendance/stores/attendance.svelte.ts)
- Pattern de types : [`leaves/types/types.ts`](../../src/lib/features/leaves/types/types.ts)
- Pattern de navigation : [`AttendanceTabs.svelte`](../../src/lib/features/attendance/components/nav/)
- Pattern de layout : [`attendance/+layout.svelte`](../../src/routes/attendance/+layout.svelte)
