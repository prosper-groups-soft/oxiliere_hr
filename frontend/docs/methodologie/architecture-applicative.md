# Architecture applicative : du domaine à l'application

> **Une approche rigoureuse** pour assembler des sous-systèmes conçus par métamodèle en une application cohérente et livrable.
>
> Complémentaire à la **Méthode de conception par métamodèle**.

---

## Quickstart : assembler une application dès maintenant

> Vous avez déjà 2-3 sous-systèmes conçus ? Voici comment les assembler.

1. **Créez `docs/application/vision-globale.md`** — En 5 minutes, écrivez le problème que votre application résout.
2. **Créez `docs/application/carte-sous-systemes.md`** — Listez vos sous-systèmes, leurs responsabilités et leurs dépendances.
3. **Dessinez les flux** — Prenez 2 sous-systèmes qui doivent communiquer, choisissez le mode (événement / requête / commande / données partagées).
4. **Structurez le code** — Un dossier `domains/<sous-système>/` par sous-système, avec `types.ts`, `use-cases/`, `infrastructure/`.
5. **Testez avec un scénario global** — Tracez un cas d'usage complet du début à la fin.

> [!TIP]
> L'ordre est important : commencez par les sous-systèmes les plus indépendants (souvent Auth ou le cœur métier), puis ajoutez ceux qui en dépendent.

---

## Table des matières

