# Gestion de projet

> **Pratiques d'organisation** pour planifier, suivre et livrer le travail en équipe, en lien avec les documents de conception.

> ⚠️ **Document organisationnel** — Il ne décrit pas une technique de développement, mais la manière dont l'équipe s'organise pour appliquer les autres méthodes.

---

## Quickstart

```
1. Un besoin métier est identifié → Issue dans le backlog
2. L'issue est liée au document de conception concerné
3. Priorisation → Sprint planning → Développement → Review → Release
4. La documentation de conception est mise à jour si nécessaire
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Artefacts de projet](#2-artefacts-de-projet)
3. [Le backlog](#3-le-backlog)
4. [Les sprints](#4-les-sprints)
5. [Estimation et priorisation](#5-estimation-et-priorisation)
6. [Relation entre conception et tickets](#6-relation-entre-conception-et-tickets)
7. [Suivi d'avancement](#7-suivi-davancement)
8. [Réunions et rythme](#8-réunions-et-rythme)
9. [Anti-patterns](#9-anti-patterns)

---

## 1. Philosophie

> **La gestion de projet est au service de la conception, pas l'inverse.**

Nos principes :

1. **La conception guide la priorisation** — On ne commence pas une feature sans comprendre où elle se place dans la carte des sous-systèmes.
2. **Les tickets décrivent le problème, pas la solution** — La solution est dans les documents de conception.
3. **Le rythme est régulier** — Mieux vaut des livraisons petites et fréquentes que des gros lots espacés.
4. **L'équipe s'auto-organise** — Le PO fixe les priorités métier, l'équipe décide comment implémenter.

---

## 2. Artefacts de projet

### 2.1 Issues

Chaque élément de travail est une issue, avec :

```markdown
## Titre
[Concis, verbe d'action]

## Description
### Contexte
Pourquoi cette issue existe ?

### Comportement attendu
Ce qui doit se passer quand l'issue est résolue.

### Critères d'acceptation
- [ ] Critère 1
- [ ] Critère 2

### Liens
- Document de conception : [lien]
- Issues liées : #42, #57
```

### 2.2 Labels

| Label | Signification |
|-------|---------------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `enhancement` | Amélioration d'existant |
| `tech-debt` | Dette technique |
| `documentation` | Documentation |
| `security` | Sécurité |
| `blocked` | Bloqué par une dépendance externe |
| `good-first-issue` | Pour les nouveaux contributeurs |

### 2.3 Milestones

Les milestones correspondent aux versions (SemVer) :

```
v1.0.0 — MVP
v1.1.0 — Notifications
v2.0.0 — Refonte workflow
```

---

## 3. Le backlog

### 3.1 Structure

```
Backlog (toutes les issues)
├── 🎯 Sprint en cours
├── ⏳ Prochains sprints (priorisées)
├── 📋 À prioriser
└── 💤 Icebox (idées, pas encore priorisées)
```

### 3.2 Règles

- **Le backlog est vivant** — Révisé régulièrement (triage hebdomadaire)
- **Pas d'issue sans description** — Un titre ne suffit pas
- **Les issues trop grosses sont découpées** — Si une issue dure plus d'un sprint, la découper
- **Les issues orphelines sont supprimées** — Si personne ne comprend à quoi elle sert, la fermer

---

## 4. Les sprints

### 4.1 Rythme

| Durée | Rituels |
|-------|---------|
| **2 semaines** | Planning (1h) → Dev → Review (30min) → Rétro (30min) |

### 4.2 Sprint planning

- L'équipe sélectionne les issues du backlog, par ordre de priorité
- Chaque issue est estimée et assignée
- L'équipe s'engage sur un périmètre réaliste
- Les issues doivent être **prêtes** : décrites, estimées, non-bloquées

### 4.3 Sprint review

- Démo des fonctionnalités livrées
- Le PO valide ou ajuste
- Mise à jour du backlog si nécessaire

### 4.4 Rétrospective

- Ce qui a bien fonctionné
- Ce qui peut être amélioré
- Actions concrètes pour le prochain sprint

---

## 5. Estimation et priorisation

### 5.1 Estimation

Utiliser la **taille relative** (story points), pas le temps :

| Taille | Story points | Exemple |
|--------|-------------|---------|
| 🐣 Très petite | 1 | Correction de typo, changement de config |
| 🐥 Petite | 2 | Ajout d'un champ dans un formulaire |
| 🐔 Moyenne | 3-5 | Nouvelle fonctionnalité simple |
| 🦅 Grande | 8-13 | Nouveau sous-système complet |
| 🐉 Trop grande | > 13 | À découper |

### 5.2 Priorisation

**Matrice valeur / effort** pour prioriser :

```
        Effort faible ←─────────→ Effort fort
              │                        │
Valeur haute  │  ✅ Faire d'abord     │  ⚠️ Planifier
              │                        │
Valeur basse  │  🔵 Si le temps       │  ❌ Éviter
              │                        │
```

### 5.3 Velocity

- La vélocité (points par sprint) est mesurée sur 3-5 sprints pour trouver un rythme
- La vélocité n'est pas un objectif — c'est une mesure pour améliorer les prévisions
- Ne pas comparer la vélocité entre équipes

---

## 6. Relation entre conception et tickets

### 6.1 Correspondance

```
Document de conception          Issue associée
──────────────────────          ────────────────
vision.md (ajout d'objectif)    « Ajouter le support multi-langue »
metamodel.md (nouveau concept)  « Ajouter le concept "Contrat" »
semantics.md (cas manquant)     « Précision : que faire si solde négatif ? »
catalogue.md (nouveau type)     « Ajouter le type "SickLeave" »
api.md (nouvelle fonction)      « Exposer getBalances() dans l'API »
```

### 6.2 Règle

> **Une issue doit référencer le document de conception qu'elle impacte. Un document de conception qui change doit avoir une issue correspondante.**

Si une PR modifie la conception, elle doit aussi mettre à jour la documentation. Ce n'est pas optionnel.

---

## 7. Suivi d'avancement

### 7.1 Ce qu'on suit

| Métrique | Utilité |
|----------|---------|
| ✅ Issues fermées / sprint | Progression |
| 📊 Vélocité | Prévision des prochains sprints |
| 🔴 Bugs ouverts | Qualité |
| 📈 Couverture de conception | % des sous-systèmes documentés |

### 7.2 Tableau de bord

```
Projet : Oxilière HR
─────────────────────────────────────────────────
Sprint actuel    : Sprint 5 (v1.1.0)
Issues :   5/8 complétées    ████████░░  62%
Bugs :     3 ouverts          ███░░░░░░░  1 critique
Conception : 4/6 sous-systèmes documentés 🟢
Vélocité :   12 pts/sprint (moy. sur 3 sprints)
```

---

## 8. Réunions et rythme

### 8.1 Rituels hebdomadaires

| Jour | Rituel | Durée | Participants |
|------|--------|-------|--------------|
| Lundi | Point d'équipe | 15 min | Tous |
| Mercredi | Triage du backlog | 30 min | PO + lead dev |
| Vendredi | Revue de sprint (toutes les 2 sem) | 30 min | Tous + PO |

### 8.2 Règles

- **Les réunions ont un ordre du jour** — Pas de réunion sans but
- **Les réunions commencent à l'heure** — La ponctualité est une forme de respect
- **Pas plus de 30 min** — Si un sujet prend plus de temps, c'est une réunion dédiée
- **Documenter les décisions** — Compte-rendu dans l'issue ou le document concerné

---

## 9. Anti-patterns

### Anti-pattern 1 : Tickets usine à gaz

**Symptôme** : Des tickets de 50 lignes avec des specs détaillées, rarement lues.

**Solution** : La spec est dans le document de conception. Le ticket est un rappel + des critères d'acceptation courts.

### Anti-pattern 2 : Sprint chargé à 110%

**Symptôme** : Chaque sprint, l'équipe prend plus qu'elle ne peut livrer.

**Solution** : Mieux vaut livrer 80% des tickets que d'en décaler 40%. Prendre moins, finir tout.

### Anti-pattern 3 : Backlog poubelle

**Symptôme** : 200 issues dans le backlog, dont la moitié sont des idées vieilles de 2 ans.

**Solution** : Nettoyer régulièrement. Si une issue n'a pas été touchée depuis 6 mois, la fermer ou la déplacer dans l'icebox.

### Anti-pattern 4 : La vélocité comme objectif

**Symptôme** : « On doit faire 15 points ce sprint parce qu'on en a fait 15 le mois dernier. »

**Solution** : La vélocité est une mesure, pas une cible. Si l'équipe ralentit, comprendre pourquoi plutôt que pousser plus.

---

> **Dernier conseil** : La gestion de projet n'est pas de la bureaucratie — c'est l'outil qui permet à l'équipe de se concentrer sur ce qui compte. Si un rituel ou un artefact ne sert à personne, supprimez-le. Gardez ce qui aide, jetez ce qui ralentit.
