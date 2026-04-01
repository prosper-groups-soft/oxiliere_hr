# Plan de Développement - Module Settings (Admin)

## Vue d'ensemble

Développement du module **Settings** complet pour l'application RH Oxilière, conforme au contexte légal de la République Démocratique du Congo (RDC).

---

## Objectifs

1. **Gestion des Utilisateurs & RBAC** : Interface de gestion des comptes avec matrice des permissions
2. **Configuration des Congés** : Paramétrage selon le Code du Travail RDC
3. **Fiscalité IPR & Social** : Configuration du barème progressif IPR et cotisations
4. **Paramètres Régionaux** : Gestion multi-devises (CDF/USD) avec taux de change

---

## Architecture du Module

### Structure des Dossiers

```
features/admin/settings/
├── types/
│   ├── user.types.ts          # User, Role, Permission
│   ├── leave.types.ts         # Config congés RDC
│   ├── tax.types.ts           # Barème IPR, CNSS
│   └── currency.types.ts      # CDF/USD, taux de change
├── stores/
│   ├── userSettingsStore.svelte.ts
│   ├── leaveSettingsStore.svelte.ts
│   ├── taxSettingsStore.svelte.ts
│   └── currencySettingsStore.svelte.ts
├── components/
│   ├── users/                 # Gestion utilisateurs & RBAC
│   │   ├── UserList.svelte
│   │   ├── UserForm.svelte
│   │   ├── RoleSelector.svelte
│   │   └── PermissionMatrix.svelte
│   ├── leaves/                # Config congés
│   │   ├── LeaveConfigForm.svelte
│   │   ├── SpecialLeaveCard.svelte
│   │   └── SeniorityBonusConfig.svelte
│   ├── tax/                   # IPR & CNSS
│   │   ├── IPRBracketEditor.svelte
│   │   ├── FamilyDeductionConfig.svelte
│   │   └── CNSSConfig.svelte
│   └── currency/              # Multi-devises
│       ├── ExchangeRateForm.svelte
│       ├── CurrencySelector.svelte
│       └── ExchangeRateHistory.svelte
└── services/
    └── settingsService.ts

routes/admin/settings/
├── +page.svelte               # Page principale avec navigation par tabs
├── +layout.svelte             # Layout avec sidebar/tabs de navigation
├── users/+page.svelte         # Gestion utilisateurs
├── leaves/+page.svelte        # Config congés
├── tax/+page.svelte           # Fiscalité IPR
└── currency/+page.svelte      # Devises et taux de change
```

---

## Livrables Détaillés

### 1. Gestion des Utilisateurs & RBAC

#### Rôles Définis
| Rôle | Description | Niveau |
|------|-------------|--------|
| `SUPER_ADMIN` | Accès total, configuration système | 1 |
| `RH_ADMIN` | Gestion RH, paie, employés | 2 |
| `MANAGER` | Validation congés équipe, vue limitée | 3 |
| `EMPLOYEE` | Espace personnel uniquement | 4 |

#### Permissions (Matrice CRUD)
- **Module Employés** : Create, Read, Update, Delete, Export
- **Module Congés** : Create Request, Approve Request, View All, Config Rules
- **Module Paie** : View Own, View All, Process Payroll, Config IPR
- **Module Settings** : View, Edit Users, Edit Config

#### Composants
- `UserList.svelte` : Table avec pagination, filtres, actions
- `UserForm.svelte` : Création/édition utilisateur
- `RoleSelector.svelte` : Sélection rôle avec description
- `PermissionMatrix.svelte` : Grille permissions par rôle

### 2. Configuration des Congés (Code du Travail RDC)

#### Forfait Annuel
- **Configuration** : Input numérique éditable
- **Valeur par défaut** : 18 jours ouvrables (congé annuel légal RDC)
- **Options** : Possibilité de passer à 24 jours selon convention collective

#### Congés de Circonstances (Éditables)
| Type | Jours par défaut | Description |
|------|-----------------|-------------|
| Mariage | 2 | Mariage de l'employé |
| Naissance | 2 | Naissance d'un enfant |
| Décès conjoint/enfant | 4 | Deuil famille proche |
| Décès ascendant | 3 | Deuil parent/grand-parent |

#### Bonus d'Ancienneté
- **Règle** : +1 jour de congé par tranche de 5 ans d'ancienneté
- **Configuration** : Activer/désactiver + modifier la tranche (années)

#### Composants
- `LeaveConfigForm.svelte` : Formulaire principal congés
- `SpecialLeaveCard.svelte` : Carte configurateur congés circonstances
- `SeniorityBonusConfig.svelte` : Configuration bonus ancienneté

