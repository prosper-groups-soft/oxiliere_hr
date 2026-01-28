# Documentation - Module Attendance

## Vue d'ensemble

Le module **Attendance** gère le suivi de la présence des employés, les horaires de travail, les pointages et la gestion des heures travaillées. Il calcule les heures réelles par rapport aux heures prévues et génère des rapports pour la paie et l'analyse du temps de travail.

## Fonctionnalités principales

### 1. Politiques de travail
- Définition des horaires standards par équipe
- Détails quotidiens (heures de début/fin)
- Pauses autorisées (durée et timing)
- Jours de travail par semaine
- Flexibilité des horaires

### 2. Schémas d'emploi
- Attribution de politiques de travail aux employés
- Dates d'effectivité (de, jusqu'à)
- Support de contrats saisonniers
- Historique des changements
- Statut actif/inactif

### 3. Assignations de poste
- Attribution d'un poste spécifique
- Dates (de, jusqu'à)
- Shift spécifique au poste
- Historique des assignations

### 4. Pointages
- Enregistrement des arrivées/départs
- Timestamps précis
- Types de punch (Arrivée, Départ, Pause début, Pause fin)
- Vérification de cohérence

### 5. Feuilles de temps
- Enregistrement journalier des heures
- Calcul des heures travaillées
- Heure supplémentaires
- Absence et motifs
- Approbation par manager

### 6. Rapports
- Feuille de présence par employé/département
- Heures supplémentaires
- Absences et motifs
- Conformité aux horaires
- Coûts de travail

## Architecture

### Modèles principaux

#### ShiftPolicy
Politique de travail (horaires types)
- Nom unique
- Description
- Heures hebdomadaires cibles
- Applicable aux employés

#### ShiftDetail
Détails journaliers d'une politique
- Lien avec ShiftPolicy
- Jour de la semaine
- Heure de début/fin
- Heure de pause et durée
- Jour travaillé (oui/non)
- Flexibilité (heures fixes vs durée)

#### EmploymentScheme
Assignation d'une politique à un employé
- Employé
- Politique
- Dates d'effectivité (de, jusqu'à)
- Statut actif/inactif

