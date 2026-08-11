# F3 — Modification du Taux de Change

> **Écrans impliqués :** S3 (aperçu taux), S2 (création), S8 (configuration), `exchange-rates.md`

---

## Contexte

Le taux de change CDF/USD peut changer en cours de cycle. Ce flux décrit comment le gestionnaire gère une modification de taux :

**Déclencheurs :**
1. Nouveau taux BCC (mise à jour automatique quotidienne)
2. Saisie manuelle (week-end, panne API BCC)
3. Correction manuelle d'un taux qui a changé après création du run

---

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────────────────┐
│           MODIFICATION DU TAUX DE CHANGE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ DÉTECTION│  Le système détecte un nouveau taux BCC (2 860,00 au lieu de
│ TAUX     │  2 850,00) ou le gestionnaire le saisit manuellement
└─────┬────┘
      │
      ▼
┌──────────┐
│ S3 / S2  │  Selon l'endroit où se trouve l'utilisateur :
│          │
│ S2       │  → Le taux est sélectionné à la création du run
│ (Créa)   │  → La pastille BCC est VERTE (taux frais)
│          │
│ S3       │  → Le run existe déjà, taux FROZEN
│ (Détail) │  → Une alerte s'affiche :
└─────┬────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  Nouveau taux BCC disponible : 2 860,00 CDF/USD (actuel : 2 850,00)     │
│  Le taux actuel est gelé au moment de la création du run. Tout changement   │
│  modifiera les montants en USD pour ce cycle.                               │
│                                                                             │
│  [🔒 Conserver le taux actuel (2 850,00)]  [🔄 Appliquer le nouveau taux]  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ Si "Appliquer le nouveau taux" :
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔄 Application du nouveau taux                                             │
│                                                                             │
│  Nouveau taux : 2 860,00 CDF/USD (+0,35 %)                                  │
│                                                                             │
│  Impact estimé sur le run :                                                 │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │  Employés concernés : 12 (contrats USD)                           │      │
│  │  Variation brute totale : +14 200 CDF                             │      │
│  │  Variation nette totale : +11 800 CDF                             │      │
│  │                                                                   │      │
│  │  3 bulletins passeront en DRAFT (recalcul nécessaire)             │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│  [Annuler]    [Confirmer le changement de taux]                             │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────┐
│ IMPACT   │  1. Le taux du run est mis à jour
│          │  2. Les bulletins des employés concernés passent en DRAFT
│          │  3. Le gestionnaire doit recalculer (S3 → Lancer calcul)
│          │  4. L'audit trail enregistre le changement
└──────────┘
```

---

## Règles

| # | Règle |
|---|-------|
| 1 | Le taux est **gelé** à la création du run pour garantir l'auditabilité |
| 2 | La modification du taux **après** création est un événement d'audit tracé |
| 3 | Seuls les bulletins **impactés** (employés avec contrat USD) passent en DRAFT |
| 4 | Si le run est déjà PAYÉ, le taux ne peut plus être modifié |
| 5 | Le changement de taux déclenche une **notification** aux gestionnaires concernés |

## États du taux dans le run

| État | Icône | Description |
|------|-------|-------------|
| Frozen (intact) | 🔒 | Taux BCC au moment de la création, jamais modifié |
| Frozen (modifié) | 🔓 | Taux modifié après création, tracé dans l'audit |
| Manuel | ✏️ | Taux saisi manuellement (fallback) |
| Erreur | ❌ | Taux manquant, blocage |

## Cas particuliers

| Cas | Comportement |
|-----|-------------|
| Plusieurs modifications | Seul le dernier changement est conservé, l'historique est tracé |
| Run déjà calculé | Tous les bulletins passent en DRAFT → recalcul nécessaire |
| Run PAYÉ | Refus de modification (le verrouillage est définitif) |
| Taux BCC indisponible | Fallback automatique (cf. S8 Configuration) |
