# S4 — Fiche de Paie Individuelle (Bulletin)

> **Version :** RH Complète avec mode Audit
> **Dépendances :** `exchange-rates.md` (taux de change), `catalogue.md` (éléments de paie)

---

## Contexte

La fiche de paie est le **document central** du module paie. 
C'est le Bulletin de Paie officiel qui détaille le calcul du salaire d'un employé pour une période donnée. 
Elle sert à la fois :

- **Document légal** : preuve de paiement, justification des cotisations et retenues
- **Outil de révision RH** : le gestionnaire doit pouvoir vérifier chaque ligne, comprendre le calcul, et détecter des anomalies
- **Document employé** : version simplifiée diffusée sur le portail employé (S4e)

Cet écran couvre la **vue RH complète** avec mode audit.

---

## Wireframe ASCII

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ← Paies  /  Juin 2026  /  Jean Mbemba      [BROUILLON]                    │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  📄  BULLETIN DE PAIE  ·  Juin 2026                                  │  │
│  │                                                                      │  │
│  │  Matricule : EMP-0042      Entrée : 01/03/2020    Jours : 30/30      │  │
│  │  Contrat : CDI·Classe 4·Éch. 3   Département : Production            │  │
│  │  Période : 01/06/2026 → 30/06/2026                                   │  │
│  │  Devise contrat : USD    Taux : 2 850,00 CDF/USD (BCC·30/06/2026)    │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │                                                                      │  │
│  │         RUBRIQUE                     BASE        MONTANT (CDF)       │  │
│  │  ──────────────────────────────────────────────────────────────────  │  │
│  │  🔵  GAINS                                                           │  │
│  │     Salaire de base                 2 000,00 USD     5 700 000       │  │
│  │     Indemnité de logement               270 000        270 000       │  │
│  │     Indemnité de transport               30 000         30 000       │  │
│  │     Heures sup. 30% (4h × T×1,3)         21 000         21 000       │  │
│  │     Prime de performance                 50 000         50 000       │  │
│  │     ──────────────────────────────────────────────────               │  │
│  │     SALAIRE BRUT                                     6 071 000       │  │
│  │                                                                      │  │
│  │  🔴  RETENUS SALARIALES                                              │  │
│  │     CNSS (5%)                        6 071 000        303 550        │  │
│  │     IPR / IRPP                       5 449 450        568 754        │  │
│  │     ──────────────────────────────────────────────────               │  │
│  │     TOTAL RETENUS                                      872 304       │  │
│  │                                                                      │  │
│  │  🟠  CHARGES PATRONALES                                              │  │
│  │     CNSS (13%)                       6 071 000        789 230        │  │
│  │     INPP (3,5%)                      6 071 000        212 485        │  │
│  │     ONEM (0,5%)                      6 071 000         30 355        │  │
│  │     ──────────────────────────────────────────────────               │  │
│  │     TOTAL CHARGES PATRONALES                         1 032 070       │  │
│  │                                                                      │  │
│  │  🟣  DÉDUCTIONS POST-NET                                             │  │
│  │     Avance sur salaire (échéance 5/6)                 100 000        │  │
│  │     Saisie-arrêt                                      150 000        │  │
│  │     ──────────────────────────────────────────────────               │  │
│  │     TOTAL DÉDUCTIONS                                   250 000       │  │
│  │                                                                      │  │
│  │  ──────────────────────────────────────────────────────────────────  │  │
│  │                                                                      │  │
│  │  💰  NET À PAYER                                    4 948 696  CDF   │  │
│  │       Coût total employeur                           7 103 070  CD   │  │
│  │                                                                      │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  [🔄 Mode Audit]          [📥 Exporter PDF]  [🖨️ Imprimer]          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### Vue Mode Audit (toggle activé)

