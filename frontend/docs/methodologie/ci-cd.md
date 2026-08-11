# CI/CD

> **Pratiques d'intégration continue et de déploiement continu** pour automatiser la construction, la validation et la livraison du logiciel.

---

## Quickstart

```yaml
# .github/workflows/ci.yml (exemple GitHub Actions)
name: CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Architecture des pipelines](#2-architecture-des-pipelines)
3. [Pipeline CI : Intégration Continue](#3-pipeline-ci--intégration-continue)
4. [Pipeline CD : Déploiement Continu](#4-pipeline-cd--déploiement-continu)
5. [Environnements](#5-environnements)
6. [Stratégie de déploiement](#6-stratégie-de-déploiement)
7. [Gestion des secrets](#7-gestion-des-secrets)
8. [Qualité des pipelines](#8-qualité-des-pipelines)
9. [Bonnes pratiques](#9-bonnes-pratiques)
10. [Anti-patterns](#10-anti-patterns)

---

## 1. Philosophie

> **Tout ce qui peut être automatisé doit l'être, pour que l'humain se concentre sur ce qui a de la valeur.**

Nos principes :

1. **CI d'abord** — Le pipeline CI est la porte d'entrée : si la CI est rouge, rien ne va en production.
2. **Feedback rapide** — Un développeur doit savoir si son code casse quelque chose en moins de 5 minutes.
3. **Reproductibilité** — Le build doit être identique sur machine locale et en CI.
4. **Environnements identiques** — staging = production (même configuration, mêmes dépendances).

---

## 2. Architecture des pipelines

```
                    ┌──────────────────┐
                    │   Commit / PR    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   CI Pipeline    │
                    │                  │
                    │  ┌────────────┐  │
                    │  │  Lint      │  │
                    │  ├────────────┤  │
                    │  │  Test      │  │
                    │  ├────────────┤  │
                    │  │  Build     │  │
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Déploiement│  │ Déploiement│  │ Déploiement│
     │ Dev (auto) │  │Staging (PR)│  │  Prod (tag)│
     └────────────┘  └────────────┘  └────────────┘
