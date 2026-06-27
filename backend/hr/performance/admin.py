from django.contrib import admin
from .models import PerformanceReview


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ('employee', 'review_period_start', 'review_period_end', 'status', 'overall_rating')
    list_filter = ('status',)
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
