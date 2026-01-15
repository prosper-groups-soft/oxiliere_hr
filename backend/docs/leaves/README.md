# Leave Management Module Documentation

## Overview

The **Leave Management module** is a rule-based engine that manages the full lifecycle of employee absences. It tracks entitlements, accruals, requests, approvals, and balances while ensuring data integrity, auditability, and compliance with company and local regulations.

The module handles planned and unplanned leaves, special legal events, carry-overs, and multi-year leaves, integrating seamlessly with payroll and HR reporting.

---

## Core Concepts

### 1. **LeaveBalance**

Represents the employee’s available leave entitlements.

* Fields: `employee_id`, `balance_type`, `total_days`, `used_days`, `reserved_days`, `expiry_date`.

* Features:

  * **Pro-rata Calculation** → Mid-year joiners receive entitlements based on active days.
  * **Seniority Bonus** → Extra days awarded according to `hire_date`.
  * **Carry-over** → Remaining days from the previous year transferred atomically, up to policy limits.

* Validations: Ensures no over-consumption or double-spending through database locking and atomic transactions.

---

### 2. **LeaveRequest**

Represents an individual leave submission.

* Fields: `employee_id`, `leave_type`, `start_date`, `end_date`, `status`, `attachment_id`, `balance_deduction`.

* Workflow States:

  | Status       | Description             | Balance Impact              |
  | ------------ | ----------------------- | --------------------------- |
  | **PENDING**  | Awaiting manager review | Reserved (days blocked)     |
  | **APPROVED** | Manager confirmed       | Committed (balance reduced) |
  | **REJECTED** | Denied by manager       | Released (days returned)    |
  | **TAKEN**    | Leave period passed     | Finalized (archived)        |

* Validations: Proof attachments required for legal events; ensures no modification after approval unless policy allows.

---

### 3. **WorkingDaysEngine**

Calculates effective leave duration considering calendars.

* Factors:

  * Standard weekends (e.g., Saturday/Sunday).
  * Statutory holidays (via `Holidays` service).
  * Company closure periods.

* Features: Accurate pro-rata and calendar-aware leave computation.

---

### 4. **ConsumptionPriority**

Determines the order of leave balance usage.

* Priority:

  1. Expiring Carry-over
  2. Annual Entitlement
  3. Anticipated Leave (if policy allows)

* Features: Protects employee benefits and avoids negative balances.

---

### 5. **SpecialLeave**

Manages legal or exceptional leave events.

* Types: Marriage, Bereavement, Jury Duty, etc.

* Rules:

  * Fixed legal durations override standard balances.
  * Proof validation required for approval.

* Features: Ensures compliance with labor law requirements.

---

### 6. **AutomationTasks**

Automates leave accruals, expirations, and transitions.

* Implemented via Celery Beat:

  * `daily_accrual_check` → Updates pro-rata entitlements.
  * `carryover_expiry_job` → Expires old carry-over days.
  * `auto_take_transition` → Moves approved leaves to `TAKEN` status automatically.

* Features: Reduces manual intervention and enforces policies consistently.

---

## Features & Capabilities

1. **Accurate Leave Tracking**

   * Tracks entitlements, usage, reservations, and expirations.
   * Prevents double-spending and ensures atomic transactions.

2. **Calendar-Aware Duration Calculation**

   * Considers weekends, holidays, and company closures.
   * Supports multi-year leaves.

3. **State Machine Enforcement**

   * PENDING → APPROVED → TAKEN with strict transitions.
   * Balances updated automatically based on state.

4. **Special Leave Management**

   * Legal events with fixed durations.
   * Proof attachments validated before approval.

5. **Pro-rata & Seniority Logic**

   * Mid-year joiners receive proportional entitlements.
   * Seniority bonus days calculated automatically.

6. **Carry-over Handling**

   * Atomic transfer of unused days to the new cycle.
   * Expiration handled automatically.

7. **Automation & Scheduled Maintenance**

   * Daily accruals, expirations, and automated leave transitions.

8. **Audit & Compliance**

   * Every action logged with user, timestamp, and change details.
   * Ensures data integrity for HR audits and payroll integration.

---

## Typical Workflow

1. **Balance Initialization**

   * System calculates annual entitlement, carry-over, and seniority bonuses.

2. **Leave Submission**

   * Employee submits `LeaveRequest` → Status: PENDING → APPROVED → TAKEN.

3. **Balance Deduction**

   * Leave balances are consumed in FIFO order: Carry-over → Annual → Anticipated.

4. **Special Leave Handling**

   * Legal events validated with proof attachment.

5. **Automation & Maintenance**

   * Daily accruals, carry-over expiration, and automatic TAKEN transitions.

6. **Audit & Reporting**

   * All actions logged; balances and requests reportable per employee and fiscal year.

---

## Relationships

* `Employee` → `LeaveBalance` → `LeaveRequest`
* `LeaveRequest` → optional `SpecialLeave`
* `WorkingDaysEngine` → calculates duration for `LeaveRequest`
* `AutomationTasks` → manage balances, transitions, and expirations

---

## Validation Rules

* Leave cannot exceed available balance.
* Special leave requires proof attachment for approval.
* Balances updated atomically; no direct modification allowed.
* Multi-year leaves split automatically across fiscal years.
* All transitions logged for audit purposes.

---

## Conclusion

This module enables **full-featured leave management**:

* Tracks entitlements, balances, requests, approvals, and multi-year leaves.
* Automatically applies calendar rules, pro-rata, and seniority logic.
* Ensures auditability, data integrity, and compliance with company and legal regulations.
* Integrates with payroll, HR reporting, and automation tasks for minimal manual intervention.

---
