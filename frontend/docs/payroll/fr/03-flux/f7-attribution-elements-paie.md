# F7 — Attribution des Éléments de Paie à un Contrat

> **Écrans impliqués :** S10 (éléments contrat), S8 (catalogue), `catalogue.md`

---

## Contexte

Lorsqu'un employé est embauché (ou qu'un contrat est modifié), le gestionnaire doit lui **attribuer ses éléments de paie** : primes, indemnités, avantages. C'est ce qui déterminera le calcul automatique des bulletins.

Deux cas d'usage :
1. **Nouvel employé** : configuration initiale des éléments
2. **Changement de contrat** : ajout/retrait/modification d'éléments

---

## Diagramme de flux — Nouvel employé

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            ATTRIBUTION DES ÉLÉMENTS DE PAIE (nouvel employé)                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ EMPLOYÉ  │  Création du contrat dans le module Employés
│ CRÉÉ     │  → Salaire de base : 2 000 000 CDF
└─────┬────┘  → Classe : 3, Échelon : 2
      │       → Département : Production
      │
      ▼
┌──────────┐
│ S10      │  Le gestionnaire ouvre la page Éléments de paie
│ ACCUEIL  │  → Liste vide (aucun élément attribué)
└─────┬────┘  → Message : "Aucun élément de paie configuré"
      │       → [Ajouter un élément]
      │
      ▼
┌──────────┐
│ S10      │  Recherche dans le catalogue
│ AJOUT    │  → Tape "indemnité" dans la barre de recherche
└─────┬────┘  → Sélectionne "Indemnité de logement"
      │       → Configure : Fixe · 200 000 CDF · Mensuel
      │       → [Ajouter]
      │
      ▼
┌──────────┐
│ S10      │  L'élément apparaît dans la liste
│ LISTE    │  → Active par défaut
└─────┬────┘  → Date début : mois en cours
      │
      ▼
┌──────────┐
│ SUITE    │  Répéter pour chaque élément :
│ ÉLÉMENTS │  → Prime transport : 80 000 CDF
│          │  → Prime panier : 2 500 CDF/jour
│          │  → Assurance médicale : 150 000 CDF
└──────────┘
```

---

## Diagramme de flux — Changement de contrat

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            MODIFICATION DES ÉLÉMENTS (changement de contrat)               │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────┐
│ EMPLOYÉ  │  Jean Mbemba change de classe (Classe 4 → Classe 5)
│ PROMOTION│  → Le salaire de base passe de 5 700 000 à 7 200 000 CDF
└─────┬────┘
      │
      ▼
┌──────────┐
│ S10      │  Le gestionnaire ouvre S10
│ LISTE    │  → Les éléments existants sont visibles
└─────┬────┘
      │
      ├──────────────────────────────────────────────┐
      │                                              │
      ▼                                              ▼
┌────────────┐                              ┌────────────┐
│ MODIFIER   │                              │ AJOUTER    │
│ EXISTANT   │                              │ NOUVEAU    │
│            │                              │            │
│ Ex: Prime  │                              │ Ex: Voiture│
│ logement   │                              │ de fonction│
│ 270 000 →  │                              │ 350 000 CDF│
│ 320 000 CDF│                              │            │
└─────┬──────┘                              └─────┬──────┘
      │                                              │
      └──────────┬───────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  Les modifications suivantes impacteront le prochain cycle de paie :    │
│                                                                             │
│  • Indemnité logement : 270 000 → 320 000 CDF (+50 000 CDF)                 │
│  • Voiture de fonction : Nouvel élément (350 000 CDF)                       │
│  • Suppression : Prime transport (100 000 CDF)                              │
│                                                                             │
│  Impact net estimé : +300 000 CDF / mois                                    │
│                                                                             │
│  [Annuler]    [Appliquer les changements]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────┐
│ S10      │  ✅ Modifications enregistrées
│ TERMINÉ  │  → Les nouveaux éléments seront actifs à partir du prochain cycle
└──────────┘  → Les cycles passés ne sont pas impactés
```

---

## Règles

| # | Règle |
|---|-------|
| 1 | L'ajout d'un élément est effectif à partir du **prochain cycle** (sauf rétroactif explicite) |
| 2 | La suppression d'un élément l'est aussi à partir du prochain cycle |
| 3 | Un élément peut avoir une **date de fin** planifiée (ex: prime sur 3 mois) |
| 4 | La modification en cours de cycle marque le bulletin DRAFT si déjà calculé |
| 5 | Les éléments inactifs sont conservés dans l'historique du contrat |

---

## Actions rapides

| Action | Comportement |
|--------|-------------|
| Désactiver un élément | L'élément n'est plus inclus dans le calcul mais reste visible |
| Dupliquer un élément | Crée une copie avec les mêmes paramètres |
| Appliquer à plusieurs contrats | Reporté au mode groupé (S5 étendu) |
| Planifier une fin | L'élément se désactive automatiquement à la date choisie |

---

## Cas particuliers

| Cas | Comportement |
|-----|-------------|
| Élément rétroactif | Appliqué au cycle en cours (si pas PAYÉ) ou bulletin rectificatif |
| Élément expiré | L'élément passe en inactif automatiquement, notification au gestionnaire |
| Conflit de période | Deux éléments de même type sur la même période → validation demande clarification |
| Contrat suspendu | Les éléments sont automatiquement désactivés pendant la suspension |

