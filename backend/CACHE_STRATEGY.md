# Stratégie de Caching avec CacheOps

## Vue d'ensemble

Ce document détaille le plan d'implémentation du caching pour tous les modules HR utilisant **CacheOps** avec Redis.

---

## 1. Architecture du Caching

### Configuration existante

```
Backend: Redis (via REDIS_URL)
Library: cacheops
Default timeout: 3600s (1 heure)
```

### Principes de cache dans CacheOps

1. **Cache automatique des modèles** : Les querysets sont cachés automatiquement
2. **Invalidation intelligente** : Les changements de modèle invalident le cache related
3. **Timeout granulaire** : Différents timeout par modèle
4. **Ops configurables** : `get`, `fetch`, `count`, `all`, etc.

---

## 2. Plan d'implémentation par module

### 2.1 PAYROLL (Critique - Cache élevée priorité)

**Modèles clés à cacher:**
- `PayrollConfiguration` - ✅ Lecture fréquente, mise à jour rare
- `EmployeeContract` - ✅ Lecture très fréquente (chaque calcul)
- `PayrollRun` - ✅ Lecture pendant exécution
- `PayslipLine` - ✅ Cache après génération
- `SalaryAdvance` - ✅ Consulte à chaque calcul
- `WorkedDaysRecord` - ✅ Consulte à chaque calcul

**Timeout recommandé:** 
- Configuration: `60*60*24` (24h - rarement modifiée)
- Contrats: `60*60` (1h - peut changer en journée)
- Paies: `60*15` (15m - critère de fraîcheur)
- Avances: `60*30` (30m)

**Opérations à cacher:**
```python
'hr.payroll.*': {
    'ops': ('get', 'fetch', 'count'),  # Lecture + count
    'timeout': 60*60  # Défaut
}
```

**Points de cache explicite (dans services):**
- `get_employee_contract_by_date()` → Cache par employé+date
- `calculate_gross_salary()` → Cache par employé+période
- `get_payroll_configuration()` → Cache globalement
- `list_salary_advances()` → Cache par employé

---

### 2.2 LEAVES (Très important - Cache élevée priorité)

**Modèles clés à cacher:**
- `LeavePolicy` - ✅ Configuration rare
- `SeniorityRule` - ✅ Config rare
- `CircumstanceLeaveRule` - ✅ Config rare
- `EmployeeLeaveAllocation` - ✅ Lecture fréquente
- `LeaveRequest` - ✅ Consulte avant approuver
- `LeaveTransaction` - ✅ Audit trail

**Timeout recommandé:**
- Policies: `60*60*24` (24h - config)
- Rules: `60*60*24` (24h - config)
- Allocations: `60*60` (1h - peut changer)
- Requests: `60*30` (30m - état changeant)

**Points de cache explicite:**
- `get_leave_balance()` → Cache par employé+année
- `check_leave_availability()` → Cache résultat
- `get_applicable_rules()` → Cache par policy+type
- `calculate_leave_entitlement()` → Cache calcul

---

### 2.3 ATTENDANCE (Important - Cache moyenne priorité)

**Modèles clés à cacher:**
- `ShiftPolicy` - ✅ Config rarement changée
- `ShiftDetail` - ✅ Config rarement changée
- `EmploymentScheme` - ✅ Config rarement changée
- `Punch` - ⚠️ Cache court (arrivées/départs en temps réel)
- `DailyRegister` - ⚠️ Cache court (mis à jour chaque jour)
- `TimeSheet` - ⚠️ Cache court (en cours)

**Timeout recommandé:**
- Shift policies: `60*60*24` (24h)
- Punch: `60*5` (5m - données temps réel)
- Daily registers: `60*10` (10m - mis à jour fréquemment)
- Timesheets: `60*15` (15m)

**Points de cache explicite:**
- `get_employee_shifts()` → Cache par employé+période
- `get_shift_policy()` → Cache global
- `calculate_worked_hours()` → Cache par jour
- `generate_daily_register()` → Cache période

---

### 2.4 EMPLOYEES (Important - Cache moyenne priorité)

