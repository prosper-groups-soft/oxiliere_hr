# Documentation - Module Employees

## Vue d'ensemble

Le module **Employees** gère l'identité centrale de tous les collaborateurs. Il maintient les données personnelles, professionnelles, administratives et les contacts d'urgence des employés, servant de base pour tous les autres modules de l'application RH.

## Fonctionnalités principales

### 1. Profil employé
- Identité complète (nom, prénom, numéro de matricule)
- Données personnelles (date de naissance, genre, nationalité)
- Informations de contact (email, téléphone)
- Statut du contrat (Actif, En congé, Suspendu, Résilié)
- Dates d'embauche et résiliation

### 2. Documents et pièces justificatives
- Types de documents (Passeport, Permis de résidence, Visa)
- Fichiers attachés et références
- Dates de validité
- Statut de vérification

### 3. Bénéficiaires et dépendants
- Relation de famille (Conjoint, Enfant, Parent)
- Informations personnelles du bénéficiaire
- Bénéficiaire d'assurance
- Bénéficiaire en cas de décès

### 4. Adresses et localisation
- Adresse personnelle
- Adresse de travail
- Plusieurs adresses possibles
- Géolocalisation

### 5. Données académiques
- Niveau d'études (Primaire, Secondaire, Licence, Master, Doctorat)
- Domaines de spécialisation
- Historique de formation

### 6. Statuts et indicateurs
- Statut marital (Célibataire, Marié, Divorcé, Veuf)
- Nombre de dépendants
- Activé/Désactivé
- Archivé

## Architecture

### Modèles principaux

#### Employee
Profil central d'un employé
- Identité (matricule unique, nom, prénom, etc.)
- Données personnelles (genre, date de naissance, nationalité)
- Contact (email, téléphone)
- Dates (embauche, résiliation)
- Statut (Actif, Congé, Suspendu, Résilié)
- Lien avec utilisateur système (optionnel)

