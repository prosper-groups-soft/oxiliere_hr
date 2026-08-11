# S7 — Validation (Revue avant exécution)

> **Dépendances :** `s3-detail-run.md` (entrée), `s5-saisie-variables.md` (données saisies), `Guide_Calcul_Paie_RDC.md` (règles métier)

---

## Contexte

L'écran de Validation est une **revue en un coup d'œil** de tous les bulletins d'un run avant de lancer l'exécution du calcul. 
Le gestionnaire vérifie qu'il n'y a pas d'incohérences, d'erreurs de saisie, ou d'anomalies avant de déclencher le pipeline.

C'est la **dernière étape avant que le système ne produise les bulletins définitifs**. Après le calcul, les bulletins passent en statut CALCULÉ, 
et le gestionnaire peut toujours faire des corrections (S4 → correction → recalcul).

Deux sous-vues :
1. **Synthèse** — métriques agrégées du run (total brut, total net, anomalies)
2. **Revue détaillée** — liste des bulletins avec indicateurs d'anomalie

---

## Wireframe ASCII — Synthèse de Validation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Paies  /  Juin 2026  /  Validation                                       │
│                                                                             │
│  🔍 VALIDATION AVANT EXÉCUTION  ·  Juin 2026                                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  📊 SYNTHÈSE                                                          │  │
│  │                                                                       │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │  │
│  │  │  45          │  │  42 200 000  │  │  31 500 000  │  │  5         │ │  │
│  │  │  Employés    │  │  Brut total  │  │  Net total   │  │  Anomalies │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │  │
│  │                                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │  │  Aperçu des charges                                              │ │  │
│  │  │                                                                  │ │  │
│  │  │  CNSS part. :   45 × 25 000 CDF   =   1 125 000 CDF              │ │  │
│  │  │  CNSS employé :   45 × 25 000 CDF   =   1 125 000 CDF            │ │  │
│  │  │  IPR total    :   4 200 000 CDF   (moyenne 93 333 CDF/emp)       │ │  │
│  │  │  ONEM         :   45 × 10 000 CDF   =     450 000 CDF            │ │  │
│  │  │  INPP         :   45 × 10 000 CDF   =     450 000 CDF            │ │  │
│  │  │                                                                  │ │  │
│  │  │  Coût total employeur  :  45 350 000 CDF                         │ │  │
│  │  │  Net total distribué   :  31 500 000 CDF                         │ │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  ⚠️ ANOMALIES DÉTECTÉES (5)  [Voir tout ▼]                            │  │
│  │                                                                       │  │
│  │  Jean Mbemba       · Brut : 98 200 000 CDF  ⚠️ Anomalie (x17 vs M-1)  │  │
│  │  Albert Mbuyu      · Net négatif : -15 000 CDF ⚠️                     │  │
│  │  Marie Kabasele    · IPR manquant (taux 0%) ⚠️                        │  │
│  │  Paulin Ngoy       · Absence justifiée sans déduction                 │  │
│  │  Nathalie Banza    · HS > 50% jours ouvrés ⚠️                         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  [Retour]              [⚠️ Forcer exécution (5 anomalies)]                  │
│                        [▶️ Lancer le calcul (aucune anomalie bloquante)]    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe — Revue détaillée

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Validation  /  Détail                                                    │
│                                                                             │
│  🔍 DÉTAIL DES EMPLOYÉS  ·  Juin 2026                                       │
│                                                                             │
│  [🔎 Rechercher un employé...]                                              │
│                                                                             │
│  Filtres rapides : [Tous] [⚠️ Anomalies (5)] [✅ OK (40)]                  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  ⚠️ Anomalie │ Employé      │ Brut CDF       │ Net CDF      │ Statut  │  │
│  ├───────────────────────────────────────────────────────────────────────┤  │
│  │  ⚠️          │ Jean Mbemba  │ 98 200 000     │ 85 000 000   │ DRAFT   │  │
│  │  ⚠️          │ Albert Mbuyu │ 150 000        │ -15 000      │ DRAFT   │  │
│  │  ⚠️          │ Marie Kabase │ 4 250 000      │ 4 250 000    │ DRAFT   │  │
│  │  ⚠️          │ Paulin Ngoy  │ 2 100 000      │ 1 500 000    │ DRAFT   │  │
│  │  ⚠️          │ Nathalie Ban │ 3 800 000      │ 2 850 000    │ DRAFT   │  │
│  │  ✅          │ Pierre Lunda│ 1 250 000      │ 900 000      │ DRAFT    │  │
│  │  ✅          │ ...         │ ...            │ ...          │ ...      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  [Retour synthèse]                              [▶️ Lancer le calcul]       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Types d'anomalies détectées