### 3. Fiscalité IPR & Social

#### Barème IPR Progressif (RDC)
| Tranche | Revenu imposable (USD) | Taux |
|---------|----------------------|------|
| 1 | 0 - 300 | 3% |
| 2 | 300 - 500 | 15% |
| 3 | 500 - 1000 | 30% |
| 4 | > 1000 | 40% |

#### Contraintes Légales
- **Plafond global** : L'IPR ne peut excéder 30% du revenu net imposable
- **Déductions famille** : 2% par enfant à charge, maximum 9 enfants
- **Base de calcul** : Revenu brut - Charges sociales - Abattements professionnels

#### CNSS (Optionnel)
- **Part patronale** : Configurable (défaut: 15% selon législation RDC)
- **Part ouvrière** : Configurable (défaut: 5% selon législation RDC)
- **Plafond de salaire** : Configurable pour le calcul

#### Composants
- `IPRBracketEditor.svelte` : Éditeur visuel des tranches IPR
- `FamilyDeductionConfig.svelte` : Configuration déductions famille
- `CNSSConfig.svelte` : Paramètres cotisations sociales

### 4. Paramètres Régionaux

#### Multi-Devises
- **Devise principale** : CDF (Franc Congolais)
- **Devise secondaire** : USD (Dollar américain)
- **Affichage** : Possibilité d'afficher les deux devises côte à côte

#### Taux de Change
- **Saisie quotidienne** : Input pour taux CDF/USD du jour
- **Historique** : Conservation des taux (30 derniers jours)
- **Source** : Saisie manuelle avec option API centrale bancaire

#### Formats Régionaux
- **Format date** : JJ/MM/AAAA (format RDC)
- **Format nombre** : Séparateur décimal = virgule
- **Langue** : Français par défaut

#### Composants
- `ExchangeRateForm.svelte` : Saisie taux de change
- `CurrencySelector.svelte` : Sélection devise affichage
- `ExchangeRateHistory.svelte` : Historique des taux

---

## Interface Utilisateur

### Navigation par Onglets

La page `/admin/settings` présente une navigation par onglets verticaux :

```
┌─────────────────────────────────────────────────────────────┐
│  PARAMÈTRES                                                 │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  👤 Utilisateurs  │  [Contenu dynamique selon l'onglet]      │
│              │                                              │
│  🌴 Congés       │                                              │
│              │                                              │
│  💰 Fiscalité    │                                              │
│              │                                              │
│  💱 Devises      │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### Routes
- `/admin/settings` → Redirection vers `/admin/settings/users`
- `/admin/settings/users` → Gestion utilisateurs
- `/admin/settings/leaves` → Configuration congés
- `/admin/settings/tax` → Configuration IPR/CNSS
- `/admin/settings/currency` → Devises et taux de change

---

## Pattern des Stores

Les stores suivent le pattern **Classe** recommandé par l'architecture :

```typescript
// Example: taxSettingsStore.svelte.ts
class TaxSettingsStore {
  // State
  iprBrackets = $state<IPRBracket[]>([]);
  familyDeductionRate = $state<number>(0.02);
  maxChildrenDeduction = $state<number>(9);
  cnssRates = $state<CNSSRates>({ employer: 0.15, employee: 0.05 });
  isLoading = $state<boolean>(false);
  error = $state<string | null>(null);

  // Getters
  get maxIPRRate() { return Math.max(...this.iprBrackets.map(b => b.rate)); }
  get isValid() { return this.iprBrackets.length > 0; }

  // Actions
  async loadSettings() {
    this.isLoading = true;
    try {
      const data = await settingsService.getTaxSettings();
      this.iprBrackets = data.iprBrackets;
      this.familyDeductionRate = data.familyDeductionRate;
    } catch (err) {
      this.error = err.message;
    } finally {
      this.isLoading = false;
    }
  }

  async updateIPRBracket(index: number, bracket: IPRBracket) {
    this.iprBrackets[index] = bracket;
    await this.saveSettings();
  }

  async saveSettings() {
    await settingsService.saveTaxSettings({
      iprBrackets: this.iprBrackets,
      familyDeductionRate: this.familyDeductionRate,
      maxChildrenDeduction: this.maxChildrenDeduction,
      cnssRates: this.cnssRates
    });
  }
}

export const taxSettingsStore = new TaxSettingsStore();
```

---

## Types TypeScript

### User & RBAC
```typescript
export type UserRole = 'SUPER_ADMIN' | 'RH_ADMIN' | 'MANAGER' | 'EMPLOYEE';

