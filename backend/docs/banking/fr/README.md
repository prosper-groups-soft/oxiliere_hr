# Documentation - Module Banking

## Vue d'ensemble

Le module **Banking** gère les informations bancaires des employés et les institutions financières. Il maintient les détails des comptes bancaires pour traiter les virements de paie et gérer les paiements aux fournisseurs et prestataires.

## Fonctionnalités principales

### 1. Gestion des banques
- Répertoire des banques et institutions financières
- Codes SWIFT standardisés
- Support des fournisseurs de mobile money
- Flag pour paie de masse
- Gestion des pays et devises

### 2. Comptes bancaires employés
- Multiples comptes par employé
- Support de plusieurs devises
- Compte primaire par devise
- Types de comptes (Courant, Épargne)
- IBAN optionnel
- Vérification du statut

### 3. Gestion des actions
- Activation/Désactivation de comptes
- Blocage temporaire
- Suppression logique
- Audit trail complet

### 4. Intégration paiement
- Support pour virements bancaires
- Support pour mobile money
- Formatage des coordonnées bancaires
- Validation des IBAN/SWIFT

### 5. Conformité
- Vérification des comptes
- Historique des modifications
- Audit trail complet

## Architecture

### Modèles principaux

#### Bank
Institution financière ou fournisseur de mobile money
- Nom unique
- Code bancaire
- Code SWIFT (8 ou 11 caractères pour banques standard)
- Flag mobile money
- Pays
- Statut (Actif/Inactif)

#### BankAccount
Compte bancaire d'un employé
- Employé propriétaire
- Banque
- Numéro de compte
- Nom du titulaire
- Type de compte (Courant, Épargne)
- Devise
- IBAN optionnel
- Branche code (pour transferts de masse)
- Statut (Actif, Inactif, Bloqué, Vérifié, Non vérifié)
- Compte primaire par devise
- Historique des actions

### Énumérations

- **AccountType** : CHECKING, SAVINGS, CURRENT, MONEY_MARKET
- **BankAccountAction** : ACTIVATE, DEACTIVATE, BLOCK, UNBLOCK, VERIFY, PRIMARY, SECONDARY
- **Currency** : CDF, USD, EUR, GBP, ZAR, etc.
- **CountryCode** : ISO 2-letter codes

## Endpoints API

### Banques

```
GET    /api/v1/banking/banks                   - Lister les banques
POST   /api/v1/banking/banks                   - Créer une banque
GET    /api/v1/banking/banks/{id}              - Détail d'une banque
PUT    /api/v1/banking/banks/{id}              - Mettre à jour
DELETE /api/v1/banking/banks/{id}              - Supprimer (soft delete)
GET    /api/v1/banking/banks/search?name=...   - Rechercher par nom
GET    /api/v1/banking/banks/country/{code}    - Banques par pays
```

### Comptes bancaires

```
GET    /api/v1/banking/accounts                - Lister tous les comptes
POST   /api/v1/banking/accounts                - Créer un compte
GET    /api/v1/banking/accounts/{id}           - Détail d'un compte
PUT    /api/v1/banking/accounts/{id}           - Mettre à jour
DELETE /api/v1/banking/accounts/{id}           - Supprimer
GET    /api/v1/banking/employees/{emp_id}/accounts - Comptes d'un employé
GET    /api/v1/banking/accounts/primary/{emp_id}/{currency} - Compte primaire
```

### Actions sur comptes

```
PATCH  /api/v1/banking/accounts/{id}/activate   - Activer
PATCH  /api/v1/banking/accounts/{id}/deactivate - Désactiver
PATCH  /api/v1/banking/accounts/{id}/block      - Bloquer
PATCH  /api/v1/banking/accounts/{id}/unblock    - Débloquer
PATCH  /api/v1/banking/accounts/{id}/verify     - Marquer vérifié
PATCH  /api/v1/banking/accounts/{id}/set-primary - Définir primaire
```

### Rapports

```
GET    /api/v1/banking/reports/payroll-summary - Résumé pour paie
GET    /api/v1/banking/reports/transfers       - Historique transferts
GET    /api/v1/banking/reports/unverified      - Comptes non vérifiés
GET    /api/v1/banking/reports/multi-currency  - Employés multi-devises
```

## Cas d'usage courants

