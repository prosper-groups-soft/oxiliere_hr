from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .api import api
from hr.employees.views import EmployeeProfilePDFView
from hr.recruitment.views import CandidateEvaluationPDFView
from hr.payroll.views import PayslipPDFView, PayslipBulkZipView


urlpatterns = [
    path('api/employees/<uuid:pk>/export/', EmployeeProfilePDFView.as_view(), name='employee_export_pdf'),
    path('api/recruitment/candidates/<uuid:pk>/export/', CandidateEvaluationPDFView.as_view(), name='candidate_evaluation_pdf'),
    path('api/payroll/payslips/<uuid:pk>/export/', PayslipPDFView.as_view(), name='payslip_export_pdf'),
    path('api/payroll/payslips/export/zip/', PayslipBulkZipView.as_view(), name='payslips_export_zip'),
    path('api/', api.urls),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )

    