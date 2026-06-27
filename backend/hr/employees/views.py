from oxutils.pdf import WeasyTemplateView
from hr.employees.models import Employee
from hr.employees.services.query import EmployeeQueryService
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _, override as force_lang
from django.shortcuts import get_object_or_404


class EmployeeProfilePDFView(WeasyTemplateView):
    template_name = 'employees/pdf/profile.html'
    pdf_attachment = True

    def get_pdf_filename(self):
        employee = self.get_employee()
        return f"profil_{employee.matricule}_{employee.last_name}.pdf"

    def get_context_data(self, **kwargs):
        # Force French translation context for the PDF
        with force_lang('fr'):
            context = super().get_context_data(**kwargs)
            employee = self.get_employee()
            
            # Get optimized instance with all prefetches
            query_service = EmployeeQueryService()
            full_employee = query_service.get_employee_by_id(employee.id)        
            context['employee'] = full_employee
            
            # Handle Photo URL for WeasyPrint
            if full_employee.profile_photo:
                context['photo_url'] = self.request.build_absolute_uri(full_employee.profile_photo.url)
            else:
                context['photo_url'] = None

            context['title'] = _("Fiche Employé")
            return context

    def get_employee(self):
        return get_object_or_404(Employee, pk=self.kwargs['pk'])

