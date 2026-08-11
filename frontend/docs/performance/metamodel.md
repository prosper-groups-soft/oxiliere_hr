# Métamodèle : Performance

> Concepts fondamentaux du cycle d'évaluation des performances.

---

## Cartographie des concepts

```
Campagne ──1──>* Évaluation ──1──>* Objectif
                                  ──1──>* Compétence
                                  ──1───1 Plan de développement
    
Évaluation ──1──>* Calibrage (0..1)

Rôles : Employé, Manager, RH
```

---

## Concept : Campagne

### Définition
Une **Campagne** est une période d'évaluation définie par le service RH, qui constitue le cadre temporel et organisationnel dans lequel les évaluations sont réalisées.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `name` | string | oui | Nom lisible (ex: "SA1 2026", "Annuel 2025") |
| `description` | text | non | Description / instructions générales |
| `start_date` | date | oui | Date de début de la période d'évaluation |
| `end_date` | date | oui | Date de fin de la période d'évaluation |
| `submission_deadline` | date | oui | Date limite de soumission des évaluations |
| `status` | enum | oui | `DRAFT → ACTIVE → CLOSED` |
| `created_by` | ref(User) | oui | Utilisateur RH qui a créé la campagne |
| `goal_weight` | float | non | Poids des objectifs dans le score (défaut: 0.6) |
| `skill_weight` | float | non | Poids des compétences dans le score (défaut: 0.4) |

### Relations
```
Campagne ──1──>* Évaluation (Une campagne contient plusieurs évaluations)
Campagne ──1──>* Employé (Une campagne cible un ensemble d'employés)
```

### Cycle de vie
```
DRAFT ──(activation)──> ACTIVE ──(clôture)──> CLOSED
```

| Étape | Description | Déclencheur |
|-------|-------------|-------------|
| `DRAFT` | La campagne est en préparation, pas encore visible | Création par RH |
| `ACTIVE` | Les employés/managers peuvent faire leurs évaluations | Activation par RH |
| `CLOSED` | Les évaluations ne peuvent plus être modifiées | Clôture automatique ou manuelle |

### Invariants
- Une campagne ne peut pas être supprimée si elle contient des évaluations
- `start_date ≤ end_date ≤ submission_deadline`
- Le statut `DRAFT → ACTIVE` est irréversible (on ne peut pas désactiver une campagne)
- Une campagne `ACTIVE` peut être clôturée à tout moment par RH

### Exemple concret
```json
{
  "name": "SA1 2026",
  "description": "Évaluation semestrielle — premier semestre 2026",
  "start_date": "2026-01-01",
  "end_date": "2026-06-30",
  "submission_deadline": "2026-07-15",
  "status": "ACTIVE"
}
```

---

## Concept : Évaluation

### Définition
Une **Évaluation** est l'instance d'évaluation d'un employé pour une campagne donnée. Elle contient les contributions de l'employé (auto-évaluation) et du manager (évaluation), ainsi que les résultats du calibrage.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `campaign` | ref(Campagne) | oui | Campagne parente |
| `employee` | ref(Employee) | oui | Employé évalué |
| `manager` | ref(Employee) | oui | Manager N+1 évaluateur |
| `status` | enum | oui | `EMPLOYEE_DRAFT → MANAGER_DRAFT → SUBMITTED → CALIBRATED → ACKNOWLEDGED` |
| `disputed` | bool | non | Flag de contestation par l'employé (défaut: false) |
| `employee_comment` | text | non | Commentaire de l'employé (auto-évaluation) |
| `manager_comment` | text | non | Commentaire du manager |
| `overall_score` | float | non | Score final calculé (0-5) |
| `manager_overall_score` | float | non | Note globale saisie par le manager (0-5) |
| `submitted_at` | datetime | non | Date de soumission par le manager |
| `acknowledged_at` | datetime | non | Date de prise de connaissance par l'employé |
| `calibrated_score` | float | non | Score ajusté après calibrage RH |

### Relations
```
Évaluation ──1──>* Objectif
Évaluation ──1──>* Compétence
Évaluation ──0..1──1 Plan de développement
Évaluation ──0..1──> Calibrage
```

