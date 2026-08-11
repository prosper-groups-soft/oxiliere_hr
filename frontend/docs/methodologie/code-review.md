# Code Review

> **Processus et standards** pour que chaque modification de code soit revue avant d'être intégrée, garantissant qualité, cohérence et transmission de connaissance.

---

## Quickstart

```bash
# 1. Créer une PR
gh pr create --title "feat(congés): validation du solde" --body "Description..."

# 2. Demander une review
gh pr review --request @team

# 3. Review : commentaires → modifications → approbation

# 4. Merge (squash)
gh pr merge --squash
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Rôles](#2-rôles)
3. [Cycle de vie d'une PR](#3-cycle-de-vie-dune-pr)
4. [Checklist pour l'auteur](#4-checklist-pour-lauteur)
5. [Checklist pour le reviewer](#5-checklist-pour-le-reviewer)
6. [Comment faire une bonne review](#6-comment-faire-une-bonne-review)
7. [Comment recevoir une review](#7-comment-recevoir-une-review)
8. [Critères d'approbation](#8-critères-dapprobation)
9. [Cas particuliers](#9-cas-particuliers)
10. [Bonnes pratiques](#10-bonnes-pratiques)
11. [Anti-patterns](#11-anti-patterns)

---

## 1. Philosophie

> **La review est un moment de collaboration, pas de jugement.**

Notre approche :

- **La review ne vérifie pas seulement le code** — Elle vérifie aussi que le code correspond à la conception documentée.
- **L'auteur et le reviewer sont responsables ensemble** — L'objectif n'est pas de « coincer » l'auteur, mais d'améliorer le code.
- **Le ton est constructif** — On critique le code, pas la personne.
- **La review est une transmission de connaissance** — C'est l'occasion de comprendre le code des autres et d'apprendre.

---

## 2. Rôles

| Rôle | Responsabilité |
|------|----------------|
| **Auteur** | Écrit le code, crée la PR, répond aux commentaires, intègre les retours |
| **Reviewer** | Relit le code, pose des questions, suggère des améliorations, approuve ou demande des changements |
| **Mainteneur** | Garantit la cohérence globale, merge la PR (souvent l'architecte ou le lead dev) |

### 2.1 Nombre de reviewers recommandé

- **Changement simple** (correction de typo, refactor mineur) : 1 reviewer
- **Nouvelle fonctionnalité** : 2 reviewers
- **Changement d'architecture** : 2 reviewers + architecte
- **Hotfix** : 1 reviewer (validation accélérée)

---

## 3. Cycle de vie d'une PR

```
1. CRÉATION
   │
   ├── L'auteur crée la PR
   ├── Ajoute une description complète
   └── Assigne les reviewers

2. REVIEW
   │
   ├── Les reviewers commentent
   ├── L'auteur répond et modifie
   └── Itération jusqu'à approbation

3. APPROBATION
   │
   ├── Tous les reviewers approuvent
   └── Les checklists CI sont vertes

4. MERGE
   │
   ├── Squash & Merge (recommandé)
   └── La branche est supprimée
```

---

## 4. Checklist pour l'auteur

### Avant de créer la PR

- [ ] Le code compile sans erreur (`npm run build` / `npm run check`)
- [ ] Les tests passent (`npm test`)
- [ ] Le linter passe (`npm run lint`)
- [ ] La branche est à jour avec `develop` (rebase ou merge récent)
- [ ] Les commits suivent la convention [Conventional Commits](git-flow-et-versioning.md#1-conventional-commits)
- [ ] Les tests couvrent les nouveaux cas (unitaires + intégration si pertinent)

### Dans la description de la PR

La description doit répondre à ces questions :

```markdown
## Quoi ?
Une phrase qui décrit le changement.

## Pourquoi ?
Quel problème résout ce changement ? Quel besoin métier ?

## Comment ?
- Approche technique choisie
- Architecture ou design pattern utilisé
- Points d'attention

## Tests
- [ ] Tests unitaires ajoutés / modifiés
- [ ] Tests d'intégration
- [ ] Tests manuels effectués

## Related issues
Closes #42
Related to #57