### 1. Créer une banque
```json
POST /api/v1/banking/banks
{
  "name": "Rawbank",
  "code": "RBCD",
  "swift_code": "RBCDCDKI",
  "is_mobile_money": false,
  "country_code": "CD",
  "is_active": true
}
```

### 2. Créer un fournisseur de mobile money
```json
POST /api/v1/banking/banks
{
  "name": "M-Pesa",
  "code": "MPESA",
  "is_mobile_money": true,
  "country_code": "KE",
  "is_active": true
}
```

### 3. Ajouter un compte bancaire employé
```json
POST /api/v1/banking/accounts
{
  "employee_id": "emp_123",
  "bank_id": "bank_456",
  "account_number": "0123456789",
  "account_name": "Jean Dupont",
  "account_type": "CHECKING",
  "currency": "CDF",
  "iban": "CD94CBCD0000123456789012",
  "branch_code": "001",
  "is_active": true
}
```

### 4. Définir un compte comme primaire
```json
PATCH /api/v1/banking/accounts/acc_789/set-primary
{
  "is_primary": true
}
```

### 5. Vérifier un compte bancaire
```json
PATCH /api/v1/banking/accounts/acc_789/verify
{
  "verified": true,
  "verification_method": "BANK_STATEMENT",
  "verification_date": "2026-01-20"
}
```

### 6. Récupérer tous les comptes d'un employé
```json
GET /api/v1/banking/employees/emp_123/accounts
Response:
{
  "employee_id": "emp_123",
  "accounts": [
    {
      "id": "acc_001",
      "bank": "Rawbank",
      "account_number": "0123456789",
      "currency": "CDF",
      "is_primary": true,
      "is_active": true,
      "is_verified": true
    },
    {
      "id": "acc_002",
      "bank": "BCDC",
      "account_number": "9876543210",
      "currency": "USD",
      "is_primary": true,
      "is_active": true,
      "is_verified": false
    }
  ]
}
```

## Règles de validation

### Pour les banques
- Nom unique
- Code unique
- Code SWIFT : 8 ou 11 caractères pour banques standard
- Pays valide ou NULL (global)

### Pour les comptes
- Un seul compte primaire par devise par employé
- Numéro de compte unique par banque
- Nom du titulaire non vide
- Devise valide
- IBAN valide (si fourni) : format ISO 13616
- Statut valide

## Intégrations

- **Module Payroll** : Utilise comptes primaires pour virements
- **Module Employees** : Lien avec employés
- **Système d'export** : Bordereau de virement
- **Système de réconciliation** : Rapprochement bancaire

## Statuts de compte

- **ACTIVE** : Compte actif pour paie
- **INACTIVE** : Compte désactivé, non utilisable
- **BLOCKED** : Compte bloqué temporairement
- **VERIFIED** : Compte vérifié
- **UNVERIFIED** : En attente de vérification
- **ARCHIVED** : Compte archivé

## Processus typique

1. **Création** : Ajouter compte bancaire pour employé
2. **Vérification** : Vérifier les coordonnées (appel, relevé)
3. **Activation** : Marquer comme prêt pour paiement
4. **Utilisation** : Utilisé pour virements de paie
5. **Maintenance** : Mettre à jour si changement de compte
6. **Archivage** : Conserver après départ de l'employé

## Rapports disponibles

- **Employés par banque** : Distribution par institution
- **Multi-devises** : Employés avec comptes dans plusieurs devises
- **Comptes non vérifiés** : À valider
- **Comptes inactifs** : À réactiver
- **Historique des modifications** : Audit trail

## Bonnes pratiques

1. **Vérification** : Toujours vérifier avant premier paiement
2. **Primaire** : Définir un compte primaire par devise
3. **Documentation** : Conserver preuves de vérification
4. **Sécurité** : Ne pas partager coordonnées bancaires
5. **Mise à jour** : Demander confirmation annuelle
6. **Archivage** : Ne jamais supprimer, archiver seulement

## Conformité et sécurité

- Conformité RGPD pour données bancaires
- Cryptage des numéros de compte
- Audit trail complet des modifications
- Contrôle d'accès par rôle
- Logs des actions sensibles
- Historique des changements

## Support et dépannage

Pour toute question ou problème :
1. Vérifier que le compte est actif
2. Valider le format du numéro de compte
3. S'assurer qu'un compte primaire existe par devise
4. Consulter l'historique de modifications
5. Vérifier que la banque est configurée
6. Contacter Trésorier/Paie pour problèmes de transfert