Quand le mode audit est activé, chaque ligne de montant devient un lien cliquable qui révèle la formule de calcul :

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ← Paies  /  Juin 2026  /  Jean Mbemba      [BROUILLON]                   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  📄  BULLETIN DE PAIE  ·  Juin 2026   🔍  MODE AUDIT                │  │
│  │                                                                       │  │
│  │         RUBRIQUE                     MONTANT (CDF)       FORMULE      │  │
│  │  ───────────────────────────────────────────────────────────────────  │  │
│  │  🔵  GAINS                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │ Salaire de base                 5 700 000                        │ │  │
│  │  │ → 2 000,00 USD × 2 850,00 CDF/USD                              │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │ Heures sup. 30%                    21 000                        │ │  │
│  │  │ → Taux horaire × 1,3 × 4h                                       │ │  │
│  │  │ → (900 000/195) × 1,3 × 4 = 4 615,38 × 1,3 × 4                │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  🔴  RETENUES                                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │ IPR / IRPP                       568 754                        │ │  │
│  │  │ → Barème progressif sur base imposable nette                   │ │  │
│  │  │ → Base : 6 071 000 - 303 550 (CNSS) - 270 000 (logt)          │ │  │
│  │  │        = 5 449 450 CDF                                          │ │  │
│  │  │ → Tranche 1:     0 -   43 680 →      0 ×  0% =       0         │ │  │
│  │  │ → Tranche 2: 43 681 - 119 000 → 75 320 × 15% =  11 298         │ │  │
│  │  │ → Tranche 3: 119 001 - 225 000 → 106 000 × 20% = 21 200        │ │  │
│  │  │ → Tranche 4: 225 001 - 385 000 → 160 000 × 22.5% = 36 000      │ │  │
│  │  │ → …                                                              │ │  │
│  │  │ → Plafonnement 30 % : 5 449 450 × 30 % = 1 634 835 (ok)        │ │  │
│  │  │ → Abattement 3 pers. : × (1 - 0,06)                            │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  💰  NET À PAYER                                    4 948 696  CDF    │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │  │
│  │  │ Brut - Retenues - Déductions post-net                            │ │  │
│  │  │ 6 071 000 - 872 304 - 250 000 = 4 948 696                      │ │  │
│  │  └─────────────────────────────────────────────────────────────────┘ │  │
│  ├──────────────────────────────────────────────────────────────────────┤  │
│  │  [🔄 Mode Audit ✓]          [📥 Exporter PDF]  [🖨️ Imprimer]          │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Contenu | Rôle |
|------|---------|------|
| **En-tête** | ← Breadcrumb, statut run (badge) | Navigation et contexte |
| **Identité employé** | Matricule, date entrée, jours, contrat, classe, département | Identification légale |
| **Période & devise** | Mois, devise contrat, taux de change appliqué | Contexte de calcul |
| **Section Gains** | Salaire base, primes, indemnités, HS → brut | Visualisation du salaire brut |
| **Section Retenues** | CNSS, IPR/IRPP | Visualisation des cotisations et impôt |
| **Section Charges Patronales** | CNSS Pat., INPP, ONEM | Coût employeur |
| **Section Déductions Post-Net** | Avances, saisies | Ce qui est déduit après impôt |
| **Récapitulatif** | Net à payer, coût total employeur | Indicateurs clés |
| **Barre d'outils** | Mode Audit, Exporter PDF, Imprimer | Actions |

---

## États visuels

### En-tête — Statut du bulletin

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| **Brouillon** | Bulletin généré, non révisé | Badge `[BROUILLON]` bleu clair |
| **Validé** | Gestionnaire a marqué comme validé | Badge `[VALIDÉ]` vert |
| **Payé** | Run marqué comme payé | Badge `[PAYÉ]` vert foncé |
| **Correction** | Bulletin correctif créé | Badge `[CORRECTIF v2]` orange |
| **Verrouillé** | Payé ou archivé | Pas de bouton d'action |

### Mode Audit

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| **Normal** | Par défaut | Formules cachées, montants simples |
| **Audit** | Toggle cliqué | Formules visibles sous chaque ligne |
| **Audit + Chargement** | Recalcul en cours | Spinner sur les formules |

