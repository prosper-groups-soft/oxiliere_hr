# Catalogue : Performance

> Types concrets du module performance, leurs configurations et cas d'usage.

---

## Tableau récapitulatif des types

| Type | Concept parent | Description | Utilisation typique |
|------|----------------|-------------|-------------------|
| `CampagneAnnuelle` | Campagne | Campagne annuelle (janv-déc) | Cycle standard |
| `CampagneSemestrielle` | Campagne | Campagne semestrielle | 2 fois par an |
| `CampagneProbation` | Campagne | Période d'essai (3-6 mois) | Nouveaux employés |
| `ObjectifQualitatif` | Objectif | Objectif SMART qualitatif | "Améliorer la com interne" |
| `ObjectifKPI` | Objectif | Objectif quantitatif | "Atteindre 95% satisfaction" |
| `CompétenceTechnique` | Compétence | Savoir-faire technique | Python, Excel, SQL |
| `CompétenceComportementale` | Compétence | Soft skill | Communication, leadership |

---

## Types de Campagne

### Campagne Annuelle

| Propriété | Valeur |
|-----------|--------|
| Description | Évaluation annuelle sur l'année calendaire |
| Durée typique | 12 mois (1 janv - 31 déc) |
| Deadline soumission | 31 janvier N+1 |
| Participants | Tous les employés ayant ≥ 6 mois d'ancienneté |
| Défaut `name` | `Annuel {année}` |

**Correspondance code** : Filtre `type` sur `Campagne`.

### Campagne Semestrielle

| Propriété | Valeur |
|-----------|--------|
| Description | Évaluation semestrielle (S1 ou S2) |
| Durée typique | 6 mois |
| Deadline soumission | 1 mois après fin de période |
| Participants | Tous les employés ayant ≥ 3 mois d'ancienneté |
| Défaut `name` | `SA{1|2} {année}` |

**Correspondance code** : Filtre `type` sur `Campagne`.

### Campagne Probation

| Propriété | Valeur |
|-----------|--------|
| Description | Évaluation de fin de période d'essai |
| Durée typique | Période définie dans le contrat |
| Deadline soumission | 1 semaine avant fin de probation |
| Participants | Employés en période d'essai |
| Défaut `name` | `Probation - {employé}` |

**Correspondance code** : La campagne est liée à un seul employé (ou une cohorte).

---

## Types d'Objectif

### Objectif Qualitatif (`OBJECTIVE`)

| Propriété | Valeur |
|-----------|--------|
| Concept parent | Objectif |
| Description | Objectif SMART qualitatif, non mesurable numériquement |
| Comportement par défaut | Évalué sur 1-5, basé sur l'appréciation |
| Poids par défaut | 1/N |
| Exemple | "Améliorer la qualité de la documentation interne" |

### Objectif KPI (`KPI`)

| Propriété | Valeur |
|-----------|--------|
| Concept parent | Objectif |
| Description | Objectif quantitatif avec cible mesurable |
| Comportement par défaut | Évalué sur 1-5 en fonction du taux d'atteinte |
| Poids par défaut | 1/N (mais souvent plus élevé que les qualitatifs) |
| Validation | Le taux d'atteinte est saisi par le manager |
| Exemple | "Atteindre 95% de satisfaction client (cible: 95%, réel: 92%)" |

---

## Types de Compétence

### Compétence Technique (`TECHNICAL`)

| Propriété | Valeur |
|-----------|--------|
| Concept parent | Compétence |
| Description | Savoir-faire technique lié au poste |
| Échelle | 1-5 |
| Exemples | Python, Django, Excel, SQL, Gestion de projet |

### Compétence Comportementale (`BEHAVIORAL`)

| Propriété | Valeur |
|-----------|--------|
| Concept parent | Compétence |
| Description | Soft skill, comportement au travail |
| Échelle | 1-5 |
| Exemples | Communication, Travail d'équipe, Adaptabilité |

### Compétence Leadership (`LEADERSHIP`)

| Propriété | Valeur |
|-----------|--------|
| Concept parent | Compétence |
| Description | Capacité à diriger, manager, influencer |
| Échelle | 1-5 |
| Exemples | Prise de décision, Mentorat, Vision stratégique |
| Note | Applicable uniquement aux managers/leads |

