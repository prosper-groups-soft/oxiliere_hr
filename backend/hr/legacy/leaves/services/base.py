from django.db.models import Q
from hr.leaves.choices import LeaveStatus
from hr.leaves.models import Leave


class LeaveOverlapService:

    @staticmethod
    def has_overlap(*, employee, start_date, end_date, exclude_leave=None):
        qs = Leave.objects.filter(
            status=LeaveStatus.APPROVED.value,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if exclude_leave:
            qs = qs.exclude(id=exclude_leave.id)

        qs = qs.filter(Q(everyone=True) | Q(leaves_employees__employee=employee))
        return qs.exists()