**Modèles clés à cacher:**
- `Employee` - ✅ Lecture très fréquente
- `EmployeeDocument` - ✅ Lecture moyenne
- `EmployeeFamilyMember` - ✅ Lecture moyenne
- `EmployeeEducation` - ✅ Lecture rare
- `EmployeeAddress` - ✅ Lecture rare

**Timeout recommandé:**
- Employee: `60*60*24` (24h - données stables)
- Documents: `60*60*24` (24h)
- Family members: `60*60*24` (24h)
- Education: `60*60*24` (24h - historique)

**Points de cache explicite:**
- `get_employee_by_matricule()` → Cache global (très fréquent)
- `get_active_employees()` → Cache par département
- `get_employee_family()` → Cache par employé
- `check_document_validity()` → Cache période

---

### 2.5 JOBS (Important - Cache moyenne priorité)

**Modèles clés à cacher:**
- `JobFamily` - ✅ Org structure stable
- `Position` - ✅ Org structure stable
- `Department` - ✅ Org structure stable
- `EmploymentPosition` - ✅ Historique
- `CareerTransition` - ✅ Historique

**Timeout recommandé:**
- Job families: `60*60*24` (24h - structure org)
- Positions: `60*60*24` (24h)
- Departments: `60*60*24` (24h)
- Employment positions: `60*60*12` (12h - changement possible)
- Career transitions: `60*60*24` (24h - historique)

**Points de cache explicite:**
- `get_department_tree()` → Cache global (org structure)
- `get_positions_by_family()` → Cache par famille
- `get_current_position()` → Cache par employé
- `check_hierarchy()` → Cache par département

---

### 2.6 CALENDAR (Critique pour payroll - Cache très élevée priorité)

**Modèles clés à cacher:**
- `CalendarEvent` - ✅ Données stables
- `PublicHoliday` - ✅ Données annuelles

**Timeout recommandé:**
- Calendar events: `60*60*24*7` (7 jours - stables)
- Public holidays: `60*60*24*30` (30 jours - annuels)

**Points de cache explicite:**
- `get_holidays_in_period()` → Cache par mois
- `is_working_day()` → Cache par date
- `count_working_days()` → Cache par période
- `get_company_calendar()` → Cache global

---

### 2.7 BANKING (Important - Cache moyenne priorité)

**Modèles clés à cacher:**
- `Bank` - ✅ Données stables
- `BankAccount` - ✅ Données moyennement stables

**Timeout recommandé:**
- Banks: `60*60*24*7` (7 jours - rarissimes changements)
- Bank accounts: `60*60` (1h - peuvent être désactivées)

**Points de cache explicite:**
- `get_active_bank_accounts()` → Cache global
- `get_bank_account_by_iban()` → Cache par IBAN
- `verify_account()` → Cache période
- `get_payment_methods()` → Cache global

---

### 2.8 RECRUITMENT (Basse priorité - Cache basse)

**Modèles clés à cacher:**
- `JobOffer` - ✅ Données semi-stables
- `Candidate` - ⚠️ Cache court (changements fréquents)
- `Application` - ⚠️ Cache court (processus dynamique)
- `Interview` - ⚠️ Cache court (processus dynamique)
- `HiringDecision` - ⚠️ Cache court (décisions finales)

**Timeout recommandé:**
- Job offers: `60*60*24` (24h)
- Candidates: `60*30` (30m - données volatiles)
- Applications: `60*30` (30m)
- Interviews: `60*15` (15m - processus en cours)
- Hiring decisions: `60*30` (30m)

**Points de cache explicite:**
- `get_active_job_offers()` → Cache par département
- `list_qualified_candidates()` → Cache par type poste
- `get_interview_schedule()` → Cache par date
- `get_hiring_pipeline()` → Cache global

---

## 3. Configuration CACHEOPS_CONFIG mise à jour

