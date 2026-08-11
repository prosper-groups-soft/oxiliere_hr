# S5 — Saisie des Variables de Paie

> **Dépendances :** `catalogue.md` (éléments de paie), `s3-detail-run.md` (entrée depuis la liste)

---

## Contexte

La Saisie des Variables est l'écran où le gestionnaire de paie **saisit ou modifie les éléments variables** pour chaque 
employé avant de lancer le calcul : heures supplémentaires, primes exceptionnelles, absences, indemnités, etc.

C'est un écran **critique** car c'est là que les erreurs de saisie humaine sont les plus fréquentes. 
Le design doit maximiser la productivité tout en minimisant les erreurs.

Deux modes sont proposés :
1. **Mode individuel** : saisie pour un employé à la fois
2. **Mode groupé** : saisie en lot pour plusieurs employés (même prime, même motif)

---

## Wireframe ASCII — Mode individuel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Paies  /  Juin 2026  /  Jean Mbemba  /  Saisie variables                 │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  ✏️  SAISIE DES VARIABLES  ·  Juin 2026                               │  │
│  │                                                                       │  │
│  │  📋 Jean Mbemba · EMP-0042 · Classe 4 Éch. 3                         │  │
│  │  💰 Salaire de base : 5 700 000 CDF (2 000 USD × 2 850,00)           │  │
│  │                                                                      │  │
│  │  ──── Présence & Absences ────────────────────────────               │  │
│  │                                                                      │  │
│  │  Jours ouvrés : 21     Jours calendaires : 30                        │  │
│  │                                                                      │  │
│  │  Jours travaillés : [21] / 21  (modifiable pour absences)            │  │
│  │  Jours d'absence (non payés) : [0]                                   │  │
│  │  Jours de congé payé : [0]                                           │  │
│  │                                                                      │  │
│  │  ──── Heures supplémentaires ────────────────────────────            │  │
│  │                                                                      │  │
│  │  Type                       Heures        Montant estimé             │  │
│  │  Majoration 30% (HS 1-2h)   [4] heures    21 000 CDF                 │  │
│  │  Majoration 60% (HS 3+h)    [0] heures        0 CDF                  │  │
│  │  Jours fériés (100%)        [0] heures        0 CDF                  │  │
│  │  Heures de nuit (50%)       [0] heures        0 CDF                  │  │
│  │                                                                      │  │
│  │  ──── Primes et Indemnités ────────────────────────────              │  │
│  │                                                                      │  │
│  │  Ajouter une prime : [Sélectionner... ▼]  [+]                        │  │
│  │                                                                      │  │
│  │  Type                        Montant       Quantité        Total     │  │
│  │  Prime de performance        [50 000]      [1]           50 000 CDF  │  │
│  │  Indemnité de logement       [270 000]     —             270 000 CDF │  │
│  │  Prime de panier             [2 500]       [21 jours]     52 500 CDF │  │
│  │                                                                      │  │
│  │  ──── Avances et Déductions ────────────────────────────             │  │
│  │                                                                      │  │
│  │  Avance sur salaire : [100 000] CDF · Échéance 5/6                   │  │
│  │  📎 Voir historique : 2 avances en cours (solde : 250 000 CDF)       │  │
│  │                                                                      │  │
│  │  ──── Notes internes ──────────────────────────────────              │  │
│  │                                                                      │  │
│  │  [Prime validée par N+1 le 25/06 · HS approuvées par chef atelier]   │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  │  ⚠️  Modifications non sauvegardées (2)                          │   │
│  │  │  [Annuler]              [Enregistrer]  [Enreg. & bulletin]       │   │
│  │  └──────────────────────────────────────────────────────────────────┘   │
│  └───────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe — Mode groupé

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Saisie en lot  ·  Prime exceptionnelle  ·  Département Production          │
│                                                                             │
│  Appliquer à : [☑ 12 employés sélectionnés depuis S3]                       │
│                                                                             │
│  Type de prime : [Prime exceptionnelle ▼]                                   │
│  Montant : [50 000] CDF chacun                                              │
│  Justificatif : [Prime de fin de chantier]                                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Aperçu avant application                                             │  │
│  │                                                                       │  │
│  │  Jean Mbemba          → +50 000 CDF  (salaire brut : 6 121 000)       │  │
│  │  Albert Mbuyu         → +50 000 CDF  (salaire brut :   900 000)       │  │
│  │  Marie Kabasele       → +50 000 CDF  (salaire brut : 4 250 000)       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  [Annuler]          [Appliquer à 12 employés]                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Mode | Contenu |
|------|------|---------|
| **Barre supérieure** | Indiv. | Breadcrumb, info employé, salaire de base |
| **Présence & Absences** | Indiv. | Jours travaillés, absences, congés payés |
| **Heures supplémentaires** | Indiv. | Types HS avec heures et estimation |
| **Primes & Indemnités** | Indiv./Groupé | Liste des primes avec ajout sélectable |
| **Avances & Déductions** | Indiv. | Avances en cours, solde, historique |
| **Notes internes** | Indiv. | Champ texte libre |
| **Barre d'action** | Indiv. | Annuler, Enregistrer, Enreg. & bulletin |
| **Sélection** | Groupé | Liste des employés cibles |
| **Type + Montant** | Groupé | Paramètres communs |
| **Aperçu** | Groupé | Simulation avant application |