| Code | Anomalie | Seuil | Bloquant ? |
|------|----------|-------|------------|
| `BRUT_SPIKE` | Brut anormal vs M-1 | > 300 % ou < 50 % | Oui |
| `NET_NEGATIF` | Net négatif après déductions | < 0 | Oui |
| `IPR_MISSING` | IPR = 0 pour un revenu imposable | IPR = 0 & salaire > SMIG | Oui |
| `HS_EXCESS` | HS > 50 % des jours ouvrés | > 50 % | Non (info) |
| `ABS_NO_DEDUCT` | Absence sans déduction correspondante | | Non (info) |
| `DUAL_CURRENCY` | Contrat USD mais taux non configuré | | Oui |
| `BASELESS_PRIME` | Prime sans base légale attachée | | Non (info) |
| `CNSS_CEIL_EXCEEDED` | Salaire > plafond CNSS sans mention | > 150 000 CDF (plafond) | Non (info) |
| `PAYELEM_MISSING` | Élément obligatoire manquant (CNSS, IPR) | | Oui |
| `MULTI_CONTRACT` | Employé multi-contrats sans répartition | | Oui |
| `ZERO_SALARY` | Salaire de base = 0 | = 0 | Oui |

### Règles de détermination

Les anomalies sont calculées **côté serveur** via une analyse statique des données avant exécution :

1. Pour `BRUT_SPIKE` : comparaison avec le run précédent du même cycle
2. Pour `NET_NEGATIF` : simulation rapide des déductions fixes (avances, IPR)
3. Pour `IPR_MISSING` : vérification que le taux IPR est > 0 si salaire > seuil
4. Pour `HS_EXCESS` : (total HS heures) / (jours ouvrés × 8) > 50 %
5. Les anomalies non-bloquantes peuvent être **marquées comme ignorées** par le gestionnaire

---

## États visuels

### Carte de synthèse

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Normal | 0 anomalie | Fond vert, ✅ Aucune anomalie |
| Avertissement | 1-3 anomalies non bloquantes | Fond jaune, ⚠️ N anomalies non bloquantes |
| Bloquant | ≥ 1 anomalie bloquante | Fond rouge, 🚫 N anomalies bloquantes |

### Bouton de lancement

| État | Déclencheur | Texte | Désactivé ? |
|------|-------------|-------|-------------|
| Prêt | 0 anomalie | ▶️ Lancer le calcul | Non |
| Avec infos | Anomalies non bloquantes uniquement | ⚠️ Lancer le calcul (N infos) | Non |
| Bloqué | ≥ 1 anomalie bloquante | 🚫 N anomalies bloquantes | Oui |
| Forcé | Gestionnaire force | ⚠️ Forcer exécution (N anomalies) | Non |

---

## Composants UI proposés

### `ValidationSummaryCard.svelte`

Carte de synthèse du run.

```svelte
<script lang="ts">
  let {
    employeeCount = 0,
    grossTotal = 0,
    netTotal = 0,
    anomalyCount = 0,
    chargeBreakdown = [] as ChargeLine[],
    employerTotalCost = 0,
  } = $props();
</script>
```

### `AnomalyList.svelte`

Liste des anomalies détectées.

```svelte
<script lang="ts">
  type Anomaly = {
    code: string;
    severity: "blocking" | "warning" | "info";
    employeeName: string;
    employeeId: string;
    description: string;
    canIgnore: boolean;
    ignored: boolean;
  };

  let {
    anomalies = [] as Anomaly[],
    onToggleIgnore = (index: number) => {},
    onViewEmployee = (id: string) => {},
  } = $props();
</script>
```