### Contenu — États particuliers

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| **Employé en USD** | Contrat en USD | Bloc `💱 Salaire contractuel` en haut avec taux et calcul |
| **Employé en CDF** | Contrat en CDF | Bloc absent (ou note subtile "Aucune conversion") |
| **Aucune donnée variable** | Pas de HS, primes, etc. | Section Gains réduite, juste salaire de base |
| **Présence d'avances** | Avance active avec échéance | Section déductions post-net visible |
| **Absence d'avances** | Pas d'avance | Section déductions post-net masquée |
| **Saisie-arrêt active** | Saisie judiciaire | Section déductions post-net visible |

---

## Règles d'interaction

| # | Règle | Justification |
|---|-------|---------------|
| 1 | Le mode audit révèle les formules **sans recharger la page** (toggle local) | Fluidité, pas de round-trip serveur |
| 2 | En mode audit, chaque montant majoré (> 1 ligne) s'affiche avec `→ formule` en dessous | Lisibilité < 1 ligne = pas de panneau |
| 3 | Les formules en audit sont **read-only** (pas de modification depuis la fiche) | La modification se fait via S5 (Variables) |
| 4 | Le bouton PDF exporte le bulletin **sans les formules d'audit** (même si le toggle est actif) | Le PDF est le document officiel |
| 5 | Le statut du bulletin détermine l'affichage des boutons d'action | Cohérence avec le workflow |
| 6 | Les sections gains/retenues/charges sont **repliables** par groupe (par défaut : tout déplié) | Aération pour bulletins complexes |

### Workflow de navigation depuis la fiche

```
Depuis S3 (liste employés)
    │
    ▼
┌─────────────────────┐
│  Clic ligne employé  │
│  ou bouton Consulter │
└────────┬────────────┘
         │
         ▼
    ┌────────────┐
    │  S4 Fiche   │  ← Navigation latérale : ← Précédent / Suivant →
    │  Jean M.    │     (parcours des employés du run)
    └────────────┘
```

### Raccourcis clavier (power user)

| Touche | Action |
|--------|--------|
| `Ctrl+A` | Activer/désactiver mode audit |
| `Ctrl+P` | Imprimer |
| `Ctrl+E` | Exporter PDF |
| `←` / `→` | Employé précédent / suivant (même run) |
| `Escape` | Revenir à S3 (liste employés) |

---

## Composants UI proposés

### `PayslipHeader.svelte`

En-tête de fiche avec breadcrumb, statut, et informations employé.

```svelte
<script lang="ts">
  let {
    employee,       // Employee
    contract,       // Contract
    period,         // { start, end }
    status,         // "DRAFT" | "VALIDATED" | "PAID" | "CORRECTION"
    runId,          // string
  } = $props();
</script>
```

**Props :**
| Prop | Type | Défaut | Description |
|------|------|--------|-------------|
| `employee` | `Employee` | requis | Infos employé |
| `contract` | `Contract` | requis | Contrat et classification |
| `period` | `{ start: Date, end: Date }` | requis | Période de paie |
| `status` | `PayslipStatus` | requis | Statut du bulletin |
| `runId` | `string` | requis | Pour breadcrumb ← Run |

### `PayslipSection.svelte`

Section générique du bulletin (Gains, Retenues, Charges, etc.).

```svelte
<script lang="ts">
  let {
    title = "",         // "Gains", "Retenues", ...
    icon = "📄",        // 🔵 🔴 🟠 🟣 💰
    items = [],         // PayslipLine[]
    total = 0,          // Montant total de la section
    auditMode = false,  // Mode audit activé ?
    defaultOpen = true, // Section dépliée par défaut ?
  } = $props();
</script>
```

**Événements :**
| Event | Payload | Déclencheur |
|-------|---------|-------------|
| `toggle` | `{ sectionId, isOpen }` | Ouverture/fermeture |

### `PayslipLine.svelte`

Ligne individuelle avec montant et formule optionnelle.