```python
CACHEOPS = {
    # PAYROLL - Très prioritaire
    'hr.payroll.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h défaut
    },
    'payroll.payrollconfiguration': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h - config stable
    },
    'payroll.employeecontract': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },
    'payroll.payrollrun': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*15  # 15m
    },
    'payroll.salaryadvance': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },
    'payroll.workeddaysrecord': {
        'ops': ('get', 'fetch'),
        'timeout': 60*30  # 30m
    },

    # LEAVES - Très prioritaire
    'hr.leaves.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h défaut
    },
    'leaves.leavepolicy': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.seniorityrule': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.circumstanceleaverule': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'leaves.employeeleaveallocation': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },
    'leaves.leaverequest': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },

    # ATTENDANCE
    'hr.attendance.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h défaut
    },
    'attendance.shiftpolicy': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'attendance.shiftdetail': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'attendance.punch': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*5  # 5m - temps réel
    },
    'attendance.dailyregister': {
        'ops': ('get', 'fetch'),
        'timeout': 60*10  # 10m
    },
    'attendance.timesheet': {
        'ops': ('get', 'fetch'),
        'timeout': 60*15  # 15m
    },

    # EMPLOYEES
    'hr.employees.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h
    },
    'employees.employee': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h - données stables
    },

    # JOBS
    'hr.jobs.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.jobfamily': {
        'ops': 'all',
        'timeout': 60*60*24  # 24h
    },
    'jobs.position': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.department': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'jobs.employmentposition': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*12  # 12h
    },

    # CALENDAR - Très prioritaire
    'hr.calendar.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60*24  # 24h défaut
    },
    'calendar.calendarevent': {
        'ops': 'all',
        'timeout': 60*60*24*7  # 7 jours
    },

    # BANKING
    'hr.banking.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*60  # 1h défaut
    },
    'banking.bank': {
        'ops': 'all',
        'timeout': 60*60*24*7  # 7 jours
    },
    'banking.bankaccount': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60  # 1h
    },

    # RECRUITMENT
    'hr.recruitment.*': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m défaut
    },
    'recruitment.joboffer': {
        'ops': ('get', 'fetch'),
        'timeout': 60*60*24  # 24h
    },
    'recruitment.candidate': {
        'ops': ('get', 'fetch'),
        'timeout': 60*30  # 30m
    },
    'recruitment.application': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*30  # 30m
    },
    'recruitment.interview': {
        'ops': ('get', 'fetch', 'count'),
        'timeout': 60*15  # 15m
    },
}
```

---

## 4. Implémentation dans les services

### Pattern générique pour service

```python
# services/cache_helpers.py
from functools import wraps
from django.core.cache import cache
from cacheops import cache_on_save

def cache_query(timeout=None, key_pattern=None):
    """Décorateur pour cacher les résultats de requête"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer clé de cache
            cache_key = key_pattern or f"{func.__module__}.{func.__name__}"
            
            # Ajouter args/kwargs à clé si pertinent
            if args or kwargs:
                key_parts = [cache_key]
                if args:
                    key_parts.extend(str(arg) for arg in args[1:])  # Skip 'self'
                if kwargs:
                    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Vérifier cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Exécuter et cacher
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout or 60*60)
            return result
        
        return wrapper
    return decorator
```

### Pattern par module

**Payroll Service:**
```python
from hr.payroll.models import PayrollConfiguration, EmployeeContract
from cacheops import cache_on_save

class PayrollService:
    
    @staticmethod
    @cache_on_save([PayrollConfiguration])
    def get_configuration():
        """Retourne config (cachée car stable)"""
        return PayrollConfiguration.objects.first()
    
    @staticmethod
    def get_employee_contract_for_date(employee, date):
        """Retourne contrat actif à une date"""
        # Pattern: hr:payroll:contract:{emp_id}:{date}
        cache_key = f"hr:payroll:contract:{employee.id}:{date}"
        contract = cache.get(cache_key)
        if contract is None:
            contract = EmployeeContract.objects.filter(
                employee=employee,
                effective_date__lte=date,
                end_date__gte=date
            ).first()
            cache.set(cache_key, contract, timeout=60*60)
        return contract
```

