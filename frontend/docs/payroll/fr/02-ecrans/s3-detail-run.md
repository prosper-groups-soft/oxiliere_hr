# S3 — Détail d'un Run (Liste des employés)

> **Dépendances :** `s4-fiche-de-paie.md` (navigation vers la fiche), `exchange-rates.md` (colonne taux)

---

## Contexte

La vue Détail d'un Run est le **tableau de bord opérationnel** du gestionnaire de paie pendant un cycle. C'est l'écran central où il passe le plus clair de son temps : il visualise la liste des employés, leurs montants, leurs statuts, et déclenche les actions (saisie variables, validation, export).

---

## Wireframe ASCII

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ← Paies  /  Juin 2026                  [BROUILLON]  ·  Créé le 30/06/2026      │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │  📊  RÉSUMÉ DU RUN                                                        │  │
│  │                                                                           │  │
│  │  Masse salariale         Effectif      Coût employeur      Statut         │  │
│  │   6 071 000 CDF             42          7 103 070 CDF      ◉ Brouillon    │  │
│  │                                                                           │  │
│  │  Variation M-1 : +3,2 %      ▲ 1          ▼ 2                             │  │
│  │                                                                           │  │
│  │  [Modifier taux]  [Saisie variables]  [⚡ Lancer le calcul]  [✓ Valider]  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │  💱  TAUX DE CHANGE APPLIQUÉ                                              │  │
│  │                                                                           │  │
│  │     2 850,00  CDF/USD  ·  Source : BCC  ·  Capturé le 30/06/2026 à 09:15  │  │
│  │                                                                           │  │
│  │  📌  8 contrats en USD · 34 contrats en CDF                               │  │
│  │                                                                           │  │
│  │  [Modifier]  (si DRAFT)                                                   │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Filtres ─────────────────────────────────────────────────────────────────┐  │
│  │  Département : [Tous ▼]   Statut : [Tous ▼]   Devise : [Toutes ▼]         │  │
│  │  Q  [Rechercher un employé...                      ]                      │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │  ☐  Matricule │ Employé                │ Statut      │ Brut (CDF)   │ Net │  │
│  ├───────────────────────────────────────────────────────────────────────────┤  │
│  │  ☐  EMP-0042   Jean Mbemba              ◉ Calculé   6 071 000   4 948 696 │  │
│  │  ☐  EMP-0087   Marie Kabasele           ◉ Calculé   4 200 000   3 214 000 │  │
│  │  ☐  EMP-0012   Albert Mbuyu             ◯ Brouillon    850 000       —    │  │
│  │  ☐  EMP-0093   Paulin Bianga            ◉ Calculé   9 975 000   7 812 000 │  │
│  │  ☐  EMP-0051   Sophie D.                ⚠️ Erreur    3 000 EUR       —    │  │
│  │  ☐  EMP-0033   Joseph Kasongo           ◉ Calculé   3 200 000   2 456 000 │  │
│  │  ☐  EMP-0072   Béatrice Mwamba          ◯ Brouillon  1 200 000       —    │  │
│  │  ☐  EMP-0021   Pierre Lufungulo         ◉ Calculé   5 400 000   4 120 000 │  │
│  │  ☐  ...                                                                   │  │
│  ├───────────────────────────────────────────────────────────────────────────┤  │
│  │  Totaux :               ──────────         42 emp.    60 896 000   ...    │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  ┌─ Actions groupées ─────────────────────────────────────────────────────────┐ │
│  │  [📋 Valider la sélection] [📥 Exporter sélection] [✏️ Variables groupées]│ │
│  └───────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Contenu | Rôle |
|------|---------|------|
| **Barre supérieure** | ← Breadcrumb, statut run (badge), date création | Navigation et contexte |
| **Cartes résumé** | Masse salariale, effectif, coût employeur, statut | Vue macro du run |
| **Comparatif M-1** | Variation % masse salariale, ▲/▼ employés | Détection d'anomalies |
| **Boutons d'action** | Modifier taux, Saisie variables, Lancer calcul, Valider | Actions principales |
| **Cartouche taux** | Taux appliqué, source, répartition USD/CDF | Transparence change |
| **Filtres** | Département, statut, devise, recherche | Navigation rapide |
| **Table employés** | Liste des employés avec checkboxes, statuts, montants | Revue et actions individuelles |
| **Ligne de totaux** | Aggrégations en bas du tableau | Synthèse permanente |
| **Actions groupées** | Valider, exporter, modifier en lot | Productivité |

