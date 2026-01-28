# Documentation - Module Leaves

## Vue d'ensemble

Le module **Leaves** gère l'ensemble du processus de congés, incluant les demandes, approbations, allocations légales et suivis des congés des employés. Il supporte les congés annuels, congés circonstanciels, et les règles spécifiques de chaque juridiction.

## Fonctionnalités principales

### 1. Politique de congés
- Définition des congés standard par pays/juridiction
- Nombre de jours annuels (ex: 18, 21, 30 jours)
- Configuration du report des congés non utilisés
- Expiration des reports (généralement avant fin mars)
- Règles d'ancienneté (bonus jours selon années de service)

### 2. Allocations de congés
- Calcul automatique par employé
- Base = jours annuels + bonus ancienneté
- Ajustements par circonstance (naissance, décès, mariage)
- Déduction des congés utilisés
- Solde disponible actualisé

### 3. Demandes de congés
- Soumission par employé ou administrateur
- Types de congés (Annuel, Maladie, Maternité, Circonstanciel)
- Dates de début et fin
- Raison et documents justificatifs optionnels
- Workflow d'approbation hiérarchique

### 4. Approbations
- Validation par manager direct ou RH
- Statuts multiples (En attente, Approuvé, Rejeté, Annulé)
- Commentaires et feedback
- Historique des modifications
- Permissions et rôles configurables

### 5. Gestion du solde
- Suivi du solde actuel par employé
- Historique des transactions de congés
- Détail des utilisations
- Prévisions et planifications
- Alertes pour surutilisation

### 6. Intégration avec la paie
- Déduction automatique des congés approuvés
- Calcul du salaire pendant congé
- Paiement du solde non utilisé (le cas échéant)
- Rapport au module Payroll

## Architecture

### Modèles principaux

#### LeavePolicy
Politique de congés par pays/juridiction
- Nom et code pays
- Nombre de jours annuels standard
- Configuration du report (permet/interdit, max jours, expiration)
- Règles d'ancienneté associées

#### SeniorityRule
Bonus de congés basés sur l'ancienneté
- Lien avec la politique
- Années de service requises
- Nombre de jours bonus
- Ex: +1 jour après 3 ans, +2 jours après 5 ans

#### CircumstanceLeaveRule
Congés spéciaux selon circonstances
- Type (Naissance, Décès, Mariage, Maladie, Maternité)
- Nombre de jours accordés
- Justification requise
- Fréquence (une fois par an, par événement)

#### EmployeeLeaveAllocation
Allocation annuelle de congés par employé
- Lien avec employé et politique
- Année civile
- Jours alloués (calculé = base + ancienneté)
- Jours utilisés
- Solde disponible
- Jours reportés de l'année précédente

#### LeaveRequest
Demande de congé soumise par employé
- Employé demandeur
- Type de congé
- Dates (début, fin)
- Nombre de jours demandés
- Raison / Description
- Statut (Brouillon, Soumis, Approuvé, Rejeté, Annulé)
- Documents justificatifs

#### LeaveApproval
Approbation hiérarchique d'une demande
- Lien avec la demande
- Approbateur (manager, RH)
- Statut de décision
- Commentaires
- Date d'approbation
- Signature/Validation

#### LeaveTransaction
Enregistrement de chaque utilisation de congé
- Type (Allocation, Utilisation, Retour, Ajustement)
- Nombre de jours
- Référence (LeaveRequest, PayrollRun)
- Date de transaction
- Notes

### Énumérations

- **LeaveCategory** : ANNUAL, SICK, MATERNITY, PATERNITY, BEREAVEMENT, MARRIAGE, CIRCUMSTANCE, UNPAID
- **LeaveStatus** : DRAFT, SUBMITTED, APPROVED, REJECTED, CANCELLED, EXPIRED
- **CircumstanceType** : BIRTH, DEATH, MARRIAGE, SERIOUS_ILLNESS, ACCIDENT
- **LeaveTransactionTypes** : ALLOCATION, USAGE, RETURN, ADJUSTMENT, CARRYOVER

## Endpoints API

### Politiques de congés

```
GET    /api/v1/leaves/policies                  - Lister les politiques
POST   /api/v1/leaves/policies                  - Créer une politique
GET    /api/v1/leaves/policies/{id}             - Détail d'une politique
PUT    /api/v1/leaves/policies/{id}             - Mettre à jour
DELETE /api/v1/leaves/policies/{id}             - Supprimer
```

### Règles d'ancienneté

```
GET    /api/v1/leaves/policies/{policy_id}/seniority - Lister les règles
POST   /api/v1/leaves/policies/{policy_id}/seniority - Créer une règle
PUT    /api/v1/leaves/policies/{policy_id}/seniority/{rule_id} - Mettre à jour
```

### Allocations de congés

```
GET    /api/v1/leaves/allocations              - Lister les allocations
POST   /api/v1/leaves/allocations              - Créer une allocation
GET    /api/v1/leaves/allocations/{id}         - Détail d'une allocation
GET    /api/v1/leaves/allocations/employee/{emp_id} - Allocation d'un employé
GET    /api/v1/leaves/allocations/employee/{emp_id}/year/{year} - Par année
```

### Demandes de congé

