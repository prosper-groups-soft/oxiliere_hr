# S6 — Avances sur Salaire
> **Dépendances :** `s1-liste-executions.md` (accès), `s5-saisie-variables.md` (déclaration dans le cycle)

---

## Contexte

L'écran de gestion des Avances sur Salaire permet de gérer le cycle de vie complet des avances demandées par les employés :

1. **Demande** (initiée par l'employé ou le gestionnaire RH)
2. **Approbation** (validation N+1 ou RH)
3. **Déduction** (intégration dans le cycle de paie)
4. **Suivi** (solde restant, échéances)

> **Contexte RDC :** Les avances sur salaire sont très courantes en RDC. 
Elles sont généralement remboursées sur 1 à 3 mois par déduction sur le bulletin. La loi autorise l'avance sans intérêt, avec un plafond implicite (généralement 30-50 % du salaire net). 
Le suivi est crucial car les défauts de remboursement sont fréquents.

---

## Wireframe ASCII — Liste des avances

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  💰 Paie  /  Avances sur salaire                                            │
│                                                                             │
│  AVANCES SUR SALAIRE                                                        │
│                                                                             │
│  [+ Nouvelle avance]                                                        │
│                                                                             │
│  Filtres : [Tous ▼]  Statut : [Tous ▼]  🔎 [Rechercher employé...]          │
│                                                                             │
│  ┌──────┬──────────────┬────────────┬───────┬───────┬──────────┬─────────┐  │
│  │      │ Employé      │ Montant    │ Reste │ Éch.  │ Statut   │ Cycle   │  │
│  ├──────┼──────────────┼────────────┼───────┼───────┼──────────┼─────────┤  │
│  │  📌  │ Jean Mbemba  │ 500 000    │ 300 K │ 09/26 │ Active   │ Juin 26 │  │
│  │  ✅  │ Albert Mbuyu │ 200 000    │ 0     │ 06/26 │ Remb.    │ Mai 26  │  │
│  │  ⏳  │ Marie Kabase │ 300 000    │ 300 K │ 07/26 │ En att.  │ —       │  │
│  │  ❌  │ Paulin Ngoy  │ 150 000    │ 150 K │ 06/26 | Rejetée  │ —       │  │
│  │  🔁  │ Nathalie Ban │ 400 000    │ 200 K │ 08/26 │ Active   │ Juin 26 │  │
│  └──────┴──────────────┴────────────┴───────┴───────┴──────────┴─────────┘  │
│                                                                             │
│  Légende : 📌 Active  ✅ Remboursée  ⏳ En attente  ❌ Rejetée  🔁 Plan recalculé  │
│                                                                             │
│  [+ Voir historique complet]  [📤 Exporter]                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe ASCII — Détail d'une avance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Avances  /  Jean Mbemba  /  500 000 CDF                                  │
│                                                                             │
│  📋 DÉTAIL DE L'AVANCE                                                      │
│                                                                             │
│  Employé         :  Jean Mbemba (EMP-0042)                                  │
│  Montant         :  500 000 CDF                                             │
│  Solde restant   :  300 000 CDF                                             │
│  Date demande    :  01/06/2026                                              │
│  Approuvée par   :  P. Kazadi (DG) le 02/06/2026                            │
│  Statut          :  ✅ Active (2/5 échéances payées)                        │
│                                                                             │
│  ──── Motif ───────────────────────────────────────────────                 │
│  "Urgence familiale - frais médicaux"                                       │
│                                                                             │
│  ──── Plan de remboursement ────────────────────────────────                │
│                                                                             │
│  N°   Période      Montant     Reste       Statut                           │
│  1    Juin 2026    100 000     400 000     ✅ Déduit (bulletin 002323)      │
│  2    Juillet 2026 100 000     300 000     📅 Prévisionnel                  │
│  3    Août 2026    100 000     200 000     📅 Prévisionnel                  │
│  4    Sept. 2026   100 000     100 000     📅 Prévisionnel                  │
│  5    Oct. 2026    100 000     0           📅 Prévisionnel                  │
│                                                                             │
│  ──── Actions ──────────────────────────────────────────────                │
│                                                                             │
│  [✏️ Modifier] [📄 Bulletin] [🗑️ Annuler l'avance] [🔁 Recalculer plan]    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  ⚠️  Modification du plan de remboursement                           │   │
│  │  Voulez-vous modifier les échéances ? Cette action impactera les     │   │
│  │  cycles de paie à venir.                                             │   │
│  │  [Annuler]    [Modifier le plan]                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe ASCII — Nouvelle demande d'avance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Avances  /  Nouvelle demande                                             │
│                                                                             │
│  ✏️ NOUVELLE DEMANDE D'AVANCE                                               │
│                                                                             │
│  Employé : [Jean Mbemba ▼]                                                  │
│  Montant : [500 000] CDF                                                    │
│  Motif   : [Urgence familiale - frais médicaux]                             │
│                                                                             │
│  Plan de remboursement suggéré                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Salaire net estimé : 820 000 CDF                                     │  │
│  │  Mensualité suggérée : 100 000 CDF/mois (12,2 % du net)               │  │
│  │  Durée suggérée      : 5 mois                                         │  │
│  │  Plafond recommandé  : 410 000 CDF (50 % du net)                      │  │
│  │                                                                       │  │
│  │  ⚠️  Le montant demandé (500 000 CDF) dépasse le plafond recommandé   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Mensualité : [100 000] CDF  ·  Durée : [5] mois  ·  1ère éch. : [Juin 2026]│
│                                                                             │
│  [Annuler]    [Soumettre pour approbation]                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Écran | Contenu |
|------|-------|---------|
| **Liste des avances** | Liste | Tableau avec filtres, statuts, soldes |
| **Détail d'une avance** | Détail | Infos complètes, plan de remboursement, historique |
| **Nouvelle demande** | Création | Formulaire, suggestions, règles de validation |
| **Approbation** | (intégré ou notifications) | Validation par N+1/RH |

---

## Composants UI proposés

### `AdvanceList.svelte`

Tableau listant toutes les avances.

```svelte
<script lang="ts">
  type AdvanceRow = {
    id: string;
    employeeName: string;
    employeeMatricule: string;
    amount: number;
    remaining: number;
    dueDate: string;
    status: AdvanceStatus;
    linkedCycle?: string;
  };

  let {
    rows = [] as AdvanceRow[],
    filters = { status: "all", search: "" },
    onNew = () => {},
    onRowClick = (id: string) => {},
  } = $props();
</script>
```

### `AdvanceDetail.svelte`

Détail d'une avance avec plan de remboursement.

```svelte
<script lang="ts">
  type AdvanceDetail = {
    id: string;
    employee: EmployeeInfo;
    amount: number;
    remaining: number;
    requestedAt: string;
    approvedBy?: string;
    approvedAt?: string;
    status: AdvanceStatus;
    reason: string;
    repaymentPlan: RepaymentLine[];
  };

  type RepaymentLine = {
    index: number;
    periodLabel: string;
    amount: number;
    remainingAfter: number;
    status: "paid" | "scheduled" | "missed";
    payslipRef?: string;
  };

  let {
    detail = null as AdvanceDetail | null,
    onEdit = () => {},
    onCancel = () => {},
    onRecalculate = () => {},
  } = $props();
</script>
```

### `AdvanceCreateForm.svelte`

Formulaire de création d'une demande.

```svelte
<script lang="ts">
  type AdvanceCreateData = {
    employeeId: string;
    amount: number;
    reason: string;
    monthlyPayment: number;
    durationMonths: number;
    firstPeriod: string;
  };

  let {
    employees = [] as EmployeeInfo[],
    onSubmit = (data: AdvanceCreateData) => Promise<void>,
    onCancel = () => {},
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/advances` | `GET` | Liste des avances |
| `/payroll/advances/{id}` | `GET` | Détail d'une avance |
| `/payroll/advances` | `POST` | Créer une demande |
| `/payroll/advances/{id}/approve` | `POST` | Approuver une demande |
| `/payroll/advances/{id}/reject` | `POST` | Rejeter une demande |
| `/payroll/advances/{id}/cancel` | `POST` | Annuler une avance active |
| `/payroll/advances/{id}/plan` | `PUT` | Modifier le plan de remboursement |
| `/payroll/advances/preview` | `POST` | Suggérer un plan de remboursement |

### Réponse `AdvanceListOut`

```json
{
  "items": [
    {
      "id": "uuid",
      "employee": { "id": "uuid", "name": "Jean Mbemba", "matricule": "EMP-0042" },
      "amount": 500000,
      "remaining": 300000,
      "due_date": "2026-09-01",
      "status": "active",
      "linked_cycle": "Juin 2026"
    }
  ],
  "totals": {
    "active": { "count": 12, "amount": 3500000, "remaining": 2100000 },
    "pending": { "count": 3, "amount": 800000 }
  }
}
```

### Corps `AdvanceCreateIn`

```json
{
  "employee_id": "uuid",
  "amount": 500000,
  "reason": "Urgence familiale - frais médicaux",
  "monthly_payment": 100000,
  "duration_months": 5,
  "first_period": "2026-06"
}
```

---

## Cycle de vie et statuts

```
                    ┌──────────┐
                    │ PENDING  │ (en attente d'approbation)
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌──────────┐
        │ ACTIVE  │ │ REJECTED│ │ CANCELLED│
        └────┬────┘ └─────────┘ └──────────┘
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌──────────┐
│ PAID   │ │ ACTIVE │ │ DEFAULT │
│ (tout) │ │ (partiel)│ (impayé) │
└────────┘ └────────┘ └──────────┘
```

| Statut | Description |
|--------|-------------|
| `PENDING` | En attente d'approbation (N+1 ou RH) |
| `ACTIVE` | Approuvée, en cours de remboursement |
| `REJECTED` | Rejetée (motif stocké) |
| `CANCELLED` | Annulée par le gestionnaire ou employé |
| `PAID` | Intégralement remboursée |
| `DEFAULT` | Une ou plusieurs échéances non honorées |

---

## Règles métier

| # | Règle | Niveau |
|---|-------|--------|
| 1 | Une avance ne peut pas dépasser 50 % du salaire net estimé | Warning |
| 2 | Maximum 3 avances actives simultanément par employé | Bloquant |
| 3 | Le remboursement se fait obligatoirement par déduction sur bulletin | Fixe |
| 4 | Pas d'intérêt sur l'avance (conformité légale RDC) | Fixe |
| 5 | La 1ère échéance ne peut pas être avant le cycle en cours | Validation |
| 6 | La durée max est de 6 mois (défaut au-delà) | Warning |
| 7 | Tout défaut de paiement bloque les nouvelles avances | Bloquant |
| 8 | L'approbation est automatique pour les montants < 200 000 CDF | Règle configurable |

---

## Intégration avec S5 (Saisie Variables)

Quand une avance est active et que son échéance tombe sur la période en cours :

1. S5 affiche l'avance dans la zone **Avances et Déductions**
2. Le montant de l'échéance est **pré-rempli** dans les variables de l'employé
3. Le gestionnaire peut modifier le montant (ex: remboursement anticipé partiel)
4. La modification est répercutée sur le plan de remboursement

```
Exemple :
Avance Jean Mbemba : Échéance Juin 2026 = 100 000 CDF
→ S5 affiche : "Avance salaire (Juin) : [100 000] CDF"
→ Si modifié à 150 000 : le plan est ajusté automatiquement
```
