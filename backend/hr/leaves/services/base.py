from django.db.models import Q
from hr.leaves.enums import LeaveStatus
from hr.leaves.models import Leave


class LeaveOverlapService:
    """
    Service for detecting overlapping leaves.  
    Vectorized version (bulk reasoning).
    """

    @staticmethod
    def has_overlap_bulk(
        *,
        employees,
        start_date,
        end_date,
        exclude_leave=None,
    ) -> bool:
        """
        Detects if there is AT LEAST one overlap
        for the given set of employees.
        """

        qs = Leave.objects.filter(
            status__in=[
                LeaveStatus.PENDING.value,
                LeaveStatus.APPROVED.value,
            ],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if exclude_leave:
            qs = qs.exclude(id=exclude_leave.id)

        qs = qs.filter(
            Q(everyone=True) |
            Q(leaves_employees__employee__in=employees)
        )

        return qs.exists()