```
GET    /api/v1/leaves/requests                 - Lister les demandes
POST   /api/v1/leaves/requests                 - Soumettre une demande
GET    /api/v1/leaves/requests/{id}            - Détail d'une demande
PUT    /api/v1/leaves/requests/{id}            - Mettre à jour
DELETE /api/v1/leaves/requests/{id}            - Annuler
GET    /api/v1/leaves/requests/employee/{emp_id} - Demandes d'un employé
```

### Approbations

```
GET    /api/v1/leaves/approvals                - Lister les approbations
PATCH  /api/v1/leaves/approvals/{request_id}/approve - Approuver
PATCH  /api/v1/leaves/approvals/{request_id}/reject  - Rejeter
GET    /api/v1/leaves/approvals/pending        - Approbations en attente
```

### Transactions et soldes

```
GET    /api/v1/leaves/transactions             - Historique des transactions
GET    /api/v1/leaves/transactions/employee/{emp_id} - Par employé
GET    /api/v1/leaves/balances/employee/{emp_id} - Solde actuel
```

## Cas d'usage courants

### 1. Créer une politique de congés
```json
POST /api/v1/leaves/policies
{
  "name": "Politique RDC Standard",
  "country_code": "CD",
  "standard_annual_days": 18,
  "allows_carry_over": true,
  "max_carry_over_days": 5,
  "carry_over_expiration_month": 3
}
```

### 2. Ajouter une règle d'ancienneté
```json
POST /api/v1/leaves/policies/{policy_id}/seniority
{
  "years_of_service": 5,
  "bonus_days": 2
}
```

### 3. Soumettre une demande de congé annuel
```json
POST /api/v1/leaves/requests
{
  "employee_id": "emp_123",
  "leave_type": "ANNUAL",
  "start_date": "2026-02-01",
  "end_date": "2026-02-15",
  "reason": "Vacances familiales",
  "documents": []
}
```

### 4. Soumettre une demande de congé circonstanciel
```json
POST /api/v1/leaves/requests
{
  "employee_id": "emp_123",
  "leave_type": "CIRCUMSTANCE",
  "circumstance_type": "BIRTH",
  "start_date": "2026-02-10",
  "end_date": "2026-02-12",
  "reason": "Naissance d'un enfant",
  "documents": ["birth_certificate.pdf"]
}
```

### 5. Approuver une demande
```json
PATCH /api/v1/leaves/requests/{request_id}/approve
{
  "approver_id": "emp_456",
  "status": "APPROVED",
  "comments": "Approuvé - pas de conflit calendaire"
}
```

### 6. Vérifier le solde de congés
```json
GET /api/v1/leaves/balances/employee/emp_123
{
  "employee_id": "emp_123",
  "year": 2026,
  "days_allocated": 20,
  "days_used": 5,
  "days_available": 15,
  "days_carried_over": 2,
  "total_balance": 17
}
```

## Processus de congé

### Flux standard
1. **Demande** : Employé ou RH crée une demande avec dates et type
2. **Validation** : Système vérifie la disponibilité de jours
3. **Soumission** : Demande envoyée à l'approbateur
4. **Approbation** : Manager/RH approuve ou rejette
5. **Publication** : Demande approuvée devient effective
6. **Déduction** : Lors du calcul de paie, jours sont déduits
7. **Clôture** : Marquée comme utilisée après les dates

### Statuts de demande
- **DRAFT** : Non soumise, peut être modifiée
- **SUBMITTED** : En attente d'approbation
- **APPROVED** : Approuvée, congé confirmé
- **REJECTED** : Refusée par approbateur
- **CANCELLED** : Annulée par demandeur
- **EXPIRED** : Dépassée (dates révues)

## Calcul des allocations

### Formule
```
Jours alloués = Jours de base + Bonus ancienneté + Ajustements circonstanciels
```

### Exemple pour RDC
```
Employé embauché depuis 2021 (5 ans d'ancienneté):
- Base: 18 jours
- Bonus 5 ans: +2 jours
- Naissance en cours d'année: +3 jours
- Total allocation: 23 jours
```

### Solde à date
```
Solde = Allocation totale - Jours utilisés - Jours en attente approbation
```

## Intégrations

- **Module Employees** : Données employé, politique par employé
- **Module Payroll** : Déduction des congés approuvés
- **Module Attendance** : Absence pendant les congés
- **Module Calendar** : Jours fériés affectant le calcul

## Rapports disponibles

- **Résumé des allocations** : Par employé et année
- **Demandes en attente** : À approuver
- **Utilisation par type** : Annuel, maladie, circonstanciel
- **Prévisions** : Congés planifiés futurs
- **Solde par département** : Vue managériale
- **Audit trail** : Historique complet des modifications

## Bonnes pratiques

1. **Planification** : Encourager la planification anticipée
2. **Communication** : Notifier manager et équipe des absences
3. **Conformité** : Respecter les minimums légaux par pays
4. **Documentation** : Exiger les justificatifs pour circonstanciels
5. **Transparence** : Afficher les soldes aux employés
6. **Audit** : Conserver l'historique complet

## Considérations légales

- Respect du code du travail RDC
- Minimum 18 jours par an (RDC)
- Interdiction du paiement en remplacement en cas de non-usage
- Conservation du droit aux congés pendant suspension contrat
- Calcul correct de l'indemnité en cas de résiliation

## Support et dépannage

Pour toute question ou problème :
1. Vérifier la politique applicable à l'employé
2. Vérifier le solde actuel
3. Consulter l'historique des transactions
4. Valider les dates et période
5. Contacter le responsable RH pour les décisions
