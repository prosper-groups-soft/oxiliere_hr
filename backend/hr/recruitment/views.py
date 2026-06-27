from oxutils.pdf import WeasyTemplateView
from django.shortcuts import get_object_or_404
from django.utils.translation import (
    gettext_lazy as _, 
    override as force_lang
)
from hr.recruitment.models import Candidate, Application
from django.http import Http404


class CandidateEvaluationPDFView(WeasyTemplateView):
    template_name = 'recruitment/pdf/candidate_evaluation.html'
    pdf_attachment = True

    def get_pdf_filename(self):
        candidate = get_object_or_404(Candidate, pk=self.kwargs['pk'])
        return f"evaluation_{candidate.last_name}_{candidate.middle_name}_{candidate.first_name}.pdf"

    def get_context_data(self, **kwargs):
        with force_lang('fr'):
            context = super().get_context_data(**kwargs)
            candidate = get_object_or_404(Candidate, pk=self.kwargs['pk'])

            app_id = self.request.GET.get('application_id')
            if not app_id:
                raise Http404(_("application_id is required"))

            applications = Application.objects.filter(
                candidate=candidate, id=app_id
            )

            applications = applications.select_related(
                'job_offer', 'target_position'
            ).prefetch_related(
                'interviews__interviewer'
            ).order_by('-applied_at')

            # Build enriched application data with evaluation criteria from the job offer
            applications_data = []
            for app in applications:
                # Extract evaluation criteria from the job offer for this target position
                criteria = []
                template = app.job_offer.evaluation_template or {}
                pos_id_str = str(app.target_position_id) if app.target_position_id else None
                if pos_id_str and pos_id_str in template:
                    for item in template[pos_id_str]:
                        weight = item.get('weight', 1)
                        if weight <= 0:
                            continue
                        name = item.get('name', 'Critère')
                        source = item.get('source', '')
                        score = app.scores.get(name) if app.scores else None
                        criteria.append({
                            'name': name,
                            'weight': weight,
                            'source': source,
                            'score': score,
                        })

                applications_data.append({
                    'app': app,
                    'criteria': criteria,
                })

            context['candidate'] = candidate
            context['applications_data'] = applications_data

            if candidate.profile_photo:
                context['photo_url'] = self.request.build_absolute_uri(candidate.profile_photo.url)
            else:
                context['photo_url'] = None

            context['title'] = _("Évaluation Candidat")
            return context