### Cycle de vie
```
EMPLOYEE_DRAFT ──(employee submits)──> MANAGER_DRAFT ──(manager submits)──> SUBMITTED
SUBMITTED ──(RH calibrates)──> CALIBRATED
CALIBRATED ──(employee acknowledges)──> ACKNOWLEDGED

Sous-étapes possibles :
  EMPLOYEE_DRAFT : l'employé remplit ses objectifs, compétences, commentaire
  MANAGER_DRAFT : le manager évalue les objectifs, compétences, ajoute son commentaire et note
```

| Étape | Description | Qui peut éditer |
|-------|-------------|-----------------|
| `EMPLOYEE_DRAFT` | L'employé prépare son auto-évaluation | Employé uniquement |
| `MANAGER_DRAFT` | L'employé a soumis, le manager évalue | Manager uniquement |
| `SUBMITTED` | Le manager a soumis, en attente de calibrage | RH uniquement |
| `CALIBRATED` | RH a calibré, visible par l'employé | Lecture seule |
| `ACKNOWLEDGED` | L'employé a pris connaissance | Lecture seule |

### Invariants
- Une évaluation appartient à une **seule** campagne et un **seul** employé
- `manager ≠ employee` (un employé ne peut pas être son propre évaluateur)
- Le score final est calculé automatiquement : `weighted_mean(goals_rating) × goal_weight + weighted_mean(skills_level) × skill_weight`
  - Les poids (`goal_weight`, `skill_weight`) sont configurables sur la campagne (défauts: 0.6 / 0.4)
- Le `calibrated_score` écrase le `overall_score` si présent
- Un employé ne peut avoir qu'une seule évaluation par campagne
- La transition vers `ACKNOWLEDGED` nécessite que l'employé ait vu l'évaluation (signature électronique)

### Exemple concret
```json
{
  "campaign": "SA1 2026",
  "employee": "Jean Dupont",
  "manager": "Marie Martin",
  "status": "SUBMITTED",
  "employee_comment": "J'ai atteint tous mes objectifs ce semestre...",
  "manager_comment": "Jean a dépassé les attentes sur le projet X...",
  "overall_score": 4.2,
  "manager_overall_score": 4,
  "submitted_at": "2026-06-15T14:30:00Z"
}
```

---

## Concept : Objectif

### Définition
Un **Objectif** est un but SMART défini pour la période d'évaluation, évalué par l'employé (auto-évaluation) et par le manager.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `description` | string | oui | Description de l'objectif |
| `type` | enum | oui | `OBJECTIVE` (qualitatif) ou `KPI` (quantitatif) |
| `weight` | float | non | Poids de l'objectif dans le score (0-1, défaut: 1/n) |
| `employee_rating` | int(1-5) | non | Auto-évaluation par l'employé |
| `manager_rating` | int(1-5) | non | Évaluation par le manager |
| `status` | enum | oui | `PENDING → ACHIEVED → PARTIAL → NOT_ACHIEVED → CANCELLED` |

### Relations
```
Objectif ──*──1 Évaluation
```

### Cycle de vie
```
PENDING ──(évaluation)──> ACHIEVED | PARTIAL | NOT_ACHIEVED
CANCELLED (peut être marqué à tout moment)
```

### Invariants
- Un objectif `CANCELLED` n'est pas compté dans le score
- `weight` doit être > 0 et la somme des poids ≤ 1
- `employee_rating` et `manager_rating` sont indépendants

### Exemple concret
```json
{
  "description": "Lancer la feature X avant fin Q2",
  "type": "OBJECTIVE",
  "weight": 0.5,
  "employee_rating": 4,
  "manager_rating": 3,
  "status": "ACHIEVED"
}
```

---

## Concept : Compétence

### Définition
Une **Compétence** est une capacité technique ou comportementale évaluée sur une échelle de 1 à 5.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `name` | string | oui | Nom de la compétence |
| `category` | enum | non | `TECHNICAL`, `BEHAVIORAL`, `LEADERSHIP` |
| `employee_level` | int(1-5) | non | Auto-évaluation par l'employé |
| `manager_level` | int(1-5) | non | Évaluation par le manager |

### Relations
```
Compétence ──*──1 Évaluation
```

### Invariants
- `employee_level` et `manager_level` sont indépendants
- Une compétence sans catégorie est classée comme `BEHAVIORAL` par défaut

### Exemple concret
```json
{
  "name": "Communication écrite",
  "category": "BEHAVIORAL",
  "employee_level": 4,
  "manager_level": 3
}
```

