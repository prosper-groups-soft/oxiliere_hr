# API : Performance

> Interfaces concrètes backend (Django Ninja) et frontend (Svelte / TanStack Query).

---

## 1. Modèles Django

### Campaign

```python
class Campaign(BaseAuditableModel):
    """Campagne d'évaluation (ex: SA1 2026)."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    campaign_type = models.CharField(max_length=20, choices=CampaignType.choices)  # ANNUAL, SEMESTRIAL, PROBATION
    start_date = models.DateField()
    end_date = models.DateField()
    submission_deadline = models.DateField()
    status = models.CharField(max_length=15, choices=CampaignStatus.choices, default=CampaignStatus.DRAFT)
    goal_weight = models.FloatField(default=0.6)
    skill_weight = models.FloatField(default=0.4)
    participants = models.ManyToManyField('hr_employees.Employee', through='CampaignParticipation')
```

### PerformanceReview (refactoré)

```python
class PerformanceReview(BaseAuditableModel):
    """Évaluation d'un employé pour une campagne."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='reviews')
    employee = models.ForeignKey('hr_employees.Employee', on_delete=models.CASCADE, related_name='performance_reviews')
    manager = models.ForeignKey('hr_employees.Employee', on_delete=models.SET_NULL, null=True, related_name='reviews_given')
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.EMPLOYEE_DRAFT)
    disputed = models.BooleanField(default=False)

    # Auto-évaluation (rempli par l'employé)
    goals = models.JSONField(default=list)
    skills = models.JSONField(default=list)
    employee_comment = models.TextField(blank=True)

    # Évaluation manager
    goals_manager = models.JSONField(default=list)  # manager_rating, manager_comment par objectif
    skills_manager = models.JSONField(default=list)  # manager_level par compétence
    manager_comment = models.TextField(blank=True)
    manager_overall_score = models.PositiveSmallIntegerField(null=True, blank=True)  # saisie indicative

    # Scores
    overall_score = models.FloatField(null=True, blank=True)  # calculé
    calibrated_score = models.FloatField(null=True, blank=True)  # ajusté par RH

    # Dates clés
    employee_submitted_at = models.DateTimeField(null=True, blank=True)
    manager_submitted_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
```