```

---

## 3. Pipeline CI : Intégration Continue

### 3.1 Déclencheurs

| Événement | Pipeline | Action |
|-----------|----------|--------|
| Push sur `feat/*` | CI rapide | lint + tests |
| PR vers `develop` | CI complète | lint + tests + build |
| PR vers `main` | CI complète + vérification | lint + tests + build + validation |
| Tag `v*` | CI complète + CD | Déploiement production |

### 3.2 Étapes du pipeline CI

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: npm ci
      - run: npm run lint
      - run: npm run check        # Svelte check / TypeScript check

  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm ci
      - run: npm test              # Tests unitaires + intégration
      - run: npm run coverage      # Génération du rapport

  build:
    runs-on: ubuntu-latest
    steps:
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: build/
```

### 3.3 Temps d'exécution

| Étape | Objectif | Maximum |
|-------|----------|---------|
| Lint | < 30s | 1 min |
| Tests unitaires | < 1 min | 3 min |
| Tests intégration | < 3 min | 5 min |
| Build | < 2 min | 5 min |
| **Total CI** | **< 5 min** | **10 min** |

> [!IMPORTANT]
> Si la CI prend plus de 10 minutes, les développeurs contournent la CI (push forcés, merges sans attendre). Optimisez en priorité.

---

## 4. Pipeline CD : Déploiement Continu

### 4.1 Stratégie

| Environnement | Déclencheur | Automatisation | Supervision |
|---------------|-------------|----------------|-------------|
| **Dev** | Push sur `develop` | Automatique | Aucune (peut planter) |
| **Staging** | PR vers `main` approuvée | Automatique | Vérification manuelle rapide |
| **Production** | Tag `v*.*.*` approuvé | Automatique | Validation manuelle + rollback possible |

### 4.2 Pipeline de déploiement

```yaml
deploy-staging:
  runs-on: ubuntu-latest
  needs: [lint, test, build]
  if: github.event_name == 'pull_request' && github.base_ref == 'main'
  steps:
    - uses: actions/download-artifact@v4
    - run: ./deploy.sh staging
    - run: ./smoke-test.sh https://staging.example.com

deploy-production:
  runs-on: ubuntu-latest
  needs: [lint, test, build]
  if: startsWith(github.ref, 'refs/tags/v')
  steps:
    - uses: actions/download-artifact@v4
    - run: ./deploy.sh production
    - run: ./smoke-test.sh https://example.com
    - run: ./health-check.sh https://example.com/api/health
```

---

## 5. Environnements

### 5.1 Définition

| Environnement | URL | Usage | Données | Stabilité |
|---------------|-----|-------|---------|-----------|
| **Local** | `localhost:5173` | Développement | Mock / fixtures | ± stable |
| **Dev** | `dev.oxiliere.app` | Intégration continue | Synthétiques | Instable |
| **Staging** | `staging.oxiliere.app` | Validation avant prod | Anonymisées | Stable |
| **Production** | `app.oxiliere.app` | Utilisateurs finaux | Réelles | Très stable |

### 5.2 Règles

- **Dev = doit planter** — C'est normal, c'est fait pour ça. Pas d'alertes pour la CI qui pète sur develop.
- **Staging = doit marcher** — Avant une PR vers main, staging doit être vert.
- **Prod = doit être surveillé** — Toute dégradation en production est une alerte critique.

### 5.3 Feature flags

Pour les fonctionnalités qui nécessitent une activation différée, utiliser des **feature flags** :

```typescript
// Activer/désactiver sans déploiement
if (featureFlags.isEnabled('nouveau-module-conges')) {
  renderNewModule();
} else {
  renderOldModule();
}
```

---

## 6. Stratégie de déploiement

### 6.1 Déploiement progressif

Privilégier un déploiement qui minimise l'impact en cas de problème :

```
1. Déploiement staging     → Validation automatique (smoke tests)
2. Déploiement prod canary → 10% des utilisateurs pendant 15 min
3. Déploiement prod complet → 100% des utilisateurs
```

### 6.2 Rollback

Tout déploiement doit être réversible :

```bash
# Rollback vers la version précédente
./deploy.sh production v1.1.0   # version précédente
```

**Conditions de rollback** :
- Erreur 500 > 1% des requêtes
- Temps de réponse > 2x la normale
- Alerte critique d'un monitoring

---

## 7. Gestion des secrets

### 7.1 Règles

- **Jamais de secrets dans le code** — Ni en dur, ni dans les fichiers `.env` commités
- **Tous les secrets dans un coffre** — GitHub Secrets, Vault, ou équivalent
- **Rotation régulière** — Changement tous les 90 jours minimum
- **Limiter les accès** — Chaque environnement a ses propres secrets

### 7.2 Exemple

```yaml
- name: Deploy to production
  env:
    SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
    SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
    VITE_API_URL: ${{ secrets.VITE_API_URL_PROD }}
  run: ./deploy.sh
```

---

## 8. Qualité des pipelines

### 8.1 Gates de qualité

Chaque étape du pipeline est une **gate** : si elle échoue, le pipeline s'arrête.

```
Commit → Lint → Test → Build → Déploiement
  │        │       │       │          │
  │       erreur  échec   échec       │
  │        │       │       │          │
  └────────┴───┬───┴───┬───┘          │
               │       │              │
               ▼       ▼              ▼
            Pas de merge vers develop
```

| Gate | Condition d'échec |
|------|-------------------|
| 🔴 Lint | Une règle ESLint est violée |
| 🟠 Tests | Un test échoue ou la couverture baisse de > 5% |
| 🔵 Build | Le build échoue |

### 8.2 Notifications

- **CI échouée** → Notification sur le canal de l'équipe + tag du développeur concerné
- **CI verte** → Pas de notification (le silence est bon signe)
- **Déploiement prod réussi** → Notification sur le canal général

---

## 9. Bonnes pratiques

### 9.1 Pipeline

- **Paralléliser les jobs indépendants** — lint et tests peuvent tourner en même temps
- **Mettre en cache les dépendances** — `node_modules` ne devrait pas être téléchargé à chaque run
- **Purger le cache régulièrement** — Pour éviter les conflits de version
- **Utiliser des actions officielles** — Pas de scripts maison si une solution standard existe

### 9.2 Développement local

- **Tester la CI localement** — `act` (GitHub Actions) ou équivalent
- **Les mêmes outils** — Même version de Node, même OS (autant que possible)

### 9.3 Monitoring

- **Up-time monitoring** — L'application répond-elle ?
- **Smoke tests** — Les fonctionnalités critiques marchent-elles ?
- **Performance monitoring** — Les temps de réponse sont-ils normaux ?

---

## 10. Anti-patterns

### Anti-pattern 1 : CI trop lente

**Symptôme** : La CI prend 20 minutes. Les développeurs mergent sans attendre la fin.

**Solution** : Optimiser (parallélisation, cache), ou découper en pipelines spécialisés (CI rapide pour lint + tests, CI complète pour le build).

### Anti-pattern 2 : CI qui passe en local mais pas en CI

**Symptôme** : « Ça marche sur ma machine™ »

**Solution** : Standardiser l'environnement (Docker, nvm, versions de dépendances figées). Utiliser la même config en local et en CI.

### Anti-pattern 3 : Déploiement manuel

**Symptôme** : Le déploiement en production se fait à la main, via SSH.

**Solution** : Automatiser. Si le déploiement manuel est la seule option, documenter exactement chaque étape et prévoir un script.

### Anti-pattern 4 : Secrets dans le code

**Symptôme** : Des clés API ou des mots de passe dans le dépôt Git.

**Solution** : Utiliser les secrets de la plateforme CI. Ne jamais commit de fichier `.env`. Ajouter `.env` au `.gitignore`.

### Anti-pattern 5 : Pipeline sans tests

**Symptôme** : La CI fait juste `npm run build` et ne teste rien.

**Solution** : Ajouter au moins une gate de lint et une gate de test unitaire. Un build réussi ne garantit pas que le code fonctionne.

---

> **Dernier conseil** : La CI/CD n'est pas un luxe — c'est le minimum. Sans pipeline automatisé, chaque déploiement est une source d'anxiété. Investissez dans vos pipelines autant que dans votre code de production.
