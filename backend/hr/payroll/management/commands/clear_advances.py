from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import tenant_context
from safedelete.config import HARD_DELETE

from core.models import Tenant
from hr.payroll.models import SalaryAdvance


class Command(BaseCommand):
    help = 'Supprime TOUTES les avances sur salaire en dur (HARD_DELETE) — développement uniquement.'

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
            help='Confirme la suppression de toutes les avances sur salaire',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('ATTENTION : cette commande supprime TOUTES les avances sur salaire.')
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

        self.stdout.write('Suppression des avances sur salaire en cours...')

        total_deleted = 0
        for tenant in tenants:
            self.stdout.write(f'>> Traitement du tenant : {tenant.schema_name}')

            with tenant_context(tenant):
                with transaction.atomic():
                    # La suppression en dur cascade vers les remboursements
                    # (RepaymentRecord) et les configurations de déduction
                    # (AdvanceDeductionConfiguration) via on_delete=CASCADE.
                    advances = SalaryAdvance.objects.all_with_deleted()
                    count = advances.count()
                    if count > 0:
                        advances.delete(force_policy=HARD_DELETE)
                        total_deleted += count
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  OK : {count} avance(s) supprimée(s) '
                                f'(incluant soft-deleted, avec cascade)'
                            )
                        )
                    else:
                        self.stdout.write('  (aucune avance à supprimer)')

        self.stdout.write(
            self.style.SUCCESS(f'Terminé. {total_deleted} avance(s) supprimée(s) au total.')
        )