**Leaves Service:**
```python
from hr.leaves.models import LeavePolicy, SeniorityRule

class LeaveService:
    
    @staticmethod
    def get_leave_balance(employee, year):
        """Retourne solde congés (cachée)"""
        cache_key = f"hr:leaves:balance:{employee.id}:{year}"
        balance = cache.get(cache_key)
        if balance is None:
            allocation = EmployeeLeaveAllocation.objects.get(
                employee=employee,
                year=year
            )
            # Calculer balance...
            balance = {...}
            cache.set(cache_key, balance, timeout=60*60)
        return balance
    
    @staticmethod
    def get_applicable_rules(policy, leave_type):
        """Retourne règles applicable"""
        cache_key = f"hr:leaves:rules:{policy.id}:{leave_type}"
        rules = cache.get(cache_key)
        if rules is None:
            rules = list(
                SeniorityRule.objects.filter(policy=policy)
                .order_by('years_of_service')
            )
            cache.set(cache_key, rules, timeout=60*60*24)
        return rules
```

**Calendar Service:**
```python
from hr.calendar.models import CalendarEvent
from django.utils import timezone

class CalendarService:
    
    @staticmethod
    def get_holidays_in_period(start_date, end_date):
        """Retourne jours fériés période"""
        cache_key = f"hr:calendar:holidays:{start_date}:{end_date}"
        holidays = cache.get(cache_key)
        if holidays is None:
            holidays = list(
                CalendarEvent.objects
                .filter(type="holiday", date__range=[start_date, end_date])
                .values_list('date', flat=True)
            )
            cache.set(cache_key, holidays, timeout=60*60*24*7)
        return holidays
    
    @staticmethod
    def count_working_days(start_date, end_date):
        """Compte jours travaillés (cachée)"""
        cache_key = f"hr:calendar:working_days:{start_date}:{end_date}"
        count = cache.get(cache_key)
        if count is None:
            holidays = CalendarService.get_holidays_in_period(
                start_date, end_date
            )
            total_days = (end_date - start_date).days + 1
            weekend_days = sum(
                1 for i in range(total_days)
                if (start_date + timezone.timedelta(days=i)).weekday() >= 5
            )
            count = total_days - len(holidays) - weekend_days
            cache.set(cache_key, count, timeout=60*60*24*7)
        return count
```

**Attendance Service:**
```python
from hr.attendance.models import ShiftPolicy, Punch

class AttendanceService:
    
    @staticmethod
    def get_employee_shifts(employee, period_start, period_end):
        """Retourne shifts employé"""
        cache_key = f"hr:attendance:shifts:{employee.id}:{period_start}:{period_end}"
        shifts = cache.get(cache_key)
        if shifts is None:
            shifts = list(
                EmploymentScheme.objects
                .filter(employee=employee, effective_date__lte=period_start)
                .latest('effective_date')
                .shift_policy.shiftdetail_set.all()
            )
            cache.set(cache_key, shifts, timeout=60*60*24)
        return shifts
    
    @staticmethod
    def calculate_worked_hours(employee, date):
        """Calcule heures travaillées jour"""
        cache_key = f"hr:attendance:hours:{employee.id}:{date}"
        hours = cache.get(cache_key)
        if hours is None:
            punches = Punch.objects.filter(
                daily_register__employee=employee,
                daily_register__date=date
            )
            hours = sum(p.duration.total_seconds() / 3600 for p in punches)
            cache.set(cache_key, hours, timeout=60*60)
        return hours
```

**Employees Service:**
```python
from hr.employees.models import Employee

class EmployeeService:
    
    @staticmethod
    def get_employee_by_matricule(matricule):
        """Très utilisé - cache élevée"""
        cache_key = f"hr:employees:matricule:{matricule}"
        employee = cache.get(cache_key)
        if employee is None:
            employee = Employee.objects.get(matricule=matricule)
            cache.set(cache_key, employee, timeout=60*60*24)
        return employee
    
    @staticmethod
    def get_active_employees(department=None):
        """Retourne employés actifs"""
        cache_key = f"hr:employees:active:{department.id if department else 'all'}"
        employees = cache.get(cache_key)
        if employees is None:
            query = Employee.objects.filter(status="active")
            if department:
                query = query.filter(current_position__department=department)
            employees = list(query)
            cache.set(cache_key, employees, timeout=60*60*24)
        return employees
```