---

## Concept : Plan de développement

### Définition
Un **Plan de développement** est un ensemble d'actions de formation ou de mentorat définies après l'évaluation pour améliorer les compétences d'un employé.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `evaluation` | ref(Évaluation) | oui | Évaluation associée |
| `items` | json[] | oui | Liste d'actions (description, deadline, status) |
| `created_at` | datetime | oui | Date de création |
| `completed_at` | datetime | non | Date de complétion |

### Relations
```
Plan de développement ──1──1 Évaluation
```

### Cycle de vie
```
OPEN ──(all items completed)──> COMPLETED
```

### Exemple concret
```json
{
  "items": [
    {"action": "Formation Excel avancé", "deadline": "2026-09-01", "status": "PENDING"},
    {"action": "Mentorat avec Marie sur la gestion de projet", "deadline": "2026-12-01", "status": "PENDING"}
  ]
}
```

---

## Concept : Calibrage

### Définition
Le **Calibrage** est le processus par lequel le service RH ajuste les scores pour assurer la cohérence et l'équité entre les équipes.

### Attributs
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `evaluation` | ref(Évaluation) | oui | Évaluation concernée |
| `original_score` | float | oui | Score avant calibrage |
| `calibrated_score` | float | oui | Score après calibrage |
| `reason` | text | oui | Justification de l'ajustement |
| `calibrated_by` | ref(User) | oui | RH qui a effectué le calibrage |
| `calibrated_at` | datetime | oui | Date du calibrage |

### Invariants
- `calibrated_score` peut être supérieur ou inférieur à `original_score`
- Une évaluation ne peut être calibrée qu'une seule fois (sauf nouveau calibrage explicite)
- Le calibrage est visible par le manager et l'employé

### Exemple concret
```json
{
  "original_score": 4.5,
  "calibrated_score": 4.0,
  "reason": "Ajustement suite au comité de calibrage — note trop élevée par rapport au reste de l'équipe"
}
```

---

## Relations inter-concepts

```
Campagne (1) ──────────── (N) Évaluation
Évaluation (N) ───────── (N) Objectif
Évaluation (N) ───────── (N) Compétence
Évaluation (1) ───────── (0..1) Plan de développement
Évaluation (1) ───────── (0..1) Calibrage
```

### Cycle de vie global

```
[RH crée campagne] ──> DRAFT
  │
  ├──> [RH active] ──> ACTIVE
  │      │
  │      ├──> [Employé remplit auto-évaluation] ──> EMPLOYEE_DRAFT
  │      │      │
  │      │      └──> [Employé soumet] ──> MANAGER_DRAFT
  │      │             │
  │      │             └──> [Manager évalue et soumet] ──> SUBMITTED
  │      │                    │
  │      │                    ├──> [RH calibre] ──> CALIBRATED
  │      │                    │      │
  │      │                    │      └──> [Employé prend connaissance] ──> ACKNOWLEDGED
  │      │                    │
  │      │                    └──> (calibrage automatique si pas de calibrage manuel)
  │      │
  │      └──> [RH clôture campagne] ──> CLOSED
  │
  └──> ...
```

---

## Invariants globaux

- Un employé ne peut avoir qu'une **seule** évaluation active par campagne
- Le score final est **toujours calculé**, jamais saisi (le manager saisit une note indicative pour référence)
- Une évaluation `ACKNOWLEDGED` est immutable
- Une campagne `CLOSED` ne peut plus être modifiée
- Toute modification d'une évaluation est **horodatée et tracée**

---

## Glossaire des types

| Type | Valeurs | Description |
|------|---------|-------------|
| `Campagne.status` | `DRAFT`, `ACTIVE`, `CLOSED` | Statut de la campagne |
| `Évaluation.status` | `EMPLOYEE_DRAFT`, `MANAGER_DRAFT`, `SUBMITTED`, `CALIBRATED`, `ACKNOWLEDGED` | Statut de l'évaluation |
| `Objectif.type` | `OBJECTIVE`, `KPI` | Type d'objectif |
| `Objectif.status` | `PENDING`, `ACHIEVED`, `PARTIAL`, `NOT_ACHIEVED`, `CANCELLED` | Statut de l'objectif |
| `Compétence.category` | `TECHNICAL`, `BEHAVIORAL`, `LEADERSHIP` | Catégorie de compétence |
