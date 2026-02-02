# Documentation - Module Payroll

## Vue d'ensemble

Le module **Payroll** gère l'ensemble du processus de calcul et de distribution des salaires. Il automatise les calculs complexes de rémunération, les déductions, les allocations légales et les cotisations sociales selon les normes de la RDC et autres juridictions.

## Fonctionnalités principales

### 1. Configuration de la paie
- **Paramètres globaux** : Devise, méthode de paiement par défaut, heures de travail mensuelles
- **Allocations** : Allocations familiales, allocations logement avec pourcentages minimums
- **Heures supplémentaires** : Configuration du multiplicateur (défaut 1.5x)
- **Déductions** : Intégration des congés, jours théoriques d'absence
- **Conversion de devises** : Taux USD/CDF pour les paiements en devises étrangères

### 2. Contrats d'employé
- Création et gestion des contrats par employé
- Types de contrats (CDI, CDD, Contrat à l'essai)
- Périodes de paiement (Hebdomadaire, Bi-hebdomadaire, Mensuel)
- Salaire de base et modes de calcul (Salaire fixe, Salaire brut)
- Historique des modifications avec audit trail

### 3. Calcul de la paie
- **Heures travaillées** : Enregistrement des jours travaillés et absence
- **Allocations légales** : Allocations logement, familiales, SMIG
- **Heures supplémentaires** : Calcul automatique avec coefficient configurable
- **Cotisations sociales** : INSS, CNSS, taxes selon règles de la RDC
- **Avances de salaire** : Demandes, approbations et déductions

### 4. Ajustements et corrections
- Ajustements manuels (bonus, retenues spéciales)
- Corrections de paie précédente
- Traçabilité complète des modifications

### 5. Bulletins de paie (Payslips)
- Génération automatique des bulletins
- Détail ligne par ligne (base, allocations, déductions)
- Exports en PDF et formats multiples
- Consultation par employé via portail

### 6. Gestion des avances de salaire
- Demande et approbation d'avances
- Configuration du taux de remboursement
- Déduction automatique du prochain salaire
- Suivi du solde des avances

## Architecture

### Modèles principaux

#### PayrollConfiguration
Configuration globale du système de paie
- Devise par défaut
- Méthode de paiement standard
- Paramètres de calcul (heures, allocations, cotisations)
- Taux de change

#### EmployeeContract
Contrat d'emploi d'un employé
- Lien avec l'employé
- Type et période de contrat
- Salaire de base
- Mode de calcul
- Statut (Actif, Suspendu, Terminé)

#### PayrollRun
Exécution globale de paie pour une période
- Code unique généré automatiquement
- Période couverte
- Statut (Brouillon, Approuvée, Publiée, Payée)
- Total des salaires, cotisations, déductions

#### EmployeePayslip
Bulletin individuel pour chaque employé
- Lien avec PayrollRun
- Salaire brut, net
- Détail de toutes les lignes
- Statut de paiement

#### PayslipLine
Détail ligne par ligne du bulletin
- Type de ligne (Salaire, Allocation, Déduction)
- Montant
- Référence (contrat, règle appliquée)

#### SalaryAdvance
Gestion des avances de salaire
- Montant demandé et approuvé
- Taux de remboursement
- Statut (Approuvée, Remboursée, Annulée)

### Énumérations

- **PaymentMethod** : CASH, BANK_TRANSFER, MOBILE_MONEY, CHECK, PAYPAL, CRYPTOCURRENCY
- **ContractType** : CDI, CDD, INTERNSHIP, APPRENTICESHIP, SERVICE_PROVIDER
- **PaymentPeriod** : WEEKLY, BIWEEKLY, MONTHLY, QUARTERLY, SEMI_ANNUAL, ANNUAL
- **RemunerationType** : FIXED_SALARY, GROSS_SALARY, HOURLY_RATE, DAILY_RATE
- **PayrollStatus** : DRAFT, APPROVED, PUBLISHED, PAID, CANCELLED, REVERSED
- **AdjustmentType** : BONUS, PENALTY, ADVANCE_DEDUCTION, CORRECTION

## Endpoints API

### Configuration de paie

```
GET    /api/payroll/config              - Récupérer la configuration
POST   /api/payroll/config              - Créer la configuration
PUT    /api/payroll/config/{id}         - Mettre à jour la configuration
DELETE /api/payroll/config/{id}         - Supprimer la configuration
```

### Contrats

```
GET    /api/payroll/contracts           - Lister les contrats
POST   /api/payroll/contracts           - Créer un contrat
GET    /api/payroll/contracts/{id}      - Détail d'un contrat
PUT    /api/payroll/contracts/{id}      - Mettre à jour un contrat
DELETE /api/payroll/contracts/{id}      - Supprimer un contrat
```

### Exécution de paie

```
GET    /api/payroll/runs                - Lister les exécutions
POST   /api/payroll/runs                - Créer une exécution
GET    /api/payroll/runs/{id}           - Détail d'une exécution
PATCH  /api/payroll/runs/{id}/approve   - Approuver l'exécution
PATCH  /api/payroll/runs/{id}/publish   - Publier l'exécution
```

### Bulletins de paie

```
GET    /api/payroll/payslips            - Lister les bulletins
GET    /api/payroll/payslips/{id}       - Détail d'un bulletin
GET    /api/payroll/payslips/{id}/pdf   - Exporter en PDF
GET    /api/payroll/payslips/employee/{emp_id} - Bulletins d'un employé
```

### Avances de salaire

```
GET    /api/payroll/advances            - Lister les avances
POST   /api/payroll/advances            - Demander une avance
GET    /api/payroll/advances/{id}       - Détail d'une avance
PATCH  /api/payroll/advances/{id}/approve - Approuver une avance
PATCH  /api/payroll/advances/{id}/reject - Rejeter une avance
```

### Ajustements

```
GET    /api/payroll/adjustments         - Lister les ajustements
POST   /api/payroll/adjustments         - Créer un ajustement
GET    /api/payroll/adjustments/{id}    - Détail d'un ajustement
PUT    /api/payroll/adjustments/{id}    - Mettre à jour
DELETE /api/payroll/adjustments/{id}    - Supprimer
```

## Cas d'usage courants

### 1. Créer une configuration de paie
```json
POST /api/payroll/config
{
  "currency": "CDF",
  "default_payment_method": "BANK_TRANSFER",
  "work_hours_per_month": 195,
  "housing_allowance_min_percentage": 30.0,
  "family_allowance_min_amount": 262.0,
  "overtime_multiplier": 1.5,
  "include_leaves_in_payroll": true,
  "exchange_rate_usd_cdf": 2850.0
}
```

### 2. Créer un contrat d'employé
```json
POST /api/payroll/contracts
{
  "employee_id": "emp_123",
  "contract_type": "CDI",
  "payment_period": "MONTHLY",
  "base_salary": 50000.00,
  "remuneration_type": "GROSS_SALARY",
  "status": "ACTIVE",
  "start_date": "2026-01-01"
}
```

### 3. Exécuter une paie
```json
POST /api/payroll/runs
{
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "payment_method": "BANK_TRANSFER"
}
```

### 4. Demander une avance de salaire
```json
POST /api/payroll/advances
{
  "employee_id": "emp_123",
  "amount": 10000.00,
  "repayment_rate": 0.25,
  "requested_date": "2026-01-15"
}
```

## Processus de paie

1. **Préparation** : Créer une exécution de paie pour la période
2. **Calcul** : Le système calcule automatiquement :
   - Salaire brut = salaire de base + allocations
   - Cotisations sociales
   - Déductions (absences, avances, etc.)
   - Salaire net = brut - cotisations - déductions
3. **Révision** : Vérifier et approuver les calculs
4. **Publication** : Approuver les bulletins pour paiement
5. **Exécution** : Traiter les paiements selon la méthode configurée

## Intégrations

- **Module Employees** : Données personnelles et contrats
- **Module Attendance** : Jours travaillés, heures supplémentaires
- **Module Leaves** : Déduction des congés approuvés
- **Module Banking** : Comptes bancaires pour virements
- **Module Calendar** : Jours fériés affectant le calcul

## Configuration avancée

### Allocations familiales
- Basées sur le SMIG (Salaire Minimum Interprofessionnel Garanti)
- Montant minimum par enfant (ex: 262 FC)
- Diviseur SMIG configurable (défaut 27)

### Allocations logement
- Pourcentage minimum du salaire (défaut 30%)
- Peut être personnalisée par contrat
- Validation des minimums

### Cotisations sociales
- INSS (Institut National de Sécurité Sociale)
- CNSS (Caisse Nationale de Sécurité Sociale)
- Taux configurables
- Plafonds applicables

### Heures supplémentaires
- Détection automatique des heures au-delà du seuil
- Multiplicateur configurable (défaut 1.5x)
- Intégration avec le module Attendance

## Rapports disponibles

- **Registre de paie** : Résumé par employé
- **Bordereau de virement** : Pour traitement bancaire
- **Feuille de cotisations sociales** : Récapitulatif des cotisations
- **Registre des avances** : Suivi des avances accordées
- **Rapport fiscal** : Déductions à déclarer

## Considérations légales

- Respect des normes de la RDC
- Audit trail complet des modifications
- Historique des paies
- Versionning des configurations
- Conformité RGPD sur les données sensibles

## Support et dépannage

Pour toute question ou problème :
1. Vérifier les logs dans `/logs/payroll/`
2. Consulter la configuration active
3. Valider les données d'entrée
4. Contacter l'équipe d'administration RH

