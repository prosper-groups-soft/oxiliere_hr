# S10 — Éléments de Paie du Contrat

> **Dépendances :** `catalogue.md` (bibliothèque d'éléments), `metamodel.md` (contrat)

---

## Contexte

L'écran **Éléments de Paie du Contrat** permet d'associer des éléments de paie (primes, indemnités, avantages) à un contrat employé. 
C'est la **définition** de ce qui sera appliqué automatiquement à chaque cycle.

Contrairement à S5 (variables saisies manuellement à chaque cycle), ici on définit des **éléments récurrents** qui sont automatiquement inclus dans le calcul de chaque bulletin.

> Exemple : un contrat peut avoir "Indemnité de logement : 270 000 CDF" en élément permanent, et "Prime de performance : variable" qui sera saisi en S5 chaque mois.

---

## Wireframe ASCII — Éléments de paie d'un contrat

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Employés  /  Jean Mbemba  /  Éléments de paie                            │
│                                                                             │
│  📋 ÉLÉMENTS DE PAIE · Jean Mbemba (EMP-0042)                               │
│  Contrat : CDI - Classe 4 Éch. 3 - Département Production                   │
│                                                                             │
│  ──── Éléments récurrents ──────────────────────────────────                │
│                                                                             │
│  Actif │ Élément                    Type         Montant      Cycle         │
│  ──────┼───────────────────────────────────────────────────────────         │
│  ☑     │ Indemnité de logement      Fixe         270 000 CDF  Mensuel       │
│  ☑     │ Indemnité de transport     Fixe         100 000 CDF  Mensuel       │
│  ☑     │ Prime de panier            Quantité    2 500/jour    Mensuel       │
│  ☐     │ Assurance médicale         Fixe         150 000 CDF  Mensuel       │
│                                                                             │
│  [+ Ajouter un élément]                                                     │
│                                                                             │
│  ──── Éléments variables (saisie en S5) ────────────────────                │
│                                                                             │
│  Actif │ Élément                     Interv.      Défaut                    │
│  ──────┼───────────────────────────────────────────────────────────         │
│  ☑     │ Prime de performance         Mensuel      0 CDF                    │
│  ☑     │ Heures supplémentaires       Mensuel      0 heures                 │
│  ☑     │ Avance sur salaire           Mensuel      0 CDF                    │
│                                                                             │
│  ──── Résumé contrat ───────────────────────────────────────                │
│                                                                             │
│  Salaire de base      : 5 700 000 CDF (2 000 USD × 2 850,00)                │
│  Total éléments fixes : 370 000 CDF                                         │
│  Brut mensuel estimé  : 6 070 000 CDF                                       │
│  ------------------------------------------------------------------------   │
│  [Sauvegarder]     [Réinitialiser aux valeurs par défaut]                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Wireframe ASCII — Ajout d'un élément

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Ajouter un élément de paie                                                 │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────      │
│                                                                             │
│  Élément : [Rechercher dans le catalogue... ▼]                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Résultats                                                          │    │
│  │  💰 Prime de performance              · Variable · Non imposable    │    │
│  │  🛡️ Assurance médicale                · Fixe    · Non imposable     │    │
│  │  🏠 Indemnité de logement             · Fixe    · Imposable         │    │
│  │  ...                                                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Type de valeur : [Fixe ▼]                                                  │
│  Montant : [270 000] CDF                                                    │
│  Fréquence : [Mensuel ▼]                                                    │
│  Début d'application : [Juin 2026 ▼]                                        │
│  Fin d'application : [---] (optionnel)                                      │
│                                                                             │
│  Notes : [Indemnité selon convention collective]                            │
│                                                                             │
│  [Annuler]    [Ajouter]                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Zones fonctionnelles

| Zone | Description | Contenu |
|------|-------------|---------|
| **En-tête contrat** | Identification | Nom, matricule, type contrat, classe, département |
| **Éléments récurrents** | Liste des éléments fixes | Cases à cocher, type, montant, cycle |
| **Éléments variables** | Liste des éléments à saisir en S5 | Type, intervalle, valeur par défaut |
| **Résumé** | Estimation du brut mensuel | Salaire de base + fixes = brut estimé |
| **Ajout d'élément** | Modale de sélection | Recherche catalogue, paramètres |

---

## Composants UI proposés

### `ContractPayElementList.svelte`

Liste des éléments associés à un contrat.

```svelte
<script lang="ts">
  type ContractPayElement = {
    id: string;
    elementCode: string;
    elementLabel: string;
    valueType: "fixed" | "quantity" | "percentage" | "variable";
    amount?: number;
    quantity?: number;
    recurrence: "monthly" | "quarterly" | "yearly" | "one-time";
    active: boolean;
    startPeriod: string;
    endPeriod?: string;
  };

  let {
    contractElements = [] as ContractPayElement[],
    onToggleActive = (id: string, active: boolean) => {},
    onAdd = () => {},
    onRemove = (id: string) => {},
    onSave = () => Promise<void>,
  } = $props();
</script>
```

### `PayElementPickerModal.svelte`

Modale de sélection d'un élément de paie depuis le catalogue.

```svelte
<script lang="ts">
  type CatalogElement = {
    code: string;
    label: string;
    description: string;
    valueType: string;
    isTaxable: boolean;
    category: string;
  };

  let {
    show = false,
    catalog = [] as CatalogElement[],
    onSelect = (element: CatalogElement) => {},
    onClose = () => {},
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/contracts/{id}/pay-elements` | `GET` | Liste des éléments du contrat |
| `/payroll/contracts/{id}/pay-elements` | `POST` | Ajouter un élément |
| `/payroll/contracts/{id}/pay-elements/{elem_id}` | `PATCH` | Modifier un élément |
| `/payroll/contracts/{id}/pay-elements/{elem_id}` | `DELETE` | Supprimer un élément |
| `/payroll/catalog` | `GET` | Catalogue complet des éléments |
| `/payroll/catalog?search=...` | `GET` | Recherche dans le catalogue |

### Réponse `ContractPayElementListOut`

```json
{
  "contract_id": "uuid",
  "employee": {
    "id": "uuid",
    "name": "Jean Mbemba",
    "matricule": "EMP-0042"
  },
  "contract_type": "CDI",
  "base_salary": 5700000,
  "elements": [
    {
      "id": "uuid",
      "catalog_code": "INDEM_LOGEMENT",
      "label": "Indemnité de logement",
      "value_type": "fixed",
      "amount": 270000,
      "is_active": true,
      "is_taxable": true,
      "recurrence": "monthly",
      "start_period": "2026-01",
      "end_period": null
    }
  ],
  "estimated_gross": 6070000
}
```

---

## Règles d'interaction

| # | Règle | Justification |
|---|-------|---------------|
| 1 | Un élément peut être **désactivé** temporairement sans être supprimé | Audit trail |
| 2 | La date de fin d'application désactive automatiquement l'élément au cycle concerné | Automatisation |
| 3 | Seuls les éléments marqués `is_active` sont inclus dans le calcul | Précision |
| 4 | La suppression d'un élément demande **confirmation** avec motif | Sécurité |
| 5 | Un élément **non imposable** est marqué visuellement (🛡️) | Transparence |
| 6 | Les éléments variables (`value_type: "variable"`) ont un **montant par défaut** qui sera proposé en S5 | Productivité |

---

## Types de valeur

| Type | Description | Exemple | Saisie |
|------|-------------|---------|--------|
| `fixed` | Montant fixe chaque cycle | Indemnité de logement | Automatique |
| `quantity` | Basé sur une quantité (jours, unités) | Prime panier | S5 |
| `percentage` | Pourcentage du salaire de base | Commission | S5 |
| `variable` | Montant libre saisi à chaque cycle | Prime performance | S5 |

---

## Synchronisation avec la création du contrat

Idéalement, cet écran est accessible depuis :

1. **Module Employés** → Contrat → Éléments de paie (configuration initiale)
2. **Module Paie** → S1 Liste exécutions → Accès rapide "Éléments de paie"
3. **Lien direct** depuis S3 / S4 pour modification en cours de cycle (avec marquage DRAFT)
