# Alignement Frontend/Backend - Module Carrières (Careers)

## Vue d'ensemble

Ce document établit la correspondance entre les fonctionnalités frontend du module Carrières et les endpoints/backend disponibles.

---

## 1. Familles de Métiers (Job Families)

### Frontend (`CareersHeader`, formulaires Position)
**Fonctionnalités actuelles:**
- Liste déroulante des familles de métiers
- Création automatique d'une famille si inexistante (lors création position)

### Backend
| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/api/jobs/families` | GET | Liste toutes les familles | ✅ Disponible |
| Création via `/api/jobs/positions` | POST | `JobService.create_position_with_family()` crée la famille si besoin | ✅ Disponible |

### Correspondance
```
Frontend (saisie famille) → Backend (get_or_create)
PositionCreateIn.family_name → JobFamily.name
```

---

## 2. Positions (Postes)

### Frontend (`PositionsList`, `PositionSheet`)
**Fonctionnalités actuelles:**
- Liste des positions avec recherche/filtres
- Création/Édition/Suppression de positions
- Association à une unité organisationnelle
- Niveau de séniorité

### Backend
| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/api/jobs/positions` | POST | Créer une position (avec famille) | ✅ Disponible |
| `/api/jobs/families/{family_id}/career-path` | GET | Parcours de carrière d'une famille | ✅ Disponible |
| `/api/jobs/positions/level/{level}` | GET | Positions par niveau de séniorité | ✅ Disponible |
| `/api/jobs/catalog` | GET | Structure complète {famille: [positions]} | ✅ Disponible |
| `/api/org/units/{unit_id}/positions` | GET | Positions d'une unité org | ✅ Disponible |

### Gaps Identifiés
| Frontend Attend | Backend Fournit | Action |
|-----------------|-----------------|--------|
| `PUT /positions/{id}` (modification) | ❌ Manquant | À implémenter |
| `DELETE /positions/{id}` (suppression) | ❌ Manquant | À implémenter |
| `GET /positions` (liste complète) | ❌ Manquant | À implémenter |

### Correspondance Types
```typescript
// Frontend (JobPosition)
interface JobPosition {
  id: string;
  title: string;           → Position.name
  orgUnitId: string;       → Via EmployeePositionHistory.org_unit
  seniority: SeniorityLevel; → Position.level (mapping nécessaire)
  salaryRange: {...};      // ❌ Non dans backend
  requirements: string[];   // ❌ Non dans backend
  skills: {...};           // ❌ Non dans backend
}

// Backend (PositionOut)
Position {
  id: UUID;
  name: string;            → title
  job_family: JobFamilyOut;
  level: PositionLevel;   → seniority (avec conversion)
  description: string;    → requirements (alternative)
}
```

---

## 3. Niveaux de Séniorité (Seniority Levels) - ✅ DYNAMIQUE

### Frontend (`SeniorityMatrix`, `SenioritySheet`)
**Fonctionnalités actuelles:**
- Matrice des 9 niveaux backend (TRAINEE → EXECUTIVE)
- Labels français via `SENIORITY_LABELS`
- Définition des prérequis par niveau
- Couleurs associées à chaque niveau

### Backend (PositionLevel Enum + SeniorityLevelDefinition)
```python
# Enum fixe (9 valeurs)
PositionLevel: TRAINEE, APPRENTICE, JUNIOR, INTERMEDIATE, SENIOR, LEAD, MANAGER, DIRECTOR, EXECUTIVE

# Modèle dynamique pour personnalisation
SeniorityLevelDefinition {
  level: str (unique, lié à PositionLevel)
  rank: int (1-9)
  label: str (affichage personnalisé)
  requirements: List[str] (prérequis)
  is_active: bool
}
```

### Endpoints Backend
| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/api/jobs/seniority-levels` | GET | Liste les niveaux avec prérequis | ✅ Disponible |
| `/api/jobs/seniority-levels/{level}` | PUT | Met à jour un niveau | ✅ Disponible |

### Correspondance
```typescript
// Frontend (SeniorityLevelDefinition)
interface SeniorityLevelDefinition {
  id: string;
  level: SeniorityLevel;    // TRAINEE, JUNIOR, etc.
  name: string;             // Label (Stagiaire, Junior...)
  rank: number;           // 1-9
  requirements: string[]; // Prérequis
  is_active?: boolean;
}
```

### ✅ Résolu
- Les 9 niveaux backend sont exposés dynamiquement
- Les prérequis sont stockés en JSON dans la base
- Les labels peuvent être personnalisés par niveau

---

## 4. Parcours de Carrière (Career Path)

### Frontend (`SeniorityMatrix`)
**Fonctionnalités actuelles:**
- Visualisation du parcours par famille de métiers
- Progression des niveaux

### Backend
| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/api/jobs/families/{family_id}/career-path` | GET | Positions ordonnées par séniorité | ✅ Disponible |

### Correspondance
```
Frontend (matrice visualisation) → Backend (career-path endpoint)
JobFamily → Positions triées par level
```

---

## 5. Historique de Carrière (Career History)

### Frontend (non encore visible dans careers page)
**Fonctionnalités prévues:**
- Timeline des transitions (PROMOTION, TRANSFER)