#### ShiftAssignment
Assignation d'un shift spécifique
- Employé
- Policy
- Dates (de, jusqu'à)

#### Punch
Pointage (arrivée, départ, pause)
- Employé
- Timestamp exact
- Type (CLOCK_IN, CLOCK_OUT, BREAK_START, BREAK_END)
- Location optionnel
- Device (badge, app, web)

#### DailyRegister
Registre journalier consolidé
- Employé et date
- Code généré automatiquement
- Status de la timesheet
- Heures calculées
- Anomalies détectées

#### TimeSheet
Feuille de temps pour période (jour/semaine/mois)
- Employé
- Période
- Heures travaillées
- Heures supplémentaires
- Absences
- Approbation (manager)
- Status (Brouillon, Soumis, Approuvé, Rejeté)

### Énumérations

- **TimeSheetStatus** : DRAFT, SUBMITTED, APPROVED, REJECTED, FINALIZED
- **PunchType** : CLOCK_IN, CLOCK_OUT, BREAK_START, BREAK_END
- **WeekdayEnum** : MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
- **DeviceType** : BADGE_READER, MOBILE_APP, WEB_PORTAL, BIOMETRIC, MANUAL

## Endpoints API

### Politiques de travail

```
GET    /api/v1/attendance/policies              - Lister les politiques
POST   /api/v1/attendance/policies              - Créer une politique
GET    /api/v1/attendance/policies/{id}         - Détail d'une politique
PUT    /api/v1/attendance/policies/{id}         - Mettre à jour
DELETE /api/v1/attendance/policies/{id}         - Supprimer
GET    /api/v1/attendance/policies/{id}/details - Détails journaliers
```

### Schémas d'emploi

```
GET    /api/v1/attendance/schemes               - Lister les schémas
POST   /api/v1/attendance/schemes               - Assigner un schéma
GET    /api/v1/attendance/schemes/{id}          - Détail d'un schéma
PUT    /api/v1/attendance/schemes/{id}          - Mettre à jour
GET    /api/v1/attendance/employees/{emp_id}/scheme - Schéma actuel
```

### Pointages

```
GET    /api/v1/attendance/punches               - Lister les pointages
POST   /api/v1/attendance/punches               - Enregistrer un pointage
GET    /api/v1/attendance/punches/{id}          - Détail d'un pointage
GET    /api/v1/attendance/employees/{emp_id}/punches - Pointages employé
GET    /api/v1/attendance/punches?date=2026-01-15 - Par date
GET    /api/v1/attendance/punches?date_range=2026-01-01..2026-01-31 - Période
```

### Registre journalier

```
GET    /api/v1/attendance/daily-register        - Lister les registres
GET    /api/v1/attendance/daily-register/{id}   - Détail d'un registre
GET    /api/v1/attendance/employees/{emp_id}/daily-register - Registre employé
GET    /api/v1/attendance/daily-register/{date} - Registre de la date
```

### Feuilles de temps

```
GET    /api/v1/attendance/timesheets            - Lister les timesheets
POST   /api/v1/attendance/timesheets            - Créer/Soumettre
GET    /api/v1/attendance/timesheets/{id}       - Détail d'une timesheet
PUT    /api/v1/attendance/timesheets/{id}       - Mettre à jour
PATCH  /api/v1/attendance/timesheets/{id}/submit - Soumettre
PATCH  /api/v1/attendance/timesheets/{id}/approve - Approuver
PATCH  /api/v1/attendance/timesheets/{id}/reject - Rejeter
GET    /api/v1/attendance/employees/{emp_id}/timesheets - Timesheets employé
```

### Rapports

```
GET    /api/v1/attendance/reports/presence     - Rapport de présence
GET    /api/v1/attendance/reports/overtime     - Rapport heures supplémentaires
GET    /api/v1/attendance/reports/absences     - Rapport d'absences
GET    /api/v1/attendance/reports/summary      - Résumé par département
```

## Cas d'usage courants

### 1. Créer une politique de travail standard
```json
POST /api/v1/attendance/policies
{
  "name": "Standard 40h/semaine",
  "description": "Horaires standards 9h-17h",
  "weekly_target_hours": "40:00:00"
}
```

### 2. Ajouter les horaires journaliers
```json
POST /api/v1/attendance/policies/{policy_id}/details
{
  "weekday": "MONDAY",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "break_start_time": "12:00:00",
  "break_duration": "01:00:00",
  "is_working_day": true,
  "flexible_hours": false
}
```

### 3. Assigner une politique à un employé
```json
POST /api/v1/attendance/schemes
{
  "employee_id": "emp_123",
  "policy_id": "policy_456",
  "valid_from": "2026-01-01",
  "is_active": true
}
```

### 4. Enregistrer un pointage
```json
POST /api/v1/attendance/punches
{
  "employee_id": "emp_123",
  "punch_type": "CLOCK_IN",
  "timestamp": "2026-01-15T09:05:00+02:00",
  "location": "Entrée principale",
  "device": "BADGE_READER"
}
```

### 5. Consulter le registre du jour
```json
GET /api/v1/attendance/daily-register/2026-01-15
Response:
{
  "date": "2026-01-15",
  "total_employees_scheduled": 150,
  "employees_present": 148,
  "employees_absent": 2,
  "employees_late": 5,
  "overtime_hours": 12.5,
  "register_code": "2026-01-15-REG001"
}
```

### 6. Soumettre une feuille de temps hebdomadaire
```json
POST /api/v1/attendance/timesheets
{
  "employee_id": "emp_123",
  "period_start": "2026-01-13",
  "period_end": "2026-01-19",
  "hours_worked": 40,
  "hours_overtime": 2,
  "absences": 0,
  "notes": "Tout à fait normal"
}
```

### 7. Approuver une feuille de temps
```json
PATCH /api/v1/attendance/timesheets/ts_123/approve
{
  "approver_id": "emp_456",
  "status": "APPROVED",
  "comments": "Approuvé, tout conforme"
}
```

## Calcul des heures

### Heures travaillées
```
Heures = (Heure départ - Heure arrivée) - Durée pauses
```

### Heure supplémentaire
```
Heures supplémentaires = Heures travaillées - Heures cibles
(si > 0)
```

### Absence
```
Absence = Jour travaillé mais aucun pointage
= Heures cibles de la journée
```

## États de la feuille de temps

- **DRAFT** : Non soumise, modifiable
- **SUBMITTED** : Soumise en attente d'approbation
- **APPROVED** : Approuvée par manager
- **REJECTED** : Rejetée, corrections requises
- **FINALIZED** : Intégrée à la paie

## Intégrations

- **Module Payroll** : Heures travaillées pour calcul paie
- **Module Jobs** : Horaires selon poste
- **Module Leaves** : Jours de congé comptabilisés comme présents
- **Module Calendar** : Jours fériés exclus du calcul
- **Module Employees** : Données employé

## Rapports disponibles

### Par employé
- Feuille de présence mensuelle
- Heures supplémentaires
- Absences et motifs
- Tendances

### Par département
- Présence totale
- Taux de présence
- Heures supplémentaires
- Coûts de travail

### Globaux
- Effectifs présents/absent
- Retards
- Départs anticipés
- Anomalies

## Bonnes pratiques

1. **Politique claire** : Définir clairement les horaires
2. **Vérification** : Vérifier quotidiennement le registre
3. **Correction rapide** : Corriger les anomalies rapidement
4. **Approbation** : Approuver timesheets en temps opportun
5. **Documentation** : Documenter les absences
6. **Réconciliation** : Rapprocher avec paie mensuellement

## Validation des données

- Pointages : Timestamp valide, type valide
- Horaires : Fin ≥ début, cohérence avec politique
- Timesheets : Heures ≥ 0, correspondance avec pointages
- Schéma : Dates cohérentes, chevauchement validé

## Anomalies courantes

- **Oubli pointage** : Pas de clock-in ou clock-out
- **Pause manquante** : Pas de break enregistré
- **Durée anormale** : Heures sans rapport avec horaires
- **Chevauchement** : Deux politiques actives simultanément
- **Incohérence** : Timesheet vs pointages différents

## Support et dépannage

Pour toute question ou problème :
1. Vérifier la politique assignée à l'employé
2. Consulter les pointages enregistrés
3. Valider les dates et périodes
4. Comparer avec le registre journalier
5. Contacter Manager/Paie pour corrections
6. Vérifier les intégrations avec autres modules
