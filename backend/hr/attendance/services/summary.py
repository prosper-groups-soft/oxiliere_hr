from __future__ import annotations
from datetime import date, timedelta
from uuid import UUID
from django.db.models import Sum, Count, Q
from hr.attendance.models import TimeSheet, TimeSheetStatus
# Cache integration
from hr.services.cache_helpers import cache_query


class AttendanceSummaryService:
    """ Provides aggregated attendance metrics for payroll and reporting. """

    @staticmethod
    @cache_query(timeout=3600, key_args=(0, 1, 2))
    def get_attendance_summary(employee_id: UUID, start_date: date, end_date: date) -> dict:
        """ Calculates worked days, hours, and overtime breakdown for a specific period. """
        
        # Seuls les registres FINALISÉS alimentent la paie : avant finalisation un
        # TimeSheet est encore par défaut ABSENT et ses heures ne sont pas
        # réconciliées. Compter du non finalisé gonflerait faussement les absences.
        finalized = Q(register__is_finalized=True)
        worked = Q(status__in=[
            TimeSheetStatus.PRESENT, TimeSheetStatus.PARTIAL, TimeSheetStatus.LATE
        ])
        qs = TimeSheet.objects.filter(
            employee_id=employee_id,
            register__date__range=(start_date, end_date)
        )
        summary = qs.aggregate(
            worked_days=Count('id', filter=worked & finalized),
            absence_days=Count('id', filter=Q(status=TimeSheetStatus.ABSENT) & finalized),
            total_work=Sum('recorded_work', filter=worked & finalized),
            std_overtime=Sum('overtime', filter=worked & finalized),
            hld_overtime=Sum('overtime', filter=Q(status=TimeSheetStatus.HOLIDAY) & finalized),
            # Jours de la période pas encore finalisés (donc exclus du calcul ci-dessus).
            unfinalized_days=Count('id', filter=Q(register__is_finalized=False)),
        )

        def to_hours(td: timedelta | None) -> float:
            """ Converts timedelta to decimal hours rounded to two units. """
            if not td: return 0.0
            return round(td.total_seconds() / 3600.0, 2)

        return {
            'regular_days': summary['worked_days'] or 0,
            'absence_days': summary['absence_days'] or 0,
            'total_worked_hours': to_hours(summary['total_work']),
            'overtime_hours_standard': to_hours(summary['std_overtime']),
            'overtime_hours_holiday': to_hours(summary['hld_overtime']),
            # Jours de la période dont les registres ne sont pas encore finalisés.
            # Leur absence/heures ne sont volontairement PAS comptées ci-dessus.
            'unfinalized_days': summary['unfinalized_days'] or 0,
        }