### Backend (CareerController)
| Endpoint | Méthode | Description | Statut |
|----------|---------|-------------|--------|
| `/api/career/{employee_id}/history` | GET | Historique complet | ✅ Disponible |
| `/api/career/{employee_id}/onboard` | POST | Premier assignment | ✅ Disponible |
| `/api/career/{employee_id}/promote` | POST | Promotion/Transfert | ✅ Disponible |

### Correspondance Types
```typescript
// Frontend (Transition)
interface Transition {
  id: string;
  employeeId: string;
  type: 'PROMOTION'|'TRANSFER'|'HIRE'|'OFFBOARD';
  date: string;
  fromPositionId?: string;
  toPositionId: string;
  fromOrgUnitId?: string;
  toOrgUnitId: string;
}

// Backend (CareerHistoryOut)
CareerHistoryOut {
  id: UUID;
  position: PositionOut;
  org_unit: OrgUnitOut;
  start_date: date;
  end_date: Optional[date];
  is_current: bool;
  description: Optional[str];
}
```

---

## 6. Transitions & Mobility

### Frontend (prévu mais non implémenté)
**Fonctionnalités:**
- Formulaire de transition (stepper)
- Vacancy Tracker

### Backend
| Service | Méthode | Description | Statut |
|---------|---------|-------------|--------|
| `CareerService.move_employee()` | POST | Gère promotions/transferts | ✅ Disponible |
| `/reports/vacancies` | GET | Positions vacantes | 🔍 À vérifier |

---

## ✅ Mises à jour récentes (Phase 1 complétée)

### Endpoints API
| Fonctionnalité | Endpoint | Statut |
|---------------|----------|--------|
| Liste positions | `GET /api/jobs/positions` | ✅ Créé |
| Modifier position | `PUT /api/jobs/positions/{id}` | ✅ Créé |
| Supprimer position | `DELETE /api/jobs/positions/{id}` | ✅ Créé |
| Liste seniority levels | `GET /api/jobs/seniority-levels` | ✅ Créé |
| Modifier seniority level | `PUT /api/jobs/seniority-levels/{level}` | ✅ Créé |

### Modèles Backend
| Modèle | Description | Statut |
|--------|-------------|--------|
| `SeniorityLevelDefinition` | Table dynamique pour niveaux de séniorité avec requirements JSON | ✅ Créé |

---

## Tableau Récapitulatif des Gaps Restants

| # | Fonctionnalité | Statut | Priorité | Action Requise |
|---|---------------|--------|----------|----------------|
| 1 | ~~CRUD Positions complet~~ | ✅ **Complété** | - | Endpoints créés |
| 2 | ~~Liste positions~~ | ✅ **Complété** | - | `GET /api/jobs/positions` |
| 3 | Stockage prérequis positions | ❌ Manquant | Moyenne | Ajouter champ `requirements` JSON |
| 4 | Stockage skills positions | ❌ Manquant | Moyenne | Nouvelle table `PositionSkill` |
| 5 | ~~Séniorité~~ | ✅ **Résolu** | - | Endpoint dynamique créé |
| 6 | Salary range positions | ❌ Manquant | Basse | Ajouter `salary_min`/`salary_max` |
| 7 | Vacancy tracker | 🔍 À vérifier | Basse | Confirmer endpoint `/reports/vacancies` |

---

## Recommandations d'Implémentation - Phases mises à jour

### ✅ Phase 1 - COMPLÉTÉE
- [x] Créer `GET /api/jobs/positions` pour lister toutes les positions
- [x] Ajouter `PUT /api/jobs/positions/{id}` pour modification
- [x] Ajouter `DELETE /api/jobs/positions/{id}` pour suppression
- [x] Créer `GET /api/jobs/seniority-levels` pour niveaux dynamiques
- [x] Supprimer `DEFAULT_SENIORITY_LEVELS` du frontend
- [x] Créer queries TanStack pour nouveaux endpoints

### Phase 2 (Amélioration)
1. Ajouter stockage des prérequis et skills
2. Connecter les composants frontend aux nouveaux endpoints

### Phase 3 (Features avancées)
3. Implémenter Vacancy Tracker
4. Connecter le formulaire de transition au backend

---

## Architecture Frontend Actuelle

```
Careers Page
├── CareersHeader (tabs: positions | seniority)
│   └── Search + filtres (orgUnit, seniority)
├── PositionsList
│   └── PositionCard (CRUD via jobsStore)
├── SeniorityMatrix
│   └── SeniorityCard (CRUD via jobsStore)
├── PositionSheet (formulaire)
└── SenioritySheet (formulaire)

Stores:
- positionsStore.svelte.ts (filtres, recherche)
- jobs.svelte.ts (data: positions[], seniorityLevels[])
```

## Architecture Backend Disponible

```
Jobs Module
├── JobController
│   ├── GET /families
│   ├── POST /positions
│   ├── GET /families/{id}/career-path
│   ├── GET /positions/level/{level}
│   └── GET /catalog
├── CareerController
│   ├── GET /{id}/history
│   ├── POST /{id}/onboard
│   └── POST /{id}/promote
└── Services
    ├── JobService (CRUD positions/families)
    └── CareerService (transitions)
```