```svelte
<script lang="ts">
  let {
    label = "",             // "Salaire de base"
    amount = 0,             // 5700000
    currency = "CDF",       // Devise
    formula = null,         // null | "2 000 USD × 2 850,00"
    details = null,         // null | TrancheIRPP[] (pour audit détaillé)
    auditMode = false,
    isHighlighted = false,  // Ligne à souligner (net, total)
  } = $props();
</script>
```

### `AuditToggle.svelte`

Bouton à bascule pour le mode audit.

```svelte
<script lang="ts">
  let {
    active = $bindable(false),
    disabled = false,
  } = $props();
</script>
```

### `PayslipActionBar.svelte`

Barre d'outils en pied de fiche.

```svelte
<script lang="ts">
  let {
    payslipId = "",
    status = "DRAFT",
    onExportPdf = () => {},
    onPrint = () => {},
  } = $props();
</script>
```

### `CurrencyConversionBanner.svelte`

Bannière affichant la conversion USD → CDF (pour contrats USD).

```svelte
<script lang="ts">
  let {
    contractAmount = 2000,
    contractCurrency = "USD",
    rate = 2850,
    rateSource = "BCC",
    rateDate = "2026-06-30",
    convertedAmount = 5700000,
  } = $props();
</script>
```

### `PayslipAuditPanel.svelte`

Panneau de formule étendu pour le mode audit (détail du calcul IRPP par tranche).

```svelte
<script lang="ts">
  let {
    formula = "",
    details = [],           // AuditDetail[]
    collapsed = false,
  } = $props();

  type AuditDetail = {
    label: string,          // "Tranche 4: 225 001 - 385 000"
    amount: number,         // 160000
    rate: number,           // 0.225
    result: number,         // 36000
  };
</script>
```

---

## États de chargement et d'erreur

### Skeleton (loading)

```
┌──────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────────────┐  │
│  │  ████████  ████████████████████████████████    │  │
│  │  ████████  ████████████████████████████████    │  │
│  ├────────────────────────────────────────────────┤  │
│  │                                                 │  │
│  │  ██████  ████████████████████████████████████  │  │
│  │  ██████  ████████████████████████████████████  │  │
│  │  ██████  ████████████████████████████████████  │  │
│  │  ██████  ████████████████████████████████████  │  │
│  │                                                 │  │
│  │  ██████  ████████████████████████               │  │
│  │  ██████  ████████████████████████               │  │
│  │                                                 │  │
│  │  💰  ██████████████                             │  │
│  ├────────────────────────────────────────────────┤  │
│  │  [████████████]  [████████]  [██████]           │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### États d'erreur

| Cas | Affichage | Action |
|-----|-----------|--------|
| **Bulletin introuvable** | Écran `404` avec message : "Ce bulletin n'existe pas ou a été supprimé" | Retour vers la liste |
| **Erreur de chargement** | `⚠️ Impossible de charger ce bulletin. Réessayer` | Bouton [Réessayer] |
| **Données corrompues** (snapshot invalide) | `⚠️ Ce bulletin présente une anomalie de signature. Contacter le support.` | Badge rouge, pas d'export |
| **Paramètre légal manquant** | `⚠️ Le barème IPR/IRPP n'est pas configuré pour cette période.` | Lien vers S8 (Configuration) |

---

## API associée