> [!NOTE]
> On garde `goals` et `skills` en JSON pour la flexibilité (comme aujourd'hui), mais on ajoute `goals_manager` et `skills_manager` pour que l'employé et le manager aient chacun leur évaluation.

### Nouveaux schémas

```python
# Goal avec ratings séparés
class GoalSchema(Schema):
    description: str
    type: PerformanceGoalType
    weight: Optional[float] = None
    employee_rating: Optional[int] = None  # saisi par employé en EMPLOYEE_DRAFT
    manager_rating: Optional[int] = None  # saisi par manager en MANAGER_DRAFT
    status: Optional[str] = "PENDING"

class SkillSchema(Schema):
    name: str
    category: Optional[str] = "BEHAVIORAL"
    employee_level: Optional[int] = None
    manager_level: Optional[int] = None
```

---

## 2. Endpoints REST

### Campagnes

```
GET    /api/performance/campaigns                 → List (paginated)
POST   /api/performance/campaigns                 → Create
GET    /api/performance/campaigns/{id}            → Detail
PATCH  /api/performance/campaigns/{id}            → Update
POST   /api/performance/campaigns/{id}/activate   → DRAFT → ACTIVE
POST   /api/performance/campaigns/{id}/close       → ACTIVE → CLOSED
GET    /api/performance/campaigns/{id}/participants → Participants list
POST   /api/performance/campaigns/{id}/add-participant → Ajouter un participant
```

### Évaluations

```
GET    /api/performance/reviews                    → List (paginated, filtres: campaign, status, employee)
POST   /api/performance/reviews                    → Create (automatique via campagne)
GET    /api/performance/reviews/{id}               → Detail
PATCH  /api/performance/reviews/{id}               → Update (selon statut)
DELETE /api/performance/reviews/{id}               → Delete (DRAFT only)

POST   /api/performance/reviews/{id}/submit-employee  → EMPLOYEE_DRAFT → MANAGER_DRAFT
POST   /api/performance/reviews/{id}/submit-manager    → MANAGER_DRAFT → SUBMITTED
POST   /api/performance/reviews/{id}/calibrate         → SUBMITTED → CALIBRATED (RH only)
POST   /api/performance/reviews/{id}/acknowledge       → CALIBRATED → ACKNOWLEDGED
POST   /api/performance/reviews/{id}/dispute            → disputed = true
```

---

## 3. Types TypeScript Frontend

```typescript
// Basé sur banking types — même pattern

export type CampaignStatus = 'DRAFT' | 'ACTIVE' | 'CLOSED';
export type CampaignType = 'ANNUAL' | 'SEMESTRIAL' | 'PROBATION';

export interface Campaign {
  id: string;
  name: string;
  description: string;
  campaign_type: CampaignType;
  start_date: string;
  end_date: string;
  submission_deadline: string;
  status: CampaignStatus;
  goal_weight: number;
  skill_weight: number;
  created_at: string;
}

export type ReviewStatus = 'EMPLOYEE_DRAFT' | 'MANAGER_DRAFT' | 'SUBMITTED' | 'CALIBRATED' | 'ACKNOWLEDGED';

export interface Goal {
  description: string;
  type: 'OBJECTIVE' | 'KPI';
  weight?: number;
  employee_rating?: number;
  manager_rating?: number;
  status: 'PENDING' | 'ACHIEVED' | 'PARTIAL' | 'NOT_ACHIEVED' | 'CANCELLED';
}

export interface Skill {
  name: string;
  category?: 'TECHNICAL' | 'BEHAVIORAL' | 'LEADERSHIP';
  employee_level?: number;
  manager_level?: number;
}

export interface PerformanceReview {
  id: string;
  campaign_id: string;
  campaign_name: string;
  employee_id: string;
  employee_name: string;
  manager_id: string;
  manager_name: string;
  status: ReviewStatus;
  disputed: boolean;
  goals: Goal[];
  skills: Skill[];
  employee_comment: string;
  manager_comment: string;
  manager_overall_score?: number;
  overall_score?: number;
  calibrated_score?: number;
  employee_submitted_at?: string;
  manager_submitted_at?: string;
  acknowledged_at?: string;
  created_at: string;
}
```

---

## 4. Composants UI (planifiés)

| Composant | Usage | Pages associées |
|-----------|-------|-----------------|
| `CampaignList` | Tableau des campagnes | `/performance/campaigns` |
| `CampaignSheet` | Création/édition campagne | Sheet |
| `CampaignCard` | Résumé d'une campagne | Dashboard |
| `ReviewList` | Liste des évaluations | `/performance/reviews` |
| `ReviewDetail` | Détail d'une évaluation | `/performance/reviews/[id]` |
| `ReviewSheet` | Formulaire (employé + manager) | Sheet |
| `GoalEditor` | Interface d'objectifs | Dans ReviewSheet |
| `SkillEditor` | Interface de compétences | Dans ReviewSheet |
| `ScoreDisplay` | Affichage du score calculé | Dans ReviewDetail |
| `CalibrationPanel` | Calibrage RH | `/performance/calibration` |
| `DevPlanPanel` | Plan de développement | Dans ReviewDetail |

---

## 5. Queries TanStack

```typescript
// Campagnes
export function useCampaignsQuery(filters: ...) = createQuery(...)
export function useCreateCampaignMutation() = createMutation(...)
export function useActivateCampaignMutation() = createMutation(...)

// Évaluations
export function useReviewsQuery(filters: ...) = createQuery(...)
export function useReviewDetailQuery(id: () => string) = createQuery(...)
export function useCreateReviewMutation() = createMutation(...)
export function useUpdateReviewMutation() = createMutation(...)
export function useSubmitEmployeeMutation() = createMutation(...)
export function useSubmitManagerMutation() = createMutation(...)
export function useCalibrateMutation() = createMutation(...)
export function useAcknowledgeMutation() = createMutation(...)
export function useDisputeMutation() = createMutation(...)
```