### `ValidationEmployeeTable.svelte`

Tableau détaillé des employés avec statut d'anomalie.

```svelte
<script lang="ts">
  type ValidationEmployeeRow = {
    id: string;
    name: string;
    grossPay: number;
    netPay: number;
    anomalyCount: number;
    anomalySeverity: "none" | "warning" | "blocking";
    status: PayslipStatus;
  };

  let {
    rows = [] as ValidationEmployeeRow[],
    filter = "all" as "all" | "anomalies" | "ok",
    search = "",
  } = $props();
</script>
```

### `ValidationActionBar.svelte`

Barre d'action en bas de l'écran.

```svelte
<script lang="ts">
  let {
    blockingCount = 0,
    warningCount = 0,
    onExecute = () => Promise<void>,
    onForceExecute = () => Promise<void>,
    onBack = () => {},
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/runs/{id}/validation` | `GET` | Récupérer la synthèse de validation |
| `/payroll/runs/{id}/validation/anomalies` | `GET` | Liste des anomalies |
| `/payroll/runs/{id}/execute` | `POST` | Lancer l'exécution du calcul |
| `/payroll/runs/{id}/execute?force=true` | `POST` | Forcer l'exécution même avec anomalies |
| `/payroll/runs/{id}/validation/anomalies/{anomaly_id}/ignore` | `POST` | Marquer une anomalie comme ignorée |

### Réponse `ValidationSummaryOut`

```json
{
  "run_id": "uuid",
  "period_label": "Juin 2026",
  "employee_count": 45,
  "gross_total": 42200000,
  "net_total": 31500000,
  "employer_total_cost": 45350000,
  "charge_breakdown": [
    { "code": "CNSS", "label": "CNSS part patronale", "total": 1125000 },
    { "code": "IPR", "label": "IPR total", "total": 4200000 },
    { "code": "ONEM", "label": "ONEM", "total": 450000 },
    { "code": "INPP", "label": "INPP", "total": 450000 }
  ],
  "anomaly_summary": {
    "blocking": 2,
    "warning": 3,
    "info": 0,
    "total": 5
  }
}
```

### Réponse `ValidationAnomalyOut`

```json
{
  "id": "uuid",
  "employee": {
    "id": "uuid",
    "name": "Jean Mbemba",
    "matricule": "EMP-0042"
  },
  "code": "BRUT_SPIKE",
  "severity": "blocking",
  "description": "Brut anormal : 98 200 000 CDF (x17 vs M-1 : 5 700 000 CDF)",
  "can_ignore": false,
  "ignored": false
}
```

---

## Notes de conception

### Cycle de vie du run

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  DRAFT   │ →   │  READY   │ →   │PROCESSING│ →   │ COMPLETED│
│ (créé)   │     │(validé)  │     │(calcul)  │     │ (fait)   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

- Le passage de `DRAFT` vers `READY` se fait automatiquement à l'affichage de S7
- `READY` signifie : "prêt pour exécution", pas de verrouillage
- Le calcul peut être **annulé** si en `PROCESSING` (retour à `DRAFT`)
- Après `COMPLETED`, tout modification nécessite une correction

### Forçage et responsabilité

Quand un gestionnaire force l'exécution avec des anomalies bloquantes :

1. Un **commentaire obligatoire** est demandé : "Raison du forçage"
2. Le commentaire est horodaté et signé (nom du gestionnaire)
3. Les anomalies forcées sont stockées dans l'audit trail du run
4. Un rapport post-calcul vérifie si les anomalies étaient justifiées

```
🚫 Pour procéder au forçage, veuillez justifier :
[Prime exceptionnelle approuvée par DG le 28/06 - dépassement temporaire]

[Annuler]    [Confirmer le forçage]
```

### Performance

- La synthèse de validation doit être calculée en **< 2 secondes** pour 500 employés
- Les anomalies sont calculées côté serveur (pas de téléchargement des données brutes)
- Utilisation de requêtes agrégées SQL pour les totaux
- Mise en cache des résultats de validation (invalidée si S5 est modifié)
