# Qualité et Tests

> **Standards et pratiques** pour garantir que le code est fiable, maintenable et conforme aux spécifications.

---

## Quickstart

```bash
# Linter
npm run lint

# Tests unitaires
npm run test

# Tests d'intégration
npm run test:integration

# Tests E2E
npm run test:e2e

# Voir la couverture
npm run coverage
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Pyramide des tests](#2-pyramide-des-tests)
3. [Linting et formatage](#3-linting-et-formatage)
4. [Tests unitaires](#4-tests-unitaires)
5. [Tests d'intégration](#5-tests-dintégration)
6. [Tests E2E](#6-tests-e2e)
7. [Couverture de code](#7-couverture-de-code)
8. [Stratégie de test par couche](#8-stratégie-de-test-par-couche)
9. [Test des concepts du métamodèle](#9-test-des-concepts-du-métamodèle)
10. [Bonnes pratiques](#10-bonnes-pratiques)
11. [Anti-patterns](#11-anti-patterns)

---

## 1. Philosophie

> **Tester, c'est valider que le code correspond à la conception, pas l'inverse.**

Nos principes :

1. **Les tests protègent la conception** — Si un test est difficile à écrire, c'est souvent la conception qu'il faut améliorer, pas le test.
2. **Un test non automatisé n'existe pas** — Les tests manuels sont faillibles et coûteux.
3. **Priorité au domaine** — La logique métier est ce qu'il y a de plus important à tester.
4. **Les tests sont du code** — Ils doivent être aussi bien écrits que le code de production.

---

## 2. Pyramide des tests

```
            ╱╲
           ╱  ╲
          ╱ E2E╲              ← Quelques tests de bout en bout
         ╱______╲
        ╱        ╲
       ╱  INTÉG.  ╲           ← Tests d'intégration (API, DB, services)
      ╱____________╲
     ╱              ╲
    ╱   UNITAIRE     ╲        ← Beaucoup de tests unitaires (logique pure)
   ╱__________________╲
  ╱                    ╲
 ╱   STATIQUE (lint)    ╲     ← Le plus de règles possible (lint, types)
╱________________________╲
```

| Niveau | Nombre | Vitesse | Portée | Confiance |
|--------|--------|---------|--------|-----------|
| Statique | Infini | Instantané | Syntaxe, types, conventions | Faible |
| Unitaire | Beaucoup | ms | Une fonction, une classe | Moyenne |
| Intégration | Moyen | s | Composants, API, base de données | Haute |
| E2E | Peu | min | Parcours utilisateur complet | Très haute |

---

## 3. Linting et formatage

### 3.1 Outils

- **ESLint** — Règles de qualité et de style pour TypeScript/JavaScript
- **Prettier** — Formatage automatique (indentation, espaces, virgules)
- **Svelte check** — Vérification spécifique Svelte (syntaxe, props, stores)

### 3.2 Règles

- **Le linting est exécuté à chaque commit** (via pre-commit hook ou CI)
- **Le formatage est automatique** — Prettier s'exécute au save dans l'IDE
- **Pas de warning ignoré** — Si une règle est trop contraignante, on la désactive explicitement dans la config, pas avec un commentaire `// eslint-disable-next-line`
- **Les règles sont documentées** — Toute déviation de la config par défaut est justifiée

### 3.3 Configuration minimale

```jsonc
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:svelte/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "no-console": "warn"
  }
}
```

```jsonc
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100
}
```

---

## 4. Tests unitaires

### 4.1 Quoi tester en priorité

- **La logique métier** — Règles de validation, calculs, transitions d'état
- **Les invariants du métamodèle** — Contraintes documentées dans `metamodel.md`
- **Les cas limites** — Valeurs nulles, vides, extrêmes
- **Les fonctions pures** — Elles n'ont pas d'effet de bord

### 4.2 Quoi ne pas tester en unitaire

- L'UI (composants Svelte) — réservé aux tests d'intégration
- Les appels API / base de données — réservé aux tests d'intégration
- Le code trivial (getters, setters, constantes)

### 4.3 Structure d'un test

