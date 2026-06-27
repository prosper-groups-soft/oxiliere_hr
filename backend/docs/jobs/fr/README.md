# Documentation - Module Jobs

## Vue d'ensemble

Le module **Jobs** constitue le socle organisationnel d'Oxiliere. Il définit la hiérarchie de l'entreprise, les familles de métiers et les parcours de carrière, permettant une gestion structurée du capital humain.

## Composants Clés

### 1. Structure Organisationnelle (Départements)
- Définition de la hiérarchie fonctionnelle (Arborescence).
- Gestion des responsables d'unités (Managers).
- Suivi analytique des effectifs par département.

### 2. Référentiel Métiers (Familles & Positions)
- **Familles de métiers** : Regroupement logique par domaine d'expertise (ex: Ingénierie, Ventes).
- **Positions** : Rôles spécifiques avec niveaux de séniorité gradués (ex: Junior → Senior → Executive).
- **Parcours de carrière** : Définition des progressions logiques au sein de l'entreprise.

### 3. Gestion des Carrières
- **Historique** : Traçabilité complète des rôles occupés par chaque collaborateur.
- **Mobilité** : Gestion des promotions, mutations et changements de département.
- **Calcul d'ancienneté** : Suivi précis du temps passé dans chaque fonction.

### 4. Développement & Compétences
- **Formation** : Enregistrement des sessions de formation et certifications professionnelles.
- **Conformité** : Suivi automatisé des dates de validité et alertes d'expiration des certificats.
- **Matrice de compétences** : Vue agrégée du profil professionnel de l'employé.

## Modèles de Données

| Entité | Rôle Business |
| :--- | :--- |
| **JobFamily** | Catégorie de spécialité professionnelle. |
| **Position** | Définition d'un poste et de son niveau hiérarchique. |
| **Department** | Unité organisationnelle (Direction, Service, Équipe). |
| **EmployeePositionHistory** | Journal des affectations et des mouvements de carrière. |
| **Training** | Registre des formations et certifications acquises. |

## Niveaux de Séniorité

Oxiliere utilise une échelle standardisée pour harmoniser les carrières :
- `INTERN` / `JUNIOR` / `CONFIRMED` / `SENIOR` : Progression technique et expertise.
- `LEAD` / `MANAGER` / `DIRECTOR` / `EXECUTIVE` : Responsabilités d'encadrement et stratégiques.

## Intégrations

Le module Jobs sert de pivot pour :
- **Employees** : Affectation des nouveaux contrats.
- **Payroll** : Détermination des structures salariales selon le poste.
- **Recruitment** : Définition des profils de postes à pourvoir.
- **Leaves** : Validation hiérarchique basée sur l'organigramme.

## Bonnes Pratiques

1. **Intégrité de l'Organigramme** : Chaque département doit avoir un manager assigné pour garantir les flux d'approbation.
2. **Standardisation** : Utiliser des titres de postes harmonisés pour faciliter les analyses RH globales.
3. **Mise à jour en temps réel** : Enregistrer les mouvements de carrière dès leur effet pour maintenir la fiabilité des données historiques.
ou domaine de métier
- Nom unique
- Description
- Groupement logique des positions
- Utilisé pour l'organisation du recrutement

#### Position
Position ou poste dans une famille de métier
- Lien avec JobFamily
- Nom du poste
- Niveau (Junior, Confirmé, Senior, Manager, Directeur)
- Description des responsabilités
- Exigences spécifiques
- Unique par combinaison (famille, nom, niveau)

#### Department
Département fonctionnel
- Nom unique
- Parent (pour hiérarchie)
- Manager/Responsable
- Description
- Membres (via EmploymentPosition)

#### EmploymentPosition
Assignation d'un employé à une position/département
- Employé
- Position
- Département
- Dates (de, à)
- Niveau d'ancienneté dans le poste
- Statut (Actif, Suspendu, Archivé)

#### CareerTransition
Historique des changements de poste
- Employé
- Position précédente
- Position nouvelle
- Type (Promotion, Mutation, Rétrogradation)
- Raison
- Dates

