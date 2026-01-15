# Attendance Module Documentation

## Overview

The **Attendance module** manages employee working time using a **policy-driven, punch-based architecture**.
It supports daily registers, per-employee timesheets, raw time punches, policy-based schedules, and immutable archival periods.

The system is designed for:

* Accurate work and break tracking (including night shifts)
* Contractual schedule enforcement via policies
* HR auditability and manual adjustments
* Payroll-safe period locking
* Multi-policy, multi-period employee contracts

The module separates **theoretical work expectations** from **actual recorded time**, enabling precise deviation analysis (overtime / shortfall).

---

## Core Domain Concepts (Model Mapping)

### 1. **ShiftPolicy**

Defines the **contractual working time policy**.

**Model:** `ShiftPolicy`

* Represents a reusable work policy (e.g. *Standard 40h*, *Night Shift*, *Weekend Crew*)
* Defines the **weekly target hours**
* Acts as the parent for detailed weekday schedules

**Key fields**

* `name`
* `weekly_target_hours`
* `description`

> A policy defines *what is expected*, not what is worked.

---

### 2. **ShiftDetail**

Defines **expected working hours per weekday** within a policy.

**Model:** `ShiftDetail`

* One record per weekday per policy
* Supports strict or flexible enforcement
* Determines theoretical daily working duration

**Key fields**

* `weekday`
* `start_time`, `end_time`
* `is_working_day`
* `flexible_hours`

**Rules**

* Unique per `(policy, weekday)`
* Used as the baseline for overtime / shortfall calculations

---

### 3. **EmploymentScheme**

Associates an employee with a shift policy over time.

**Model:** `EmploymentScheme`

* Handles **contract validity periods**
* Supports seasonal or evolving work conditions
* Only active schemes are considered for calculations

**Key fields**

* `employee`
* `policy`
* `valid_from`, `valid_until`
* `is_active`

> This enables clean historical tracking of policy changes without rewriting attendance data.

---

### 4. **DailyRegister**

Acts as the **master attendance container for a given date**.

**Model:** `DailyRegister`

* One register per calendar day
* Groups all employee timesheets for that date
* Holds daily-level metrics and status

**Key fields**

* `date`
* `code` (auto-generated: `DR-YYYYMMDD-XXXX`)
* `total_employees_expected`
* `total_absences`
* `is_finalized`

> Comparable to a daily attendance ledger.

---

### 5. **TimeSheet**

Represents the **daily attendance summary for one employee**.

**Model:** `TimeSheet`

* One per `(employee, date)`
* Aggregates raw punches into meaningful totals
* Compares actual work against expected schedule

**Computed fields**

* `recorded_work`
* `recorded_break`
* `overtime`
* `shortfall`

**Status**

* Derived from punches and policy rules
* Uses `TimeSheetStatus` enum (present, absent, etc.)

**Validation**

* Cannot be modified if the date is archived
* Clean separation between raw data and derived totals

---

### 6. **TimePunch**

Represents an **atomic time segment** (raw attendance data).

**Model:** `TimePunch`

* Uses `DateTimeField` to support night shifts
* Each punch represents a continuous interval
* Automatically computes its own duration

**Key fields**

* `punch_type` (work, break, exit, etc.)
* `start_at`, `end_at`
* `duration`
* `is_manual_entry`

> This is the single source of truth for worked time.

---

### 7. **PeriodArchiveLock**

Defines an **immutability boundary** for attendance data.

**Model:** `PeriodArchiveLock`

* Locks all data **up to a given date**
* Prevents retroactive edits after payroll closure
* Typically used for monthly closing

**Key fields**

* `locked_until`
* `reason`
* `locked_by`

---

### 8. **AttendanceSettings**

Global configuration and enforcement layer.

**Model:** `AttendanceSettings` (Singleton)

Defines universal rules applied across the module.

**Key fields**

* `active_archive_lock`
* `late_grace_period`
* `rounding_precision`

**Responsibilities**

* Central access to the current lock date
* Late arrival tolerance
* Time rounding rules

---

## Functional Capabilities

### 1. Time Tracking (Punch-Based)

* Multiple punches per day
* Work, break, and auxiliary punch types
* Automatic duration computation
* Night shift support (crossing midnight)

---

### 2. Policy-Based Scheduling

* Weekly expectations via `ShiftPolicy`
* Per-day rules via `ShiftDetail`
* Flexible vs strict schedules
* Contract validity handled cleanly

---

### 3. Overtime & Shortfall Calculation

* Actual work (`TimePunch`) vs expected work (`ShiftDetail`)
* Automatically computed at the `TimeSheet` level
* Fully auditable and reproducible

---

### 4. Manual Adjustments & Audit Trail

* HR can add or correct punches
* `is_manual_entry` flags enforced
* Full traceability via `BaseAuditableModel`

---

### 5. Period Closing & Data Integrity

* Archive locks prevent historical edits
* Validation enforced at model level
* Payroll-safe by design

---

### 6. Multi-Policy & Multi-Period Support

* Employees can change schedules over time
* Past attendance remains untouched
* Suitable for complex organizations and countries

---

## Typical Workflow

### 1. Policy Setup

* Create `ShiftPolicy`
* Define weekly structure via `ShiftDetail`

### 2. Employee Assignment

* Attach employees using `EmploymentScheme`
* Control validity periods precisely

### 3. Daily Operations

* System creates a `DailyRegister`
* `TimeSheet` created per employee
* `TimePunch` records actual activity

### 4. Review & Corrections

* HR reviews deviations
* Manual corrections logged explicitly

### 5. Archival

* Period locked using `PeriodArchiveLock`
* All prior data becomes immutable

---

## Conclusion

This Attendance module provides a **robust, payroll-grade time management system**:

* Clear separation between policy, raw data, and computed results
* Full auditability and legal compliance
* Flexible scheduling without sacrificing data integrity
* Designed for real-world HR complexity and future scalability

In short:
**Policy defines intent. Punches capture reality. Timesheets reconcile both.**
