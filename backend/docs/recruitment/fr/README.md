# Documentation - Module Recruitment

## Vue d'ensemble

Le module **Recruitment** gère l'ensemble du processus de recrutement, depuis la création d'une offre d'emploi jusqu'à l'embauche d'un candidat. Il permet de gérer les candidatures, les entretiens, les évaluations et le suivi du pipeline de recrutement.

## Fonctionnalités principales

### 1. Offres d'emploi
- Création et publication d'offres basées sur des postes définis
- Description complète des postes et exigences
- Plage salariale et avantages
- Gestion des places disponibles et quotas de candidatures
- Statut de publication et dates de fin
- Association avec département et responsable recrutement

### 2. Gestion des candidats
- Base de données de candidats et prospects
- Profil complet avec informations personnelles
- Historique de candidatures par candidat
- Notes et commentaires du recruteur
- Documents attachés (CV, lettres, certificats)

### 3. Candidatures
- Soumission de candidatures pour des offres
- Suivi du statut de candidature
- Notes d'évaluation et feedback
- Mécanisme de shortlist
- Rejet avec motifs personnalisés

### 4. Entretiens
- Programmation d'entretiens (téléphone, en personne, vidéo)
- Évaluations et scoring
- Notes d'interviewer
- Feedback structuré
- Statuts d'entretien (Planifié, En cours, Terminé)

### 5. Processus d'embauche
- Sélection finale des candidats
- Génération de lettres d'offre
- Suivi de l'acceptation
- Intégration avec le module Employees
- Documents d'onboarding

### 6. Pipeline et rapports
- Vue d'ensemble du pipeline de recrutement
- Indicateurs clés (taux de conversion, durée, coût)
- Rapports par position, département
- Suivi des sources de candidats

## Architecture

### Modèles principaux

#### JobOffer
Offre d'emploi publiée
- Titre et slug unique
- Lien avec Position (module Jobs)
- Département associé
- Description détaillée et exigences
- Plage salariale et localisation
- Nombre de places disponibles
- Statut de publication
- Recruteur responsable
- Quota de candidatures

#### Candidate
Profil de candidat
- Informations personnelles (nom, prénom, email)
- Numéro de téléphone
- Compétences et domaines d'expertise
- Localisation
- Statut dans la base de données
- Historique des applications

#### Application
Candidature pour une offre d'emploi
- Lien avec Candidat et Offre
- Statut (En attente, En sélection, Shortlist, Rejet, Acceptée)
- Date de soumission
- Évaluation et score
- Notes du recruteur

#### Interview
Entretien avec un candidat
- Lien avec Application
- Type d'entretien (Téléphone, En personne, Vidéo)
- Date et heure programmées
- Interviewer(s)
- Feedback et notes
- Score/Évaluation
- Statut (Planifié, Réalisé, Reporté, Annulé)

#### HiringDecision
Décision d'embauche finale
- Lien avec Application
- Statut (Approuvée, Rejetée, En attente)
- Offre d'emploi générée
- Salaire proposé
- Date de début
- Documents générés

### Énumérations

- **ApplicationStatus** : SUBMITTED, UNDER_REVIEW, SHORTLISTED, REJECTED, OFFER_MADE, ACCEPTED, ONBOARDING
- **InterviewType** : PHONE_SCREENING, TECHNICAL, BEHAVIORAL, PANEL, VIDEO, ASSESSMENT
- **HiringStatus** : PENDING, APPROVED, REJECTED, WITHDRAWN

## Endpoints API

### Offres d'emploi

```
GET    /api/v1/recruitment/job-offers              - Lister les offres
POST   /api/v1/recruitment/job-offers              - Créer une offre
GET    /api/v1/recruitment/job-offers/{id}         - Détail d'une offre
PUT    /api/v1/recruitment/job-offers/{id}         - Mettre à jour
DELETE /api/v1/recruitment/job-offers/{id}         - Supprimer
PATCH  /api/v1/recruitment/job-offers/{id}/publish - Publier l'offre
PATCH  /api/v1/recruitment/job-offers/{id}/close   - Fermer l'offre
```

### Candidats

```
GET    /api/v1/recruitment/candidates              - Lister les candidats
POST   /api/v1/recruitment/candidates              - Créer un candidat
GET    /api/v1/recruitment/candidates/{id}         - Détail d'un candidat
PUT    /api/v1/recruitment/candidates/{id}         - Mettre à jour
DELETE /api/v1/recruitment/candidates/{id}         - Supprimer
GET    /api/v1/recruitment/candidates/{id}/applications - Candidatures
```

### Candidatures

```
GET    /api/v1/recruitment/applications            - Lister les candidatures
POST   /api/v1/recruitment/applications            - Soumettre une candidature
GET    /api/v1/recruitment/applications/{id}       - Détail d'une candidature
PUT    /api/v1/recruitment/applications/{id}       - Mettre à jour le statut
PATCH  /api/v1/recruitment/applications/{id}/shortlist - Ajouter à la shortlist
PATCH  /api/v1/recruitment/applications/{id}/reject    - Rejeter
GET    /api/v1/recruitment/job-offers/{job_id}/applications - Candidatures pour offre
```

### Entretiens

