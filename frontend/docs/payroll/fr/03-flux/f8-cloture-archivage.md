# F8 — Clôture et Archivage (flux transverse)

> **Écrans impliqués :** S3 (Run Détail) → S1 (Liste exécutions)
> **Déclencheur :** Run en statut **PAID** ou **COMPLETED** nécessitant clôture

---

## Résumé

Flux de clôture et d'archivage d'un cycle de paie. Intervient après le paiement (F1) ou après une correction définitive (F5).  
Une fois clôturé, le run est **verrouillé en lecture seule** et ses données sont figées pour conservation légale.

---

## Types de clôture

| Type | Quand | Effet |
|------|-------|-------|
| **Clôture normale** | Après marquage PAYÉ | Verrouillage + archivage + mise à jour historique |
| **Clôture corrective** | Après F5 (correction validée) | Run recalculé verrouillé, l'original gardé en trace |
| **Clôture forcée** | Décision manuelle (super-admin) | Verrouillage immédiat même si anomalies résiduelles |

---

## Diagramme de flux

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      FLUX DE CLÔTURE ET ARCHIVAGE                        │
└──────────────────────────────────────────────────────────────────────────┘

                         DÉCLENCHEUR
                              │
                              ▼
                     ┌──────────────────────┐
                     │   Run en PAID ou     │
                     │   COMPLETED          │
                     └──────────┬───────────┘
                                │
               ┌────────────────┴────────────────┐
               │                                 │
               ▼                                 ▼
    ┌──────────────────────┐        ┌──────────────────────┐
    │  Clôture automatique │        │  Clôture manuelle    │
    │  (via S3 → bouton    │        │  (via S8 ou S1 →     │
    │   "Clôturer")        │        │   Action "Forcer     │
    └──────────┬───────────┘        │   clôture")          │
               │                    └──────────┬───────────┘
               │                               │
               └───────────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  VÉRIFICATIONS       │
                    │  PRÉ-CLÔTURE         │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
        ┌──────────────────┐    ┌──────────────────────┐
        │  Échec           │    │  OK                  │
        │  → Blocage       │    │  → Run figé          │
        │  → Message       │    │  → Statut : CLOSED   │
        └──────────────────┘    └──────────┬───────────┘
                                           │
                               ┌───────────┴───────────┐
                               │                       │
                               ▼                       ▼
                    ┌──────────────────┐    ┌──────────────────────┐
                    │  ARCHIVAGE       │    │  HISTORIQUE COMPTABLE│
                    │  → Export S3/S4  │    │  → Mise à jour des   │
                    │  → Conservation  │    │    cumuls annuels    │
                    │    légale        │    │  → Compteur ONEM     │
                    └──────────┬───────┘    └──────────┬───────────┘
                               │                       │
                               └───────────┬───────────┘
                                           │
                                           ▼
                               ┌──────────────────────┐
                               │  RETOUR S1           │
                               │  → Run affiché comme │
                               │    "CLOSED" (lecture │
                               │    seule possible)   │
                               └──────────────────────┘
```

---

## Rôles impliqués

| Étape | Rôle | Actions |
|-------|------|---------|
| Déclenchement | Gestionnaire paie | Bouton "Clôturer" sur S3 |
| Forçage | Super-admin / Chef comptable | Dérogation via S8 |
| Vérifications | Système (automatique) | Tests pré-clôture |
| Archivage | Système | Export + stockage |
| Historique | Système | Mise à jour des cumuls |

---

## Vérifications pré-clôture

| # | Vérification | Comportement si échec |
|---|-------------|-----------------------|
| 1 | Tous les bulletins sont-ils **CALCULÉS** ou **PAYÉS** ? | Blocage : bulletins en DRAFT ou ERROR |
| 2 | Y a-t-il des corrections en cours (F5) ? | Blocage : attendre validation correction |
| 3 | Le paiement est-il confirmé (hors système) ? | Avertissement uniquement |
| 4 | Les avances (S6) sont-elles toutes soldées ? | Blocage si avances non remboursées |
| 5 | La période comptable est-elle ouverte ? | Blocage si période clôturée en compta |
| 6 | Les exports DSN/DEC sont-ils générés ? | Avertissement si export manquant |

---

## Archivage des données

| Donnée | Durée légale (RDC) | Format |
|--------|-------------------|--------|
| Bulletins de paie | 5 ans | PDF + JSON structuré |
| Registre de paie | 5 ans | CSV/Excel |
| Contrats et avenants | 5 ans après fin contrat | PDF |
| Déclarations ONEM/CNSS | 10 ans | PDF + XML |
| Calculs et historiques | 3 ans | JSON compressé |

---

## Structure des exports d'archivage

```
exports/payroll/{year}/{period}/
├── bulletins/
│   ├── 2026-06-bulletin-EMP001.pdf
│   ├── 2026-06-bulletin-EMP002.pdf
│   └── ...
├── registre/
│   └── 2026-06-registre-paie.csv
├── declarations/
│   ├── 2026-06-onem.xml
│   └── 2026-06-cnss.xml
├── calculs/
│   └── 2026-06-run-data.json
└── MANIFEST.json
```

---

## Règles de clôture

| # | Règle |
|---|-------|
| 1 | Une clôture est **irréversible**. Pour corriger un bulletin clôturé, passer par **F5 Correction** avec création d'un nouveau run correctif |
| 2 | Un run **CLOSED** interdit toute modification : variables, éléments contrat, taux |
| 3 | L'export d'archivage est généré **automatiquement** à la clôture |
| 4 | Si l'export échoue, le run reste en **CLOSING_ERROR** — une action manuelle est requise |
| 5 | Seul un utilisateur avec le rôle **super-admin** peut forcer une clôture |
| 6 | La clôture mise à jour les **cumuls annuels** (IRPP, CNSS, ONEM) pour les employés du run |

---

## Gestion des erreurs

```
Clôture automatique :
├── Succès → Run CLOSED, export généré
├── Échec vérif. 1, 2, 4, 5 → Blocage, message explicite
└── Échec vérif. 3, 6 → Avertissement, clôture possible

Clôture forcée :
├── Forçage par super-admin
├── Run CLOSED même si anomalies
└── Motif obligatoire (traçabilité)

Échec export :
├── Run en CLOSING_ERROR
├── Export réessayable depuis S3
└── Si impossible → export manuel via S1
```