export interface Permission {
  module: string;           // 'employees', 'leaves', 'payroll', 'settings'
  action: string;           // 'create', 'read', 'update', 'delete', 'approve'
  allowed: boolean;
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: Date;
  lastLogin?: Date;
}
```

### Leave Configuration
```typescript
export interface LeaveConfig {
  annualLeaveDays: number;           // 18 ou 24
  specialLeaves: SpecialLeave[];
  seniorityBonus: {
    enabled: boolean;
    yearsPerBonus: number;           // 5
    bonusDays: number;                 // 1
  };
}

export interface SpecialLeave {
  type: 'MARRIAGE' | 'BIRTH' | 'DEATH_SPOUSE_CHILD' | 'DEATH_ANCESTOR';
  label: string;
  daysAllowed: number;
  description?: string;
}
```

### Tax Configuration
```typescript
export interface IPRBracket {
  id: string;
  min: number;                      // Seuil inférieur (USD)
  max: number | null;               // Seuil supérieur (null = illimité)
  rate: number;                     // Taux (0.03, 0.15, 0.30, 0.40)
  label: string;                    // "Tranche 1", etc.
}

export interface TaxConfig {
  iprBrackets: IPRBracket[];
  familyDeductionRate: number;      // 0.02 (2%)
  maxChildrenDeduction: number;     // 9
  globalCapRate: number;            // 0.30 (30%)
  cnssEmployerRate: number;         // 0.15 (15%)
  cnssEmployeeRate: number;         // 0.05 (5%)
  cnssSalaryCap: number;            // Plafond salaire CNSS
}
```

### Currency Configuration
```typescript
export type CurrencyCode = 'CDF' | 'USD';

export interface Currency {
  code: CurrencyCode;
  name: string;                     // "Franc Congolais"
  symbol: string;                   // "FC"
  isPrimary: boolean;
  decimals: number;
}

export interface ExchangeRate {
  id: string;
  from: CurrencyCode;
  to: CurrencyCode;
  rate: number;                     // 1 USD = 2800 CDF
  date: Date;
  source: 'MANUAL' | 'API';
}

export interface CurrencyConfig {
  primaryCurrency: Currency;
  secondaryCurrency?: Currency;
  currentRate: ExchangeRate;
  rateHistory: ExchangeRate[];
}
```

---

## Service API

```typescript
// settingsService.ts
export const settingsService = {
  // Users & RBAC
  async getUsers(): Promise<User[]>;
  async createUser(data: CreateUserInput): Promise<User>;
  async updateUser(id: string, data: Partial<User>): Promise<User>;
  async deleteUser(id: string): Promise<void>;
  async getRolePermissions(role: UserRole): Promise<Permission[]>;
  async updateRolePermissions(role: UserRole, permissions: Permission[]): Promise<void>;

  // Leave Settings
  async getLeaveSettings(): Promise<LeaveConfig>;
  async saveLeaveSettings(config: LeaveConfig): Promise<void>;

  // Tax Settings
  async getTaxSettings(): Promise<TaxConfig>;
  async saveTaxSettings(config: TaxConfig): Promise<void>;

  // Currency Settings
  async getCurrencySettings(): Promise<CurrencyConfig>;
  async saveCurrencySettings(config: CurrencyConfig): Promise<void>;
  async addExchangeRate(rate: Omit<ExchangeRate, 'id'>): Promise<ExchangeRate>;
  async getExchangeRateHistory(days: number): Promise<ExchangeRate[]>;
};
```

---

## Phases de Développement

### Phase 1 : Architecture
- Créer la structure `features/admin/settings/`
- Créer les types TypeScript
- Configurer les stores de base

### Phase 2 : Gestion Utilisateurs
- Implémenter `userSettingsStore`
- Créer les composants users/
- Page `/admin/settings/users`

### Phase 3 : Configuration Congés
- Implémenter `leaveSettingsStore`
- Créer les composants leaves/
- Page `/admin/settings/leaves`

### Phase 4 : Fiscalité IPR
- Implémenter `taxSettingsStore`
- Créer les composants tax/
- Page `/admin/settings/tax`

### Phase 5 : Devises
- Implémenter `currencySettingsStore`
- Créer les composants currency/
- Page `/admin/settings/currency`

### Phase 6 : Intégration
- Layout avec navigation par onglets
- Page principale avec redirection
- Validation et tests

---

## Références Légales RDC

- **Code du Travail RDC** : Congés annuels (Art. 126-131)
- **Ordonnance IPR** : Barème progressif et déductions
- **Loi CNSS** : Taux de cotisation sociale
- **Réglementation BCC** : Gestion des devises

---

*Document créé le : Mars 2026*
*Projet : Oxilière HR - Frontend*