---

## États visuels

### Statut du Run

| État | Couleur badge | Actions disponibles |
|------|--------------|-------------------|
| **DRAFT** | Bleu | Créer, Lancer calcul, Modifier taux, Saisir variables |
| **PROCESSING** | Jaune (spinner) | Aucune (calcul en cours) |
| **COMPLETED** | Vert | Valider, Exporter, Consulter |
| **PAID** | Vert foncé | Exporter uniquement, lecture seule |
| **CANCELED** | Rouge | Lecture seule |

### Statut par ligne employé

| Statut | Icône | Signification | Actions ligne |
|--------|-------|---------------|---------------|
| **Brouillon** | `◯` bleu clair | Employé présent, pas encore calculé | Consulter, Modifier variables |
| **Calculé** | `◉` vert | Payslip généré avec succès | Consulter, Exporter PDF |
| **En erreur** | `⚠️` rouge | Anomalie lors du calcul | Voir détail erreur |
| **En attente** | `⟳` gris | Données manquantes (pas de contrat actif) | Configurer contrat |
| **Exclu** | `⛔` gris | Exclu manuellement du run | Réintégrer |

### États de la table

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| **Chargement** | Ouverture du run | Skeleton lines × 8 |
| **Vide** | Aucun employé pour la période | Message : "Aucun employé trouvé pour cette période" |
| **Filtré** | Filtre actif | Badge `Filtre : Production · Actif` avec bouton [Effacer] |
| **Sélection multiple** | Checkboxes cochées | Barre d'actions groupées apparaît |
| **Taux manquant** | Run sans USD mais taux pas défini | Badge `⚠️ Taux manquant` dans cartouche |

---

## Règles d'interaction

| # | Règle | Justification |
|---|-------|---------------|
| 1 | Le clic sur une ligne ouvre **S4** pour cet employé | Navigation rapide |
| 2 | La checkbox en entête **sélectionne/désélectionne tout** | Manipulation par lot |
| 3 | Les filtres sont **cumulatifs** (AND) | Précision de recherche |
| 4 | Le lancement du calcul remplace les bulletins **DRAFT** uniquement (préserve les VALIDÉS) | Pas de recalcul intempestif |
| 5 | En **DRAFT**, les montants peuvent être vides (pas encore calculés) | Cohérence |
| 6 | La ligne de totaux se met à jour **en temps réel** quand la séchange change ou que les filtres s'appliquent | Feedback immédiat |
| 7 | Un clic sur `Modifier taux` ouvre le dialogue d'échange défini dans `exchange-rates.md` | Réutilisation |
| 8 | Le passage en **PROCESSING** bloque toute modification | Éviter les mutations pendant le calcul |

### Barre d'actions dynamiques

La barre d'actions sous les cartes résumé change selon le statut du run :

```
DRAFT:
[Modifier taux]  [Saisie variables]  [⚡ Lancer le calcul]  [✓ Valider (disabled)]

DRAFT + calcul lancé (employés calculés):
[Modifier taux]  [Saisie variables]  [🔄 Recalculer]  [✓ Valider]

COMPLETED:
[Saisie variables]  [📋 Recalculer]  [✓ Valider]  [📤 Exporter tout]

PAID:
[📤 Exporter tout]  [📊 Rapport]
```

### Actions sur ligne

Chaque ligne a un menu contextuel (clic droit ou `⋯`) :

```
[Consulter le bulletin]
[Modifier les variables]
[Exporter le PDF]
[Exclure du run]  (si DRAFT)
[Signaler une anomalie]
```

---

## Composants UI proposés

### `RunSummaryCards.svelte`

Cartes de résumé en haut de la vue détail.

