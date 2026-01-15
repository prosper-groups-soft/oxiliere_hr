# Employee Module Documentation

## Overview

The **Employee module** is the core of the HR system, tailored for the **Francophone (DRC) market**. It manages employee identity, administrative lifecycle, addresses, documents, family, education, emergency contacts, and historical tracking. The module ensures strict data integrity, compliance with DRC regulations, and a fully auditable service-oriented architecture.

It supports complete HR operations, from onboarding to offboarding, including personal data management, family benefits calculation, academic background tracking, and HR reporting.

---

## Core Concepts

### 1. **EmployeeProfile**

Represents the static identity and legal information of an employee.

* Fields: `matricule`, `first_name`, `last_name`, `email`, `hire_date`, `civil_status`.

* Actions:

  * `onboard_employee(data)` → Initializes employee with unique ID, normalized data, and hire date.
  * `update_personal_info(employee_id, data)` → Updates civil status and personal info (except structural fields).
  * `get_full_profile(employee_id)` → Aggregates all related data (addresses, education, documents) for HR File.

* Validations: Ensures uniqueness of `matricule` and proper formatting of names/emails.

---

### 2. **EmployeeStatus**

Manages contractual state, system permissions, and lifecycle events.

* Actions:

  * `transition_status(employee_id, new_status, effective_date, reason)` → Logs status changes in `EmployeeStatusHistory`.
  * `suspend_access(employee_id, reason)` → Temporarily disables system access (`can_connect=False`).
  * `offboard_employee(employee_id, end_date, reason)` → Closes the record and sets `is_active=False`.

* Features: Tracks history of employment, probation, sabbatical, and termination events.

---

### 3. **EmployeeAddress**

Tracks physical residency and movement history.

* Actions:

  * `register_move(employee_id, data, effective_date)` → Closes previous address and creates a new one.
  * `correct_current_address(address_id, data)` → Administrative corrections without breaking history.

* Features: Supports temporality management for tax and logistics purposes.

---

### 4. **EmployeeDocuments**

Manages legal and academic documents (KYC).

* Actions:

  * `upload_document(employee_id, data, file)` → Stores scans of ID, voter cards, diplomas.
  * `verify_document(document_id, hr_user_id)` → HR validation against physical originals.

* Features: Ensures legal compliance and document authenticity.

---

### 5. **EmployeeFamily**

Handles dependents and family-related benefits.

* Actions:

  * `declare_child(employee_id, data)` → Adds child with birthdate validation.
  * `remove_child(child_id)` → Soft delete preserves historical payroll records.

* Features: Supports family allowance calculation and audits.

---

### 6. **EmployeeEducation**

Tracks academic and professional qualifications (LMD-compatible).

* Actions:

  * `add_education(employee_id, data)` → Adds degrees or certifications.
  * `update_education(education_id, data)` → Updates institute or major.

* Features: Supports professional development tracking and HR reporting.

---

### 7. **EmployeeEmergency**

Manages emergency contacts for employees.

* Actions:

  * `set_emergency_contacts(employee_id, contact_list)` → Reorders or replaces contacts.

* Features: Always ensures a valid "Priority 1" contact.

---

### 8. **EmployeeQuery**

Read-only service for fast employee lookup.

* Actions:

  * `list_employees(filters)` → Filterable list with `.distinct()` management.
  * `search_employees(query)` → Search across matricule, name, city, or document number.

* Features: Optimized for performance following CQRS principles.

---

## Features & Capabilities

1. **Employee Lifecycle Management**

   * Onboarding, status transitions, suspension, offboarding.
   * Maintains a full historical trail for audits.

2. **Personal & Legal Information Management**

   * Handles identity, civil status, addresses, and documents.
   * Ensures DRC compliance with local identifiers.

3. **Family & Dependents**

   * Supports family allowances and historical integrity.

4. **Education & Professional Background**

   * Tracks degrees and certifications for HR and payroll purposes.

5. **Emergency Contact Management**

   * Ensures rapid access to validated emergency contacts.

6. **Global Employee Search & Reporting**

   * Fast, cross-model querying and aggregation of employee data.

7. **Audit & Data Stewardship**

   * Every change is logged with `auditlog`, ensuring transparency.

8. **Temporal Management (Effective Dating)**

   * Status changes, addresses, and other updates support `effective_date`.

9. **Compliance & Policy Enforcement**

   * Handles local DRC HR rules and LMD education system.
   * Soft deletes preserve historical integrity for payroll and legal purposes.

---

## Typical Workflow

1. **Onboarding**

   * `onboard_employee()` → Assigns matricule, normalizes data, sets hire date.

2. **Status Changes**

   * `transition_status()` → Updates employment status with effective date.

3. **Address & Document Updates**

   * `register_move()` or `upload_document()` → Keeps history of moves and verified documents.

4. **Family & Education Management**

   * Declare dependents or add education history.

5. **Emergency Contacts Setup**

   * Set or update priority contacts.

6. **Employee Query & Reporting**

   * List or search employees across multiple filters.

7. **Offboarding**

   * `offboard_employee()` → Locks record, disables access, logs termination.

---

## Validation Rules

* Unique `matricule` for each employee.
* Names normalized (Title Case) and emails lowercase.
* Addresses support temporality.
* Documents must be verified before HR approval.
* Children and dependents use soft deletes for historical integrity.
* Status transitions cannot overwrite immutable fields (hire date, employee ID).
* All changes logged for audit purposes.

---

## Conclusion

This module enables **comprehensive employee management**:

* Tracks personal, legal, and professional data throughout the employee lifecycle.
* Maintains strict audit trails, historical integrity, and DRC compliance.
* Supports HR operations from onboarding to offboarding, including family, education, and emergency contact management.
* Provides fast employee queries, reporting, and integration with payroll or other HR modules.

---
