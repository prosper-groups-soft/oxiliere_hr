# S2 — Création d'un Run

> **Dépendances :** `exchange-rates.md` (sélecteur de taux), `s3-detail-run.md` (redirection après création)

---

## Contexte

La création d'un Run de paie est le **point d'entrée** de chaque cycle mensuel. Le gestionnaire de paie définit la période, le taux de change, et les paramètres du run. Une fois créé, le système détecte automatiquement les employés éligibles.

---

## Wireframe ASCII

```
┌────────────────────────────────────────────────────────────────┐
│  ← Paies                                                       │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📄  NOUVELLE PAIE                                       │  │
│  │                                                          │  │
│  │  Période                                                 │  │
│  │  ┌────────────────────┐  ┌────────────────────┐          │  │
│  │  │  01/06/2026        │  │  30/06/2026        │          │  │
│  │  └────────────────────┘  └────────────────────┘          │  │
│  │                                                          │  │
│  │  Libellé                                                 │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Paie Juin 2026                                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  Méthode de paiement                                     │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  💳 Virement bancaire  ▼                           │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  ──── Exchange Rate (USD → CDF) ────────────────────     │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────     │  │
│  │  │  Taux de change USD/CDF    ⟳ (fetch BCC...)     │    │  │
│  │  │                                                  │    │  │
│  │  │  ┌──────────────────────────────────────────────┐│    │  │
│  │  │  │  2 850,00                                    ││    │  │
│  │  │  └──────────────────────────────────────────────┘│    │  │
│  │  │                                                  │    │  │
│  │  │  ✓ BCC · Mis à jour il y a 5 min                 │    │  │
│  │  │  📌 8 contrats en USD seront convertis           │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                          │  │
│  │  ──── Prévisualisation ────────────────────────────      │  │
│  │                                                          │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  Employés détectés pour cette période : 42       │    │  │
│  │  │                                                  │    │  │
│  │  │  Statut                       Nombre             │    │  │
│  │  │  ✅ Contrat actif               42               │    │  │
│  │  │  ⚠️ Contrat expirant bientôt    3                │    │  │
│  │  │  ❌ Pas de contrat actif        0                │    │  │
│  │  │                                                  │    │  │
│  │  │  [📋 Voir la liste]                              │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                          │  │
│  │  ⚠️  Aucun run n'a encore été créé pour Juin 2026.       │  │
│  │      La période précédente (Mai 2026) était de           │  │
│  │      58 850 000 CDF pour 40 employés.                    │  │
│  │                                                          │  │
│  │  [Annuler]                            [Créer la paie 🔒] │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Contenu | Rôle |
|------|---------|------|
| **Période** | Date picker start / end | Définition du cycle |
| **Libellé** | Champ texte libre | Identification du run |
| **Méthode de paiement** | Select bank, cash, mobile, check | Mode de paiement |
| **Taux de change** | Sélecteur ExchangeRateInput (cf. `exchange-rates.md`) | Conversion USD |
| **Prévisualisation** | Statistiques employés détectés | Validation avant création |
| **Alerte période** | Info sur période précédente | Contexte décisionnel |
| **Boutons** | Annuler / Créer | Actions |

---

## États visuels

### Prévisualisation — Détection employés

| Statut | Icône | Signification | Action |
|--------|-------|---------------|--------|
| Contrat actif | ✅ | Employé avec contrat valide pour la période | Inclus dans le run |
| Contrat expirant bientôt | ⚠️ | Contrat se termine ≤ 30 jours après la période | Alerte, inclus |
| Pas de contrat | ❌ | Aucun contrat actif pour la période | Non inclus |
| Contrat avec taux absent | ⚠️ | Contrat USD mais taux de change non défini | Attire l'attention |

### Détection des doublons

Si un run existe déjà pour la même période :

```
┌──────────────────────────────────────────────────────────┐
│  ⚠️  Un run existe déjà pour Juin 2026                    │
│                                                           │
│  • Paie Juin 2026 · Statut : DRAFT · Créé le 27/06/2026  │
│                                                           │
│  Que souhaitez-vous faire ?                                │
│  [Modifier le run existant]  [Créer un nouveau run]       │
│  [Annuler]                                                │
└──────────────────────────────────────────────────────────┘
```

---

## Règles d'interaction

| # | Règle | Justification |
|---|-------|---------------|
| 1 | La période est obligatoire et ne peut pas être dans le futur | Cohérence légale |
| 2 | La période ne peut pas dépasser 31 jours | Cohérence mensuelle |
| 3 | Le libellé est auto-généré `Paie {MMMM YYYY}` mais modifiable | Gain de temps |
| 4 | Le taux de change est auto-fetched depuis BCC (cf. `exchange-rates.md`) | Transparence |
| 5 | La prévisualisation se met à jour dynamiquement quand la période change | Feedback immédiat |
| 6 | Si run existant pour la période, alerte avec action possible | Anti-doublon |
| 7 | La création est asynchrone : bouton `Créer 🔒` lock après clic (évite double création) | Robustesse |
| 8 | La redirection se fait vers **S3** (détail du run) après création | Flux naturel |

### Validation du formulaire

| Champ | Règle | Message d'erreur |
|-------|-------|------------------|
| Période start | Requis, ≤ date courante | "La date de début est requise" |
| Période end | Requis, ≥ start, ≤ start+31 | "La période ne peut pas dépasser 31 jours" |
| Libellé | Requis | "Le libellé est requis" |
| Taux de change | Requis si contrats USD détectés | "Le taux de change est requis (8 contrats en USD)" |
| Méthode paiement | Requis | "La méthode de paiement est requise" |

---

## Composants UI proposés

### `PayrollRunCreateForm.svelte`

Formulaire de création complet.

```svelte
<script lang="ts">
  let {
    onSubmit = (data: RunCreateData) => Promise<void>,
    existingRun = null as ExistingRun | null,
    periodStart = $bindable<Date>(),
    periodEnd = $bindable<Date>(),
    label = $bindable(""),
    paymentMethod = $bindable("BANK_TRANSFER"),
    exchangeRate = $bindable(0),
    preview = {
      activeContracts: 0,
      expiringSoon: 0,
      noContract: 0,
      usdContracts: 0,
    },
    previousPeriod = {
      grossAmount: 0,
      employeeCount: 0,
    },
  } = $props();