```svelte
<script lang="ts">
  let {
    payrollRun = {
      id: "",
      status: "DRAFT",
      period: { start: Date, end: Date },
      created_at: Date,
    },
    summary = {
      total_gross: 0,
      employee_count: 0,
      total_employer_cost: 0,
    },
    previousPeriod = {
      total_gross: 0,
      employee_count: 0,
    },
  } = $props();
</script>
```

**États :**
| État | Affichage |
|------|-----------|
| Normal | Cartes avec valeurs formatées |
| Variation positive | `▲ X %` en vert |
| Variation négative | `▼ X %` en rouge |
| Variation nulle | `— 0 %` en gris |
| Pas de période précédente | `N/A` en gris |

### `EmployeePayrollTable.svelte`

Tableau principal des employés avec filtres et sélection.

```svelte
<script lang="ts">
  type EmployeeRow = {
    id: string;
    matricule: string;
    fullName: string;
    status: "DRAFT" | "CALCULATED" | "ERROR" | "PENDING" | "EXCLUDED";
    grossPay: number | null;
    netPay: number | null;
    currency: "CDF" | "USD";
    hasAdvance: boolean;
    errorMessage?: string;
  };

  let {
    employees = [] as EmployeeRow[],
    loading = false,
    filters = {
      department: null as string | null,
      status: null as string | null,
      currency: null as string | null,
      search: "",
    },
    selectedIds = [] as string[],
    onSelect = (ids: string[]) => {},
    onRowClick = (id: string) => {},
  } = $props();
</script>
```

**Props :**
| Prop | Type | Défaut | Description |
|------|------|--------|-------------|
| `employees` | `EmployeeRow[]` | `[]` | Données lignes |
| `loading` | `boolean` | `false` | État de chargement |
| `filters` | `Filters` | — | Filtres actifs |
| `selectedIds` | `string[]` | `[]` | Lignes sélectionnées |
| `onSelect` | `(ids) => void` | — | Event sélection |
| `onRowClick` | `(id) => void` | — | Navigation vers S4 |

**États visuels :**
| État | Rendu |
|------|-------|
| Loading | 8 lignes skeleton animées |
| Empty | `📭 Aucun employé trouvé` avec suggestion |
| Filtered | Badge `Filtre actif` + bouton [Effacer] |
| Error row | `⚠️` rouge + message d'erreur dans colonne montant |

### `RunActionBar.svelte`

Barre d'actions principale, contextuelle au statut.

```svelte
<script lang="ts">
  let {
    status = "DRAFT",
    selectedCount = 0,
    onCalculate = () => {},
    onValidate = () => {},
    onExportAll = () => {},
    onVariableEntry = () => {},
  } = $props();
</script>
```

### `EmployeeRowMenu.svelte`

Menu contextuel pour chaque ligne employé.

```svelte
<script lang="ts">
  let {
    employeeId = "",
    status = "DRAFT",
    onView = () => {},
    onEditVariables = () => {},
    onExportPdf = () => {},
    onExclude = () => {},
  } = $props();
</script>
```

### `RunSummaryFilterBar.svelte`

Barre de filtres combinée.

```svelte
<script lang="ts">
  let {
    departments = [] as string[],
    statuses = ["DRAFT", "CALCULATED", "ERROR", "PENDING"],
    currencies = ["CDF", "USD"],
    activeFilters = { department: null, status: null, currency: null, search: "" },
  } = $props();
</script>
```

---

## Cas particuliers

### Run avec employés dans plusieurs devises

```
┌────┬──────────────┬─────────┬──────────┬──────────────┐
│ ☐  │ Jean Mbemba  │ ◉ Calc │ 2 000 USD│  5 700 000   │  ← ligne USD
│ ☐  │ Albert Mbuyu │ ◯ Brf  │    -     │    850 000   │  ← ligne CDF
│ ☐  │ Sophie D.    │ ⚠️ Err  │ 3 000 EUR│    —         │  ← devise non supportée
└────┴──────────────┴─────────┴──────────┴──────────────┘
```

- Les montants sont **toujours affichés en CDF** (devise de paie)
- La colonne salaire contractuel apparaît pour les contrats USD (cf. `exchange-rates.md`)
- Les employés dans une devise non supportée sont en erreur

### Run sans aucun employé