---

## Règles d'interaction

| # | Règle | Justification |
|---|-------|---------------|
| 1 | Les montants estimés dans le formulaire sont **indicatifs** (le calcul réel a lieu dans le pipeline) | Performance |
| 2 | La modification marque le bulletin comme **DRAFT** si déjà CALCULÉ | Forcer recalcul |
| 3 | L'ajout d'une prime se fait par recherche avec autocomplétion depuis le catalogue | Limiter les erreurs de saisie |
| 4 | Les champs avec valeur par défaut (ex: jours travaillés) sont pré-remplis | Gain de temps |
| 5 | Le mode groupé ne modifie que les employés sélectionnés en amont (depuis S3) | Cohérence |
| 6 | L'aperçu en mode groupé montre le brut **avant et après** l'application | Transparence |
| 7 | Les **notes internes** ne sont pas visibles sur le bulletin employé (S4e) | Confidentialité RH |
| 8 | L'historique des avances est accessible depuis cette vue (lien) | Contexte décisionnel |

### Déclencheurs de marquage DRAFT

| Modification | Impact |
|-------------|--------|
| Jours travaillés changés | Bulletin → DRAFT, recalcul nécessaire |
| HS ajoutées/modifiées | Bulletin → DRAFT |
| Prime ajoutée/supprimée | Bulletin → DRAFT |
| Montant prime changé | Bulletin → DRAFT |
| Avance modifiée | Bulletin → DRAFT |
| Notes internes | **Pas** de marquage DRAFT |
| Commentaire | **Pas** de marquage DRAFT |

---

## États visuels

### Ligne de prime

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Saisie | Champ editable | `[45000]` avec input |
| Calculé | Valeur après recalcul | Texte brut, non éditable |
| Erreur | Montant invalide | `[⚠️ Montant non valide]` bordure rouge |
| En lot | Mode groupé | `+50 000 CDF chacun` |

### Barre d'action

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Propre | Aucune modification | Barre masquée |
| Modifié | Au moins 1 champ modifié | `⚠️ Modifications non sauvegardées (N)` flottant |
| Sauvegarde | Clic Enregistrer | Spinner, bouton désactivé |
| Erreur sauvegarde | Échec réseau | `❌ Erreur lors de la sauvegarde. [Réessayer]` |
| Succès | Sauvegarde OK | `✅ Modifications enregistrées` (auto-fade 3s) |

---

## Composants UI proposés

### `VariableEntryForm.svelte`

Formulaire principal de saisie des variables.

```svelte
<script lang="ts">
  let {
    employee = {} as EmployeeInfo,
    baseSalary = 0,
    payElements = [] as PayElementVariable[],
    onSave = (data: VariableSaveData) => Promise<void>,
    onSaveAndView = (data: VariableSaveData) => Promise<void>,
  } = $props();
</script>
```

### `OvertimeFields.svelte`