```
GET    /api/v1/recruitment/interviews              - Lister les entretiens
POST   /api/v1/recruitment/interviews              - Programmer un entretien
GET    /api/v1/recruitment/interviews/{id}         - Détail d'un entretien
PUT    /api/v1/recruitment/interviews/{id}         - Mettre à jour
DELETE /api/v1/recruitment/interviews/{id}         - Annuler
PATCH  /api/v1/recruitment/interviews/{id}/feedback - Ajouter feedback
GET    /api/v1/recruitment/applications/{app_id}/interviews - Entretiens
```

### Embauche

```
GET    /api/v1/recruitment/hiring                  - Lister les décisions
POST   /api/v1/recruitment/hiring                  - Créer une décision
GET    /api/v1/recruitment/hiring/{id}             - Détail d'une décision
PATCH  /api/v1/recruitment/hiring/{id}/approve     - Approuver
PATCH  /api/v1/recruitment/hiring/{id}/reject      - Rejeter
PATCH  /api/v1/recruitment/hiring/{id}/hire        - Finaliser l'embauche
```

### Rapports

```
GET    /api/v1/recruitment/reports/pipeline        - Pipeline de recrutement
GET    /api/v1/recruitment/reports/metrics         - Métriques de recrutement
GET    /api/v1/recruitment/reports/applications    - Rapports de candidatures
```

## Cas d'usage courants

### 1. Créer une offre d'emploi
```json
POST /api/v1/recruitment/job-offers
{
  "title": "Développeur Senior Python",
  "target_position_id": "pos_123",
  "department_id": "dept_456",
  "description": "Nous recherchons un développeur Python...",
  "requirements": "5+ ans d'expérience, Django, PostgreSQL...",
  "salary_range": "40000 - 60000 USD",
  "location": "Kinshasa",
  "slots": 2,
  "max_applications": 100,
  "recruiter_id": "emp_789"
}
```

### 2. Créer un candidat
```json
POST /api/v1/recruitment/candidates
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@email.com",
  "phone": "+243812345678",
  "skills": ["Python", "Django", "PostgreSQL"],
  "location": "Kinshasa"
}
```

### 3. Soumettre une candidature
```json
POST /api/v1/recruitment/applications
{
  "candidate_id": "cand_123",
  "job_offer_id": "offer_456",
  "cover_letter": "Je suis intéressé par ce poste...",
  "resume_url": "https://example.com/resume.pdf"
}
```

### 4. Programmer un entretien
```json
POST /api/v1/recruitment/interviews
{
  "application_id": "app_123",
  "interview_type": "TECHNICAL",
  "scheduled_date": "2026-02-15",
  "scheduled_time": "10:00",
  "interviewers": ["emp_456", "emp_789"],
  "location": "Salle de conférence A"
}
```

### 5. Finaliser une embauche
```json
POST /api/v1/recruitment/hiring
{
  "application_id": "app_123",
  "salary_offered": 50000.00,
  "currency": "USD",
  "start_date": "2026-03-01",
  "job_title": "Développeur Senior Python"
}
```

## Pipeline de recrutement

### Phases typiques
1. **Publication** : Créer et publier l'offre
2. **Candidatures** : Recevoir les candidatures
3. **Tri initial** : Examiner les CV et applications
4. **Shortlist** : Sélectionner les candidats qualifiés
5. **Entretiens** : Conduire les interviews (multiple rounds possibles)
6. **Évaluation** : Évaluer les candidats après les interviews
7. **Sélection** : Choisir le meilleur candidat
8. **Offre** : Envoyer l'offre d'emploi
9. **Signature** : Recevoir l'acceptation
10. **Onboarding** : Intégrer dans le système Employees

## Intégrations

- **Module Jobs** : Positions et postes cibles
- **Module Employees** : Création du profil employé après embauche
- **Module Departments** : Département de destination
- **Système de fichiers** : Stockage des CV et documents

## Bonnes pratiques

### Pour les recruteurs
1. Toujours vérifier que la position existe dans le module Jobs
2. Définir clairement les critères d'évaluation
3. Utiliser des notes et commentaires structurés
4. Planifier les entretiens avec suffisamment d'avance
5. Documenter toutes les décisions d'embauche

### Pour le pipeline
1. Maintenir le pipeline à jour régulièrement
2. Définir des SLA pour chaque phase
3. Utiliser les métriques pour identifier les goulots
4. Impliquer les managers département dès le départ
5. Documenter le feedback candidat pour la base de données

### Conformité
1. Respecter la confidentialité des candidats
2. Conserver les dossiers selon la régulation locale
3. Non-discrimination dans la sélection
4. Transparence sur le processus

## Rapports disponibles

- **Pipeline par phase** : Nombre de candidats à chaque étape
- **Taux de conversion** : De candidature à embauche
- **Durée du processus** : Temps moyen par phase
- **Sources de candidats** : Où proviennent les meilleurs candidats
- **Coût par embauche** : Indicateur financier
- **Candidats par position** : Détail par offre

## Automatisations possibles

- Envoi automatique d'emails de confirmation
- Notifications de deadline d'offre
- Rappels d'entretien programmé
- Génération automatique de lettres d'offre
- Intégration avec système de candidatures externes

## Support et dépannage

Pour toute question ou problème :
1. Vérifier les logs dans `/logs/recruitment/`
2. S'assurer que les positions existent dans Jobs
3. Valider que les emails de candidats sont uniques
4. Contacter le responsable RH pour les décisions complexes

