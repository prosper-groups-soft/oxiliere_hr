from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import tenant_context
from safedelete.models import HARD_DELETE
from hr.recruitment.models import Application, Candidate


class Command(BaseCommand):
    help = 'Supprime TOUS les candidats et candidatures en dur (développement uniquement)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme la suppression de toutes les candidatures',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('ATTENTION: Cette commande va supprimer TOUS les candidats et candidatures!')
            )
            self.stdout.write('Pour confirmer, utilisez: --confirm')
            return

        self.stdout.write('Suppression des candidatures et candidats en cours...')

        # Recuperer tous les tenants
        from core.models import Tenant
        tenants = Tenant.objects.all()

        for tenant in tenants:
            self.stdout.write(f'Traitement du tenant: {tenant.schema_name}')

            with tenant_context(tenant):
                with transaction.atomic():
                    models_to_clear = [
                        (Application, "candidatures"),
                        (Candidate, "candidats"),
                    ]

                    for model, description in models_to_clear:
                        all_objects = model.objects.all_with_deleted()
                        count = all_objects.count()
                        if count > 0:
                            all_objects.delete(force_policy=HARD_DELETE)
                            self.stdout.write(f'  {count} {description} supprime(s) (incluant soft-deleted)')
                        else:
                            self.stdout.write(f'  Aucune {description} a supprimer')

        self.stdout.write(
            self.style.SUCCESS('Tous les candidats et candidatures ont ete supprimes!')
        )
