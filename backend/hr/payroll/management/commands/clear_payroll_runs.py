from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import tenant_context
from safedelete.models import HARD_DELETE

from core.models import Tenant
from hr.payroll.models import PayrollRun
from hr.services.cache_helpers import invalidate_cache_prefix


class Command(BaseCommand):
    help = 'Supprime TOUS les runs de paie en dur (HARD_DELETE) — développement uniquement.'

    # Caches API des runs (voir controllers/payslips.py). Sans purge, la liste
    # (TTL 24h) continuerait de renvoyer les runs supprimés et l'onglet
    # dynamique fantôme réapparaîtrait au rechargement du frontend.
    RUN_API_CACHE_PREFIXES = (
        'payroll_runs_list',
        'payroll_run_detail',
        'payroll_run_payslips',
        'payroll_run_summary',
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default=None,
            help='Nom du schéma du tenant à traiter (tous si omis)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme la suppression de tous les runs de paie',
        )

    def _invalidate_run_caches(self):
        for prefix in self.RUN_API_CACHE_PREFIXES:
            invalidate_cache_prefix(prefix)

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('ATTENTION : cette commande supprime TOUS les runs de paie.')
            )
            self.stdout.write('Pour confirmer, utilisez : --confirm')
            return

        tenant_filter = options.get('tenant')
        tenants = Tenant.objects.all()
        if tenant_filter:
            tenants = tenants.filter(schema_name=tenant_filter)

        if not tenants.exists():
            self.stdout.write(self.style.ERROR('Aucun tenant trouvé.'))
            return

        self.stdout.write('Suppression des runs de paie en cours...')

        total_deleted = 0
        for tenant in tenants:
            self.stdout.write(f'>> Traitement du tenant : {tenant.schema_name}')

            with tenant_context(tenant):
                with transaction.atomic():
                    # La suppression en dur cascade vers les bulletins
                    # (EmployeePayslip, PayslipLine, EmployerCharge, RepaymentRecord,
                    #  WorkedDaysRecord) via les on_delete=CASCADE déclarés sur les modèles.
                    runs = PayrollRun.objects.all_with_deleted()
                    count = runs.count()
                    if count > 0:
                        runs.delete(force_policy=HARD_DELETE)
                        total_deleted += count
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  OK : {count} run(s) supprimé(s) '
                                f'(incluant soft-deleted, avec cascade vers les bulletins)'
                            )
                        )
                    else:
                        self.stdout.write('  (aucun run a supprimer)')

                # Purge systématique des caches API (même si aucun run : le cache
                # de liste a pu persister un run supprimé par un autre chemin).
                self._invalidate_run_caches()

        self.stdout.write(
            self.style.SUCCESS(f'Terminé. {total_deleted} run(s) supprimé(s) au total.')
        )

