from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import tenant_context
from safedelete.models import HARD_DELETE
from hr.employees.models import (
    Employee,  EmployeeDocument, EmployeeEducation,
    EmployeeAddress, EmergencyContact, EmployeeChild
)


class Command(BaseCommand):
    help = 'Supprime TOUTES les données en dur (DANGEREUX - développement uniquement)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme la suppression de toutes les données',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('⚠️  ATTENTION: Cette commande va supprimer TOUTES les données!')
            )
            self.stdout.write('Pour confirmer, utilisez: --confirm')
            return

        self.stdout.write('🗑️  Suppression de toutes les données en cours...')

        # Récupérer tous les tenants
        from core.models import Tenant
        tenants = Tenant.objects.all()
        
        for tenant in tenants:
            self.stdout.write(f'🏢  Traitement du tenant: {tenant.schema_name}')
            
            with tenant_context(tenant):
                with transaction.atomic():
                    # Suppression dans l'ordre inverse des dépendances
                    models_to_clear = [
                        (EmployeeEducation, "formations des employés"),
                        (EmployeeChild, "enfants des employés"),
                        (EmergencyContact, "contacts d'urgence"),
                        (EmployeeDocument, "documents des employés"),
                        (EmployeeAddress, "adresses des employés"),
                        (Employee, "employés"),
                    ]

                    for model, description in models_to_clear:
                        # Compter tous les objets (y compris soft-deleted)
                        all_objects = model.objects.all_with_deleted()
                        count = all_objects.count()
                        if count > 0:
                            all_objects.delete(force_policy=HARD_DELETE)
                            self.stdout.write(f'  ✅ {count} {description} supprimé(s) (incluant soft-deleted)')
                        else:
                            self.stdout.write(f'  ℹ️  Aucune {description} à supprimer')

        self.stdout.write(
            self.style.SUCCESS('🎉 Toutes les données ont été supprimées avec succès!')
        )
        self.stdout.write(
            self.style.WARNING('⚠️  N\'oubliez pas de faire: python manage.py migrate')
        )