```typescript
describe('submitLeave', () => {
  it('rejette la demande si le solde est insuffisant', () => {
    // Arrange
    const employee = createTestEmployee({ balance: 0 });
    const request = createLeaveRequest(employee, { days: 5 });

    // Act
    const result = submitLeave(request);

    // Assert
    expect(result.status).toBe('error');
    expect(result.message).toContain('solde insuffisant');
  });

  it('approuve la demande si le solde est suffisant', () => {
    // Arrange
    const employee = createTestEmployee({ balance: 10 });
    const request = createLeaveRequest(employee, { days: 5 });

    // Act
    const result = submitLeave(request);

    // Assert
    expect(result.status).toBe('success');
    expect(result.leave.status).toBe('Pending');
  });
});
```

### 4.4 Règles

- **Un test = un comportement** — Pas de test qui vérifie 3 choses à la fois
- **Nom explicite** : `rejette la demande si le solde est insuffisant` — pas `test_1`
- **AAA Pattern** : Arrange / Act / Assert
- **Pas de logique dans les tests** — ni `if`, ni `for`, ni `try/catch`

---

## 5. Tests d'intégration

### 5.1 Quoi tester

- **Les interactions entre couches** — Use-case → Infrastructure, API → Domaine
- **Les adaptateurs** — NotificationAdapter, PersistenceAdapter
- **Les endpoints API** — Requête/réponse complète
- **Les composants UI avec état** — Formulaires, listes, workflows

### 5.2 Exemple : test d'un use-case complet

```typescript
describe('Soumission d\'une demande de congé', () => {
  it('notifie le manager quand la demande est soumise', async () => {
    // Arrange
    const notificationService = new MockNotificationService();
    const useCase = new SubmitLeaveUseCase(notificationService);
    const request = buildValidRequest();

    // Act
    await useCase.execute(request);

    // Assert
    expect(notificationService.sent).toHaveLength(1);
    expect(notificationService.sent[0].type).toBe('leave.submitted');
  });
});
```

### 5.3 Infrastructure de test

- **Mock des dépendances externes** — Ne jamais tester contre une API ou une BDD réelle en intégration
- **Environnement de test isolé** — Base de données de test dédiée, réinitialisée avant chaque session
- **Factories de test** — Pour créer des objets métier valides rapidement

---

## 6. Tests E2E

### 6.1 Quoi tester

- **Les parcours utilisateur critiques** — *Un employé crée une demande > le manager approuve > l'employé reçoit une notification*
- **Les scénarios globaux identifiés dans la conception** — Voir [Étape 6 de l'architecture applicative](architecture-applicative.md#étape-6--validation-par-des-scénarios-globaux)
- **Les régressions** — Fonctionnalités qui ont cassé par le passé

### 6.2 Règles

- **Peu de tests E2E** (5-10 par application) — Ils sont lents et fragiles
- **Les scénarios critiques seulement** — Pas les cas d'erreur (c'est le rôle des tests unitaires)
- **Pas de E2E sur des fonctionnalités instables** — Attendre la stabilisation de l'UI

---

## 7. Couverture de code

### 7.1 Objectifs

| Métrique | Objectif | Priorité |
|----------|----------|----------|
| Couverture de lignes | > 80% global | Indicatif |
| Couverture de branches | > 70% | Important |
| Couverture du domaine | > 95% | **Critique** |
| Couverture de l'UI | > 50% | Souhaitable |

> [!IMPORTANT]
> La couverture est un **indicateur**, pas un objectif. 100% de couverture ne signifie pas que le code est bien testé. Un code bien testé a des tests qui **valident le comportement**, pas les lignes.

### 7.2 Focus sur le domaine

Le code métier (dossiers `domains/`) doit avoir la couverture la plus élevée :

```
domains/
├── conges/
│   ├── types.ts               ← 100% (types uniquement)
│   ├── use-cases/
│   │   ├── submit-leave.ts    ← 100% (logique critique)
│   │   └── approve-leave.ts   ← 100% (logique critique)
│   └── infrastructure/
│       └── persistence.ts     ← 80% (dépend de la BDD)
```

---

## 8. Stratégie de test par couche

| Couche | Type de test | Ce qu'on teste | Outil |
|--------|-------------|----------------|-------|
| Domaine (métier pur) | Unitaire | Règles, invariants, calculs | Vitest / Jest |
| Application (use-cases) | Intégration | Orchestration, calls infra | Vitest + Mocks |
| Infrastructure (API, BDD) | Intégration | Contrats, requêtes | Supertest, testcontainers |
| Présentation (UI) | Intégration / E2E | Composants, flux utilisateur | Playwright, Testing Library |