---

## Échelles de notation

### Niveaux (1-5) pour objectifs

| Niveau | Label | Description |
|--------|-------|-------------|
| 1 | Insuffisant | Objectif non atteint, résultats très en dessous des attentes |
| 2 | En dessous | Partiellement atteint, des lacunes significatives |
| 3 | Satisfaisant | Atteint conformément aux attentes |
| 4 | Dépassé | Résultats au-delà des attentes |
| 5 | Exceptionnel | Résultats exceptionnels, dépasse largement les attentes |

### Niveaux (1-5) pour compétences

| Niveau | Label | Description |
|--------|-------|-------------|
| 1 | Débutant | Connaissances de base, nécessite un accompagnement |
| 2 | Novice | Peut réaliser des tâches simples en autonomie |
| 3 | Intermédiaire | Autonome sur la majorité des situations |
| 4 | Avancé | Référent, peut former les autres |
| 5 | Expert | Reconnu, innovant, peut définir la stratégie |

### Correspondance score final → mention

| Score | Mention |
|-------|---------|
| 0 - 1.9 | Insuffisant |
| 2.0 - 2.9 | À améliorer |
| 3.0 - 3.5 | Satisfaisant |
| 3.6 - 4.2 | Bon |
| 4.3 - 5.0 | Excellent |

---

## Exemples d'utilisation

### Exemple 1 : Campagne SA1 classique

```json
{
  "campaign": {
    "name": "SA1 2026",
    "type": "SEMESTRIEL",
    "start_date": "2026-01-01",
    "end_date": "2026-06-30",
    "submission_deadline": "2026-07-15",
    "status": "ACTIVE",
    "participants": ["uuid-employe-1", "uuid-employe-2", "..."]
  },
  "evaluation": {
    "employee": "uuid-employe-1",
    "manager": "uuid-manager-1",
    "status": "MANAGER_DRAFT",
    "goals": [
      {
        "description": "Lancer la feature reporting RH",
        "type": "OBJECTIVE",
        "weight": 0.6,
        "employee_rating": 4,
        "manager_rating": 3
      },
      {
        "description": "Atteindre 95% de complétion des évaluations",
        "type": "KPI",
        "weight": 0.4,
        "employee_rating": 5,
        "manager_rating": 4
      }
    ],
    "skills": [
      { "name": "Python", "category": "TECHNICAL", "employee_level": 4, "manager_level": 3 },
      { "name": "Communication", "category": "BEHAVIORAL", "employee_level": 3, "manager_level": 4 }
    ]
  }
}
```

### Exemple 2 : Campagne Probation

```json
{
  "campaign": {
    "name": "Probation - Jean Dupont",
    "type": "PROBATION",
    "start_date": "2026-03-01",
    "end_date": "2026-08-31",
    "submission_deadline": "2026-08-24",
    "status": "ACTIVE",
    "participants": ["uuid-jean-dupont"]
  },
  "evaluation": {
    "employee": "uuid-jean-dupont",
    "manager": "uuid-marie-martin",
    "status": "SUBMITTED",
    "goals": [
      {
        "description": "Maîtriser le processus de paie",
        "type": "OBJECTIVE",
        "employee_rating": 3,
        "manager_rating": 3
      }
    ],
    "skills": [
      { "name": "Django", "category": "TECHNICAL", "employee_level": 2, "manager_level": 3 },
      { "name": "Travail d'équipe", "category": "BEHAVIORAL", "employee_level": 4, "manager_level": 4 }
    ]
  }
}
```

---

## Correspondances avec le code (planifié)

| Concept | Backend (Django) | Frontend (Svelte) |
|---------|-----------------|-------------------|
| Campagne | `Campaign` model + `CampaignController` | `campaigns/` routes + sheets |
| Évaluation | `PerformanceReview` model (refactored) | `reviews/` routes + components |
| Objectif | `Goal` model (nouveau, table séparée) | `GoalEditor` (refactored) |
| Compétence | `Skill` model (nouveau, table séparée) | `SkillEditor` (refactored) |
| Plan de développement | `DevelopmentPlan` model | `plans/` components |
| Calibrage | `Calibration` model | `calibration/` components (RH) |
| Scoring | Service `ScoreCalculator` | Affiché dans `ReviewDetail` |