</script>
```

**États :**
| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Normal | Formulaire vide | Champs prêts, taux en fetch |
| Fetching taux | Appel BCC en cours | Spinner sur le champ taux |
| Taux OK | BCC répond | Badge vert, taux pré-rempli |
| Taux indisponible | BCC ne répond pas | Badge jaune, fallback config |
| Validation erreur | Champs invalides | Messages d'erreur sous les champs |
| Soumission | Clic sur Créer | Bouton désactivé, spinner |
| Doublon période | Run existant détecté | Dialogue alerte |

### `PeriodPreview.svelte`

Bloc de prévisualisation des employés détectés.

```svelte
<script lang="ts">
  let {
    activeContracts = 0,
    expiringSoon = 0,
    noContract = 0,
    usdContracts = 0,
    loading = false,
    onViewList = () => {},
  } = $props();
</script>
```

### `DuplicateRunAlert.svelte`

Dialogue d'alerte pour période en doublon.

```svelte
<script lang="ts">
  let {
    existingRun = {
      label: "",
      status: "",
      created_at: Date,
    },
    onEdit = () => {},
    onCreateNew = () => {},
    onCancel = () => {},
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/runs` | `POST` | Création du run |
| `/payroll/runs/bcc-preview/` | `GET` | Fetch taux BCC |
| `/payroll/runs/preview/` | `POST` | Prévisualisation employés avant création |
| `/payroll/runs?period_start=...&period_end=...` | `GET` | Détection doublon période |

### Requête `PayrollRunCreateIn`

```json
{
  "period_start": "2026-06-01",
  "period_end": "2026-06-30",
  "label": "Paie Juin 2026",
  "payment_method": "BANK_TRANSFER",
  "exchange_rate_applied": 2850.00,
  "exchange_rate_source": "bcc"
}
```

### Réponse `PayrollRunOut` (201)

```json
{
  "id": "uuid-du-run",
  "status": "DRAFT",
  "period_start": "2026-06-01",
  "period_end": "2026-06-30",
  "label": "Paie Juin 2026",
  "exchange_rate_applied": 2850.00,
  "employee_count": 42
}
```

---

## Notes de conception

- Le composant `ExchangeRateInput` est celui défini dans `exchange-rates.md` — réutilisé ici
- La prévisualisation n'est pas bloquante (le formulaire peut être soumis même si elle est en erreur)
- Le taux de change est **optionnel** si aucun contrat USD n'est détecté
- La création du run **ne calcule pas encore les bulletins** — c'est une action séparée dans S3