### Énumérations

- **PositionLevel** : INTERN, JUNIOR, CONFIRMED, SENIOR, LEAD, MANAGER, DIRECTOR, VP, C_LEVEL
- **CareerTransitionType** : PROMOTION, DEMOTION, TRANSFER, SECONDMENT, RETURN
- **EmploymentStatus** : ACTIVE, SUSPENDED, LEAVE, TERMINATED, ARCHIVED

## Endpoints API

### Familles de métiers

```
GET    /api/v1/jobs/families                   - Lister les familles
POST   /api/v1/jobs/families                   - Créer une famille
GET    /api/v1/jobs/families/{id}              - Détail d'une famille
PUT    /api/v1/jobs/families/{id}              - Mettre à jour
DELETE /api/v1/jobs/families/{id}              - Supprimer
GET    /api/v1/jobs/families/{id}/positions    - Positions dans la famille
```

### Positions

```
GET    /api/v1/jobs/positions                  - Lister les positions
POST   /api/v1/jobs/positions                  - Créer une position
GET    /api/v1/jobs/positions/{id}             - Détail d'une position
PUT    /api/v1/jobs/positions/{id}             - Mettre à jour
DELETE /api/v1/jobs/positions/{id}             - Supprimer
GET    /api/v1/jobs/positions/{id}/employees   - Employés à ce poste
```

### Départements

```
GET    /api/v1/jobs/departments                - Lister les départements
POST   /api/v1/jobs/departments                - Créer un département
GET    /api/v1/jobs/departments/{id}           - Détail d'un département
PUT    /api/v1/jobs/departments/{id}           - Mettre à jour
DELETE /api/v1/jobs/departments/{id}           - Supprimer
GET    /api/v1/jobs/departments/{id}/hierarchy - Vue hiérarchique
GET    /api/v1/jobs/departments/{id}/members   - Membres du département
GET    /api/v1/jobs/departments/{id}/subs      - Sous-départements
```

### Assignations d'emploi

```
GET    /api/v1/jobs/employment-positions       - Lister les assignations
POST   /api/v1/jobs/employment-positions       - Assigner un employé
GET    /api/v1/jobs/employment-positions/{id}  - Détail d'une assignation
PUT    /api/v1/jobs/employment-positions/{id}  - Mettre à jour
GET    /api/v1/jobs/employees/{emp_id}/positions - Postes d'un employé
GET    /api/v1/jobs/employees/{emp_id}/current - Poste actuel
```

### Carrière

```
GET    /api/v1/jobs/career-transitions         - Lister les transitions
POST   /api/v1/jobs/career-transitions         - Enregistrer une transition
GET    /api/v1/jobs/career-transitions/{id}    - Détail d'une transition
GET    /api/v1/jobs/employees/{emp_id}/history - Historique de carrière
GET    /api/v1/jobs/careers/{emp_id}/path      - Parcours de carrière
```

### Rapports

```
GET    /api/v1/jobs/reports/org-chart          - Organigramme
GET    /api/v1/jobs/reports/headcount          - Effectifs par département
GET    /api/v1/jobs/reports/positions-filled   - Positions pourvues
GET    /api/v1/jobs/reports/vacancies          - Positions vacantes
```

## Cas d'usage courants

### 1. Créer une famille de métier
```json
POST /api/v1/jobs/families
{
  "name": "Ingénierie Logiciel",
  "description": "Équipe de développement de produits logiciels"
}
```

### 2. Créer des positions dans une famille
```json
POST /api/v1/jobs/positions
{
  "job_family_id": "fam_123",
  "name": "Développeur Python",
  "level": "SENIOR",
  "description": "Développeur Python senior pour projets backend"
}
```

### 3. Créer un département
```json
POST /api/v1/jobs/departments
{
  "name": "Ingénierie",
  "parent_id": null,
  "manager_id": "emp_456",
  "description": "Département d'ingénierie principal"
}
```

### 4. Créer un sous-unité organnisationnelle
```json
POST /api/v1/jobs/units
{
  "name": "Backend",
  "parent_id": "unit_123",
  "manager_id": "emp_789",
  "description": "Équipe développement backend"
}
```