Champs de saisie des heures supplémentaires.

```svelte
<script lang="ts">
  type OvertimeLine = {
    type: "HS_30" | "HS_60" | "HS_JF" | "HS_NUIT";
    label: string;
    multiplier: number;
    hours: number;
    estimatedAmount: number;
  };

  let {
    lines = [] as OvertimeLine[],
    hourlyRate = 0,
    disabled = false,
  } = $props();
</script>
```

**Règle de calcul estimatif :**
```
Montant estimé = (salaire_de_base / 195) × coefficient × heures
```

### `PayElementList.svelte`

Liste des primes et indemnités avec ajout.

```svelte
<script lang="ts">
  let {
    items = [] as PayElementItem[],
    catalog = [] as PayElementTemplate[],
    allowAdd = true,
    onAdd = (code: string) => {},
    onRemove = (index: number) => {},
    onChange = (index: number, field: string, value: any) => {},
  } = $props();
</script>
```

### `AttendanceFields.svelte`

Champs de présence/absence.

```svelte
<script lang="ts">
  let {
    workingDays = 21,
    calendarDays = 30,
    daysWorked = 21,
    unpaidAbsenceDays = 0,
    paidLeaveDays = 0,
    readonly = false,
    onChange = (field: string, value: number) => {},
  } = $props();
</script>
```

**Validations :**
```
daysWorked + unpaidAbsenceDays + paidLeaveDays ≤ calendarDays
daysWorked ≤ workingDays (sauf si HS le week-end)
```

### `BatchVariableEntry.svelte`

Formulaire de saisie groupée.

```svelte
<script lang="ts">
  let {
    employees = [] as EmployeeSummary[],
    payElementCode = "",
    amount = 0,
    label = "",
    onApply = (data: BatchApplyData) => Promise<void>,
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/adjustments/types` | `GET` | Liste des types d'ajustement disponibles |
| `/payroll/adjustments/employee` | `POST` | Créer/modifier un ajustement pour un employé |
| `/payroll/adjustments/employee?payroll_run=X&employee=Y` | `GET` | Charger les ajustements existants |
| `/payroll/adjustments/employee/{id}` | `PATCH` | Mettre à jour un ajustement |
| `/payroll/adjustments/employee/{id}` | `DELETE` | Supprimer un ajustement |
| `/payroll/runs/{run_id}/payslips/{payslip_id}/mark-draft` | `POST` | Forcer le passage en DRAFT après modification |

### Requête `EmployeeAdjustmentCreateIn`

```json
{
  "employee": "uuid-employee",
  "payroll_run": "uuid-run",
  "adjustment_type": "uuid-type",
  "amount": 50000,
  "quantity": 1,
  "label": "Prime exceptionnelle"
}
```

### Réponse `EmployeeAdjustmentOut`

```json
{
  "id": "uuid",
  "employee": "uuid",
  "adjustment_type": {
    "code": "PRIME_EXCEP",
    "label": "Prime exceptionnelle",
    "is_taxable": true
  },
  "amount": 50000,
  "quantity": 1,
  "total": 50000,
  "label": "Prime exceptionnelle"
}
```

---

## Notes de conception

### Interaction avec le pipeline

Les données saisies dans S5 sont utilisées **à l'étape 2 (Collect)** du pipeline de calcul :
- Les `EmployeeAdjustment` sont collectés et injectés comme éléments de paie dans le flux
- La modification d'un ajustement marque le bulletin comme DRAFT mais ne déclenche **pas** le recalcul automatiquement (le gestionnaire doit le lancer depuis S3)

### Cache local

Les données du formulaire sont sauvegardées dans un **cache local** (localStorage/IndexedDB) toutes les 30 secondes pour éviter la perte en cas de crash navigateur. Une restauration est proposée :

```
💾 Des modifications non sauvegardées ont été trouvées (datant du 30/06 14:32).
[Restaurer] [Ignorer]
```

### Navigation entre employés (mode individuel)

La barre en bas ou un `← Précédent` / `Suivant →` permet de naviguer entre les employés du même run sans revenir à S3. Les modifications sont automatiquement sauvegardées au changement d'employé.
