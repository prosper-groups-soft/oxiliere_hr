from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .api import api
from hr.employees.views import EmployeeProfilePDFView
from hr.recruitment.views import CandidateEvaluationPDFView


urlpatterns = [
    path('api/employees/<uuid:pk>/export/', EmployeeProfilePDFView.as_view(), name='employee_export_pdf'),
    path('api/recruitment/candidates/<uuid:pk>/export/', CandidateEvaluationPDFView.as_view(), name='candidate_evaluation_pdf'),
    path('api/', api.urls),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )

    