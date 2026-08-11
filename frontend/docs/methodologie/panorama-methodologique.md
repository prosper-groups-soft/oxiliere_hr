# Panorama méthodologique

> **Une cartographie de toutes les méthodes de travail** qui encadrent le cycle de vie d'un logiciel, de la conception à l'exploitation en production.

---

## Quickstart

| Vous cherchez… | Lisez… |
|----------------|--------|
| …à concevoir un sous-système complexe | [Conception par métamodèle](conception-par-metamodele.md) |
| …à assembler plusieurs sous-systèmes | [Architecture applicative](architecture-applicative.md) |
| …à organiser vos branches Git | [Git Flow & Versioning](git-flow-et-versioning.md) |
| …à définir vos standards de qualité | [Qualité et Tests](qualite-et-tests.md) |
| …à mettre en place les reviews | [Code Review](code-review.md) |
| …à automatiser le build et le déploiement | [CI/CD](ci-cd.md) |
| …à sécuriser votre application | [Sécurité applicative](securite-applicative.md) |
| …à surveiller la production | [Monitoring et Observabilité](monitoring-observabilite.md) |
| …à organiser votre travail d'équipe | [Gestion de projet](gestion-de-projet.md) |

---

## Vision d'ensemble

```
┌───────────────────────────────────────────────────────────┐
│                     MÉTIER                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  CONCEPTION (QUOI / POURQUOI)                       │  │
│  │  ┌─────────────────┐  ┌─────────────────────────┐   │  │
│  │  │ Par métamodèle  │  │ Architecture applicative│   │  │
│  │  │ (un sous-syst.) │  │ (assemblage)            │   │  │
│  │  └─────────────────┘  └─────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  RÉALISATION (COMMENT)                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │  │
│  │  │ Git Flow    │  │ Code Quality │  │ Code      │  │  │
│  │  │ & Versioning│  │ & Tests      │  │ Review    │  │  │
│  │  └─────────────┘  └──────────────┘  └───────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  LIVRAISON (AUTOMATISATION)                         │  │
│  │  ┌──────┐                                           │  │
│  │  │CI/CD │                                           │  │
│  │  └──────┘                                           │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                │
│    ┌──────────────────────┼──────────────────────┐         │
│    │                      │                      │         │
│    ▼                      ▼                      ▼         │
│  ┌──────────┐       ┌──────────────┐      ┌──────────┐    │
│  │ Sécurité │       │  Monitoring  │      │ Gestion  │    │
│  │(transv.) │       │  (transv.)   │      │ de projet│    │
│  └──────────┘       └──────────────┘      │  (orga.) │    │
│                                           └──────────┘    │
└───────────────────────────────────────────────────────────┘
```

---

## Les 9 piliers méthodologiques

### 1. 🏗️ Conception

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Conception par métamodèle](conception-par-metamodele.md) | Concevoir un sous-système isolé (concepts, sémantique, catalogue, API) | Concepteurs, architectes |
| [Architecture applicative](architecture-applicative.md) | Assembler plusieurs sous-systèmes (vision, carte, intégration, structure) | Architectes, développeurs seniors |

### 2. 🌿 Git & Versioning

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Git Flow & Versioning](git-flow-et-versioning.md) | Conventions de commits, stratégie de branches, gestion de versions | Toute l'équipe |

### 3. ✅ Qualité & Tests

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Qualité et Tests](qualite-et-tests.md) | Linting, tests unitaires/intégration/E2E, couverture, invariants ↔ tests | Toute l'équipe |

### 4. 👀 Code Review

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Code Review](code-review.md) | Processus de PR, checklists, rôles, critères d'approbation | Toute l'équipe |

### 5. 🔄 CI/CD

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [CI/CD](ci-cd.md) | Pipeline build/test/deploy, environnements, stratégie de déploiement | Développeurs, DevOps |

### 6. 🛡️ Sécurité (transverse)

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Sécurité applicative](securite-applicative.md) | OWASP, SAST, dépendances, secrets, validation, contrôle d'accès | Toute l'équipe |

### 7. 📊 Monitoring & Observabilité (transverse)

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Monitoring et Observabilité](monitoring-observabilite.md) | Logs structurés, métriques, alerting, health checks, audit | Développeurs, DevOps |

### 8. 📋 Gestion de projet (organisation)

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [Gestion de projet](gestion-de-projet.md) | Backlog, sprints, estimation, priorisation, lien conception ↔ tickets | PO, équipe |

---

## Relations entre les piliers

```
                    Gestion de projet
                    (cadence, priorisation, backlog)
                           │
                           ▼
Conception ──→ Git Flow ──→ Qualité & Tests ←──→ Code Review
                                                │
                                                ▼
                                          CI/CD ──→ Production
                           │                      │
                           ▼                      ▼
                    Sécurité              Monitoring
                    (transverse)           (transverse)
```

---

## Correspondance avec le cycle de vie d'une feature

```
1. IDÉE
   ├── Issue / Ticket                           ← Gestion de projet
   └── Besoin métier identifié

2. CONCEPTION
   ├── Vision globale (application)             ← Architecture applicative
   ├── Carte des sous-systèmes                  ← Architecture applicative
   └── Métamodèle du sous-système               ← Conception par métamodèle

3. IMPLÉMENTATION
   ├── Création de branche                      ← Git Flow
   ├── Écriture du code                         ← Qualité & Tests, Sécurité
   ├── Tests unitaires / intégration            ← Qualité & Tests
   └── PR et code review                        ← Code Review, Sécurité

4. INTÉGRATION
   ├── CI : build + lint + tests + scan sécu    ← CI/CD, Sécurité
   ├── Merge dans develop                       ← Git Flow
   └── Déploiement sur staging                  ← CI/CD

5. LIVRAISON
   ├── Validation produit
   ├── Release et versionning                   ← Git Flow
   └── Déploiement en production                ← CI/CD, Monitoring

6. EXPLOITATION
   ├── Monitoring et alertes                    ← Monitoring
   ├── Analyse des logs et métriques            ← Monitoring
   ├── Correction de bugs (hotfix)              ← Git Flow
   ├── Évolution des concepts                   ← Méthodes de conception
   └── Mise à jour de la documentation          ← Tous
```

---

> **Dernier conseil** : Ces méthodologies sont conçues pour être **combinées**. Ne les appliquez pas isolément. Une bonne conception sans code review livre des bugs. Un bon Git Flow sans CI/CD est chronophage. Une bonne qualité de code sans conception claire empêche l'évolution.