**Jobs Service:**
```python
from hr.jobs.models import Department, Position

class JobService:
    
    @staticmethod
    def get_department_tree():
        """Structure org - très stable"""
        cache_key = "hr:jobs:department_tree"
        tree = cache.get(cache_key)
        if tree is None:
            # Construire arborescence...
            tree = build_department_hierarchy()
            cache.set(cache_key, tree, timeout=60*60*24)
        return tree
    
    @staticmethod
    def get_positions_by_family(family):
        """Postes par famille"""
        cache_key = f"hr:jobs:positions:{family.id}"
        positions = cache.get(cache_key)
        if positions is None:
            positions = list(Position.objects.filter(family=family))
            cache.set(cache_key, positions, timeout=60*60*24)
        return positions
```

**Banking Service:**
```python
from hr.banking.models import BankAccount

class BankingService:
    
    @staticmethod
    def get_active_bank_accounts():
        """Comptes actifs - cache globale"""
        cache_key = "hr:banking:active_accounts"
        accounts = cache.get(cache_key)
        if accounts is None:
            accounts = list(
                BankAccount.objects.filter(status="active")
            )
            cache.set(cache_key, accounts, timeout=60*60)
        return accounts
    
    @staticmethod
    def get_bank_account_by_iban(iban):
        """Compte par IBAN"""
        cache_key = f"hr:banking:iban:{iban}"
        account = cache.get(cache_key)
        if account is None:
            account = BankAccount.objects.get(iban=iban)
            cache.set(cache_key, account, timeout=60*60)
        return account
```

**Recruitment Service:**
```python
from hr.recruitment.models import JobOffer, Application

class RecruitmentService:
    
    @staticmethod
    def get_active_job_offers(department=None):
        """Offres actives"""
        cache_key = f"hr:recruitment:offers:{department.id if department else 'all'}"
        offers = cache.get(cache_key)
        if offers is None:
            query = JobOffer.objects.filter(status="open")
            if department:
                query = query.filter(position__department=department)
            offers = list(query)
            cache.set(cache_key, offers, timeout=60*60*24)
        return offers
    
    @staticmethod
    def list_qualified_candidates(job_offer):
        """Candidats qualifiés"""
        cache_key = f"hr:recruitment:qualified:{job_offer.id}"
        candidates = cache.get(cache_key)
        if candidates is None:
            applications = Application.objects.filter(
                job_offer=job_offer,
                status="qualified"
            ).select_related('candidate')
            candidates = [a.candidate for a in applications]
            cache.set(cache_key, candidates, timeout=60*60*12)
        return candidates
```

---

## 5. Invalidation manuelle du cache

Certains événements requièrent l'invalidation du cache :

```python
# Dans les signals ou après opérations critiques

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# PAYROLL INVALIDATION
@receiver(post_save, sender=EmployeeContract)
def invalidate_contract_cache(sender, instance, **kwargs):
    """Invalide cache contrats quand changement"""
    cache_key = f"hr:payroll:contract:{instance.employee_id}:*"
    cache.delete_many(
        [k for k in cache.keys(f"{cache_key}*")]
    )

@receiver(post_save, sender=PayrollRun)
def invalidate_payroll_cache(sender, instance, **kwargs):
    """Invalide cache paie quand changement"""
    cache.delete_many([
        f"hr:payroll:contract:*",
        f"hr:leaves:balance:*",
        f"hr:attendance:hours:*"
    ])

# LEAVES INVALIDATION
@receiver(post_save, sender=EmployeeLeaveAllocation)
def invalidate_leave_balance(sender, instance, **kwargs):
    """Invalide balance congés"""
    cache_key = f"hr:leaves:balance:{instance.employee_id}:*"
    cache.delete_pattern(cache_key)

@receiver(post_save, sender=LeaveRequest)
def invalidate_leave_request_cache(sender, instance, **kwargs):
    """Invalide cache requête congés"""
    cache.delete(f"hr:leaves:balance:{instance.employee_id}:{instance.start_date.year}")

# CALENDAR INVALIDATION
@receiver(post_save, sender=CalendarEvent)
def invalidate_calendar_cache(sender, instance, **kwargs):
    """Invalide cache calendrier"""
    cache.delete_pattern("hr:calendar:*")

# ATTENDANCE INVALIDATION
@receiver(post_save, sender=Punch)
def invalidate_attendance_cache(sender, instance, **kwargs):
    """Invalide cache présence"""
    cache_key = f"hr:attendance:hours:{instance.daily_register.employee_id}:{instance.daily_register.date}"
    cache.delete(cache_key)

# EMPLOYEE INVALIDATION
@receiver(post_save, sender=Employee)
def invalidate_employee_cache(sender, instance, **kwargs):
    """Invalide cache employé"""
    cache.delete_many([
        f"hr:employees:matricule:{instance.matricule}",
        "hr:employees:active:*"
    ])

# JOBS INVALIDATION
@receiver(post_save, sender=Department)
def invalidate_job_cache(sender, instance, **kwargs):
    """Invalide cache jobs"""
    cache.delete_many([
        "hr:jobs:department_tree",
        f"hr:jobs:positions:*"
    ])

# BANKING INVALIDATION
@receiver(post_save, sender=BankAccount)
def invalidate_banking_cache(sender, instance, **kwargs):
    """Invalide cache comptes"""
    cache.delete_many([
        "hr:banking:active_accounts",
        f"hr:banking:iban:{instance.iban}"
    ])
```

