# S9 — États et Rapports

> **Dépendances :** `s3-detail-run.md` (données sources), `s4-fiche-de-paie.md` (détail employé), `s7-validation.md` (pré-validation)

---

## Contexte

L'écran **États et Rapports** donne accès à l'ensemble des **documents exportables** et **analyses** du module paie :

- Rapports comptables (journal de paie, grand livre, balances)
- Documents légaux (CNSS, IPR, ONEM, INPP)
- Statistiques de gestion (évolution masse salariale, distribution)
- Exports bruts (Excel, CSV) pour analyse

Le gestionnaire peut :
1. **Générer** un rapport à la demande
2. **Planifier** une génération automatique (ex: 1er du mois)
3. **Télécharger** un rapport déjà généré
4. **Comparer** deux périodes

---

## Wireframe ASCII

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📊 États et Rapports    Période : [Juin 2026 ▼]    Cycle : [Tous ▼]        │
│                                                                             │
│  ──── Rapports comptables ────────────────────────────────────              │
│                                                                             │
│  Rapport                   Dernière génération      Actions                 │
│  Journal de paie           28/06/2026 15:30         [📄 PDF] [📊 Excel]     │
│  Balance des salaires      28/06/2026 15:30         [📄 PDF] [📊 Excel]     │
│  Grand livre des salaires  28/06/2026 15:30         [📄 PDF] [📊 Excel]     │
│  Écritures comptables      —                        [📊 Générer]            │
│                                                                             │
│  ──── Déclarations légales ─────────────────────────────────                │
│                                                                             │
│  Rapport                   Période                  Statut     Actions      │
│  CNSS (feuille de salaire) Juin 2026                ✅ Généré  [📄 PDF]     │
│  IPR (déclaration mensuelle) Juin 2026              ✅ Généré  [📄 PDF]     │
│  ONEM                      Juin 2026                ⏳ En attente           │
│  INPP                      Juin 2026                ⏳ En attente           │
│                                                                             │
│  ──── Statistiques ─────────────────────────────────────────                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  📈 Évolution masse salariale (6 mois)                                │  │
│  │                                                                       │  │
│  │  Jan   Fév   Mar   Avr   Mai   Juin                                   │  │
│  │  ██    ███   ██    ███   ███   █████                                  │  │
│  │  37M   41M   38M   42M   39M   42M  (brut total)                      │  │
│  │                                                                       │  │
│  │  Variation M-1 : +7,7 %  ·  Cumul annuel : 239 M CDF                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  🥧 Distribution par classe                                           │  │
│  │                                                                       │  │
│  │  Classe 1  ████████████░░░░░░░  25 employés (14,6 M)                  │  │
│  │  Classe 2  ██████████████░░░░░  10 employés (10,2 M)                  │  │
│  │  Classe 3  ██████████████████░   5 employés (8,4 M)                   │  │
│  │  Classe 4  ████████████████████   3 employés (6,0 M)                  │  │
│  │  Classe 5  ████████████████████   2 employés (3,0 M)                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Téléchargement en cours : [████████░░░░░░░] 65 % - journal_paie_juin2026.xlsx │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Types de rapports

### Rapports comptables

| Rapport | Contenu | Format | Fréquence |
|---------|---------|--------|-----------|
| **Journal de paie** | Lignes individuelles par employé (brut, déductions, net) | PDF, Excel | Mensuelle |
| **Balance des salaires** | Totaux par compte comptable | PDF, Excel | Mensuelle |
| **Grand livre des salaires** | Détail par compte (débit/crédit) | PDF, Excel | Mensuelle |
| **Écritures comptables** | Export pour import dans le logiciel compta | CSV/OFX | Mensuelle |

### Déclarations légales

| Rapport | Destinataire | Format | Échéance |
|---------|-------------|--------|----------|
| **CNSS** (feuille de salaire) | CNSS | PDF (formulaire officiel) | 15 du mois |
| **IPR** (déclaration mensuelle) | DGI | PDF | 15 du mois |
| **ONEM** | ONEM | PDF | Mensuelle |
| **INPP** | INPP | PDF | Mensuelle |