1. [Le problème : le chainon manquant](#1-le-problème-le-chainon-manquant)
2. [Principe fondamental](#2-principe-fondamental)
3. [Les 4 documents d'architecture](#3-les-4-documents-darchitecture)
4. [Niveau 0 : Vision globale](#4-niveau-0-vision-globale)
5. [Niveau 1 : Carte des sous-systèmes](#5-niveau-1-carte-des-sous-systèmes)
6. [Niveau 2 : Architecture d'intégration](#6-niveau-2-architecture-dintégration)
7. [Niveau 3 : Architecture applicative](#7-niveau-3-architecture-applicative)
8. [Le flux de conception pas à pas](#8-le-flux-de-conception-pas-à-pas)
9. [États de maturité et Definition of Done](#9-états-de-maturité-et-definition-of-done)
10. [Les invariants de la méthode](#10-les-invariants-de-la-méthode)
11. [Relations entre les deux méthodes](#11-relations-entre-les-deux-méthodes)
12. [Collaboration et modalités de travail](#12-collaboration-et-modalités-de-travail)
13. [ADR — Traçabilité des décisions](#13-adr--traçabilité-des-décisions)
14. [Anti-patterns courants](#14-anti-patterns-courants)

---

## 1. Le problème : le chainon manquant

### 1.1 Le constat

La [Méthode de conception par métamodèle](conception-par-metamodele.md) permet de concevoir rigoureusement un **sous-système isolé** (formulaires, workflow, notifications, etc.). Mais elle ne répond pas aux questions suivantes :

- Comment savoir **quels sous-systèmes** sont nécessaires ?
- Comment **découper** le métier global en sous-systèmes cohérents ?
- Comment les sous-systèmes **communiquent-ils** entre eux ?
- Comment **assembler** le tout en une application livrable ?
- Où placer le **code partagé** (UI, persistence, auth) ?
- Comment **valider** que l'ensemble tient debout ?

### 1.2 La promesse

Cette méthode complète la première en ajoutant les niveaux d'abstraction manquants :

```
Méthode par métamodèle              Cette méthode
─────────────────────────            ─────────────────────
Concevoir un sous-système            → Assembler plusieurs sous-systèmes
Définir des concepts métier          → Définir les frontières et liens
Valider par des exemples             → Valider par des scénarios globaux
Produire : vision, metamodel, ...    → Produire : stratégie de découpage,
                                        architecture d'intégration,
                                        architecture applicative
```

### 1.3 Quand utiliser cette méthode ?

- Vous avez identifié au moins **2 à 3 sous-systèmes** à concevoir
- Vous voulez garantir la **cohérence globale** de l'application
- Vous devez organiser le travail de **plusieurs équipes** ou contributeurs
- Vous anticipez l'**ajout de nouveaux sous-systèmes** dans le futur

---

## 2. Principe fondamental

> **L'application est un écosystème de sous-systèmes autonomes mais coordonnés.**

Chaque sous-système est conçu indépendamment via la méthode par métamodèle, mais ils partagent :

1. **Un langage commun** — Les concepts fondamentaux de l'application
2. **Des règles d'intégration** — Comment ils échangent et se coordonnent
3. **Une infrastructure partagée** — Couches techniques communes
4. **Une expérience unifiée** — Cohérence pour l'utilisateur final

### 2.1 Les trois niveaux d'organisation

```
Niveau 0 : Vision globale
    L'application dans son ensemble (métier, parties prenantes, objectifs)
        │
        ▼
Niveau 1 : Carte des sous-systèmes
    Découpage en sous-systèmes, frontières, responsabilités
        │
        ▼
Niveau 2 : Architecture d'intégration
    Canaux de communication, protocoles, données partagées
        │
        ▼
Niveau 3 : Architecture applicative
    Structure technique, couches, déploiement, code
```

### 2.2 Analogie : l'urbanisme

| Domaine | Niveau | Correspondance |
|---------|--------|----------------|
| Ville | Vision | Plan directeur d'urbanisme |
| Ville | Quartiers | Découpage en zones (résidentiel, commercial, industriel) |
| Ville | Rues, transports | Réseaux de communication, flux |
| Ville | Bâtiments | Structures techniques individuelles |
| Logiciel | Niveau 0 | Vision globale de l'application |
| Logiciel | Niveau 1 | Sous-systèmes et leurs responsabilités |
| Logiciel | Niveau 2 | Intégration, API, événements |
| Logiciel | Niveau 3 | Architecture technique (frontend, backend, etc.) |

---

## 3. Les 4 documents d'architecture

### 3.1 Structure des fichiers

```
docs/
└── methodologie/
    ├── conception-par-metamodele.md    ← Méthode pour un sous-système
    └── architecture-applicative.md     ← Méthode pour l'assemblage (CE FICHIER)

docs/
└── application/
    ├── vision-globale.md               ← Niveau 0 : Pourquoi l'application ?
    ├── carte-sous-systemes.md          ← Niveau 1 : Quels sous-systèmes ?
    ├── architecture-integration.md     ← Niveau 2 : Comment ils se parlent ?
    └── architecture-technique.md       ← Niveau 3 : Structure de code ?
```

### 3.2 Correspondance avec les niveaux

| Document | Niveau | Question | Dépend de |
|----------|--------|----------|-----------|
| `vision-globale.md` | 0 | Pourquoi existe-t-on ? | — |
| `carte-sous-systemes.md` | 1 | Quels sont les sous-systèmes ? | Vision globale |
| `architecture-integration.md` | 2 | Comment communiquent-ils ? | Carte des sous-systèmes |
| `architecture-technique.md` | 3 | Quelle est la structure technique ? | Architecture d'intégration |
| *(documents par sous-système)* | — | Quels sont les concepts de chaque domaine ? | Carte des sous-systèmes |

---

## 4. Niveau 0 : Vision globale

### 4.1 Finalité

Définir **pourquoi l'application existe**, à qui elle s'adresse, quels problèmes elle résout, et quel est son périmètre global.

### 4.2 Questions

- Quel est le **problème métier** global que l'on résout ?
- Qui sont les **utilisateurs** et quels sont leurs **besoins** ?
- Quels sont les **objectifs stratégiques** ?
- Quelles sont les **contraintes** (techniques, réglementaires, budgétaires) ?

### 4.3 Structure recommandée

```markdown
# Vision globale : [Nom de l'application]

## Intent
En une phrase : qu'est-ce que cette application apporte au monde ?

## Problème
Description du problème métier global.

## Utilisateurs
| Profil | Besoin principal | Fréquence d'utilisation |
|--------|------------------|------------------------|
| ...    | ...              | ...                    |

## Objectifs stratégiques
1. ...
2. ...

## Contraintes
- **Techniques** : ... (framework, infrastructure, etc.)
- **Réglementaires** : ... (RGPD, etc.)
- **Organisationnelles** : ... (taille d'équipe, etc.)

## Macro-roadmap
| Phase | Objectif | Durée estimée |
|-------|----------|---------------|
| V1    | ...      | ...           |
| V2    | ...      | ...           |
| V3    | ...      | ...           |
```

> [!NOTE]
> Ce document est le **point d'entrée** de toute personne qui arrive sur le projet. Il doit pouvoir être lu et compris en 5 minutes.

---

## 5. Niveau 1 : Carte des sous-systèmes

### 5.1 Finalité

Identifier **tous les sous-systèmes** de l'application, délimiter leurs frontières, et assigner leurs responsabilités.

### 5.2 La décomposition en sous-systèmes

#### 5.2.1 Principe

Un **sous-système** est un ensemble cohérent de concepts métier qui :

- Répond à un **besoin métier spécifique** (pas technique)
- A une **frontière claire** (on sait où il commence et où il finit)
- Est **autonome** (peut évoluer indépendamment)
- Correspond à un **bounded context** (DDD)

#### 5.2.2 Méthode de décomposition

Pour décomposer une application en sous-systèmes, suivez ces étapes :

**Étape 1 : Lister les capacités métier**

Parcourez les besoins utilisateur et listez toutes les **capacités** que l'application doit offrir. Une capacité est un verbe + nom : « Gérer les employés », « Approuver des congés », « Générer la paie ».

**Étape 2 : Grouper par affinité**

Regroupez les capacités qui partagent les mêmes **concepts fondamentaux** et les mêmes **règles métier**.

**Étape 3 : Appliquer les critères de coupure**

Un sous-système doit être :
- **Cohérent** : ses concepts sont fortement liés entre eux
- **Faiblement couplé** : il échange peu avec les autres sous-systèmes
- **Indépendant** : on peut le modifier sans casser les autres

**Étape 4 : Nommer chaque sous-système**

Donnez un nom qui reflète le **domaine métier**, pas la technologie.

> [!TIP]
> **Test de la frontière** : si vous pouvez dire « un [concept] n'existe pas en dehors de [sous-système] », alors la frontière est bonne.

### 5.3 Questions

- Quels sont les **sous-systèmes** identifiés ?
- Quelles sont leurs **responsabilités** exactes ?
- Quels **concepts** chacun possède-t-il en propre ?
- Quels sont les **chevauchements** à éviter ?
- Quels sous-systèmes existent déjà et lesquels sont à créer ?

### 5.4 Structure recommandée

```markdown
# Carte des sous-systèmes : [Application]

## Diagramme des sous-systèmes
```
┌──────────────────────────────────────────────────┐
│                    Application                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Auth    │  │ Employés │  │ Congés   │  ...   │
│  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Paie    │  │ Perf.    │  │ Notif.   │  ...   │
│  └──────────┘  └──────────┘  └──────────┘       │
└──────────────────────────────────────────────────┘
```

## Liste des sous-systèmes

### [Sous-système A]

| Propriété | Valeur |
|-----------|--------|
| **Nom** | ... |
| **Responsabilité** | ... |
| **Concepts clés** | ... |
| **Dépendances** | ... |
| **Documentation** | `docs/forms/` |
| **Priorité** | Haute / Moyenne / Basse |
| **État** | Existant / À créer / Planifié |

### [Sous-système B]
...

## Récapitulatif

| Sous-système | Responsabilité | Dépend de | Priorité |
|--------------|----------------|-----------|----------|
| ...          | ...            | ...       | ...      |

## Sous-systèmes exclus ou différés

| Sous-système | Raison de l'exclusion | Réévaluation prévue |
|--------------|-----------------------|---------------------|
| ...          | ...                   | ...                 |
```

> [!IMPORTANT]
> Chaque sous-système listé ici doit avoir (ou aura) son propre dossier `docs/<sous-système>/` avec les 5 documents de la méthode par métamodèle. Si un sous-système n'a pas de documentation métier, il n'est pas prêt à être implémenté.

### 5.5 Exemple de décomposition (application RH)

| Sous-système | Responsabilité | Concepts clés | Dépend de |
|-------------|----------------|---------------|-----------|
| Auth | Authentifier et autoriser les utilisateurs | User, Credential, Session, Role, Permission | — |
| Employés | Gérer les données des employés | Employee, Contract, Position, Department | Auth |
| Congés | Gérer les demandes et soldes | LeaveRequest, LeaveType, Balance, Approval | Employés, Auth |
| Paie | Calculer et éditer la paie | PayPeriod, Earning, Deduction, Slip | Employés, Congés |
| Notifications | Envoyer des notifications | Channel, Template, Recipient, Event | Auth |

> [!NOTE]
> La dépendance « Auth » signifie que le sous-système a besoin des identités définies dans Auth, pas que le code dépende techniquement d'Auth.

---

## 6. Niveau 2 : Architecture d'intégration

### 6.1 Finalité

Définir **comment les sous-systèmes communiquent** entre eux de manière cohérente et non-couplée.

### 6.2 Questions

- Quels **flux d'information** existent entre les sous-systèmes ?
- Quels sont les **protocoles de communication** ?
- Quelles **données** sont partagées et sous quelle forme ?
- Quels sont les **contrats** entre sous-systèmes ?
- Comment gérer les **incohérences temporaires** ?

### 6.3 Les modes d'intégration

Toute communication entre sous-systèmes doit suivre un des modes suivants :

| Mode | Description | Couplage | Utilisation typique |
|------|-------------|----------|-------------------|
| **Événement** | Un sous-système émet un événement, les autres réagissent | Faible | « Un congé a été approuvé » → notifier, mettre à jour le solde |
| **Requête** | Un sous-système demande une information à un autre | Moyen | « Quel est le solde de congés de cet employé ? » |
| **Commande** | Un sous-système demande à un autre d'exécuter une action | Moyen | « Créer une écriture comptable pour cette paie » |
| **Données partagées** | Deux sous-systèmes accèdent à la même donnée (via un store) | Fort | Un employé lu par Congés ET Paie (via un store central) |

#### 6.3.1 Règle de choix du mode

```
La donnée doit-elle être cohérente en temps réel ?
    ├── Oui → Données partagées (même store / même table)
    └── Non → Événement
                └── Un accusé réception est-il nécessaire ?
                    ├── Oui → Commande
                    └── Non → Événement simple
```

#### 6.3.2 Principe : un sous-système ne possède pas ses dépendances

Un sous-système définit les concepts qu'il expose, mais **c'est l'application** qui connecte les sous-systèmes entre eux, via un **adaptateur** :

```
[ Sous-système Congés ]                  [ Sous-système Notifications ]
        │                                        │
        │  Émet : « LeaveApproved »              │  Réagit à : LeaveApproved
        │                                        │
        └─────────────> Application <────────────┘
                             │
                        [Adaptateur : LeaveApproved → SendEmail]
```

### 6.4 Structure recommandée

```markdown
# Architecture d'intégration : [Application]

## Principes d'intégration
1. **Principe 1** : ...
2. **Principe 2** : ...

## Diagramme des flux
```
[Sous-système A] ──événement──> [Sous-système B] : LeaveApproved
[Sous-système B] ──requête────> [Sous-système C] : GetEmployeeBalance
[Sous-système C] ──commande───> [Sous-système D] : CreateAccountingEntry
```

## Contrats entre sous-systèmes

### Flux : [Nom du flux]

| Propriété | Valeur |
|-----------|--------|
| **De** | Sous-système source |
| **Vers** | Sous-système cible |
| **Mode** | Événement / Requête / Commande / Données partagées |
| **Déclencheur** | Quand est-ce émis ? |
| **Payload** | Structure de la donnée échangée |
| **Synchronisation** | Synchrone / Asynchrone |
| **Gestion d'erreur** | Que faire si l'échange échoue ? |

### Flux : [Autre flux]
...

## Tableau récapitulatif des flux

| Source | Cible | Mode | Payload | Asynchrone ? |
|--------|-------|------|---------|--------------|
| ...    | ...   | ...  | ...     | ...          |

## Données partagées

### [Concept partagé]
Définition de la donnée qui traverse les sous-systèmes (exemple : `Employee`).

| Propriété | Description |
|-----------|-------------|
| **Définition** | ... |
| **Propriétaire** | Sous-système qui en est la source de vérité |
| **Consommateurs** | Sous-systèmes qui le lisent |
| **Contrat** | Structure de la donnée |
```

> [!WARNING]
> Attention au « partage forcé » : si deux sous-systèmes partagent une même table ou un même store, ils sont fortement couplés. C'est un choix qui doit être délibéré et justifié.

---

## 7. Niveau 3 : Architecture applicative

### 7.1 Finalité

Définir la **structure technique** qui accueille tous les sous-systèmes : organisation du code, couches, dépendances, déploiement.

### 7.2 Questions

- Quelles sont les **couches techniques** de l'application ?
- Comment les sous-systèmes sont-ils **organisés dans le code** ?
- Quels sont les **composants partagés** ?
- Quel est le **flux de données** à travers l'application ?
- Comment l'application est-elle **déployée** ?

### 7.3 Les couches d'une application

Une application se compose de couches qui traversent tous les sous-systèmes :

```
┌──────────────────────────────────────────────────┐
│                   PRÉSENTATION                     │
│  (UI, composants, routage, formulaires, etc.)     │
├──────────────────────────────────────────────────┤
│                   APPLICATION                      │
│  (cas d'usage, orchestration, transactions)       │
├──────────────────────────────────────────────────┤
│                   DOMAINE                          │
│  (métier, règles, entités)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Auth    │  │ Employés │  │ Congés   │       │
│  └──────────┘  └──────────┘  └──────────┘       │
├──────────────────────────────────────────────────┤
│                INFRASTRUCTURE                      │
│  (persistence, API, filesystem, email, etc.)      │
└──────────────────────────────────────────────────┘
```

#### 7.3.1 Règles de dépendance entre couches

1. **La couche Domaine ne dépend de rien** — elle est pure
2. **La couche Application dépend du Domaine** — mais pas de l'Infrastructure
3. **La couche Infrastructure dépend du Domaine** — elle implémente ses interfaces
4. **La couche Présentation dépend de l'Application** — elle l'appelle, pas l'inverse

### 7.4 Organisation du code

#### 7.4.1 Structure par sous-système

```
src/
├── domains/                        ← Un dossier par sous-système
│   ├── auth/
│   │   ├── types.ts                ← Concepts du métamodèle
│   │   ├── use-cases/              ← Cas d'usage (Application layer)
│   │   └── infrastructure/          ← Implémentations techniques
│   ├── employees/
│   ├── leaves/
│   └── ...
├── shared/                          ← Code partagé entre sous-systèmes
│   ├── ui/                          ← Composants UI génériques
│   ├── lib/                         ← Helpers techniques
│   └── types/                       ← Types transverses
├── app/                             ← L'application qui assemble tout
│   ├── routes/                      ← Routage
│   ├── adapters/                    ← Adaptateurs entre sous-systèmes
│   ├── layout.svelte                ← Layout global
│   └── main.ts                     ← Point d'entrée
└── ...
```

#### 7.4.2 Règles de structure

1. **Un sous-système ne peut pas importer un autre sous-système directement** — il passe par l'application ou les adaptateurs
2. **Le dossier `shared/` contient uniquement du code générique** — pas de logique métier
3. **Les adaptateurs sont dans `app/`** — ce sont des décisions d'assemblage, pas de domaine

### 7.5 Structure recommandée

```markdown
# Architecture applicative : [Application]

## Stack technique
- **Framework** : ...
- **Base de données** : ...
- **Hébergement** : ...

## Diagramme des couches
```
[Diagramme des couches avec dépendances]
```

## Organisation du code
```
src/
  domains/
    <sous-système>/
      types.ts
      <use-cases>/
      <infrastructure>/
  shared/
    ui/
    lib/
  app/
    routes/
    adapters/
```

## Composants partagés
| Composant | Responsabilité | Utilisé par |
|-----------|---------------|-------------|
| ...       | ...           | ...         |

## Flux de données type
1. L'utilisateur interagit avec l'UI
2. Le routeur aiguille vers la page appropriée
3. La page appelle un use-case du sous-système
4. Le use-case orchestre la logique métier et les appels infrastructure
5. Le résultat est affiché dans l'UI
```

### 7.6 Exemple concret (Svelte + SvelteKit)

```typescript
// src/domains/leaves/types.ts — Concepts du métamodèle
interface LeaveRequest {
  id: string;
  employeeId: string;
  type: LeaveType;
  startDate: Date;
  endDate: Date;
  status: LeaveStatus;
}

// src/domains/leaves/use-cases/submit-leave.ts — Cas d'usage
async function submitLeave(
  request: LeaveRequest,
  notifier: NotificationPort    ← Port (interface) défini par le domaine
): Promise<Result> {
  // ... logique métier pure ...
  notifier.send({ type: 'leave.submitted', payload: request });
}

// src/app/adapters/notification-adapter.ts — Assemblage
// Implémente NotificationPort en appelant le sous-système Notifications
```

---

## 8. Le flux de conception pas à pas

### Étape 1 : Vision globale (Niveau 0)

**Durée** : 1 séance (2-4h)

**Actions** :
1. Rédiger la vision en une page
2. Lister les parties prenantes et leurs besoins
3. Identifier les contraintes majeures
4. Définir la roadmap macro

**Livrable** : `docs/application/vision-globale.md`

**Test** : Un nouvel arrivant lit le document en 5 minutes et sait à quoi sert l'application.

---

### Étape 2 : Carte des sous-systèmes (Niveau 1)

**Durée** : 1-2 séances

**Actions** :
1. Lister toutes les capacités métier
2. Grouper par affinité
3. Appliquer les critères de coupure
4. Nommer chaque sous-système
5. Identifier les dépendances entre sous-systèmes
6. Prioriser et identifier les exclus/différés

**Livrable** : `docs/application/carte-sous-systemes.md`

**Test** : Chaque sous-système a une responsabilité unique et non-ambiguë. Aucun concept clé n'est orphelin.

---

### Étape 3 : Conception des sous-systèmes

**Actions** : Pour chaque sous-système prioritaire, appliquer la [Méthode de conception par métamodèle](conception-par-metamodele.md) :

1. `docs/<sous-système>/vision.md`
2. `docs/<sous-système>/metamodel.md`
3. `docs/<sous-système>/semantics.md`
4. `docs/<sous-système>/catalogue.md`
5. `docs/<sous-système>/api.md`

**Ordre recommandé** : Commencer par le sous-système le plus indépendant (souvent Auth ou Employés), puis ceux qui en dépendent.

---

### Étape 4 : Architecture d'intégration (Niveau 2)

**Durée** : 1 séance

**Actions** :
1. Pour chaque paire de sous-systèmes liés : définir le flux
2. Choisir le mode d'intégration (événement, requête, commande, partagé)
3. Définir les contrats (payload, synchronisation, erreur)
4. Identifier les données partagées et leur source de vérité

**Livrable** : `docs/application/architecture-integration.md`

**Test** : On peut répondre à « Que se passe-t-il si le sous-système B est injoignable ? » pour chaque flux.

---

### Étape 5 : Architecture applicative (Niveau 3)

**Durée** : 1 séance

**Actions** :
1. Définir les couches techniques
2. Organiser le code par sous-système
3. Identifier les composants partagés
4. Définir les règles de dépendance
5. Écrire un exemple de flux de bout en bout

**Livrable** : `docs/application/architecture-technique.md`

**Test** : Un développeur peut créer un nouveau sous-système en suivant la structure sans hésitation.

---

### Étape 6 : Validation par des scénarios globaux

**Actions** :
1. Prendre un **cas d'usage réel multi-sous-systèmes**
2. Tracer le flux complet (UI → domaine → intégration → infrastructure)
3. Vérifier que chaque étape est couverte par un document
4. Si un scénario n'est pas réalisable, revenir aux étapes 2, 3 ou 4

**Exemple de scénario global RH** :
> « Un manager approuve une demande de congé. → Le solde est mis à jour. → L'employé reçoit une notification. → L'absence est transmise à la paie. → Un événement est horodaté dans le journal d'audit. »

**Sous-systèmes impliqués** : Congés, Employés, Notifications, Paie, Audit.

**Test** : Le scénario peut être tracé sans ambiguïté à travers les documents.

---

### Schéma récapitulatif du flux

```
┌──────────────────────────────────────────────────────┐
│  Étape 1 : Vision globale                             │
│  ↓                                                   │
├──────────────────────────────────────────────────────┤
│  Étape 2 : Carte des sous-systèmes                   │
│  ↓                                                   │
├──────────────────────────────────────────────────────┤
│  Étape 3 : Conception de chaque sous-système         │
│  │  (méthode par métamodèle pour chaque boîte)       │
│  ↓                                                   │
├──────────────────────────────────────────────────────┤
│  Étape 4 : Architecture d'intégration                │
│  ↓                                                   │
├──────────────────────────────────────────────────────┤
│  Étape 5 : Architecture applicative                  │
│  ↓                                                   │
├──────────────────────────────────────────────────────┤
│  Étape 6 : Validation par scénarios globaux          │
│  ↓                                                   │
└──────────────────────────────────────────────────────┘
         │
         ▼
     Implémentation
```

---

## 9. États de maturité et Definition of Done

### 9.1 États de maturité des documents d'architecture

| État | Signification | Actions possibles |
|------|---------------|-------------------|
| **📝 Ébauche** | Idées en cours, découpage non stabilisé | Modification libre |
| **🔍 En révision** | Relu par les parties prenantes | Feedback, ajustements |
| **✅ Stabilisé** | Validé sur les scénarios globaux | Ne change que si un nouveau cas le force |
| **🔄 Évolution** | Un changement de conception impacte ce document | Propagation aux documents dépendants |

```
Ébauche → Révision → Stabilisé
    ↑                       ↓
    └──← Nouveau scénario global ←──┘
```

### 9.2 Definition of Done de l'architecture

À quel moment l'architecture est-elle suffisamment spécifiée pour commencer l'implémentation ?

- [ ] La **vision globale** est validée par les parties prenantes
- [ ] La **carte des sous-systèmes** est complète (pas de concept orphelin)
- [ ] Chaque flux d'intégration critique a un **contrat défini** (payload, gestion d'erreur)
- [ ] L'organisation du code est **décrite et justifiée**
- [ ] Au moins **1 scénario global** a été tracé de bout en bout
- [ ] Aucune question *« comment ce sous-système accède-t-il à cette donnée ? »* sans réponse
- [ ] Les documents sont dans l'état **✅ Stabilisé**

> Ces critères sont une grille, pas une obligation absolue. Pour un petit projet (2-3 sous-systèmes), un sous-ensemble peut suffire.

---

## 10. Les invariants de la méthode

### Invariant 1 : Autonomie des sous-systèmes
> **Un sous-système ne dépend pas d'un autre sous-système au niveau du domaine.**
> Les dépendances sont des choix d'intégration, pas des contraintes du métamodèle.

### Invariant 2 : Frontières explicites
> **Chaque concept appartient à un et un seul sous-système.**
> Si un concept est utilisé dans plusieurs sous-systèmes, l'un d'eux en est le propriétaire (source de vérité).

### Invariant 3 : Communication par contrat
> **Toute communication entre sous-systèmes passe par un contrat explicite.**
> Pas d'appel direct entre sous-systèmes : toujours un adaptateur, un événement ou une interface.

### Invariant 4 : Le domaine est pur
> **La couche domaine ne dépend d'aucune infrastructure.**
> Elle définit des interfaces (ports) que l'infrastructure implémente. Inversion de dépendance.

### Invariant 5 : Priorité au métier
> **L'organisation du code suit le métier, pas la technologie.**
> On groupe par sous-système d'abord, par couche technique ensuite. Pas de dossiers `components/`, `pages/`, `utils/` au niveau racine.

### Invariant 6 : Cohérence entre niveaux
> **Tout changement dans un niveau doit être répercuté dans les documents des autres niveaux.**
> Si la carte des sous-systèmes change, l'architecture d'intégration et l'architecture applicative doivent être mises à jour.

---

## 11. Relations entre les deux méthodes

### 11.1 Correspondance des documents

```
Architecture applicative (ce document)         Méthode par métamodèle
─────────────────────────────────              ───────────────────────

vision-globale.md                               → vision.md (de chaque sous-système)
    |                                                |
    |  Définit la raison d'être                  |   Définit la raison d'être
    |  de l'application entière                  |   du sous-système
    |
carte-sous-systemes.md                          → cadre de chaque metamodel.md
    |                                                |
    |  Liste les sous-systèmes                  |   Définit les concepts
    |  et leurs frontières                      |   de chaque sous-système
    |
architecture-integration.md                     → sémantique des interactions
    |                                                |
    |  Contrats entre sous-systèmes             |   Définit des interactions
    |                                            |   au sein d'un sous-système
    |
architecture-technique.md                       → api.md
    |                                                |
    |  Structure du code global                 |   Structure du code
    |                                            |   du sous-système
```

### 11.2 Utilisation combinée

| Situation | Utiliser |
|-----------|----------|
| Vous démarrez un nouveau projet | Commencer par l'architecture applicative (vision → carte), puis la méthode par métamodèle pour chaque sous-système |
| Vous ajoutez un sous-système à un projet existant | Mettre à jour la carte, puis appliquer la méthode par métamodèle pour le nouveau sous-système |
| Vous refactorez une application existante | Commencer par la carte des sous-systèmes (état actuel), puis appliquer la méthode par métamodèle pour chaque sous-système réécrit |
| Vous avez un problème d'intégration | Aller directement à l'architecture d'intégration |

### 11.3 Exemple combiné

Pour une application RH :

```
docs/
├── methodologie/
│   ├── conception-par-metamodele.md          ← Comment concevoir un sous-système
│   └── architecture-applicative.md           ← Comment assembler l'application
│
└── application/
    ├── vision-globale.md                     ← Pourquoi l'app RH existe
    ├── carte-sous-systemes.md                ← Quels sous-systèmes (Auth, Employés, Congés...)
    ├── architecture-integration.md           ← Comment ils communiquent
    ├── architecture-technique.md             ← Structure SvelteKit + Supabase
    │
    ├── auth/
    │   ├── vision.md
    │   ├── metamodel.md
    │   ├── semantics.md
    │   ├── catalogue.md
    │   └── api.md
    │
    ├── employees/
    │   └── ...
    │
    ├── leaves/
    │   └── ...
    │
    └── ...
```

---

## 12. Collaboration et modalités de travail

### 12.1 À qui s'adresse cette méthode ?

| Rôle | Implication |
|------|-------------|
| **Architecte** | Garantit la cohérence globale, tranche sur les choix d'intégration |
| **Concepteur** | Rédige les documents d'architecture d'intégration et applicative |
| **Développeur·se** | Relit les documents, implémente les sous-systèmes, signale les incohérences |
| **Product Owner / Métier** | Valide la vision globale et les scénarios de validation |

### 12.2 Modalités de travail recommandées

**Pour l'architecture initiale (sprint de cadrage 3-5 jours)** :
1. **Atelier vision** (2h) : toutes les parties prenantes, définir la vision
2. **Atelier découpage** (3h) : l'équipe technique liste et groupe les capacités
3. **Rédaction individuelle** (1 jour) : l'architecte rédige carte + intégration
4. **Revue technique** (2h) : l'équipe critique le découpage et les flux
5. **Validation métier** (1h) : le PO valide que les scénarios sont couverts

**Pour un changement d'architecture** :
1. **Issue / RFC** décrivant le besoin
2. **Proposition de modification** — PR sur les documents concernés
3. **Revue** — architecte + équipe
4. **Mise à jour** — propagation aux documents dépendants

### 12.3 Règles de collaboration

- **Les frontières se discutent** — Si deux sous-systèmes ont un chevauchement flou, c'est le signe que la carte n'est pas mûre.
- **Les modes d'intégration se décident collectivement** — le choix événement vs commande a un impact fort sur la complexité.
- **Tout désaccord sur l'architecture se tranche par un scénario global** — pas par une opinion.
- **Les ADR tracent les décisions difficiles** — pour ne pas re-débattre 3 mois plus tard.

---

## 13. ADR — Traçabilité des décisions

### 13.1 Pourquoi des ADR dans l'architecture applicative ?

Les 4 documents d'architecture décrivent **le résultat** des décisions, pas **le cheminement**. Les ADR sont le complément qui garde la mémoire des choix importants :

- Pourquoi tel mode d'intégration plutôt qu'un autre ?
- Pourquoi ce sous-système a-t-il été éclaté (ou fusionné) ?
- Pourquoi ce choix technologique (base de données, framework) ?
- Pourquoi ce protocole de communication (REST vs événements vs GraphQL) ?

### 13.2 Structure d'un ADR

```markdown
# ADR-004: [Titre — ex: Communication entre Congés et Paie]

## Date
YYYY-MM-DD

## Contexte
Pourquoi cette décision est-elle nécessaire ?

## Décision
Qu'avons-nous choisi ?

## Alternatives envisagées
- **Alternative A** : avantages / inconvénients
- **Alternative B** : avantages / inconvénients

## Conséquences
- Impact sur la carte des sous-systèmes
- Impact sur l'architecture d'intégration
- Ce qui est facilité / rendu plus difficile

## Statut
Accepté / Proposé / Déprécié / Remplacé par ADR-XXX
```

### 13.3 Où les stocker ?

```
docs/
├── decisions/
│   ├── ADR-001-choix-mode-evenement.md
│   ├── ADR-002-fusion-conges-paie.md
│   ├── ADR-003-choix-supabase.md
│   └── README.md                    ← Index des ADR
└── application/                      ← Documents d'architecture
    └── ...
```

> [!TIP]
> Un bon ADR pour l'architecture applicative répond à la question : **« Pourquoi avons-nous fait ce choix plutôt qu'un autre ? »** Pas besoin de longues justifications — faites 5-15 lignes.

---

## 14. Anti-patterns courants

### Anti-pattern 1 : Sous-système technique déguisé en sous-système métier

**Symptôme** : Un sous-système s'appelle « UI », « API », « Database » ou « Components ».

**Problème** : La carte des sous-systèmes doit refléter le métier, pas la technique. Ce sont des couches, pas des sous-systèmes.

**Solution** : Déplacer ces préoccupations dans l'architecture applicative (Niveau 3). Les sous-systèmes sont toujours métier (Employés, Congés, Paie) ou techniques transverses (Auth, Notifications, Audit).

### Anti-pattern 2 : Sous-système fourre-tout

**Symptôme** : Un sous-système « Core », « Common » ou « Shared » qui contient trop de concepts hétérogènes.

**Problème** : Ce sous-système devient un point de couplage fort et perd sa cohérence.

**Solution** : Le vider progressivement en extrayant chaque concept dans son propre sous-système. Un sous-système doit pouvoir se décrire en une phrase.

### Anti-pattern 3 : Intégration par accès direct

**Symptôme** : Un use-case d'un sous-système importe directement un type ou une fonction d'un autre sous-système.

**Problème** : Les sous-systèmes deviennent fortement couplés. On ne peut plus les modifier indépendamment.

**Solution** : Passer par un adaptateur ou un port défini dans l'application. Application de l'inversion de dépendance.

### Anti-pattern 4 : Niveaux mélangés

**Symptôme** : Le document `carte-sous-systemes.md` contient des décisions techniques (base de données, framework).

**Problème** : Chaque niveau répond à une question différente. Les mélanger crée de la confusion.

**Solution** : Séparer strictement : Niveau 1 = métier, Niveau 2 = interactions, Niveau 3 = technique. Si une information ne correspond pas au niveau, la déplacer.

### Anti-pattern 5 : Sous-systèmes trop petits

**Symptôme** : Des sous-systèmes avec un seul concept ou une seule responsabilité (ex : « Adresses », « Codes postaux »).

**Problème** : Trop de sous-systèmes rend l'architecture ingérable. Le coût d'intégration dépasse le bénéfice.

**Solution** : Regrouper les petits concepts dans un sous-système plus large tant qu'ils restent cohérents. Un sous-système doit être suffisamment gros pour justifier sa propre documentation et son cycle de vie.

### Anti-pattern 6 : Diagramme sans contrat

**Symptôme** : L'architecture d'intégration montre des flèches entre sous-systèmes mais ne définit pas le contenu des échanges.

**Problème** : Les flèches donnent une illusion de conception. En pratique, chaque développeur interprète l'échange à sa façon.

**Solution** : Chaque flèche doit être accompagnée d'un contrat (payload, déclencheur, synchronisation, gestion d'erreur). Sans contrat, ce n'est pas une conception.

---

> **Dernier conseil** : L'architecture applicative et la méthode par métamodèle sont les deux faces d'une même pièce. L'une conçoit l'assemblage, l'autre conçoit les pièces. Ne faites jamais l'une sans l'autre.
