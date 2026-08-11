# Méthode de conception par métamodèle

> **Une approche universelle** pour concevoir des sous-systèmes logiciels complexes en séparant les concepts métier de leur implémentation technique.
>
> Inspirée de la **Model-Driven Architecture (MDA)** et du **Domain-Driven Design (DDD)**.

---

## Quickstart : appliquer la méthode dès maintenant

> Vous n'avez pas le temps de lire 50 pages ? Voici le strict minimum.

1. **Créez `docs/<sous-système>/metamodel.md`** — Listez 3 à 5 concepts clés, leurs relations, et un cycle de vie.
2. **Ajoutez `semantics.md`** — Prenez 2 propriétés ambiguës et écrivez leur définition précise.
3. **Ajoutez `catalogue.md`** — Décrivez 2 types concrets avec des exemples.
4. **Testez avec un cas réel** — Écrivez une configuration complète qui utilise vos concepts.
5. **Ça marche ?** Ajoutez l'API. **Ça coince ?** Revenez au métamodèle.

> [!TIP]
> Le Quickstart vous donne un **feedback immédiat** sur la solidité de vos concepts. Si vous bloquez à l'étape 4, c'est que votre métamodèle n'est pas prêt.

---

## Table des matières

1. [Pourquoi cette méthode ?](#1-pourquoi-cette-méthode)
2. [Le principe fondamental](#2-le-principe-fondamental)
3. [Les 5 documents de conception](#3-les-5-documents-de-conception)
4. [Le flux de conception pas à pas](#4-le-flux-de-conception-pas-à-pas)
5. [États de maturité et Definition of Done](#5-états-de-maturité-et-definition-of-done)
6. [Les invariants de la méthode](#6-les-invariants-de-la-méthode)
7. [Guide de décision : quand l'utiliser ?](#7-guide-de-décision-quand-lutiliser)
8. [Collaboration et modalités de travail](#8-collaboration-et-modalités-de-travail)
9. [Checklist pour chaque document](#9-checklist-pour-chaque-document)
10. [Correspondance MDA](#10-correspondance-mda)
11. [ADR — Traçabilité des décisions](#11-adr--traçabilité-des-décisions)
12. [Anti-patterns courants](#12-anti-patterns-courants)
13. [Annexes](#13-annexes)

---

## 1. Pourquoi cette méthode ?

### 1.1 Le constat

Trop souvent, la conception d'un sous-système logiciel commence par l'écriture de code :

1. On crée des composants UI (React, Svelte, Vue)
2. On ajoute de la logique métier dispersée dans ces composants
3. On découvre des incohérences quand les cas limites se présentent
4. On refait trois fois la même chose parce que les concepts n'étaient pas stabilisés

**Résultat** : une implémentation fragile, difficile à étendre, et qui ne se prête pas au changement de technologie.

### 1.2 La promesse

Cette méthode propose de **remonter d'un cran dans l'abstraction** avant d'écrire la moindre ligne de code. Elle permet de :

- **Stabiliser les concepts métier** avant de les implémenter
- **Détecter les incohérences** au niveau du design, pas du code
- **Réutiliser les décisions** entre sous-systèmes similaires
- **Changer de technologie** sans repenser tout le domaine
- **Communiquer avec les non-techniciens** sur le cœur du problème

---

## 2. Le principe fondamental

> **Décrire ce que l'on veut, pas comment le réaliser.**

Au lieu de commencer par les technologies (composants, hooks, stores, frameworks), on commence par décrire **le domaine** avec des concepts purs, indépendants de toute technologie.

```
Concepts du domaine (métamodèle)
        │
        ▼
Modèle concret (types, exemples)
        │
        ▼
API et implémentation (code)
```

Chaque couche est une **transformation** de la précédente, pas une réécriture.

### 2.1 Les trois niveaux d'abstraction

| Niveau | Question | Produit | Indépendant de |
|--------|----------|---------|----------------|
| Conceptuel | Quels sont les concepts métier ? | Métamodèle | Toute technologie |
| Concret | Quels sont les types et cas d'usage ? | Catalogue | Framework spécifique |
| Technique | Comment l'écrire en code ? | API, implémentation | Rien (c'est le code) |

### 2.2 Analogie : l'architecture d'un bâtiment

| Domaine | Étape | Résultat |
|---------|-------|----------|
| Bâtiment | Programme architectural | « Un immeuble de 5 étages avec 3 appartements par étage » |
| Bâtiment | Plans d'architecte | Plans détaillés (indépendants des matériaux) |
| Bâtiment | Plans d'exécution | Plans avec matériaux, câblage, plomberie |
| Logiciel | Métamodèle | Les concepts métier |
| Logiciel | Catalogue | Les types concrets |
| Logiciel | API | L'interface de programmation |

---

## 3. Les 5 documents de conception

### 3.1 Vision (`vision.md`) — Pourquoi ?

**Finalité** : Justifier l'existence du système, aligner les parties prenantes, cadrer le périmètre.

**Questions** :
- Quel problème résout-on exactement ?
- Pourquoi les solutions existantes ne suffisent-elles pas ?
- Quels sont les objectifs (SMART) ?
- Quels sont les non-objectifs (ce qu'on ne fera pas) ?
- Quelle est la roadmap envisagée ?

**Structure recommandée** :

```markdown
# Vision : [Nom du système]

## Pourquoi ce système ?
Constat, problèmes identifiés, opportunité

## Objectifs
### Objectif principal
En une phrase, quel est le bénéfice ultime ?

### Objectifs secondaires
- Objectif mesurable
- Objectif qualitatif

## Principes directeurs
1. **Principe 1** — Explication courte
2. **Principe 2** — Explication courte

## Parties prenantes
| Rôle | Attente principale |
|------|-------------------|
| ...  | ...               |

## Périmètre
### Dans le périmètre
- Feature A
- Feature B

### Hors périmètre
- Feature X (pourquoi)
- Feature Y (pourquoi)

## Roadmap
| Version | Fonctionnalités | Échéance |
|---------|----------------|----------|
| V0.1    | ...            | ...      |
| V1.0    | ...            | ...      |
| V2.0    | ...            | ...      |
```

> [!TIP]
> La vision est le seul document qui peut être lu par des non-techniciens. Rédigez-le dans un langage accessible.

---

### 3.2 Métamodèle (`metamodel.md`) — Quoi ?

**Finalité** : Définir les concepts fondamentaux du domaine, leurs propriétés, leurs relations, leur cycle de vie et les invariants.

**Questions** :
- Quels sont les concepts fondamentaux de mon domaine ?
- Quelles sont leurs propriétés essentielles ?
- Quelles sont leurs relations ?
- Quel est leur cycle de vie ?
- Quels sont les invariants (règles toujours vraies) ?

**Structure recommandée** :

```markdown
# Métamodèle : [Nom du système]

## Cartographie des concepts
[Diagramme ou tableau récapitulatif des concepts et leurs liens]

---

## Concept : [Nom du concept]

### Définition
Une phrase qui définit le concept sans référence à la technologie.
> *Exemple : « Un `Field` est une unité atomique de donnée présentée à l'utilisateur pour saisie, sélection ou lecture. »*

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| ... | ...  | oui/non | ...         |

### Relations
```
[Concept A] ──1──>* [Concept B] (Un A contient plusieurs B)
[Concept B] ──*──>* [Concept C] (Un B référence plusieurs C)
```

### Cycle de vie
```
[Cette étape] ──(condition)──> [Étape suivante]
```

| Étape | Description | Événement déclencheur |
|-------|-------------|-----------------------|
| 1. ... | ...        | ...                   |
| 2. ... | ...        | ...                   |
| 3. ... | ...        | ...                   |

### Invariants
- **Règle 1** : Description de la règle.
- **Règle 2** : Description de la règle.

### Exemple concret
Un exemple court qui illustre le concept.
```

> [!IMPORTANT]
> **Le métamodèle est le document le plus important.** Prenez le temps de le stabiliser avant de passer aux documents suivants. Un défaut dans le métamodèle se répercute dans tous les autres documents.

---

### 3.3 Sémantique (`semantics.md`) — Signification

**Finalité** : Lever toute ambiguïté sur la signification de chaque propriété, état et événement.

**Questions** :
- Que signifie exactement chaque propriété ?
- Dans quel ordre les événements se déclenchent-ils ?
- Que se passe-t-il dans les cas limites ?
- Comment les propriétés interagissent-elles entre elles ?

**Structure recommandée** :

```markdown
# Sémantique : [Nom du système]

Chaque section précise la signification exacte d'une propriété, d'un état
ou d'un événement du métamodèle.

---

## [Propriété / État / Événement]

### Définition précise
Ce que ça signifie, pas ce que ça fait.

### Règles
- **Condition d'application** : Dans quelles circonstances cette propriété s'applique-t-elle ?
- **Valeur par défaut** : Quelle est la valeur si non spécifiée ?
- **Précédence** : Que se passe-t-il si cette propriété entre en conflit avec une autre ?

### Valeurs "limites"
- Que signifie « absent » pour cette propriété ?
- Que signifie « vide » pour cette propriété ?
- Que signifie « invalide » pour cette propriété ?

### Interactions
| Propriété | Interaction | Comportement résultant |
|-----------|-------------|------------------------|
| ...       | ...         | ...                    |
| ...       | ...         | ...                    |

### Cas particuliers
- **Cas 1** : Situation et comportement attendu.
- **Cas 2** : Situation et comportement attendu.
```

> [!WARNING]
> La sémantique est souvent négligée parce qu'elle semble « évidente ». C'est pourtant là que se cachent la plupart des bugs futurs. Une propriété `required` n'est pas aussi simple qu'il n'y paraît : que signifie « absent » ? Quand est-ce vérifié ? Que faire des champs invisibles ?

---

### 3.4 Catalogue (`catalogue.md`) — Concret

**Finalité** : Faire le pont entre les concepts abstraits du métamodèle et les types concrets du projet.

**Questions** :
- Quels sont les types concrets dans mon domaine ?
- Quels sont leurs comportements par défaut ?
- Comment s'affichent-ils (si pertinent) ?
- Quels cas d'usage peut-on construire ?

**Structure recommandée** :

```markdown
# Catalogue : [Nom du système]

## Tableau récapitulatif des types

| Type | Concept parent | Description | Utilisation typique |
|------|----------------|-------------|-------------------|
| ...  | ...            | ...         | ...               |

---

### [Type concret]

| Propriété | Valeur |
|-----------|--------|
| Description | ... |
| Concept parent | ... |
| Valeur par défaut | ... |
| Comportements par défaut | ... |
| Validation | ... |
| Renderer associé | ... |

**Dépendances** : ...
**Correspondance code** : [fichier ou module]

---

## Exemples d'utilisation

### Exemple 1 : [Titre]
```[langage]
Configuration complète d'un cas d'usage réel
```

### Exemple 2 : [Titre]
```[langage]
Second cas d'usage, différent du premier
```
```

> [!TIP]
> Chaque type du catalogue doit avoir une correspondance claire avec le code existant ou planifié. Si ce n'est pas le cas, le catalogue est trop abstrait.

---

### 3.5 API (`api.md`) — Syntaxe

**Finalité** : Définir exactement comment le développeur va utiliser le système, avec des interfaces, des signatures et des exemples.

**Questions** :
- Quelle est la syntaxe que le développeur va écrire ?
- Quels sont les helpers disponibles ?
- Quel est l'état exposé au runtime ?
- Comment s'effectue la configuration ?

**Structure recommandée** :

```markdown
# API : [Nom du système]

## Prélude : philosophie de l'API
En une phrase, quel est le style de l'API ?
> *Exemple : « L'API privilégie la configuration déclarative et
>   masque toute la gestion d'état interne. »*

---

## Fonctions principales

### `[nomFonction]`

**Signature**
```typescript
function nomFonction(config: ConfigType): ReturnType
```

**Paramètres**
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| ... | ...  | oui/non | ...         |

**Retour**
Description de l'objet retourné, avec ses propriétés et méthodes.

**Exemple**
```typescript
// Exemple d'utilisation complet et commenté
```

---

## Helpers

### `[nomHelper]`
Description courte, signature et exemple.

---

## Hooks / Événements

| Événement | Déclencheur | Payload |
|-----------|-------------|---------|
| ...       | ...         | ...     |

---

## Exemple complet

```typescript
// Un exemple qui utilise l'API de bout en bout
// pour réaliser un cas d'usage réel
```
```

> [!IMPORTANT]
> L'API doit découler **naturellement** du métamodèle. Si l'API est contre-intuitive ou verbeuse, c'est le métamodèle qu'il faut revoir, pas l'API.

---

## 4. Le flux de conception pas à pas

### Étape 1 : Définir le métamodèle

**Durée estimée** : 30-50% du temps total de conception.

**Actions** :
1. Lister tous les **concepts** du domaine sur un tableau blanc ou un document
2. Nommer chaque concept avec un terme précis (pas de synonymes)
3. Définir chaque concept en **une phrase** (pas de détails techniques)
4. Dessiner les **relations** entre concepts (1-1, 1-n, n-m)
5. Identifier les **invariants** (règles qui doivent toujours être vraies)
6. Décrire le **cycle de vie** de chaque concept

**Livrable** : `metamodel.md`

> [!NOTE]
> **Test de validation** : Un collègue métier (non technicien) doit pouvoir lire et comprendre le métamodèle. Si ce n'est pas le cas, les concepts sont trop techniques ou mal nommés.

---

### Étape 2 : Écrire la sémantique

**Actions** :
1. Prendre chaque propriété du métamodèle
2. Pour chacune, écrire une **définition précise** (pas de description vague)
3. Lister les **cas particuliers** (valeurs nulles, vides, limites)
4. Décrire les **interactions** avec les autres propriétés
5. Documenter l'**ordre de déclenchement** des événements

**Livrable** : `semantics.md`

**Exemple de travail sur une propriété** :

> Propriété : `required`
> - Définition : Un champ required est invalide si sa valeur est absente au moment où une validation est déclenchée.
> - Valeur « absente » dépend du type de champ
> - Interaction avec `disabled` : pas validé
> - Interaction avec `readonly` : validé normalement
> - Interaction avec la visibilité : pas validé si masqué

---

### Étape 3 : Créer le catalogue

**Actions** :
1. Lister tous les **types concrets** du domaine
2. Pour chaque type : description, renderer, valeur, comportements, validation
3. Écrire des **exemples complets** d'utilisation
4. Indiquer la **correspondance avec le code** existant

**Livrable** : `catalogue.md`

**Astuce** : Le catalogue est l'endroit où l'on valide que le métamodèle est **complet** : si un type concret ne peut pas être décrit avec les concepts du métamodèle, c'est qu'il manque un concept.

---

### Étape 4 : Définir l'API

**Actions** :
1. Déduire la syntaxe des concepts du métamodèle
2. Créer des **fonctions factories** pour chaque type concret
3. Définir les **interfaces** TypeScript complètes
4. Écrire un **exemple complet** qui utilise l'API

**Livrable** : `api.md`

---

### Étape 5 : Valider par les exemples

**Actions** :
1. Prendre un **cas d'usage réel** du projet
2. L'écrire en utilisant l'API définie
3. Vérifier que l'écriture est **naturelle et concise**
4. Si ce n'est pas le cas, **revenir au métamodèle** pour le modifier en conséquence

**Règle d'or** : Si l'API n'est pas agréable à écrire, c'est le métamodèle qu'il faut améliorer, pas l'API.

**Boucle de rétroaction** :

```
Métamodèle ← Catalogue ← API ← Exemples
    └─────────────── Retour ──────────────────┘
```

---

### Schéma récapitulatif du flux

```
┌──────────────────────────────────────────────────────┐
│  Étape 1 : Métamodèle ────> metamodel.md              │
│  ↓ Répond à « Quoi ? »                               │
├──────────────────────────────────────────────────────┤
│  Étape 2 : Sémantique ────> semantics.md              │
│  ↓ Lève les ambiguïtés                               │
├──────────────────────────────────────────────────────┤
│  Étape 3 : Catalogue ────> catalogue.md               │
│  ↓ Concrétise les abstractions                       │
├──────────────────────────────────────────────────────┤
│  Étape 4 : API ────> api.md                           │
│  ↓ Définit la syntaxe                                │
├──────────────────────────────────────────────────────┤
│  Étape 5 : Validation par exemples                    │
│  ↓ Valide ou fait revenir en arrière                 │
└──────────────────────────────────────────────────────┘
         │
         ▼
     Implémentation
```

---

## 5. États de maturité et Definition of Done

### 5.1 États de maturité d'un document

La conception n'est jamais « finie » du premier coup. Chaque document traverse des états :

| État | Signification | Actions possibles |
|------|---------------|-------------------|
| **📝 Ébauche** | Idées en cours, structure non stabilisée | Modification libre, exploration |
| **🔍 En révision** | Relu par un pair / l'équipe | Modifications sous discussion, feedback |
| **✅ Stabilisé** | Validé sur des cas réels | Ne change que si un nouveau cas le force |
| **🔄 Évolution** | Un changement validé nécessite une mise à jour | Mettre à jour les documents dépendants |

```
Ébauche → Révision → Stabilisé
    ↑                       ↓
    └──← Nouveau cas réel ←──┘
```

> [!IMPORTANT]
> Un document « Stabilisé » n'est pas figé. Il peut toujours évoluer, mais chaque changement doit être justifié par un **cas réel** qui n'était pas couvert.

### 5.2 Definition of Done de la conception

À quel moment peut-on considérer qu'un sous-système est **suffisamment conçu** pour être implémenté ?

- [ ] Chaque concept du métamodèle a **au moins 1 exemple concret** dans le catalogue
- [ ] L'API a été **testée sur 3 cas d'usage réels** différents
- [ ] Aucune question du type *« que se passe-t-il si… ? »* n'est restée sans réponse dans la sémantique
- [ ] Un développeur, sans l'auteur, peut **implémenter un proto sans ambiguïté**
- [ ] Un non-technicien (métier) a **confirmé que le métamodèle reflète le domaine**
- [ ] Les documents sont dans l'état **✅ Stabilisé**

> Ces critères sont une **grille**, pas une obligation absolue. Adaptez-les au contexte (taille de l'équipe, criticité du sous-système, délais).

---

## 6. Les invariants de la méthode

Ces règles sont **indépendantes du domaine** et s'appliquent à toute utilisation de la méthode :

### Invariant 1 : Non-dépendance technologique
> **Le métamodèle ne dépend d'aucune technologie.**
> Pas de TypeScript, pas de Svelte/React, pas de HTML, pas de nom de framework. Les concepts doivent être exprimables avec un vocabulaire métier.

### Invariant 2 : Non-recouvrement sémantique
> **Chaque concept a une définition unique et exclusive.**
> Deux concepts ne doivent pas avoir des définitions qui se chevauchent. Si `Field` et `Input` décrivent la même chose, un seul doit exister.

### Invariant 3 : Primauté de la sémantique sur la syntaxe
> **Définir d'abord ce que ça signifie, ensuite comment l'écrire.**
> Ne jamais décider de la syntaxe avant d'avoir stabilisé le sens. Une API bien nommée mais mal pensée est pire qu'une API mal nommée mais bien pensée.

### Invariant 4 : Validation par les exemples
> **Les exemples précèdent l'implémentation.**
> On valide le design par des cas concrets avant d'écrire le moindre code de production. Si un cas d'usage réel ne peut pas être exprimé, le design est incomplet.

### Invariant 5 : Le catalogue comme pont
> **Le catalogue fait le lien entre concepts abstraits et types concrets.**
> Sans catalogue, le métamodèle reste trop théorique et l'API trop éloignée du domaine.

### Invariant 6 : Cohérence cyclique
> **Tout changement dans un document doit être répercuté dans les autres.**
> Si la sémantique évolue, le métamodèle, le catalogue et l'API doivent être mis à jour en conséquence.

---

## 7. Guide de décision : quand l'utiliser ?

### ✅ Quand utiliser cette méthode

Le tableau suivant aide à décider si la méthode est adaptée à votre situation :

| Situation | Indice | Méthode adaptée ? |
|-----------|--------|-------------------|
| Vous concevez un sous-système métier avec des concepts riches | Workflow, formulaire dynamique, moteur de règles | ✅ **Oui** |
| Vous voulez créer une API qui masque la complexité technique | Bibliothèque, framework, SDK | ✅ **Oui** |
| Plusieurs features partagent des patterns communs | Validation, notification, état | ✅ **Oui** |
| Vous anticipez des changements de technologie | Migration Svelte → React, web → mobile | ✅ **Oui** |
| L'équipe a du mal à se mettre d'accord sur les concepts | Désaccords récurrents sur le vocabulaire | ✅ **Oui** |
| Le système doit être documenté pour des non-techniciens | Documentation pour le métier | ✅ **Oui** |
| Vous faites un simple CRUD | Liste de tâches, blog | ❌ **Non** |
| Vous concevez un utilitaire technique | Helper de formatage, fonction mathématique | ❌ **Non** |
| Vous devez livrer rapidement un prototype | Hackathon, POC jetable | ❌ **Non** (trop lourd) |
| Le domaine est déjà parfaitement compris par toute l'équipe | Aucune ambiguïté | ❌ **Non** (surdimensionné) |

### Règle empirique

> Si vous pouvez décrire le système en moins de 10 minutes avec des concepts qui ne changent pas, la méthode est trop lourde.
>
> Si vous sentez que les concepts sont « glissants » et que l'équipe n'arrive pas à stabiliser le vocabulaire, la méthode est adaptée.

---

## 8. Collaboration et modalités de travail

### 8.1 À qui s'adresse cette méthode ?

| Rôle | Implication |
|------|-------------|
| **Concepteur / Designer** | Rédige les documents, applique la méthode |
| **Développeur·se** | Relit le métamodèle, valide l'API, implémente |
| **Métier / Product Owner** | Valide la vision et le métamodèle |
| **Pair reviewer** | Relit les documents, traque les ambiguïtés |
| **Architecte** | Garantit la cohérence entre sous-systèmes |

### 8.2 Modalités de travail recommandées

**Pour un nouveau sous-système (design sprint 2-5 jours)** :
1. **Session de cadrage** (2h) : vision + premiers concepts — avec le métier
2. **Rédaction individuelle** (1-2 jours) : l'auteur rédige metamodel + semantics
3. **Revue en équipe** (2h) : tout le monde lit et critique le métamodèle
4. **Ajustements** (0.5 jour) : corrections suite à la revue
5. **Catalogue + API** (1 jour) : l'auteur rédige
6. **Validation par cas réels** (2h) : on teste avec des cas d'usage concrets

**Pour un sous-système existant (évolution)** :
1. **Identification du besoin** — ticket ou issue décrivant le changement
2. **Proposition de modification** — PR sur les documents concernés
3. **Revue** — au moins 1 pair + validation métier si changement sémantique
4. **Merge et mise à jour** — propagation aux documents dépendants

### 8.3 Règles de collaboration

- **Tout document peut être commenté** — même par un non-technicien. La sémantique est l'affaire de tous.
- **Un document n'appartient pas à son auteur** — c'est un artefact d'équipe.
- **Les désaccords sur les concepts se tranchent par des exemples** — pas par des arguments d'autorité. *« Montre-moi un cas que ton concept ne couvre pas. »*
- **Les changements breaking sont documentés** — si un concept change de nom ou de définition, on le signale dans les documents dépendants.

---

## 9. Checklist pour chaque document

### `vision.md` — checklist
- [ ] Le problème est clairement énoncé
- [ ] Les objectifs sont mesurables
- [ ] Le périmètre est délimité (dedans/dehors)
- [ ] Les parties prenantes sont identifiées
- [ ] La roadmap est réaliste

### `metamodel.md` — checklist
- [ ] Aucun terme technique dans les définitions
- [ ] Chaque concept a une définition en une phrase
- [ ] Les relations entre concepts sont documentées
- [ ] Le cycle de vie de chaque concept est décrit
- [ ] Les invariants sont listés
- [ ] Un non-technicien peut le comprendre

### `semantics.md` — checklist
- [ ] Chaque propriété a une définition précise
- [ ] Les valeurs « limites » sont documentées (null, vide, absent)
- [ ] Les interactions entre propriétés sont documentées
- [ ] Les cas particuliers sont listés
- [ ] L'ordre des événements est spécifié

### `catalogue.md` — checklist
- [ ] Chaque type concret est documenté
- [ ] La correspondance avec le code existant est indiquée
- [ ] Des exemples complets sont fournis
- [ ] Les cas d'usage réels sont couverts
- [ ] Le catalogue est cohérent avec le métamodèle

### `api.md` — checklist
- [ ] L'API découle naturellement du métamodèle
- [ ] Les interfaces sont complètes et typées
- [ ] Un exemple de bout en bout est fourni
- [ ] L'API a été testée sur un cas réel
- [ ] L'écriture est naturelle et concise

---

## 10. Correspondance MDA

Pour ceux qui connaissent la **Model-Driven Architecture (MDA)** définie par l'OMG, voici la correspondance des documents avec les niveaux MDA :

| Document | Niveau MDA | Nom MDA | Description |
|----------|------------|---------|-------------|
| `vision.md` | — | — | Motivation et contexte (hors MDA) |
| `metamodel.md` | **CIM** | Computation Independent Model | Les concepts métier, indépendants de toute informatique |
| `semantics.md` | *(rattaché au CIM)* | — | Précision des règles du CIM |
| `catalogue.md` | **PIM** | Platform Independent Model | Les types concrets, indépendants de la plateforme d'exécution |
| `api.md` | **PSM** | Platform Specific Model | L'API spécifique à la technologie cible (TypeScript, Svelte, etc.) |

### Le flux de transformation MDA

```
CIM (metamodel.md)
  │
  │  Transformation : Ajout de concrétude
  │  (le métier devient des types identifiés)
  ▼
PIM (catalogue.md)
  │
  │  Transformation : Ajout de la plateforme
  │  (les types deviennent une API dans un langage spécifique)
  ▼
PSM (api.md)
  │
  │  Transformation : Génération / implémentation manuelle
  ▼
Code source
```

### Pourquoi c'est utile ?

- **Traçabilité** : Chaque élément du code remonte à un concept du CIM
- **Pérennité** : Le CIM ne change pas quand on change de framework
- **Parallélisation** : On peut concevoir le CIM (métier) et implémenter le PSM (technique) en parallèle

---

## 11. ADR — Traçabilité des décisions

### 11.1 Pourquoi des ADR ?

Les cinq documents de conception décrivent **l'état actuel** du système. Mais ils ne disent pas **pourquoi** les décisions ont été prises, ni **quelles alternatives** ont été envisagées.

Les **ADR (Architecture Decision Records)** comblent ce vide :

```
ADR-001: Pourquoi avons-nous choisi le mode Événement plutôt que Commande ?
ADR-002: Pourquoi le concept « Étape » a-t-il été fusionné avec « Transition » ?
ADR-003: Pourquoi l'API expose-t-elle une factory plutôt qu'un constructeur ?
```

### 11.2 Structure d'un ADR

```markdown
# ADR-001: [Titre court et explicite]

## Date
YYYY-MM-DD

## Contexte
Quel était le problème ou la question à trancher ?

## Décision
Qu'avons-nous décidé ?

## Alternatives envisagées
- **Alternative A** : avantages / inconvénients
- **Alternative B** : avantages / inconvénients

## Conséquences
- Ce qui change dans le métamodèle / l'API / le code
- Ce qui est facilité
- Ce qui est rendu plus difficile

## Statut
Accepté / Proposé / Déprécié / Remplacé par ADR-XXX
```

### 11.3 Où les stocker ?

```
docs/
├── decisions/
│   ├── ADR-001-choix-mode-evenement.md
│   ├── ADR-002-fusion-concept-etape.md
│   └── README.md                    ← Index des ADR
└── methodologie/
    ├── conception-par-metamodele.md
    └── architecture-applicative.md
```

> [!TIP]
> Un ADR n'est pas un document de conception. Gardez-le court (5-15 lignes). L'objectif est de **ne pas re-débattre la même décision** six mois plus tard.

---

## 12. Anti-patterns courants

### Anti-pattern 1 : Fuite technique dans le métamodèle

**Symptôme** : Le métamodèle contient des termes comme `Component`, `Render`, `Hook`, `Class`, `Interface`, `HTML`.

**Problème** : Le métamodèle n'est plus indépendant de la technologie.

**Solution** : Remplacer par des termes métier. Par exemple :
- ❌ `Component` → ✅ `Field`, `Section`, `Step`
- ❌ `Render` → ✅ `Affichage`, `Représentation`
- ❌ `CssClass` → ✅ `Apparence`, `Style`

### Anti-pattern 2 : Sémantique trop vague

**Symptôme** : Les définitions sont des paraphrases du nom de la propriété.
- ❌ `required` → « Le champ est requis »
- ✅ `required` → « Le champ est invalide si sa valeur est absente au moment de la validation »

**Solution** : Utiliser la technique des **cas limites** pour forcer la précision.

### Anti-pattern 3 : Métamodèle sans exemples

**Symptôme** : Le métamodèle est parfait sur le papier mais ne correspond à aucun cas réel.

**Solution** : Toujours valider chaque concept avec au moins un exemple concret du projet.

### Anti-pattern 4 : API inventée indépendamment du métamodèle

**Symptôme** : L'API a des concepts qui n'existent pas dans le métamodèle.

**Solution** : Revoir le métamodèle pour y ajouter les concepts manquants, ou simplifier l'API pour qu'elle corresponde au métamodèle.

### Anti-pattern 5 : Documentation figée

**Symptôme** : Les documents sont écrits une fois et jamais mis à jour.

**Solution** : Les documents doivent vivre avec le code. Chaque évolution du métamodèle doit être répercutée dans tous les documents.

### Anti-pattern 6 : Surcharge du catalogue

**Symptôme** : Le catalogue devient un annuaire de toutes les configurations possibles au lieu de décrire les types.

**Solution** : Le catalogue décrit des **types** (des catégories), pas des **instances** (des configurations spécifiques). Les exemples illustrent, ils n'énumèrent pas.

---

## 13. Annexes

### A. Structure de dossiers recommandée

Pour un projet organisé avec cette méthode :

```
docs/
└── <sous-système>/
    ├── vision.md          ← Pourquoi ? (problème, objectifs, roadmap)
    ├── metamodel.md        ← Quoi ? (concepts, relations, invariants)
    ├── semantics.md        ← Signification ? (définitions précises)
    ├── catalogue.md        ← Concret ? (types, exemples)
    └── api.md              ← Syntaxe ? (interfaces, helpers)
```

Exemples de `<sous-système>` : `forms`, `workflow`, `notifications`, `reporting`, `validation`, `permissions`.

### B. Génération des documents (template)

Pour démarrer un nouveau sous-système, créez les fichiers à partir des templates figurant dans ce document. Chaque doc commence vide avec sa structure prête à être remplie.

### C. Correspondance avec le Domain-Driven Design (DDD)

| Concept DDD | Correspondance dans la méthode |
|-------------|-------------------------------|
| **Ubiquitous Language** | Le vocabulaire défini dans le métamodèle, utilisé partout |
| **Bounded Context** | Un sous-système (forms, workflow, etc.) |
| **Entity** | Concept avec identité et cycle de vie |
| **Value Object** | Concept sans identité, défini par ses attributs |
| **Domain Event** | Transitions du cycle de vie |
| **Aggregate** | Groupe de concepts avec une racine |
| **Repository** | Source de données (catalogue) |
| **Domain Service** | Opération métier sans état propre |

### D. Exemples d'application par domaine

#### Domaines universels

| # | Catégorie | Domaine | Concepts du métamodèle |
|---|----------|---------|----------------------|
| 1 | **Saisie & Données** | **Formulaires** | Form, Section, Field, Validator, DataSource, Behavior, Layout, Rule |
| 2 | **Saisie & Données** | **Recherche & Filtres** | Query, Filter, Sort, Facet, Pagination, Result, Suggestion |
| 3 | **Saisie & Données** | **Import de données** | Source, Mapping, Transformer, Validator, Report, Batch, Error |
| 4 | **Saisie & Données** | **Export de données** | Query, Format, Destination, Schedule, Delivery, Compression |
| 5 | **Processus** | **Workflow / Processus** | Step, Transition, Guard, Action, State, Context, History, Timer |
| 6 | **Processus** | **Validations / Approbations** | ApprovalChain, Level, Approver, Decision, Escalation, Deadline |
| 7 | **Processus** | **Orchestration** | Pipeline, Stage, Task, Condition, Retry, Compensation |
| 8 | **Processus** | **Évaluations / Stages** | Stage, Evaluator, Criteria, Score, Decision, Feedback |
| 9 | **Communication** | **Notifications** | Channel, Template, Recipient, Event, Preference, Delivery, Schedule |
| 10 | **Communication** | **Messagerie / Chat** | Message, Thread, Participant, Attachment, Reaction, ReadReceipt |
| 11 | **Communication** | **Emails / Campagnes** | Campaign, Audience, Template, Delivery, Open, Click, Unsubscribe |
| 12 | **Communication** | **Annonces / Broadcast** | Post, Audience, Attachment, Reaction, Comment, Pinned, Expiry |
| 13 | **Communication** | **Commentaires / Reviews** | Comment, Thread, Mention, Reaction, Moderation, Report |
| 14 | **Permissions** | **RBAC / ACL** | Role, Permission, Resource, Policy, Constraint, Scope, Grant |
| 15 | **Permissions** | **Authentification** | User, Credential, Session, Token, Device, MFA, Provider |
| 16 | **Permissions** | **Délégations** | Delegation, Proxy, Period, Scope, Authority, Revocation |
| 17 | **Analyse** | **Reporting** | Dataset, Dimension, Measure, Filter, Aggregation, Chart, Export |
| 18 | **Analyse** | **Tableaux de bord** | Dashboard, Widget, Metric, Period, Filter, Layout, Refresh |
| 19 | **Analyse** | **Indicateurs (KPI)** | KPI, Formula, Target, Actual, Period, Threshold, Alert |
| 20 | **Analyse** | **Enquêtes / Sondages** | Survey, Question, Response, Anonymous, Result, Export, Quorum |
| 21 | **Évaluation** | **Feedback / Évaluations** | Review, Rating, Criteria, Score, Comment, Aggregation, Report |
| 22 | **Évaluation** | **Certifications** | Certification, Exam, Question, Attempt, Score, Validity, Badge |
| 23 | **Évaluation** | **Tests / Quiz** | Quiz, Question, Option, Answer, Score, Timer, Attempt |
| 24 | **Catalogue** | **Catalogue produits** | Product, Category, Variant, Price, Stock, Attribute, Media |
| 25 | **Catalogue** | **Inventaire / Stocks** | Stock, Warehouse, Movement, Reservation, Threshold, Reorder |
| 26 | **Catalogue** | **Contenus (CMS)** | Content, Page, Block, Template, Version, Publishing, Locale |
| 27 | **Catalogue** | **Documents / Fichiers** | Document, Version, Category, Template, Signature, Workflow, Archive |
| 28 | **Commerce** | **Panier / Checkout** | Cart, Item, Price, Discount, Tax, Shipping, Payment |
| 29 | **Commerce** | **Facturation** | Invoice, LineItem, Tax, Discount, Payment, Status, CreditNote |
| 30 | **Commerce** | **Abonnements** | Plan, Subscription, Billing, Renewal, Cancellation, Trial |
| 31 | **Commerce** | **Paiements** | Payment, Method, Transaction, Gateway, Refund, Status, Receipt |
| 32 | **Temps** | **Calendrier / Planning** | Event, Recurrence, Participant, Reminder, Availability, Overlap |
| 33 | **Temps** | **Réservation / Booking** | Resource, Slot, Reservation, Availability, Schedule, Conflict |
| 34 | **Temps** | **Agenda / Rendez-vous** | Appointment, Date, Duration, Attendee, Location, Reminder |
| 35 | **Temps** | **Compteurs / Soldes** | Balance, Accrual, Consumption, Cap, Reset, History, Threshold |
| 36 | **Finance** | **Comptabilité** | Account, Entry, Journal, Period, Balance, Reconciliation, Audit |
| 37 | **Finance** | **Budgets** | BudgetLine, Allocation, Expense, Forecast, Category, Period, Variance |
| 38 | **Finance** | **Dépenses / Notes de frais** | ExpenseReport, Line, Category, Approval, Reimbursement, Policy |
| 39 | **Gestion** | **Projets** | Project, Task, Milestone, Assignment, Timeline, Dependency, Status |
| 40 | **Gestion** | **Tâches / Todo** | Task, Checklist, Priority, Assignee, DueDate, Status, Label |
| 41 | **Gestion** | **Ressources / Planning** | Resource, Allocation, Capacity, Booking, Utilization, Forecast |
| 42 | **Gestion** | **Objectifs / OKR** | Objective, KeyResult, Target, Progress, Weight, Status, Period |
| 43 | **Apprentissage** | **E-learning / Cours** | Course, Module, Lesson, Quiz, Enrollment, Progress, Certificate |
| 44 | **Apprentissage** | **Formation / Sessions** | Session, Trainer, Trainee, Material, Attendance, Evaluation |
| 45 | **Géographie** | **Géolocalisation / Maps** | Location, Zone, Route, Distance, Boundary, Coordinate |
| 46 | **Géographie** | **Zones / Régions** | Region, Area, Country, City, PostalCode, Timezone |
| 47 | **Technique** | **API / Webhooks** | Endpoint, Auth, Payload, RateLimit, Log, Retry, Version |
| 48 | **Technique** | **Synchronisation** | Connector, Endpoint, Payload, SyncJob, Conflict, Log, Retry |
| 49 | **Technique** | **Configuration** | Setting, Parameter, Scope, Module, Value, Default, Override |
| 50 | **Technique** | **Logs / Monitoring** | Log, Metric, Alert, Dashboard, Threshold, Incident, Escalation |
| 51 | **Technique** | **Audit / Traçabilité** | Event, Actor, Action, Target, Timestamp, Delta, Reason |
| 52 | **Technique** | **Versions / Releases** | Version, Release, Changelog, Artifact, Environment, Rollback |
| 53 | **Technique** | **Files / Queue** | Job, Queue, Worker, Priority, Status, Retry, Schedule |
| 54 | **IoT / Devices** | **Appareils / Capteurs** | Device, Sensor, Reading, Alert, Command, Config, Firmware |
| 55 | **IoT / Devices** | **Maintenance** | Asset, Schedule, Task, Part, Intervention, Report, Warranty |
| 56 | **Social** | **Réseau / Relations** | Profile, Connection, Follow, Feed, Post, Reaction, Share |
| 57 | **Social** | **Gamification** | Player, Level, Badge, Quest, Reward, Score, Leaderboard |
| 58 | **Social** | **Votes / Décisions** | Poll, Question, Option, Vote, Result, Quorum, Delegation |
| 59 | **IA / Data** | **ML Pipelines** | Pipeline, Step, Model, Dataset, Metric, Artifact, Experiment |
| 60 | **IA / Data** | **Recommandations** | Item, Preference, Score, Context, Strategy, Feedback, Diversity |
| 61 | **Conformité** | **RGPD / Privacy** | Consent, Processing, Purpose, Retention, Rights, Audit, Policy |
| 62 | **Conformité** | **Contrats / Legal** | Contract, Type, Period, Clause, Renewal, Amendment, Signature |
| 63 | **Multi-tenant** | **Organisations / Équipes** | Organization, Team, Member, Role, Settings, Quota, Billing |
| 64 | **Multi-tenant** | **Espaces de travail** | Workspace, Project, Member, Permission, Template, Archive |

### E. Gouvernance et maintenance

#### Pourquoi une gouvernance ?

Sans maintenance, les documents de conception deviennent obsolètes en 3 à 6 mois. Le code évolue, les concepts dérivent, et la documentation devient un **mensonge** plutôt qu'une aide.

#### Règles de maintenance

| Règle | Description |
|-------|-------------|
| **Tout document a un owner** | Une personne responsable de sa mise à jour |
| **Tout changement de code lié à un concept** | Doit commencer par vérifier si le document de conception est impacté |
| **Revue trimestrielle** | Tous les 3 mois, chaque document est relu pour vérifier sa pertinence |
| **Signaler l'obsolescence** | Un document obsolète est marqué `⚠️ Obsolète — [raison]` en en-tête |

#### Cycle de vie d'un document

```
Création → Stabilisation → Maintenance courante
                               ↓
                          Changement dans le code ?
                               ↓
                          Mise à jour du document → Revue → Nouvelle stabilisation
                               ↓
                          Obsolescence ?
                               ↓
                          Archivage (document conservé mais marqué comme obsolète)
```

#### Responsabilités

| Rôle | Responsabilité |
|------|----------------|
| **Document Owner** | Met à jour le document, s'assure de sa cohérence avec le code |
| **Équipe** | Signale les écarts entre code et documentation |
| **Architecte** | Garantit la cohérence transverse entre documents |

#### Que faire si un document est obsolète ?

1. **Le marquer** : `⚠️ Obsolète — Ce document n'a pas été mis à jour depuis [date].`
2. **Analyser l'écart** : entre le document et la réalité du code
3. **Décider** : mise à jour (si le concept est toujours pertinent) ou archivage (si le concept a été abandonné)
4. **Planifier** : qui le fait, pour quand ?

> [!WARNING]
> Une documentation obsolète non marquée est pire que pas de documentation du tout — elle induit en erreur. Mieux vaut archiver que laisser pourrir.

### F. Exemple complet : conception du sous-système « Congés »

> Cet exemple illustre l'application de la méthode pour un sous-système de gestion de congés. Il est volontairement simplifié mais couvre tous les documents.

---

#### `vision.md`

```markdown
# Vision : Gestion des Congés

## Pourquoi ce système ?
Les employés doivent pouvoir demander des congés, les managers les approuver,
et l'entreprise suivre les soldes. Actuellement, le processus est manuel (email).

## Objectifs
- Réduire le temps de traitement d'une demande de 2 jours à 2 heures
- Garantir le respect des soldes et des règles légales (solde minimum, période d'essai)
- Fournir un historique consultable

## Périmètre
- Demandes de congés (création, modification, annulation)
- Approbation par le manager hiérarchique
- Consultation des soldes

## Hors périmètre
- Calcul de la paie (sous-système Paie) — on fournit les données
- Gestion des jours fériés (sous-système Calendrier)
```

---

#### `metamodel.md`

```markdown
# Métamodèle : Congés

## Cartographie des concepts

┌──────────┐    1..*        ┌──────────────────┐
│ Employee │──────────────>│   LeaveRequest    │
└──────────┘               │──────────────────│
                           │ id, type, status  │
                           │ startDate, endDate│
                           └──────────────────┘
                                  │
                                  ▼
                           ┌──────────────────┐
                           │  LeaveBalance     │
                           │──────────────────│
                           │ type, total       │
                           │ used, remaining   │
                           └──────────────────┘

## Concept : Employee

Définition : Personne physique employée par l'organisation, identifiée par
son contrat de travail. Source de vérité : sous-système Employés.

## Concept : LeaveRequest

Définition : Demande de congé faite par un employé, qui suit un cycle
d'approbation.

### Attributs
| Attribut | Type | Requis | Description |
|----------|------|--------|-------------|
| id | identifiant | oui | Identifiant unique |
| type | LeaveType | oui | Catégorie de congé |
| startDate | date | oui | Premier jour d'absence |
| endDate | date | oui | Dernier jour d'absence |
| status | LeaveStatus | oui | État dans le cycle |
| reason | texte | non | Justification |
| comment | texte | non | Commentaire interne |

### Cycle de vie

[Draft] ─(submit)──> [Pending] ─(approve)──> [Approved]
                              ─(reject)──> [Rejected]
[Approved] ─(cancel)──> [Cancelled]

## Concept : LeaveBalance
Définition : Solde disponible pour un employé, par type de congé.
```

---

#### `semantics.md`

```markdown
# Sémantique : Congés

## LeaveRequest.status

### Définition
État actuel de la demande dans son cycle d'approbation.

### Valeurs
- `Draft` : L'employé remplit sa demande, peut la modifier librement
- `Pending` : Soumise, en attente d'approbation — plus modifiable par l'employé
- `Approved` : Approuvée par le manager — les soldes sont décrémentés
- `Rejected` : Refusée — le solde n'est pas impacté
- `Cancelled` : Annulée par l'employé après approbation — les soldes sont recrédités

### Valeurs limites
- Que signifie « absent » pour `endDate` ? Non applicable : la date de fin est toujours requise.
- Que signifie un statut `null` ? Impossible : le statut est toujours défini à la création (`Draft`).

## LeaveBalance.total

Définition : Nombre de jours de congé accordés à l'employé pour ce type,
sur la période de référence. Ne peut pas être négatif. Change uniquement
à la nouvelle période (reset) ou par décision RH (exception).
```

---

#### `catalogue.md`

```markdown
# Catalogue : Congés

## Types concrets

| Type | Concept parent | Description | Utilisation |
|------|----------------|-------------|-------------|
| AnnualLeave | LeaveRequest | Congés payés standard | Vacances |
| SickLeave | LeaveRequest | Congé maladie | Absence médicale |
| UnpaidLeave | LeaveRequest | Congé sans solde | Disponibilité |

### AnnualLeave
| Propriété | Valeur |
|-----------|--------|
| Valeur par défaut | status: Draft |
| Validation | startDate < endDate, endDate dans l'année |
| Solde vérifié | Oui, avant soumission |

## Exemple

```typescript
// Demande de congés annuels
const request = {
  id: "LEAVE-2024-042",
  employeeId: "EMP-123",
  type: "AnnualLeave",
  startDate: "2024-08-01",
  endDate: "2024-08-15",
  status: "Draft",
  reason: "Vacances d'été en famille"
};
```
```

---

#### `api.md`

```markdown
# API : Congés

Fonctions principales :

```typescript
// Créer une demande
function createLeave(employeeId: string, type: LeaveType, start: Date, end: Date): LeaveRequest

// Soumettre pour approbation
function submitLeave(id: string): Result

// Approuver / Rejeter
function approveLeave(id: string, comment?: string): Result
function rejectLeave(id: string, reason: string): Result

// Consulter les soldes
function getBalances(employeeId: string): LeaveBalance[]
```
```

---

> **Dernier conseil** : Cette méthode est un **outil**, pas une religion. Adaptez-la à votre contexte. Si vous n'avez besoin que du métamodèle et du catalogue, faites-le. L'important est de penser d'abord aux concepts, ensuite au code.
