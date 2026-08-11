# F2 — Embauche en Cours de Période

> **Écrans impliqués :** S3 (run existant), S5 (saisie variables), S10 (éléments contrat)

---

## Contexte

Un employé est embauché en cours de mois (ex : 15/06/2026 pour un cycle Juin). Le gestionnaire doit :

1. Créer ou rattacher l'employé au cycle existant
2. Calculer le **prorata temporis** des éléments de paie
3. Saisir les variables spécifiques à cette entrée en cours de période

---

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                EMBauche EN COURS DE PÉRIODE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ EMPLOYÉ  │  Le module Employés crée le contrat de Jean (CDI, Classe 3)
│ CRÉATION │  → Date d'entrée : 15/06/2026
└─────┬────┘  → Salaire : 2 000 000 CDF
      │
      ▼
┌──────────┐
│ S10      │  Configuration des éléments de paie du contrat
│ ÉLÉMENTS │  → Indemnité logement : 200 000 CDF
│ CONTRAT  │  → Prime transport : 80 000 CDF
└─────┬────┘  → Ces éléments s'appliqueront au prorata
      │
      ▼
┌──────────┐
│ S3       │  Le gestionnaire ouvre le run Juin 2026
│ DÉTAIL   │  → L'employé apparaît dans la liste
│ RUN      │  
└─────┬────┘  ⚠️  Avec un badge "Entrée 15/06" (prorata)
      │
      ▼
┌──────────┐
│ S5       │  Saisie des variables
│ SAISIE   │  → Les champs sont pré-remplis avec le prorata
└─────┬────┘  → Jours travaillés : 12 (sur 21 jours ouvrés)
      │       → Salaire de base proratisé : 2 000 000 × 12/21 = 1 142 857 CDF
      │       → Indemnités au prorata également
      │
      ▼
┌──────────┐
│ S7       │  Validation
│ VALIDA   │  → Anomalie "ENTREE_COURS" levée (info, non bloquante)
└─────┬────┘  → Affiche la date d'entrée pour traçabilité
      │
      ▼
┌──────────┐
│ PIPELINE │  → Calcul normal
│ CALCUL   │  → Utilise les valeurs proratisées
└──────────┘
```

---

## Règles de prorata

| Élément | Règle de prorata | 
|---------|-----------------|
| Salaire de base | `brut_mensuel × (jours_travaillés / jours_ouvrés)` |
| Indemnités fixes | `montant × (jours_travaillés / jours_ouvrés)` |
| Prime panier | `montant × jours_travaillés` (quantité réelle) |
| CNSS | Sur le salaire brut réel (pas de prorata supplémentaire) |
| IPR | Calculé sur le brut imposable réel (le barème s'applique normalement) |
| Avances | Non concernées (hors cycle) |
| HS | Basées sur les heures réellement effectuées |

### Calcul détaillé

```
Données :
- Salaire mensuel : 2 000 000 CDF
- Date d'entrée : 15/06/2026
- Jours ouvrés en Juin : 21
- Jours travaillés (15/06 → 30/06) : 12 jours ouvrés

Prorata salaire : 2 000 000 × (12 / 21) = 1 142 857 CDF
Prorata indem. logement : 200 000 × (12 / 21) = 114 286 CDF
```

---

## Affichage dans S3 (Run Detail)

L'employé apparaît dans la liste avec des badges spécifiques :

```
Badge   Signification
─────── ────────────────────────────────────────
🆕      Nouvel embauché sur ce cycle (1er bulletin)
📅 15/6 Entrée en cours de période (prorata appliqué)
```

---

## Cas particuliers

| Cas | Comportement |
|-----|-------------|
| Entrée le 1er jour du mois | Pas de prorata (cycle complet) |
| Entrée après le 25 | Report au cycle suivant (saisie impossible) |
| Salaire en USD | Conversion au taux du run, puis prorata en CDF |
| Contrat avec plusieurs éléments | Chaque élément fixe est proratisé |
| Changement de classe en cours de mois | Deux lignes de paie (avant/après) |

