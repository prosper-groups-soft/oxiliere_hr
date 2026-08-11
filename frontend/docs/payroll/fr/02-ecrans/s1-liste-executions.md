# S1 — Liste des exécutions

> **Dépendances :** `vision.md`, `metamodel.md` (cycle mensuel)

---

## Contexte

La liste des exécutions (ou cycles de paie) est la **page d'accueil** du module paie. Elle permet au gestionnaire de :

1. Visualiser tous les cycles de paie passés, en cours et à venir
2. Accéder au détail de chaque cycle
3. Lancer un nouveau cycle de paie
4. Voir le statut global de chaque cycle

> **Note :** Il n'y a pas de dashboard dans ce module. Les indicateurs globaux (masse salariale, tendances) sont dans le dashboard général de l'application.

---

## Wireframe ASCII

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  💰 Paie  /  Exécutions                                                      │
│                                                                              │
│  EXÉCUTIONS DE PAIE                                                          │
│                                                                              │
│  [+ Nouveau cycle]                                                           │
│                                                                              │
│  Filtres : [Tous les statuts ▼]   [Toutes les périodes ▼]   🔎 [Rechercher] │
│                                                                              │
│  ┌───────┬───────────┬────────────┬──────────┬──────────┬──────────────────┐ │
│  │       │ Période   │ Employés   │  Brut    │  Statut  │ Actions          │ │
│  ├───────┼───────────┼────────────┼──────────┼──────────┼──────────────────┤ │
│  │  🔵   │ Juin 2026 │  45/45     │ 39,2 M   │ En cours │ [Détail] [Valider]│ │
│  │  ✅   │ Mai 2026  │  45/45     │ 38,4 M   │ Clôturé  │ [Détail]         │ │
│  │  ✅   │ Avr. 2026 │  44/44     │ 37,1 M   │ Clôturé  │ [Détail]         │ │
│  │  ✅   │ Mars 2026 │  44/44     │ 36,8 M   │ Clôturé  │ [Détail]         │ │
│  │  ⚠️   │ Fév. 2026 │  43/45     │ 35,2 M   │ Anomalie │ [Détail] [Corriger]│ │
│  └───────┴───────────┴────────────┴──────────┴──────────┴──────────────────┘ │
│                                                                              │
│                    ← Page 1 sur 3 →   25 cycles au total                     │
│                                                                              │
│  [📤 Exporter la liste]                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Description |
|------|-------------|
| **Filtres** | Filtre par statut (Tous, En cours, Clôturé, Brouillon, Anomalie) et période |
| **Tableau** | Liste des cycles avec statut, période, nombre d'employés, total brut |
| **Actions** | Accès au détail, validation, correction, etc. |
| **Nouveau cycle** | Bouton d'action pour créer un nouveau cycle |
| **Pagination** | Navigation paginée si > 20 cycles |

---

## Composant UI proposé

### `CycleList.svelte`

```svelte
<script lang="ts">
  type CycleRow = {
    id: string;
    periodLabel: string;
    status: "draft" | "processing" | "closed" | "error";
    employeeCount: number;
    totalEmployeeCount: number;
    grossTotal: number;
  };

  let {
    rows = [] as CycleRow[],
    filters = { status: "all", search: "" },
    onCreate = () => {},
    onRowClick = (id: string) => {},
    page = 1,
    totalPages = 1,
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/runs` | `GET` | Liste paginée des cycles |
| `/payroll/runs` | `POST` | Créer un nouveau cycle |

### Réponse `RunsListOut`

```json
{
  "items": [
    {
      "id": "uuid",
      "period_label": "Juin 2026",
      "status": "draft",
      "employee_count": 45,
      "total_employee_count": 45,
      "gross_total": 39200000,
      "closed_at": null
    }
  ],
  "pagination": {
    "page": 1,
    "total_pages": 3,
    "total_items": 25
  }
}
```

---

## Navigation depuis S1

```
┌─────────────────────────────────────────────────┐
│              LISTE EXÉCUTIONS (S1)              │
│                                                 │
│  ┌──────────┬──────────┬──────────┬────────────┐│
│  │ Nouveau  │ Détail   │ Valider  │ États &    ││
│  │ cycle    │ run      │          │ Rapports   ││
│  └────┬─────┴────┬─────┴────┬─────┴─────┬──────┘│
│       │          │          │           │       │
│       ▼          ▼          ▼           ▼       │
│     S2         S3         S7          S9        │
└─────────────────────────────────────────────────┘
```

## Règles d'interaction

| # | Règle |
|---|-------|
| 1 | Le cycle en cours est le plus récent avec statut `DRAFT` ou `PROCESSING` |
| 2 | Les cycles sont triés par période décroissante |
| 3 | Un clic sur une ligne → navigation vers S3 (détail du run) |
| 4 | Le bouton [+ Nouveau cycle] n'est visible que pour les gestionnaires |