### Endpoints utilisés

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/runs/{run_id}/payslips/{payslip_id}` | `GET` | Chargement du bulletin détaillé |
| `/payroll/runs/{run_id}/payslips` | `GET` | Navigation (employé précédent/suivant) |
| `/payroll/runs/{run_id}/payslips/{payslip_id}` | `PATCH` | Mise à jour statut (validation) |
| `/payroll/runs/{run_id}/payslips/{payslip_id}/export` | `GET` | Export PDF |
| `/payroll/runs/{run_id}/payslips/{payslip_id}/audit` | `GET` | Détail des formules (mode audit) |

### Réponse `EmployeePayslipDetailOut` (GET)

```json
{
  "id": "uuid",
  "employee": {
    "id": "uuid",
    "matricule": "EMP-0042",
    "full_name": "Jean Mbemba",
    "department": "Production",
    "entry_date": "2020-03-01"
  },
  "contract": {
    "type": "CDI",
    "professional_category": "Classe 4",
    "grade": "Échelon 3",
    "currency": "USD",
    "base_salary": 2000.00,
    "work_regime": "TEMPS_PLEIN"
  },
  "period": {
    "start": "2026-06-01",
    "end": "2026-06-30",
    "calendar_days": 30
  },
  "status": "DRAFT",
  "exchange_rate": {
    "rate": 2850.00,
    "source": "bcc",
    "fetched_at": "2026-06-30T09:15:00Z",
    "is_locked": false
  },
  "sections": [
    {
      "code": "GAINS",
      "label": "Gains",
      "lines": [
        {
          "code": "SAL_BASE",
          "label": "Salaire de base",
          "base_amount": 2000.00,
          "base_currency": "USD",
          "amount": 5700000.00,
          "currency": "CDF",
          "formula": "2 000,00 USD × 2 850,00 CDF/USD"
        },
        {
          "code": "IND_LOG",
          "label": "Indemnité de logement",
          "amount": 270000.00,
          "currency": "CDF",
          "formula": null
        }
      ],
      "total": 6071000.00,
      "section_type": "earning"
    },
    {
      "code": "DEDUCTIONS",
      "label": "Retenues salariales",
      "lines": [
        {
          "code": "CNSS_SAL",
          "label": "CNSS (5%)",
          "base_amount": 6071000.00,
          "amount": 303550.00,
          "currency": "CDF",
          "formula": "6 071 000 × 5%"
        },
        {
          "code": "IPR",
          "label": "IPR / IRPP",
          "base_amount": 5449450.00,
          "amount": 568754.00,
          "currency": "CDF",
          "formula": null,
          "audit_details": {
            "base": 5449450.00,
            "brackets": [
              { "from": 0, "to": 43680, "rate": 0, "amount": 0 },
              { "from": 43681, "to": 119000, "rate": 0.15, "amount": 11298 },
              { "from": 119001, "to": 225000, "rate": 0.20, "amount": 21200 }
            ],
            "cap_rate": 0.30,
            "cap_amount": 1634835.00,
            "gross_tax": 568754.00,
            "family_deduction_rate": 0.06,
            "family_deduction_count": 3,
            "final_tax": 568754.00
          }
        }
      ],
      "total": 872304.00,
      "section_type": "deduction"
    }
  ],
  "summary": {
    "gross_salary": 6071000.00,
    "total_deductions": 872304.00,
    "post_net_deductions": 250000.00,
    "net_pay": 4948696.00,
    "employer_costs": 1032070.00,
    "total_employer_cost": 7103070.00
  },
  "immutable_snapshot": {
    "signed_at": "2026-06-30T10:00:00Z",
    "sha256": "a1b2c3d4e5f6...",
    "parameters_frozen": {
      "smig": 21500,
      "cnss_rate": 0.05,
      "ipr_brackets": [ ... ],
      "exchange_rate": 2850.00
    }
  }
}
```

---

## Notes de conception

### Format des montants

| Contexte | Format |
|----------|--------|
| Montants en CDF | `X XXX XXX` avec séparateur d'espaces fines |
| Montants en USD | `X XXX,XX` suivi de `USD` |
| Taux | `X XXX,XX` avec 2 décimales |
| Pourcentages | `X %` ou `0,0X` selon contexte |

### Règle d'arrondi

- Tous les montants du bulletin sont arrondis à l'unité supérieure (règle configurable dans S8)
- Les formules en mode audit montrent les valeurs **avant arrondi** pour transparence

### Cache & Performance

- Le bulletin chargé est **mis en cache local** pendant la session (évite rechargements pendant la navigation ← →)
- Le mode audit charge les `audit_details` **à la demande** (pas inclus dans le chargement initial du bulletin)
- Les snapshots sont **validés côté frontend** au chargement : si SHA256 mismatch → alerte rouge
