# S8 — Configuration de la Paie

> **Dépendances :** `Guide_Calcul_Paie_RDC.md` (paramètres légaux), `exchange-rates.md` (taux), `catalogue.md` (catalogue)

---

## Contexte

L'écran de Configuration regroupe les **paramètres généraux** du module paie. C'est un écran sensible, 
accessible uniquement aux administrateurs RH avec un rôle spécifique (`payroll.config`).

Il est divisé en sections organisées par onglets :

1. **Paramètres légaux** (CNSS, IPR, ONEM, INPP, SMIG)
2. **Taux de change** (configuration des sources BCC)
3. **Catalogue** (gestion des éléments de paie)
4. **Cycle** (jalons, échéances, automations)
5. **Notifications** (règles d'envoi aux employés)

---

## Wireframe ASCII

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuration de la paie                                                │
│                                                                             │
│ [Paramètres légaux]  [Taux de change]  [Catalogue]  [Cycle]  [Notifications]│
│                                                                             │
│  ──── Paramètres légaux ─────────────────────────────────────────────────   │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  SMIG                                                                 │  │
│  │  Salaire minimum interprofessionnel garanti : [70 000] CDF            │  │
│  │  Date dernière révision : 01/01/2026                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  CNSS                                                                 │  │
│  │  Taux part employeur : [4.00] %                                       │  │
│  │  Taux part salarié   : [3.50] %                                       │  │
│  │  Plafond mensuel     : [150 000] CDF                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  IPR (Impôt Professionnel sur les Rémunérations)                      │  │
│  │                                                                       │  │
│  │  Barème progressif :                                                  │  │
│  │  ┌─────────────┬─────────────┬─────────┐                              │  │
│  │  │ De          │ À           │ Taux    │                              │  │
│  │  ├─────────────┼─────────────┼─────────┤                              │  │
│  │  │ 0           │ 100 000     │ 0 %     │                              │  │
│  │  │ 100 001     │ 200 000     │ 10 %    │                              │  │
│  │  │ 200 001     │ 400 000     │ 20 %    │                              │  │
│  │  │ 400 001     │ 800 000     │ 25 %    │                              │  │
│  │  │ 800 001     │ +           │ 30 %    │                              │  │
│  │  └─────────────┴─────────────┴─────────┘                              │  │
│  │  [+ Ajouter tranche]                                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  ONEM / INPP                                                          │  │
│  │  ONEM : [10 000] CDF par employé/mois                                 │  │
│  │  INPP : [10 000] CDF par employé/mois                                 │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Allocations légales                                                  │  │
│  │  ┌───────────────┬──────────────┬──────────────┬──────────────┐      │  │
│  │  │ Allocation    │ Base         │ Taux/Plafond │ Imposable    │      │  │
│  │  ├───────────────┼──────────────┼──────────────┼──────────────┤      │  │
│  │  │ Logement      │ Salaire base │ 30 %         │ > plafond    │      │  │
│  │  │ Transport     │ Forfait      │ /jour        │ Exonérée     │      │  │
│  │  └───────────────┴──────────────┴──────────────┴──────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Actions                                                              │  │
│  │  [Réinitialiser aux valeurs légales]  [Sauvegarder]                   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Onglet — Taux de change

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuration  /  Taux de change                                        │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Source BCC                                                           │  │
│  │                                                                       │  │
│  │  Mode de récupération : [Automatique (API BCC) ▼]                     │  │
│  │  URL de l'API : [https://www.bcc.cd/...]                              │  │
│  │  Fréquence de mise à jour : [Quotidienne ▼]                           │  │
│  │                                                                       │  │
│  │  💡 Dernier taux récupéré : 2 850,00 CDF/USD (30/06/2026 08:00)       │  │
│  │  [Tester la connexion]  [Forcer la récupération]                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Taux de secours (fallback)                                           │  │
│  │                                                                       │  │
│  │  Si l'API BCC est indisponible :                                      │  │
│  │                                                                       │  │
│  │  ○ Utiliser le dernier taux connu                                     │  │
│  │  ● Utiliser un taux manuel : [2 850,00] CDF/USD                       │  │
│  │  ○ Bloquer toute création de run                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Historique des taux                                                  │  │
│  │  ┌────────┬─────────────┬───────────┬──────────────┐                  │  │
│  │  │ Date   │ Taux        │ Source    │ Notes        │                  │  │
│  │  ├────────┼─────────────┼───────────┼──────────────┤                  │  │
│  │  │ 30/06  │ 2 850,00    │ BCC       │ Automatique  │                  │  │
│  │  │ 29/06  │ 2 845,00    │ BCC       │ Automatique  │                  │  │
│  │  │ 28/06  │ 2 840,00    │ Manuel    │ WE - saisi   │                  │  │
│  │  └────────┴─────────────┴───────────┴──────────────┘                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
```

---

## Onglet — Catalogue

> **Implémentation réelle :** `CatalogSettings.svelte` — CRUD complet (créer, modifier, supprimer, rechercher, filtrer, réinitialiser).
> Le catalogue regroupe les **éléments conventionnels** (primes et retenues propres à l'entreprise),
> distincts des **allocations légales** (logement, transport) gérées dans l'onglet Paramètres légaux.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuration  /  Catalogue                                             │
│                                                                             │
│  📦 CATALOGUE DES ÉLÉMENTS DE PAIE                                          │
│  Primes et bonus conventionnels de l'entreprise, activables par contrat.    │
│                                                                             │
│  [🔎 Rechercher...]  Filtre : [Tous ▼]    [+ Nouvel élément]  [↺ Réinitialiser]│
│                                                                             │
│  ┌────────────────────────────┬──────────┬────────┬─────────────┬──────┬────┐ │
│  │ Libellé                    │ Catégorie│ Calcul │ Traitement  │ Actif│ ☰  │ │
│  ├────────────────────────────┼──────────┼────────┼─────────────┼──────┼────┤ │
│  │ Allocation télétravail     │ Bonus    │ 0 CDF  │ IRPP + CNSS │ ☑    │ ✏️🗑│ │
│  │ Assurance santé entreprise │ Bonus    │ 0 %    │ IRPP + CNSS │ ☑    │ ✏️🗑│ │
│  │ Prime d'ancienneté         │ Bonus    │ 5 %    │ IRPP exclu  │ ☑    │ ✏️🗑│ │
│  └────────────────────────────┴──────────┴────────┴─────────────┴──────┴────┘ │
│                                                                             │
│  💡 Éléments conventionnels imposables et cotisables. Les allocations légales│
│     (logement, transport) sont gérées dans l'onglet Paramètres légaux.      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Fonctionnalités

| Fonction | Comportement |
|----------|-------------|
| 🔍 **Recherche** | Filtre par libellé et description/formule (insensible à la casse) |
| 🎛️ **Filtre catégorie** | Tous / Bonus / Retenues |
| ➕ **Nouvel élément** | Ouvre un dialogue : libellé, catégorie (Bonus/Retenue), mode de calcul (Montant fixe / Pourcentage), montant ou %, description/formule, toggles IRPP, CNSS, Obligatoire, Actif |
| ✏️ **Modifier** | Même dialogue pré-rempli — tous les champs sont éditables (y compris IRPP/CNSS/formule) |
| 🗑️ **Supprimer** | Confirmation globale (`notification.confirm`). Bloqué par le backend si des employés utilisent cet élément |
| 🔃 **Actif** | Toggle par ligne (PATCH `{is_active}`) |
| ↺ **Réinitialiser** | Confirmation → recharge la fixture `payroll_adjustments.json` (valeurs par défaut légales), écrase les modifications |

### Types d'éléments

| Champ | Valeurs | Notes |
|-------|---------|-------|
| `adjustment_type` | `BONUS` / `CONTRIBUTION` | Bonus = prime, Contribution = retenue |
| `calculation_mode` | `FIXED` / `PERCENTAGE` | Montant fixe (CDF) ou % du salaire de base |
| `is_taxable` | booléen | Imposable IRPP ou exclu |
| `is_cnss_subject` | booléen | Soumis CNSS ou exclu |
| `is_mandatory` | booléen | Obligatoire par contrat ou optionnel |

### API associée (catalogue)

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/adjustments/types` | `GET` | Liste paginée (cache 24h) |
| `/payroll/adjustments/types` | `POST` | Créer un élément |
| `/payroll/adjustments/{id}` | `PATCH` | Modifier un élément |
| `/payroll/adjustments/{id}` | `DELETE` | Supprimer (bloqué si référencé) |
| `/payroll/adjustments/reset/` | `POST` | Réinitialiser depuis la fixture |

> **Note de séparation :** les allocations légales (logement, transport) restent dans
> l'onglet Paramètres légaux (`/payroll/configuration/allowances/`). L'allocation familiale
> n'y figure plus : c'est une **prestation CNSS** versée directement au travailleur
> (8 100 FC / enfant / mois, payée trimestriellement par la Caisse) — hors paie employeur.

---

## Composants UI proposés

### `ConfigLegalParams.svelte`

Paramètres légaux (CNSS, IPR, SMIG, ONEM, INPP).

```svelte
<script lang="ts">
  type LegalParams = {
    smig_amount: number;
    cnss_employer_rate: number;
    cnss_employee_rate: number;
    cnss_ceiling: number;
    ipr_brackets: IPRBracket[];
    onem_amount: number;
    inpp_amount: number;
  };

  let {
    params = {} as LegalParams,
    onSave = (data: LegalParams) => Promise<void>,
    onReset = () => {},
  } = $props();
</script>
```

### `ConfigExchangeRate.svelte`

Configuration des taux de change (réutilise `ExchangeRateInput`).

```svelte
<script lang="ts">
  type ExchangeRateConfig = {
    source: "bcc_auto" | "bcc_manual" | "config_manual";
    api_url: string;
    update_frequency: "daily" | "weekly" | "monthly";
    fallback_mode: "last_known" | "manual" | "block";
    manual_rate: number;
  };

  let {
    config = {} as ExchangeRateConfig,
    onTestConnection = () => Promise<void>,
    onForceFetch = () => Promise<void>,
    onSave = (data: ExchangeRateConfig) => Promise<void>,
  } = $props();
</script>
```

### `ConfigCycle.svelte`

Configuration du cycle mensuel.

```svelte
<script lang="ts">
  type CycleConfig = {
    deadline_day: number; // ex: 5 → 5 du mois suivant
    auto_remind: boolean;
    remind_days_before: number[];
    default_payment_method: "bank" | "cash" | "check";
    validation_required: boolean;
  };

  let {
    config = {} as CycleConfig,
    onSave = (data: CycleConfig) => Promise<void>,
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/config` | `GET` | Récupérer toute la configuration |
| `/payroll/config/legal` | `PUT` | Mettre à jour les paramètres légaux |
| `/payroll/config/exchange-rate` | `PUT` | Configurer les taux de change |
| `/payroll/config/cycle` | `PUT` | Configurer les paramètres de cycle |
| `/payroll/adjustments/types` | `GET` | Catalogue des éléments de paie (pagé) |
| `/payroll/adjustments/types` | `POST` | Créer un élément du catalogue |
| `/payroll/adjustments/{id}` | `PATCH` | Modifier un élément du catalogue |
| `/payroll/adjustments/{id}` | `DELETE` | Supprimer un élément (bloqué si référencé) |
| `/payroll/adjustments/reset/` | `POST` | Réinitialiser le catalogue depuis la fixture |
| `/payroll/config/allowances` | `GET` | Allocations légales (logement, transport) |
| `/payroll/config/allowances/{id}` | `PATCH` | Modifier une allocation légale |
| `/payroll/config/allowances/reset/` | `POST` | Réinitialiser les allocations depuis la fixture |
| `/payroll/configuration/contributions/` | `GET` | Cotisations sociales (CNSS, ONEM, INPP) — taux légaux read-only |

### Réponse `PayrollConfigOut`

```json
{
  "legal": {
    "smig_amount": 70000,
    "cnss_employer_rate": 4.0,
    "cnss_employee_rate": 3.5,
    "cnss_ceiling": 150000,
    "ipr_brackets": [
      { "from": 0, "to": 100000, "rate": 0 },
      { "from": 100001, "to": 200000, "rate": 10 },
      { "from": 200001, "to": 400000, "rate": 20 },
      { "from": 400001, "to": 800000, "rate": 25 },
      { "from": 800001, "to": null, "rate": 30 }
    ],
    "onem_amount": 10000,
    "inpp_amount": 10000
  },
  "exchange_rate": {
    "source": "bcc_auto",
    "api_url": "https://www.bcc.cd/...",
    "update_frequency": "daily",
    "fallback_mode": "last_known",
    "manual_rate": null
  },
  "cycle": {
    "deadline_day": 5,
    "auto_remind": true,
    "remind_days_before": [7, 3, 1],
    "default_payment_method": "bank",
    "validation_required": true
  }
}
```

---

## Règles d'accès

| Rôle | Accès | Actions possibles |
|------|-------|-------------------|
| `payroll.admin` | Complet | Lecture + écriture partout |
| `payroll.config` | Configuration uniquement | Lecture + écriture (hors RH pur) |
| `payroll.manager` | Lecture seule | Consultation uniquement |
| `payroll.viewer` | Lecture seule restreinte | Pas d'accès à la configuration |

---

## États visuels

### Champ de paramètre légal

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Normal | Valeur à jour | Texte noir, fond blanc |
| Modifié | Valeur changée non sauvegardée | Texte bleu, pastille "Non sauvegardé" |
| Erreur | Valeur invalide | Texte rouge, message d'erreur |
| Bloqué | Rôle insuffisant | Champ grisé, cadenas 🔒 |

### Bouton de test API BCC

| État | Affichage |
|------|-----------|
| Prêt | [Tester la connexion] |
| Test en cours | Spinner + "Vérification..." |
| ✅ Succès | ✅ Connecté (taux : 2 850,00) |
| ❌ Échec | ❌ Connexion impossible (vérifiez l'URL) |
