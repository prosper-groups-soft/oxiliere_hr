# Git Flow & Versioning

> **Conventions et stratégies** pour organiser le travail collaboratif sur le code, de la première ligne au déploiement en production.

---

## Quickstart

```bash
# Convention de commit
git commit -m "feat(congés): ajoute la validation des soldes avant soumission"

# Créer une branche de fonctionnalité
git checkout -b feat/conges-validation-solde

# Créer un tag de version
git tag v1.2.0
git push --tags
```

---

## Table des matières

1. [Conventional Commits](#1-conventional-commits)
2. [Stratégie de branches](#2-stratégie-de-branches)
3. [Flux de travail par type de branche](#3-flux-de-travail-par-type-de-branche)
4. [Versioning sémantique](#4-versioning-sémantique)
5. [Gestion des releases](#5-gestion-des-releases)
6. [Changelog](#6-changelog)
7. [Bonnes pratiques](#7-bonnes-pratiques)
8. [Anti-patterns](#8-anti-patterns)

---

## 1. Conventional Commits

Tous les messages de commit doivent suivre le format [Conventional Commits](https://www.conventionalcommits.org/).

### 1.1 Format

```
<type>(<scope>): <description>

[body]

[footer(s)]
```

### 1.2 Types

| Type | Usage | Version impact |
|------|-------|----------------|
| `feat` | Nouvelle fonctionnalité | `minor` |
| `fix` | Correction de bug | `patch` |
| `docs` | Documentation uniquement | Aucun |
| `style` | Formatage, linting (pas de changement logique) | Aucun |
| `refactor` | Refactoring sans changement fonctionnel | Aucun |
| `perf` | Amélioration de performance | Aucun |
| `test` | Ajout ou modification de tests | Aucun |
| `chore` | Tâches techniques (dépendances, config) | Aucun |
| `ci` | Pipeline CI/CD | Aucun |

### 1.3 Règles

- **Toujours** en minuscules
- **Scope optionnel** — mais recommandé quand il concerne un sous-système spécifique : `feat(congés):`, `fix(auth):`
- **Description impérative** : « ajoute », « corrige », « supprime » — pas « ajouté », « corrigé »
- **Pas de point final** dans la description
- **Body** pour détailler le *pourquoi* si la description ne suffit pas
- **Footer** pour référencer les issues : `Closes #42`, `Related to #128`

### 1.4 Exemples

```
feat(congés): ajoute la validation des soldes avant soumission

Vérifie que le solde disponible est suffisant avant de passer
une demande au statut "Pending". Closes #42.

feat(employés): ajoute l'export CSV de l'annuaire

docs: met à jour le README avec les instructions d'installation

fix(notifications): corrige le doublon d'envoi sur les congés groupés

Related to #57

chore: met à jour les dépendances Svelte

refactor(forms): simplifie la gestion d'état des champs conditionnels
```

---

## 2. Stratégie de branches

### 2.1 Modèle : Git Flow simplifié

```
                      main (production)
                       │
                       ├─── v1.0.0 ──── tag
                       │
develop (intégration)
  │
  ├─── feat/conges-validation
  │         │
  │         └─── PR ──> develop
  │
  ├─── fix/notif-doublon
  │         │
  │         └─── PR ──> develop
  │
  ├─── release/v1.1.0
  │         │
  │         ├─── PR ──> main (avec tag)
  │         └─── PR ──> develop (backport correctifs)
  │
  └─── hotfix/critique-auth
            │
            ├─── PR ──> main (urgent)
            └─── PR ──> develop (backport)
```

### 2.2 Nomenclature des branches

| Branche | Préfixe | Base | Destinataire |
|---------|---------|------|--------------|
| Fonctionnalité | `feat/` | `develop` | `develop` |
| Correction | `fix/` | `develop` | `develop` |
| Release | `release/` | `develop` | `main` + `develop` |
| Hotfix | `hotfix/` | `main` | `main` + `develop` |
| Documentation | `docs/` | `develop` | `develop` |
| Refactoring | `refactor/` | `develop` | `develop` |

Le nom après le préfixe décrit brièvement le contenu, en kebab-case :
- `feat/conges-validation-solde`
- `fix/notif-doublon-envoi`
- `release/v1.1.0`

### 2.3 Règles

- **`main`** — La branche de production. Protégée : pas de push direct, uniquement des PR mergées.
- **`develop`** — La branche d'intégration. Toutes les fonctionnalités convergent ici.
- **Pas de `feature/` longues** — Une branche de fonctionnalité ne devrait pas vivre plus de 3 jours. Si c'est le cas, la découper.
- **Pas de commits sur `develop`** — Toujours passer par une PR.

---

## 3. Flux de travail par type de branche

### 3.1 Fonctionnalité

```bash
# 1. Partir de develop à jour
git checkout develop
git pull
git checkout -b feat/conges-validation-solde

# 2. Travailler (commits atomiques)
git commit -m "feat(congés): ajoute la règle de validation du solde"
git commit -m "feat(congés): expose l'erreur dans l'interface utilisateur"
git commit -m "test(congés): ajoute les tests de la validation"

# 3. Push et créer une PR vers develop
git push -u origin feat/conges-validation-solde

# 4. Après approbation de la PR → merge (squash recommendé)
```

### 3.2 Release

```bash
# 1. Créer la branche de release depuis develop
git checkout develop
git pull
git checkout -b release/v1.1.0

# 2. Correctifs de dernière minute sur la branche release (bugfix uniquement)
git commit -m "fix(paie): corrige le calcul des jours ouvrés"

# 3. PR vers main
# 4. PR vers develop (backport des correctifs)
# 5. Tag sur main
git checkout main
git tag v1.1.0
git push --tags
```

### 3.3 Hotfix (urgence production)

```bash
# 1. Partir de main
git checkout main
git pull
git checkout -b hotfix/urgence-auth

# 2. Corriger
git commit -m "fix(auth): corrige la session expirée non détectée"

# 3. PR vers main (approbation accélérée)
# 4. PR vers develop (backport obligatoire)
# 5. Tag
git tag v1.0.1
git push --tags
```

---

## 4. Versioning sémantique

### 4.1 Principe

On suit [SemVer 2.0](https://semver.org/) : `MAJEUR.MINEUR.PATCH`

| Incrément | Quand | Exemple |
|-----------|-------|---------|
| **MAJEUR** | Changement incompatible (API break, suppression de feature, refonte majeure) | `1.0.0` → `2.0.0` |
| **MINEUR** | Ajout de fonctionnalité (backward-compatible) | `1.0.0` → `1.1.0` |
| **PATCH** | Correction de bug (backward-compatible) | `1.0.0` → `1.0.1` |

### 4.2 Période de pré-lancement

```
1.0.0-alpha.1       → Première version instable
1.0.0-beta.1        → Stabilisation en cours
1.0.0-rc.1          → Release candidate
1.0.0               → Release stable
```

### 4.3 Correspondance avec les commits

Le type de commit détermine le niveau de version à incrémenter :

- `feat` + `BREAKING CHANGE` → **MAJEUR** (`x.0.0`)
- `feat` → **MINEUR** (`0.x.0`)
- `fix` → **PATCH** (`0.0.x`)
- Autres → aucun changement de version

---

## 5. Gestion des releases

### 5.1 Cycle de release recommandé

```
Sprinte 1          Sprinte 2          Sprinte 3
  ┌─────┐            ┌─────┐            ┌─────┐
  │feats│───PR──>    │feats│───PR──>    │feats│
  └─────┘            └─────┘            └─────┘
      │                 │                 │
      └────────┬────────┘                 │
               │                          │
          develop ────────────────────────┘
               │
               ▼
          release/v1.2.0 ──PR──> main ──tag──> v1.2.0
```

**Rythme conseillé** : 1 release toutes les 2-3 semaines.

### 5.2 Checklist de release

- [ ] Toutes les features prévues sont mergées dans `develop`
- [ ] Les tests passent sur la branche release (`npm test`)
- [ ] Le changelog a été mis à jour
- [ ] La version a été incrémentée dans les fichiers de configuration
- [ ] Un déploiement de validation (staging) a été effectué
- [ ] La PR vers `main` a été approuvée
- [ ] Le tag de version a été créé et poussé

---

## 6. Changelog

### 6.1 Format

Le fichier `CHANGELOG.md` suit le format [Keep a Changelog](https://keepachangelog.com/).

```markdown
# Changelog

## [1.2.0] - 2024-07-13

### Added
- Congés : validation du solde avant soumission (#42)
- Employés : export CSV de l'annuaire (#38)

### Fixed
- Notifications : correction du doublon d'envoi sur les congés groupés (#57)

### Changed
- Paie : optimisation du calcul des jours ouvrés (gain 40%)

## [1.1.0] - 2024-06-28
...
```

### 6.2 Sections

| Section | Contenu |
|---------|---------|
| `Added` | Nouvelles fonctionnalités |
| `Changed` | Modifications de fonctionnalités existantes |
| `Deprecated` | Fonctionnalités qui seront supprimées |
| `Removed` | Fonctionnalités supprimées |
| `Fixed` | Corrections de bugs |
| `Security` | Correctifs de sécurité |

### 6.3 Règles

- Le changelog est **écrit pour les humains** (utilisateurs, pas développeurs)
- Chaque entrée référence le numéro de l'issue/PR
- La date est au format ISO `YYYY-MM-DD`
- Les entrées sont en anglais ou en français (choisir et tenir)

---

## 7. Bonnes pratiques

### 7.1 Commits

- **Commits atomiques** : un commit = un changement logique
- **Commits fréquents** : mieux vaut trop de petits commits qu'un seul énorme
- **Ne pas commiter** : fichiers générés, dépendances (`node_modules`), secrets, fichiers de build
- **Commits WIP** : si vous devez commit temporairement, marquez `wip:` comme type

### 7.2 Branches

- **Supprimer après merge** : les branches de fonctionnalité sont supprimées une fois mergées
- **Garder les branches à jour** : rebase ou merge de `develop` régulièrement
- **Éviter les branches longues** : une branche > 3 jours doit être découpée

### 7.3 PR

- **Petites PR** : < 400 lignes idéalement, < 800 lignes max
- **PR = une fonctionnalité** : pas de PR qui fait 3 choses différentes
- **PR description** : explique quoi, pourquoi, et donne le contexte

---

## 8. Anti-patterns

### Anti-pattern 1 : Commits monstres

**Symptôme** : Un commit avec 50 fichiers modifiés et le message « plein de trucs ».

**Solution** : Découper en commits atomiques. Si le changement est trop gros, découper la fonctionnalité.

### Anti-pattern 2 : Branche main en avance sur develop

**Symptôme** : `main` a des correctifs qui ne sont pas dans `develop`.

**Solution** : Les hotfix doivent toujours être backportés vers `develop`. Automatiser ce backport si possible.

### Anti-pattern 3 : Version oubliée

**Symptôme** : Impossible de savoir quelle version est en production, ou le changelog est vide.

**Solution** : Automatiser la génération du changelog à partir des commits, et tagger systématiquement.

### Anti-pattern 4 : Branches de feature qui durent des semaines

**Symptôme** : Une branche `feat/gros-chantier` qui vit depuis 3 semaines, avec des merges de `develop` douloureux.

**Solution** : Découper en plus petites features livrables indépendamment. Activer les feature flags si nécessaire.

---

> **Dernier conseil** : Les conventions Git sont le squelette de votre collaboration. Sans elles, l'historique est illisible et les merges sont douloureux. Investissez dans l'automatisation (CI, hooks, templates de PR) pour que les bonnes pratiques soient faciles à suivre.