### Statistiques

| Rapport | Usage |
|---------|-------|
| **Évolution masse salariale** | Analyse budgétaire (6 derniers mois) |
| **Distribution par classe** | Structure des coûts |
| **Comparaison périodes** | Analyse des variations |
| **Top N employés** | Les plus hauts / bas salaires |

---

## Composants UI proposés

### `ReportCard.svelte`

Carte d'un rapport avec statut et actions.

```svelte
<script lang="ts">
  type Report = {
    code: string;
    label: string;
    category: "accounting" | "legal" | "statistics";
    lastGenerated?: string;
    status: "available" | "pending" | "generating" | "never";
    formats: ("pdf" | "xlsx" | "csv")[];
  };

  let {
    report = {} as Report,
    onGenerate = (format: string) => {},
    onDownload = (format: string) => {},
  } = $props();
</script>
```

### `PayrollChart.svelte`

Graphique simple (barres, lignes, camembert) pour les statistiques.

```svelte
<script lang="ts">
  type ChartData = {
    labels: string[];
    datasets: { label: string; values: number[]; color: string }[];
  };

  let {
    type = "bar" as "bar" | "line" | "pie",
    data = {} as ChartData,
    height = 300,
  } = $props();
</script>
```

### `ReportHistoryPanel.svelte`

Historique des générations passées.

```svelte
<script lang="ts">
  type ReportLog = {
    id: string;
    reportCode: string;
    period: string;
    format: string;
    generatedAt: string;
    generatedBy: string;
    size: string; // "2.3 MB"
    checksum?: string;
  };

  let {
    logs = [] as ReportLog[],
    onDownload = (logId: string) => {},
  } = $props();
</script>
```

---

## API associée

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/payroll/reports` | `GET` | Liste des rapports disponibles |
| `/payroll/reports/{code}/generate` | `POST` | Générer un rapport |
| `/payroll/reports/{code}/download?format=pdf` | `GET` | Télécharger un rapport |
| `/payroll/reports/{code}/history` | `GET` | Historique des générations |
| `/payroll/reports/schedule` | `GET` | Planification des rapports |
| `/payroll/reports/schedule` | `POST` | Créer une planification |
| `/payroll/reports/schedule/{id}` | `DELETE` | Supprimer une planification |

### Réponse `ReportListOut`

```json
{
  "items": [
    {
      "code": "JOURNAL_PAIE",
      "label": "Journal de paie",
      "category": "accounting",
      "last_generated": "2026-06-28T15:30:00Z",
      "status": "available",
      "formats": ["pdf", "xlsx"]
    }
  ],
  "pending_generations": [
    { "code": "ECRITURES_COMPTA", "progress_pct": 65, "format": "csv" }
  ]
}
```

---

## États visuels

### Carte de rapport

| État | Déclencheur | Affichage |
|------|-------------|-----------|
| Disponible | Rapport déjà généré | Fond vert, [📄 Télécharger] |
| En attente | Jamais généré pour cette période | Fond gris, [📊 Générer] |
| En cours | Génération en cours | Barre de progression + [⏳] |
| Erreur | Échec de génération | Fond rouge, ❌ Erreur, [Réessayer] |

### Barre de téléchargement

| État | Affichage |
|------|-----------|
| Inactif | Masquée |
| En cours | Barre de progression + pourcentage + nom fichier |
| Terminé | ✅ Téléchargement terminé (auto-fade 3s) |
| Échec | ❌ Échec du téléchargement. [Réessayer] |

---

## Génération asynchrone

Les rapports lourds (ex: journal de paie 500 employés sur 12 mois) sont générés **de manière asynchrone** :

1. L'utilisateur clique "Générer"
2. Le backend crée une tâche et retourne un `task_id`
3. Le frontend affiche la progression via polling ou WebSocket
4. Une notification (son + toast) signale la fin de génération
5. L'utilisateur peut quitter la page et revenir plus tard

```
📊 Génération du journal de paie...
[████████░░░░░░░] 65 %

Vous pouvez quitter cette page, la génération continue en arrière-plan.
Vous recevrez une notification quand le rapport sera prêt.
```