---

## 9. Test des concepts du métamodèle

Chaque invariant documenté dans le métamodèle doit avoir un test correspondant :

```markdown
<!-- metamodel.md -->
### Invariants
- **Règle 1** : Un employé ne peut pas avoir un solde de congés négatif.
- **Règle 2** : Une demande de congé ne peut pas chevaucher une autre demande approuvée.
```

```typescript
// test/domains/conges/invariants.test.ts
describe('Invariants du métamodèle Congés', () => {
  it('un employé ne peut pas avoir un solde négatif', () => {
    expect(() => createBalance(-5)).toThrow('solde négatif');
  });

  it('une demande ne peut pas chevaucher une autre approuvée', () => {
    const employee = createEmployee();
    const existing = createApprovedLeave(employee, '2024-08-01', '2024-08-10');
    expect(() => createLeave(employee, '2024-08-05', '2024-08-15'))
      .toThrow('chevauchement');
  });
});
```

> [!TIP]
> Cette correspondance directe entre invariants du métamodèle et tests unitaires est ce qui rend la conception robuste. Si un invariant n'a pas de test, il n'existe pas vraiment.

---

## 10. Bonnes pratiques

### 10.1 Écriture des tests

- **TDD sur la logique métier** — Écrire le test AVANT le code de production
- **Un test = un comportement** — Si le test a plus d'un assert, vérifier qu'ils testent vraiment la même chose
- **Éviter les mocks inutiles** — Si un mock est trop complexe, c'est que la conception est mauvaise
- **Nommer les variables de test clairement** — `emptyBalance`, `validRequest`, `invalidDate`

### 10.2 Organisation des fichiers

```
tests/
├── unit/
│   └── domains/
│       ├── conges/
│       │   ├── submit-leave.test.ts
│       │   ├── approve-leave.test.ts
│       │   └── invariants.test.ts
│       └── auth/
├── integration/
│   ├── api/
│   │   └── conges.test.ts
│   └── components/
│       └── LeaveRequestForm.test.ts
└── e2e/
    └── parcours-conges.spec.ts
```

### 10.3 Exécution

- `npm test` — Tests unitaires uniquement (rapides, exécutés en boucle en dev)
- `npm run test:ci` — Tous les tests (CI uniquement)
- `npm run test:changed` — Tests des fichiers modifiés (avant commit)

---

## 11. Anti-patterns

### Anti-pattern 1 : Tester l'implémentation, pas le comportement

**Symptôme** : Le test vérifie qu'une fonction interne a été appelée, pas que le résultat est correct.

```typescript
// ❌ Mauvais : test de l'implémentation
it('appelle save', () => {
  const spy = vi.spyOn(repo, 'save');
  useCase.execute(data);
  expect(spy).toHaveBeenCalled();
});

// ✅ Bon : test du comportement
it('sauvegarde la demande et retourne un succès', async () => {
  const result = await useCase.execute(data);
  expect(result.status).toBe('success');
  expect(result.leave.id).toBeDefined();
});
```

### Anti-pattern 2 : Trop de mocks

**Symptôme** : Un test avec 5 mocks qui échoue parce qu'un mock est mal configuré.

**Solution** : Si un test nécessite beaucoup de mocks, c'est que la fonction testée a trop de dépendances. Refactorer.

### Anti-pattern 3 : Ignorer les tests flaky

**Symptôme** : Des tests qui échouent une fois sur trois sans raison claire.

**Solution** : Les tests flaky sont traités comme des bugs : priorité haute, corrigés immédiatement. Ne jamais ajouter `.skip` ou `.only` sans ticket.

### Anti-pattern 4 : Pas de test pour les cas d'erreur

**Symptôme** : Tous les tests sont des *happy paths*.

**Solution** : Pour chaque fonction testée, écrire au moins un test d'erreur. Si une fonction n'a aucun cas d'erreur, c'est peut-être qu'elle ne fait rien d'utile.

---

> **Dernier conseil** : La qualité n'est pas une couche qu'on ajoute à la fin. Elle s'intègre dans le processus : lint avant commit, tests avant merge, validation avant release. Automatisez tout ce qui peut l'être.