#### EmployeeDocument
Documents d'identification et pièces justificatives
- Employé
- Type de document (Passeport, Carte d'identité, Permis de résidence)
- Numéro/Référence
- Dates de validité
- Fichier attaché
- Statut de vérification (Non vérifié, Accepté, Rejeté)

#### EmployeeFamilyMember
Bénéficiaires et dépendants
- Employé parent
- Prénom, nom
- Relation (Conjoint, Enfant, Parent, Frère/Sœur)
- Date de naissance
- Genre
- Bénéficiaire d'assurance
- Bénéficiaire en cas de décès

#### Address (AddressMixin)
Gestion des adresses (personnelle, professionnelle)
- Rue et numéro
- Ville, Province, Pays
- Code postal
- Type d'adresse

#### EmployeeEducation
Historique académique
- Employé
- Niveau d'études
- Domaine/Spécialisation
- Institution
- Dates (de, à)

### Énumérations

- **GenderStatus** : MALE, FEMALE, OTHER, NOT_SPECIFIED
- **MaritalStatus** : SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED
- **EmployeeStatus** : ACTIVE, LEAVE, SUSPENDED, TERMINATED, ARCHIVED
- **DocumentType** : PASSPORT, ID_CARD, RESIDENCE_PERMIT, VISA, DRIVING_LICENSE
- **RelationshipType** : SPOUSE, CHILD, PARENT, SIBLING, OTHER
- **AcademicLevel** : PRIMARY, SECONDARY, BACHELOR, MASTER, DOCTORATE, VOCATIONAL
- **CountryCode** : ISO 2-letter codes

## Endpoints API

### Employés

```
GET    /api/v1/employees                       - Lister les employés
POST   /api/v1/employees                       - Créer un employé
GET    /api/v1/employees/{id}                  - Détail d'un employé
PUT    /api/v1/employees/{id}                  - Mettre à jour
PATCH  /api/v1/employees/{id}                  - Mise à jour partielle
DELETE /api/v1/employees/{id}                  - Archiver/Supprimer
GET    /api/v1/employees/search                - Rechercher des employés
GET    /api/v1/employees/{id}/full-profile     - Profil complet
```

### Documents

```
GET    /api/v1/employees/{emp_id}/documents    - Lister les documents
POST   /api/v1/employees/{emp_id}/documents    - Ajouter un document
GET    /api/v1/employees/{emp_id}/documents/{doc_id} - Détail
PUT    /api/v1/employees/{emp_id}/documents/{doc_id} - Mettre à jour
DELETE /api/v1/employees/{emp_id}/documents/{doc_id} - Supprimer
PATCH  /api/v1/employees/{emp_id}/documents/{doc_id}/verify - Vérifier
```

### Bénéficiaires

```
GET    /api/v1/employees/{emp_id}/family       - Lister les dépendants
POST   /api/v1/employees/{emp_id}/family       - Ajouter un dépendant
GET    /api/v1/employees/{emp_id}/family/{fam_id} - Détail
PUT    /api/v1/employees/{emp_id}/family/{fam_id} - Mettre à jour
DELETE /api/v1/employees/{emp_id}/family/{fam_id} - Supprimer
GET    /api/v1/employees/{emp_id}/beneficiaries - Bénéficiaires assurance
```

### Adresses

```
GET    /api/v1/employees/{emp_id}/addresses    - Lister les adresses
POST   /api/v1/employees/{emp_id}/addresses    - Ajouter une adresse
GET    /api/v1/employees/{emp_id}/addresses/{addr_id} - Détail
PUT    /api/v1/employees/{emp_id}/addresses/{addr_id} - Mettre à jour
DELETE /api/v1/employees/{emp_id}/addresses/{addr_id} - Supprimer
```

### Formation

```
GET    /api/v1/employees/{emp_id}/education    - Historique académique
POST   /api/v1/employees/{emp_id}/education    - Ajouter une formation
GET    /api/v1/employees/{emp_id}/education/{edu_id} - Détail
PUT    /api/v1/employees/{emp_id}/education/{edu_id} - Mettre à jour
DELETE /api/v1/employees/{emp_id}/education/{edu_id} - Supprimer
```

## Cas d'usage courants

### 1. Créer un nouvel employé
```json
POST /api/v1/employees
{
  "matricule": "EMP001",
  "first_name": "Jean",
  "middle_name": "Paul",
  "last_name": "Dupont",
  "email": "jean.dupont@company.com",
  "phone": "+243812345678",
  "gender": "MALE",
  "birthdate": "1990-01-15",
  "nationality": "CD",
  "marital_status": "MARRIED",
  "hire_date": "2026-01-01",
  "status": "ACTIVE"
}
```

### 2. Ajouter un document
```json
POST /api/v1/employees/emp_123/documents
{
  "document_type": "PASSPORT",
  "reference_number": "XY123456",
  "issue_date": "2020-01-01",
  "expiry_date": "2030-01-01",
  "attachment": "passport.pdf"
}
```

### 3. Ajouter un bénéficiaire
```json
POST /api/v1/employees/emp_123/family
{
  "first_name": "Marie",
  "last_name": "Dupont",
  "relationship": "SPOUSE",
  "birthdate": "1992-05-20",
  "gender": "FEMALE",
  "is_beneficiary": true
}
```

### 4. Ajouter une adresse
```json
POST /api/v1/employees/emp_123/addresses
{
  "street": "123 Rue de la Paix",
  "city": "Kinshasa",
  "province": "Kinshasa",
  "country": "CD",
  "postal_code": "12345",
  "address_type": "RESIDENTIAL"
}
```

### 5. Ajouter une formation
```json
POST /api/v1/employees/emp_123/education
{
  "academic_level": "MASTER",
  "field": "Informatique",
  "institution": "Université de Kinshasa",
  "start_year": 2012,
  "end_year": 2014
}
```

## Cycle de vie d'un employé

### Phases
1. **Recrutement** : Création du profil (module Recruitment)
2. **Onboarding** : Ajout documents, adresses, bénéficiaires
3. **Actif** : Employé travaille (paie, congés, attendance)
4. **Congé** : Suspension temporaire
5. **Suspendu** : Sanction disciplinaire
6. **Résilié** : Fin de contrat
7. **Archivé** : Dossier fermé

### Statuts possibles
- **ACTIVE** : Employé actif
- **LEAVE** : Congé temporaire (sabbatique, maternité)
- **SUSPENDED** : Suspension disciplinaire
- **TERMINATED** : Contrat résilié
- **ARCHIVED** : Dossier archivé

## Intégrations

- **Module Payroll** : Données employé pour calcul paie
- **Module Leaves** : Gestion des congés
- **Module Attendance** : Suivi présence
- **Module Jobs** : Position et département
- **Module Banking** : Comptes bancaires
- **Système d'authentification** : Lien utilisateur

## Rapports disponibles

- **Liste des employés** : Actifs, tous, archivés
- **Organigramme** : Vue hiérarchique
- **Effectifs** : Par département, par position, par statut
- **Bénéficiaires** : Vue assurance, cas de décès
- **Documents** : Expiration, validation
- **Anniversaires** : Dates de naissance
- **Anniversaires d'embauche** : Ancienneté

## Validation et règles

1. **Matricule** : Unique, immuable
2. **Email** : Unique, formaté correctement
3. **Date de naissance** : Avant date d'aujourd'hui
4. **Dates** : Embauche ≤ Aujourd'hui, Résiliation ≥ Embauche
5. **Documents** : Au moins 1 document requis à l'embauche
6. **Bénéficiaires** : Au moins 1 pour assurance

## Conformité et sécurité

- Protection RGPD pour données personnelles
- Audit trail complet des modifications
- Contrôle d'accès par rôle
- Cryptage des données sensibles
- Archivage sécurisé
- Historique des changements d'employés

## Bonnes pratiques

1. **Données complètes** : Remplir tous les champs obligatoires
2. **Documents à jour** : Vérifier régulièrement expiration
3. **Bénéficiaires** : Maintenir liste à jour
4. **Archivage** : Ne jamais supprimer, archiver seulement
5. **Audit** : Garder historique complet
6. **Confidentialité** : Limiter l'accès aux données sensibles

## Support et dépannage

Pour toute question ou problème :
1. Vérifier que le matricule est unique
2. Valider le format de l'email
3. S'assurer que les dates sont cohérentes
4. Consulter l'historique de modifications
5. Contacter l'administrateur pour les problèmes d'accès