### 5. Assigner un employé à une position
```json
POST /api/v1/jobs/employment-positions
{
  "employee_id": "emp_123",
  "position_id": "pos_456",
  "department_id": "unit_789",
  "start_date": "2026-01-15",
  "status": "ACTIVE"
}
```

### 6. Enregistrer une promotion
```json
POST /api/v1/jobs/career-transitions
{
  "employee_id": "emp_123",
  "from_position_id": "pos_456",
  "to_position_id": "pos_789",
  "transition_type": "PROMOTION",
  "reason": "Performance exceptionnelle",
  "transition_date": "2026-02-01"
}
```

## Structures organisationnelles

### Exemple d'organigramme
```
Ingénierie (Manager: Jean)
├── Backend (Manager: Marie)
│   ├── Développeur Python 1
│   ├── Développeur Python 2
│   └── DevOps Engineer
└── Frontend (Manager: Pierre)
    ├── Développeur React 1
    ├── Développeur React 2
    └── UX Designer

Ressources Humaines (Manager: Sophie)
├── Recrutement
│   ├── Recruteur 1
│   └── Recruteur 2
└── Paie et Administration
    ├── Gestionnaire Paie 1
    └── Gestionnaire Paie 2
```

## Intégrations

- **Module Employees** : Assignation d'employés aux positions
- **Module Recruitment** : Positions cibles pour offres d'emploi
- **Module Payroll** : Positions liées aux contrats et salaires
- **Module Attendance** : Horaires selon poste
- **Module Leaves** : Approbateurs basés sur hiérarchie

## Rapports disponibles

### Organigramme
- Vue hiérarchique complète
- Relation manager-collaborateur
- Affichage par département

### Effectifs (Headcount)
- Par département
- Par famille de métier
- Par niveau
- Tendances (embauches, départs)

### Positions pourvues/vacantes
- Taux de pourvoir
- Positions ouvertes au recrutement
- Délai moyen de pourvoir
- Rotation des postes

### Carrière
- Historique de chaque employé
- Parcours type par position
- Taux de promotion
- Temps moyen entre promotions

## Bonnes pratiques

1. **Hiérarchie claire** : Pas d'ambiguïté dans les reportings
2. **Noms standards** : Utiliser des noms cohérents
3. **Documentation** : Description claire de chaque poste
4. **Mise à jour** : Garder l'organigramme à jour
5. **Archivage** : Conserver l'historique des changements
6. **Validation** : Manager valide les changements de poste

## Définition des niveaux

### Exemple de progression
```
INTERN        → Étudiant/Apprenti
JUNIOR        → 0-2 ans d'expérience
CONFIRMED     → 2-5 ans d'expérience
SENIOR        → 5+ ans d'expérience
LEAD          → Chef d'équipe sans management formel
MANAGER       → Management d'équipe
DIRECTOR      → Directeur de département
VP            → Vice-Président
C_LEVEL       → PDG, CFO, CTO, etc.
```

## Cas d'usage avancés

### Gestion des doubling
```
Lors d'une transition de poste :
1. Créer une période de 2-4 semaines avec ancien + nouveau poste
2. Enregistrer une transition quand l'ancien poste se termine
3. Maintenir continuité des contrats et paie
```

### Secondment temporaire
```
Assigner temporairement un employé à autre département :
1. Créer une nouvelle assignation avec dates limitées
2. Utiliser type de transition SECONDMENT
3. L'ancien poste reste assigné avec date de fin
4. Paie gérée selon lieu principal
```

### Structure matricielle
```
Un employé peut avoir plusieurs assignations :
- Position officielle + département
- Responsabilité projet/produit
- Ligne de report double (manager + directeur)
- Gérer en parallèle via plusieurs records
```

## Support et dépannage

Pour toute question ou problème :
1. Vérifier la hiérarchie de département
2. S'assurer que le manager est un employé actif
3. Valider que les positions existent
4. Consulter l'historique des transitions
5. Contacter l'équipe d'administration pour les restructurations
