import io
import zipfile
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import View
from django.template.loader import render_to_string
from django.utils.translation import override as force_lang
from weasyprint import HTML
from oxutils.pdf import WeasyTemplateView
from hr.payroll.models import EmployeePayslip
from hr.payroll.services.payroll_run import PayrollRunService


# Valeurs fictives employeur — à remplacer par PayrollConfiguration / modèle société
FICTIVE_EMPLOYER = {
    "raison_sociale": "OXILIERE SARL",
    "adresse": "Av. du 30 juin, 124 — Haut-Katanga / Lubumbashi",
    "rccm": "CD/KIN/RCCM/14-B-1234",
    "id_nat": "01-234-N12345A",
    "niu": "A0701234B",
    "cnss_employeur": "CNSS 010-1234567-8",
}


class PayslipPDFView(WeasyTemplateView):
    template_name = "payroll/pdf/payslip.html"
    pdf_attachment = True

    def get_pdf_filename(self):
        p = self.get_payslip()
        emp = p.contract.employee
        return f"bulletin_{emp.matricule}_{p.payroll_run.start_date:%Y-%m}.pdf"

    def get_context_data(self, **kwargs):
        with force_lang("fr"):
            ctx = super().get_context_data(**kwargs)
            p = self.get_payslip()
            svc = PayrollRunService()
            detail = svc.get_payslip_detail(p.id)
            ctx["payslip"] = p
            ctx["detail"] = detail
            ctx["employer"] = FICTIVE_EMPLOYER
            ctx["lines"] = list(p.lines.all())
            try:
                ctx["employer_charges"] = list(p.employer_charges.all())
            except Exception:
                ctx["employer_charges"] = []
            # photo salarié pour WeasyPrint (comme EmployeeProfilePDFView)
            emp = p.contract.employee
            if getattr(emp, "profile_photo", None) and emp.profile_photo:
                try:
                    ctx["photo_url"] = self.request.build_absolute_uri(emp.profile_photo.url)
                except Exception:
                    ctx["photo_url"] = None
            else:
                ctx["photo_url"] = None
            # ponytail: employer fictif — remplacer par vrai modèle société quand dispo
            ctx["title"] = "Bulletin de paie"
            return ctx

    def get_payslip(self):
        return get_object_or_404(
            EmployeePayslip.objects.select_related("contract", "contract__employee", "payroll_run").prefetch_related("lines", "employer_charges"),
            pk=self.kwargs["pk"],
        )


class PayslipBulkZipView(View):
    """ZIP de bulletins. Priorité: ?ids=id1,id2,… sinon ?run_id=…, sinon tous. Plafond 200."""

    def get(self, request):
        ids_param = request.GET.get("ids")
        run_id = request.GET.get("run_id")
        qs = EmployeePayslip.objects.select_related("contract", "contract__employee", "payroll_run").prefetch_related("lines", "employer_charges")
        if ids_param:
            raw = [x.strip() for x in ids_param.split(",") if x.strip()]
            # ponytail: UUID validation légère — on laisse le filtre id__in ignorer les invalides
            qs = qs.filter(id__in=raw) if raw else qs.none()
        elif run_id:
            qs = qs.filter(payroll_run_id=run_id)
        qs = qs[:200]  # plafond
        if not qs:
            raise Http404("Aucun bulletin trouvé")

        svc = PayrollRunService()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in qs:
                detail = svc.get_payslip_detail(p.id)
                emp = p.contract.employee
                try:
                    photo_url = request.build_absolute_uri(emp.profile_photo.url) if getattr(emp, "profile_photo", None) and emp.profile_photo else None
                except Exception:
                    photo_url = None
                html = render_to_string("payroll/pdf/payslip.html", {
                    "payslip": p,
                    "detail": detail,
                    "employer": FICTIVE_EMPLOYER,
                    "photo_url": photo_url,
                    "lines": list(p.lines.all()),
                    "employer_charges": list(p.employer_charges.all()) if hasattr(p, "employer_charges") else [],
                    "title": "Bulletin de paie",
                })
                pdf_bytes = HTML(string=html, base_url=request.build_absolute_uri("/")).write_pdf()
                emp = p.contract.employee
                name = f"bulletin_{emp.matricule}_{p.payroll_run.start_date:%Y-%m}.pdf"
                zf.writestr(name, pdf_bytes)
        buf.seek(0)
        resp = HttpResponse(buf.read(), content_type="application/zip")
        resp["Content-Disposition"] = 'attachment; filename="bulletins.zip"'
        return resp