```
┌──────────────────────────────────────────────────┐
│                                                   │
│  📭  Aucun employé trouvé                         │
│                                                   │
│  Il n'y a aucun contrat actif pour la période      │
│  sélectionnée (01/06/2026 → 30/06/2026).          │
│                                                   │
│  Vérifiez que des employés ont des contrats       │
│  valides pour cette période.                      │
│                                                   │
│  [← Retour à la liste des runs]                   │
└──────────────────────────────────────────────────┘
```

### Employé avec plusieurs contrats dans la période

Si un employé change de contrat en cours de mois (promotion, passage CDD → CDI), le système **fusionne** les périodes pour n'afficher qu'une seule ligne avec mention :

```
│ ☐  │ EMP-0042  │ Jean Mbemba        │ ◉ Calc │ 6 071 000  │ 4 948 696  │
│    │           │                     │  📎 2 contrats dans la période     │
```

Le clic ouvre une vue consolidée qui détaille chaque contrat.

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/runs/{run_id}` | `GET` | Détail du run + métadata |
| `/payroll/runs/{run_id}/summary` | `GET` | Résumé agrégé |
| `/payroll/runs/{run_id}/payslips` | `GET` | Liste des employés + statuts + montants |
| `/payroll/runs/{run_id}/generate` | `POST` | Lancer le calcul |
| `/payroll/runs/{run_id}/approve` | `POST` | Valider le run |
| `/payroll/runs/{run_id}/pay` | `POST` | Marquer comme payé |
| `/payroll/runs/{run_id}/exchange-rate` | `PATCH` | Modifier taux (DRAFT only) |

### Réponse `PayrollRunOut`

```json
{
  "id": "uuid",
  "label": "Paie Juin 2026",
  "period_start": "2026-06-01",
  "period_end": "2026-06-30",
  "status": "DRAFT",
  "payment_method": "BANK_TRANSFER",
  "exchange_rate_applied": 2850.00,
  "exchange_rate_source": "bcc",
  "exchange_rate_fetched_at": "2026-06-30T09:15:00Z",
  "currency": "CDF",
  "created_at": "2026-06-27T10:00:00Z",
  "created_by": "Kiban M."
}
```

### Réponse `PayrollRunSummaryOut`

```json
{
  "run_id": "uuid",
  "period": "2026-06",
  "total_gross": 6071000.00,
  "total_net": 4948696.00,
  "total_employer_contributions": 1032070.00,
  "total_employee_deductions": 872304.00,
  "employee_count": 42,
  "status": "DRAFT",
  "previous_period": {
    "total_gross": 5885000.00,
    "variation_pct": 3.2
  }
}
```

### Réponse `PayslipListOut` (liste paginée)

```json
{
  "items": [
    {
      "id": "uuid",
      "employee": {
        "id": "uuid",
        "matricule": "EMP-0042",
        "full_name": "Jean Mbemba"
      },
      "contract_currency": "USD",
      "contract_salary": 2000.00,
      "status": "CALCULATED",
      "gross_pay": 6071000.00,
      "net_pay": 4948696.00,
      "has_advance": true
    }
  ],
  "total": 42,
  "summary": {
    "total_gross": 60710000.00,
    "total_net": 49200000.00,
    "total_errors": 1
  }
}
```

---

## Considérations UX avancées

### Variation M-1 (comparaison)

- La variation est calculée **par rapport au run de la même période précédente** (mai 2026 vs juin 2026)
- Si plusieurs runs existent pour la même période (corrections), on prend le **dernier run PAYÉ**
- Si aucun run précédent, on affiche `N/A`
- La variation s'affiche aussi par employé si on survole le montant

### Mode dégradé — Recalcul partiel

Après modification des variables (S5), seuls les bulletins impactés sont marqués comme `DRAFT` et doivent être recalculés. La barre d'action affiche :

```
⚠️ 4 bulletins modifiés · [Recalculer les bulletins impactés seulement]
```

### Mode hors-ligne

Les données de la liste employés sont **mises en cache** après le premier chargement. Si le réseau est perdu pendant la navigation, un badge s'affiche :

```
📡 Mode hors-ligne — Les données affichées datent du 30/06/2026 à 09:15
```
