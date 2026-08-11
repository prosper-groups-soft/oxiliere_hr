# API Reference: DRC Payroll Engine

> **REST API endpoints, request/response schemas, and integration patterns for the Oxiliere HR Payroll Engine**

---

## Overview

The Oxiliere Payroll API follows a **RESTful design** using [Django Ninja Extra](https://github.com/eadwinCode/django-ninja-extra) with `@api_controller` decorators and `http_get`/`http_post`/`http_patch`/`http_delete` route decorators. All endpoints are prefixed with `/payroll/`.

### Authentication & Authorization

All payroll endpoints require **bearer token authentication** (JWT) with **scope-based permissions**:

| Scope | Description |
|-------|-------------|
| `payroll:r` | Read access to all payroll resources |
| `payroll:w` | Create/update payroll runs and payslips |
| `payroll:a` | Approve payroll runs |
| `payroll:admin` | Configure payroll rules and parameters |

### Common Patterns

- **Pagination**: List endpoints use `CursorPagination` via `@paginate`.
- **Caching**: Read endpoints use `@cache_api_response(timeout=..., key_prefix=..., user_specific=...)`.
- **Filtering**: List endpoints accept a `FilterSchema` via `Query(...)`.
- **Error handling**: All endpoints return standard HTTP codes (200, 201, 204, 400, 404, 422).

---

## 1. Payroll Configuration (`/payroll/configuration`)

Manages global payroll settings, legal parameters, tax brackets, and contribution rates.

### Endpoints

#### GET `/payroll/configuration`
Return the active payroll configuration for the organization.

**Response** `200` — `PayrollConfigurationOut`

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Configuration identifier |
| `currency` | `CDF` / `USD` | Default payroll currency |
| `default_payment_method` | `BANK_TRANSFER` / `CASH` / `MOBILE_MONEY` / `CHECK` | Default payment method |
| `work_hours_per_week` | int | Standard weekly hours (45h for DRC) |
| `work_hours_per_month` | int | Calculated monthly hours (195h) |
| `housing_allowance_min_percentage` | Decimal | Minimum housing allowance as % of base salary |
| `family_allowance_min_amount` | Decimal | Minimum daily allowance per child |
| `family_allowance_smig_divider` | Decimal | Divider for family allowance from SMIG |
| `overtime_multiplier` | Decimal | Overtime rate multiplier |
| `include_leaves_in_payroll` | bool | Whether to include leave days in payroll |
| `leave_deduction_divisor` | Decimal | Divisor for leave day deduction |
| `leave_deduction_mode` | `DISABLED` / `DAILY_RATE` / `CALENDAR_DAYS` / `ATTENDANCE_DAYS` / `FIXED_AMOUNT` | Exclusive absence deduction mode (ATTENDANCE_DAYS uses the employee's scheduled working days) |
| `fixed_deduction_per_absent_day` | Decimal \| None | Fixed amount deducted per absent day |
| `created_at` | datetime | Timestamp of creation |
| `updated_at` | datetime | Timestamp of last update |

#### PATCH `/payroll/configuration`
Partially update the payroll configuration.

**Request** — `PayrollConfigurationUpdateIn` (partial, any subset of fields above)

**Response** `200` — Updated `PayrollConfigurationOut`

#### GET `/payroll/configuration/smig`
List SMIG (Salaire Minimum Interprofessionnel Garanti) configurations.

**Query params**: `SMIGConfigurationListFilterIn`

**Response** `200` — Paginated list of `SMIGConfigurationOut`

#### POST `/payroll/configuration/smig`
Create a new SMIG configuration.

#### PATCH `/payroll/configuration/smig/{id}`
Update a SMIG configuration.

#### GET `/payroll/configuration/contributions`
List social contribution rates (CNSS, INPP, ONEM).

**Query params**: `SocialContributionRateListFilterIn`

**Response** `200` — Paginated list of `SocialContributionRateOut`

#### POST `/payroll/configuration/contributions`
Create a social contribution rate.

#### PATCH `/payroll/configuration/contributions/{id}`
Update a social contribution rate.

#### GET `/payroll/configuration/overtime`
List overtime rules.

#### POST `/payroll/configuration/overtime`
Create an overtime rule.

#### PATCH `/payroll/configuration/overtime/{id}`
Update an overtime rule.

#### GET `/payroll/configuration/tax-brackets`
List tax brackets (used for IPR / IRPP calculation with progressive scale).

**Query params**: `TaxBracketListFilterIn`

**Response** `200` — Paginated list of `TaxBracketOut`

#### POST `/payroll/configuration/tax-brackets`
Create a tax bracket.

#### PATCH `/payroll/configuration/tax-brackets/{id}`
Update a tax bracket.

#### GET `/payroll/configuration/allowances`
List legal allowances (housing, transport, family etc.).

**Query params**: `LegalAllowanceListFilterIn`

**Response** `200` — Paginated list of `LegalAllowanceOut`

#### POST `/payroll/configuration/allowances`
Create a legal allowance.

#### PATCH `/payroll/configuration/allowances/{id}`
Update a legal allowance.

---

## 2. Employee Contracts (`/payroll/contracts`)

Manages employment contracts with salary terms, contract types, and payment periods.

### Endpoints

#### GET `/payroll/contracts`
List employee contracts with filtering.

**Query params**: `EmployeeContractListFilterIn`
- `employee` — Filter by employee UUID
- `is_active` — Active/inactive status
- `remuneration_type` — `FIXED`, `HOURLY`, `GROSS_UP`
- `contract_type` — `CDI`, `CDD`, `FREELANCE`, `INTERN`, `PROBATION`, `TEMPORARY`
- `date_from` / `date_to` — Contract date range

**Response** `200` — Paginated list of `EmployeeContractOut`

#### GET `/payroll/contracts/{contract_id}`
Retrieve full details of a specific contract.

**Response** `200` — `EmployeeContractOut` with nested employer/employee details

#### POST `/payroll/contracts`
Create a new employee contract.

**Request** — `EmployeeContractCreateIn`
```json
{
  "employee": "uuid",
  "contract_type": "CDI",
  "remuneration_type": "FIXED",
  "salary_base_type": "GROSS",
  "base_salary": 900000.00,
  "currency": "CDF",
  "payment_period": "MONTHLY",
  "start_date": "2026-01-01",
  "end_date": null,
  "work_hours_per_week": 45,
  "payment_method": "BANK_TRANSFER"
}
```

**Response** `201` — Created `EmployeeContractOut`

#### PATCH `/payroll/contracts/{contract_id}`
Update an existing contract.

**Response** `200` — Updated `EmployeeContractOut`

#### DELETE `/payroll/contracts/{contract_id}`
Terminate a contract (soft delete).

**Response** `204` — No content

---

## 3. Payroll Runs (`/payroll/runs`)

Orchestrates the monthly payroll process: generates payslips, applies calculations, manages approvals.

### Endpoints

#### GET `/payroll/runs`
List payroll runs with filtering.

**Query params**: `PayrollRunListFilterIn`
- `status` — `DRAFT`, `PROCESSING`, `COMPLETED`, `CANCELED`
- `period_start` / `period_end` — Date range
- `payment_method` — Filter by method

**Response** `200` — Paginated list of `PayrollRunOut`

#### GET `/payroll/runs/{run_id}`
Retrieve a specific payroll run.

**Response** `200` — `PayrollRunOut`

#### POST `/payroll/runs`
Create a new payroll run (opens a new period).

**Request** — `PayrollRunCreateIn`
```json
{
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "payment_method": "BANK_TRANSFER",
  "exchange_rate": 2850.00,
  "label": "Paie Janvier 2026"
}
```

**Response** `201` — Created `PayrollRunOut`

#### PATCH `/payroll/runs/{run_id}`
Update payroll run metadata or status.

#### POST `/payroll/runs/{run_id}/generate`
Generate all payslips for the run (triggers the pipeline).

**Response** `200` — `PayslipGenerationStatusOut`
```json
{
  "run_id": "uuid",
  "status": "PROCESSING",
  "total_employees": 50,
  "generated": 0,
  "errors": []
}
```

#### GET `/payroll/runs/{run_id}/summary`
Get aggregated summary for the payroll run.

**Response** `200` — `PayrollRunSummaryOut`
```json
{
  "run_id": "uuid",
  "period": "2026-01",
  "total_gross": 45000000.00,
  "total_net": 35750000.00,
  "total_employer_contributions": 11250000.00,
  "total_employee_deductions": 9250000.00,
  "employee_count": 50,
  "status": "COMPLETED"
}
```

#### POST `/payroll/runs/{run_id}/approve`
Approve all payslips in the run (advances status to APPROVED).

#### POST `/payroll/runs/{run_id}/pay`
Mark the run as paid.

#### GET `/payroll/runs/{run_id}/payslips`
List all payslips for a specific run.

**Query params**:
- `employee_id` — Filter by employee
- `status` — `DRAFT`, `CALCULATED`, `PAID`

**Response** `200` — Paginated list of `EmployeePayslipOut`

#### GET `/payroll/runs/{run_id}/payslips/{payslip_id}`
Get detailed payslip with all lines, deductions, and contributions.

**Response** `200` — `EmployeePayslipDetailOut`

---

## 4. Salary Advances (`/payroll/advances`)

Manages employee salary advances: requests, approvals, repayment tracking.

### Endpoints

#### GET `/payroll/advances`
List salary advances with filtering.

**Query params**: `AdvanceListFilterIn`
- `employee_id` — Filter by employee
- `status` — `PENDING`, `APPROVED`, `REJECTED`, `COMPLETED`
- `date_from` / `date_to` — Request date range

**Response** `200` — Paginated list of `SalaryAdvanceOut`

#### GET `/payroll/advances/{advance_id}`
Retrieve advance details including repayment schedule.

**Response** `200` — `SalaryAdvanceDetailOut`

#### POST `/payroll/advances`
Create a new salary advance request.

**Request** — `SalaryAdvanceCreateIn`
```json
{
  "employee": "uuid",
  "amount": 500000.00,
  "currency": "CDF",
  "reason": "Urgence familiale",
  "repayment_periods": 5
}
```

**Response** `201` — Created `SalaryAdvanceOut`

#### PATCH `/payroll/advances/{advance_id}`
Update an advance (e.g., approve/reject).

**Response** `200` — Updated `SalaryAdvanceOut`

#### GET `/payroll/advances/{employee_id}/balance`
Get advance balance for a specific employee.

**Response** `200` — `AdvanceBalanceOut`
```json
{
  "employee_id": "uuid",
  "total_advanced": 1500000.00,
  "total_repaid": 900000.00,
  "remaining": 600000.00,
  "active_advances": 2
}
```

#### GET `/payroll/advances/config`
List advance deduction configurations.

#### POST `/payroll/advances/config`
Create advance deduction configuration.

#### PATCH `/payroll/advances/config/{id}`
Update advance deduction configuration.

---

## 5. Payroll Adjustments (`/payroll/adjustments`)

Manages one-time or recurring adjustments (bonuses, deductions) applied to employee pay.

### Endpoints

#### GET `/payroll/adjustments/types`
List all adjustment type templates.

**Query params**: `AdjustmentListFilterIn`

**Response** `200` — Paginated list of `PayrollAdjustmentOut`

#### POST `/payroll/adjustments/types`
Create a new adjustment type template.

**Request** — `PayrollAdjustmentCreateIn`
```json
{
  "code": "PRIME_PERF",
  "label": "Prime de Performance",
  "type": "BONUS",
  "calculation_mode": "FIXED",
  "default_amount": 50000.00,
  "is_taxable": true,
  "is_mandatory": false
}
```

**Response** `201` — Created `PayrollAdjustmentOut`

#### PATCH `/payroll/adjustments/types/{id}`
Update an adjustment type.

#### DELETE `/payroll/adjustments/types/{id}`
Soft-delete an adjustment type.

#### GET `/payroll/adjustments/employee`
List employee-level adjustments for a specific run.

**Query params**: `EmployeeAdjustmentListFilterIn`
- `payroll_run` — Filter by payroll run
- `employee` — Filter by employee
- `adjustment_type` — Filter by adjustment type

**Response** `200` — Paginated list of `EmployeeAdjustmentOut`

#### POST `/payroll/adjustments/employee`
Apply an adjustment to an employee for a payroll run.

**Request** — `EmployeeAdjustmentCreateIn`
```json
{
  "employee": "uuid",
  "payroll_run": "uuid",
  "adjustment_type": "uuid",
  "amount": 75000.00,
  "label": "Prime exceptionnelle"
}
```

**Response** `201` — Created `EmployeeAdjustmentOut`

#### PATCH `/payroll/adjustments/employee/{id}`
Update an employee adjustment.

---

## 6. Payroll Run Pipeline (Internal Process)

The payroll generation follows an **8-step pipeline**, as defined in the metamodel. This pipeline is internal (not directly exposed via REST) but can be triggered through the `/payroll/runs/{run_id}/generate` endpoint.

### Pipeline Steps

| Step | Name | Responsibility |
|------|------|----------------|
| **1** | Validation | Validate data integrity (contracts active, parameters present, no overlapping periods) |
| **2** | Collect | Gather all pay elements for each employee (base salary, adjustments, overtime, allowances) |
| **3** | Prorate | Apply calendar-day proration for mid-month hires/terminations |
| **4** | Build Bases | Calculate base amounts (CNSS base, INPP base, ONEM base, Taxable base) by filtering elements |
| **5** | Compute Deductions | Apply deduction formulas against each base: CNSS (5%), INPP (3.5%), ONEM (0.5%), IRPP (progressive scale with capping) |
| **6** | Compute Employer Costs | Apply employer contribution formulas: CNSS (13%), INPP (3.5%), ONEM (0.5%) |
| **7** | Generate Payslip | Assemble the payslip document with all computed values |
| **8** | Snapshot | Freeze legal parameters, exchange rate, and formulas into an immutable audit snapshot (SHA-256 signed) |

---

## 7. Integration Patterns

### Proration RPC (for mid-month hires)

For external validation or ad-hoc queries, the proration formula can be invoked as a utility:

```
POST /payroll/utils/prorate
```

**Request**:
```json
{
  "base_salary": 900000.00,
  "start_date": "2026-01-15",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31"
}
```

**Response** `200`:
```json
{
  "calendar_days_in_period": 31,
  "days_worked": 17,
  "prorated_salary": 493548.39,
  "formula": "900000.00 × 17/31"
}
```

### USD Salary Conversion

When a contract has a `salaire_negocie_usd` value, the system converts it to CDF at the period's exchange rate:

```
USD → CDF conversion: net_cdf_target = salaire_negocie_usd × exchange_rate
```

The actual CDF net pay should approximate this target after all deductions are applied on the gross `salaire_de_base`.

### Webhook Notifications

Payroll events can trigger webhooks for external systems (accounting, banking):

| Event | Payload | Trigger |
|-------|---------|---------|
| `payroll.run.completed` | `{ run_id, period, total_net }` | After all payslips generated |
| `payroll.run.approved` | `{ run_id, approved_by }` | After approval |
| `payroll.run.paid` | `{ run_id, payment_summary }` | After payment marked |
| `payslip.generated` | `{ payslip_id, employee_id, net_pay }` | Per individual payslip generation |

---

## 8. Mapping: Metamodel Concepts → API Resources

| Metamodel Concept | API Resource | Controller | Key Operations |
|-------------------|-------------|------------|----------------|
| `Employé` | `/employees/*` (separate module) | — | CRUD, org unit |
| `Contrat de travail` | `/payroll/contracts` | `EmployeeContractController` | CRUD, termination |
| `Période de paie` | `/payroll/runs` | `PayrollRunController` | Create, generate, approve, pay |
| `Élément de paie` | `/payroll/adjustments` + `/payroll/adjustments/employee` | `PayrollAdjustmentsController` | Type templates, per-employee |
| `Paramètre légal` | `/payroll/configuration/*` | `PayrollConfigurationController` | SMIG, tax brackets, rates, allowances |
| `Base de calcul` | Internal (step 4) | Service layer | Computed, not persisted |
| `Retenue` | Embedded in payslip | Service layer | Computed per payslip |
| `Charge patronale` | Embedded in payslip | Service layer | Computed per payslip |
| `Bulletin de paie` | `/payroll/runs/{id}/payslips` | `PayrollRunController` | Generate, view, list |
| `Avance sur salaire` | `/payroll/advances` | `SalaryAdvanceController` | Request, approve, track repayment |

---

## 9. Status & State Machines

### Payroll Run Status

```
DRAFT → PROCESSING → COMPLETED → PAID
  ↑         ↓              ↓
  └── CANCELED        CANCELED
```

- **DRAFT**: Run created, no payslips generated
- **PROCESSING**: Generating payslips (async)
- **COMPLETED**: All payslips generated, ready for review
- **PAID**: Payment confirmed, final
- **CANCELED**: Run abandoned

### Payslip Status

```
DRAFT → CALCULATED → PAID
```

### Contract Types

| Contract | Description | Has end_date? |
|----------|------------|---------------|
| `CDI` | Permanent (indeterminate) | No |
| `CDD` | Fixed-term | Yes |
| `PROBATION` | Trial period | Optional |
| `FREELANCE` | Consultancy | Yes |
| `INTERNSHIP` | Professional internship | Yes |
| `TEMPORARY` | Daily/temporary worker | No (per engagement) |

---

## 10. Error Reference

| HTTP Code | Meaning | Typical Cause |
|-----------|---------|---------------|
| `400` | Bad Request | Validation error, overlapping period |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate run for period, already paid |
| `422` | Unprocessable | Missing legal parameter for the period |
| `429` | Too Many Requests | Rate limit exceeded |

**Error response format**:
```json
{
  "detail": [
    {
      "loc": ["body", "base_salary"],
      "msg": "Value must be >= SMIG minimum",
      "type": "value_error"
    }
  ]
}
```