---

## 6. Monitoring et debugging

### Helper pour voir cache stats

```python
# utils/cache_debug.py
from django.core.cache import cache
import json

def get_cache_stats():
    """Retourne stats du cache Redis"""
    from django_redis import get_redis_connection
    
    redis_conn = get_redis_connection("default")
    info = redis_conn.info()
    
    return {
        "total_keys": redis_conn.dbsize(),
        "memory_usage_mb": info['used_memory'] / 1024 / 1024,
        "evictions": info.get('evicted_keys', 0),
        "hit_rate": (
            info['keyspace_hits'] / 
            (info['keyspace_hits'] + info['keyspace_misses'])
            if (info['keyspace_hits'] + info['keyspace_misses']) > 0
            else 0
        )
    }

def clear_all_cache():
    """Nettoie tout le cache"""
    cache.clear()

def get_cache_keys_pattern(pattern):
    """List toutes clés matchant pattern"""
    from django_redis import get_redis_connection
    redis_conn = get_redis_connection("default")
    return redis_conn.keys(f"*{pattern}*")

# Views/Command pour debugging
def cache_debug_view(request):
    """View pour voir stats cache"""
    stats = get_cache_stats()
    return JsonResponse(stats)

# Dans un management command:
# python manage.py clear_cache
# python manage.py cache_stats
```

---

## 7. Best Practices

### ✅ DO:
- ✓ Cacher les configurations/données stables
- ✓ Cacher les requêtes read-heavy
- ✓ Utiliser timeout approprié par cas
- ✓ Invalider quand données changent
- ✓ Tester sans cache d'abord
- ✓ Monitorer utilisation cache
- ✓ Vérifier hit rate régulièrement

### ❌ DON'T:
- ✗ Cacher les données volatiles
- ✗ Cacher avec timeout trop long (data stale)
- ✗ Oublier d'invalider le cache
- ✗ Cacher sans considérer multi-user
- ✗ Ne pas prévoir plan nettoyage
- ✗ Mettre données sensibles en cache sans secure
- ✗ Ignorer erreurs connexion Redis

---

## 8. Étapes d'implémentation

### Phase 1: Configuration (1 jour)
1. Mettre à jour CACHEOPS dans settings
2. Créer `services/cache_helpers.py`
3. Installer redis si nécessaire
4. Tester connexion redis

### Phase 2: Core Modules (3 jours)
1. Payroll service avec cache
2. Leaves service avec cache
3. Calendar service avec cache
4. Attendance service avec cache

### Phase 3: Support Modules (2 jours)
1. Employees service
2. Jobs service
3. Banking service
4. Recruitment service

### Phase 4: Signals & Invalidation (1 jour)
1. Créer signals pour chaque modèle
2. Tester invalidation
3. Documenter cas spéciaux

### Phase 5: Monitoring (1 jour)
1. Créer cache_debug utils
2. Ajouter management commands
3. Documenter monitoring

---

## 9. Références

- **CacheOps Docs**: https://cacheops.readthedocs.io/
- **Django Cache**: https://docs.djangoproject.com/en/stable/topics/cache/
- **Redis**: https://redis.io/