## Breaking changes ?
Non — l'API est rétrocompatible.
```

---

## 5. Checklist pour le reviewer

### Lire le code

- [ ] Le code fait-il ce que la description annonce ?
- [ ] La logique est-elle correcte (pas de bugs évidents) ?
- [ ] Y a-t-il des effets de bord non documentés ?
- [ ] Les noms de variables / fonctions sont-ils explicites ?
- [ ] Le code respecte-t-il les invariants du métamodèle ?
- [ ] Y a-t-il des tests pour les cas d'erreur ?

### Qualité

- [ ] Le code suit-il les conventions du projet (linting, formatage, structure) ?
- [ ] Les fonctions sont-elles suffisamment petites / découpées ?
- [ ] Y a-t-il de la duplication évitable ?
- [ ] Les dépendances sont-elles justifiées ?
- [ ] Les messages d'erreur sont-ils utiles ?

### Conception

- [ ] Le changement respecte-t-il les documents de conception existants ?
- [ ] Si non, les documents doivent-ils être mis à jour ?

---

## 6. Comment faire une bonne review

### 6.1 Structural — Lire la PR dans cet ordre

1. **Description** — Comprendre le *quoi* et le *pourquoi*
2. **Tests** — Vérifier que les cas sont couverts (ça donne le contexte)
3. **Code** — Lire les changements (les tests lus avant donnent la spécification)
4. **Fichiers de configuration** — Vérifier les dépendances

### 6.2 Communication

| À faire | À éviter |
|---------|----------|
| ✅ « Cette fonction pourrait être extraite pour être réutilisée. » | ❌ « Tu aurais dû extraire cette fonction. » |
| ✅ « Je ne comprends pas cette condition. Peux-tu ajouter un commentaire ? » | ❌ « C'est incompréhensible. » |
| ✅ « Bonne idée d'utiliser un port ici, ça respecte bien l'inversion de dépendance. » | ❌ « Pas mal. » (feedbacks vagues) |
| ✅ Suggérer, expliquer le *pourquoi* | ❌ Donner des ordres sans justification |

### 6.3 Priorité des commentaires

| Priorité | Label | Signification |
|----------|-------|---------------|
| 🔴 **Blocant** | `change-request` | Doit être corrigé avant merge (bug, violation d'invariant, faille de sécurité) |
| 🟡 **Important** | `suggestion` | Amélioration recommandée (lisibilité, performance, pattern) |
| 🔵 **Mineur** | `nitpick` | Détail (typo, nommage) — l'auteur peut choisir de l'ignorer |
| ⚪ **Question** | `question` | Demande de clarification |

---

## 7. Comment recevoir une review

- **Assumez la bonne foi** — Le reviewer veut améliorer le code, pas vous critiquer.
- **Répondez à chaque commentaire** — Même pour dire « Bonne suggestion, ajouté. »
- **Ne prenez pas les critiques personnellement** — On critique le code, pas la personne.
- **Si vous n'êtes pas d'accord, expliquez pourquoi** — « J'ai considéré cette approche mais elle a l'inconvénient X… »
- **Remerciez** — Une review approfondie est un cadeau.

---

## 8. Critères d'approbation

### Une PR peut être approuvée si :

- [ ] Tous les 🔴 **bloquants** sont résolus
- [ ] Les checklists CI sont vertes (build, lint, tests)
- [ ] Au moins 1 reviewer a approuvé
- [ ] Les 🟡 **suggestions** ont été discutées (acceptées ou rejetées avec justification)

### Une PR ne doit PAS être mergée si :

- Un 🔴 bloquant est en attente
- La CI est rouge (sauf si c'est un problème d'infrastructure connu)
- La PR a une taille excessive (> 800 lignes) sans justification
- La description est absente ou insuffisante

---

## 9. Cas particuliers

### 9.1 Hotfix (urgence production)

- 1 reviewer suffit
- La CI doit passer (sauf si le fix est bloqué par la CI elle-même)
- La description doit être concise mais expliquer l'urgence
- Un backport vers `develop` est créé immédiatement après le merge

### 9.2 Changement de conception / breaking change

- Doit être discuté en équipe avant la PR (issue, RFC ou ADR)
- Les documents de conception doivent être mis à jour dans la même PR (ou une PR immédiatement après)
- Nécessite l'approbation de l'architecte

### 9.3 PR de documentation

- Reviewer métier recommandé (vérifier que le contenu est correct)
- Pas de CI nécessaire (mais le lint du markdown est apprécié)

---

## 10. Bonnes pratiques

### 10.1 Taille des PR

- **Idéal** : < 200 lignes
- **Acceptable** : 200-400 lignes
- **Maximum** : 800 lignes (au-delà, découper en plusieurs PR)
- **Exception** : génération de code, renommage — ces PR doivent être marquées explicitement

### 10.2 Temps de review

- **Objectif** : une PR est reviewée dans les 24h ouvrées
- **PR urgente** : taguer `urgent` dans le titre, prévenir le reviewer directement
- **PR bloquée** : si pas de review après 48h, relancer poliment

### 10.3 Automatisation

Automatiser tout ce qui peut l'être pour que la review se concentre sur le fond :

- **Lint et formatage** — Automatique (pre-commit hook)
- **Tests** — Exécutés par la CI
- **Templates de PR** — Pour guider la description
- **Labels automatiques** — Basés sur les fichiers modifiés (ex: `domaine: conges`)

---

## 11. Anti-patterns

### Anti-pattern 1 : Review-bombing

**Symptôme** : Une PR de 2000 lignes avec 50 fichiers modifiés, impossible à reviewer sérieusement.

**Solution** : Découper en PR plus petites. Si la fonctionnalité est trop grosse, la décomposer en plusieurs PR indépendantes.

### Anti-pattern 2 : Review en silo

**Symptôme** : Les mêmes 2 personnes reviewent toujours les PR des 3 mêmes personnes.

**Solution** : Encourager la rotation des reviewers. Tout le monde devrait reviewer régulièrement.

### Anti-pattern 3 : LGTM systématique

**Symptôme** : Un reviewer approuve en 30 secondes sans commentaires.

**Solution** : Fixer une règle : pas de approbation sans au moins un commentaire constructif (ou une question). Ça force la lecture.

### Anti-pattern 4 : Nitpicking

**Symptôme** : Des dizaines de commentaires sur le style (espaces, nommage) alors que le linter aurait dû les attraper.

**Solution** : Automatiser tout le formatage. Si ça passe le linter, c'est que c'est acceptable.

### Anti-pattern 5 : Review trop tardive

**Symptôme** : Une PR créée il y a 5 jours, toujours pas reviewée.

**Solution** : La review a la priorité sur le nouveau code. Commencer la journée par les PR en attente.

---

> **Dernier conseil** : Une bonne review n'est ni une formalité (LGTM) ni un procès. C'est une conversation technique qui améliore le code, transmet la connaissance et renforce la cohésion de l'équipe. Investissez-y du temps — il vous sera rendu en bugs évités.
