from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from django_tenants.utils import tenant_context
from safedelete.models import HARD_DELETE
from core.models import Tenant
from hr.attendance.models import EmploymentScheme


class Command(BaseCommand):
    help = (
        "Trouve et supprime les affectations (EmploymentScheme) en double "
        "(même employee_id). Pour chaque employé, seule la plus récente est conservée."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default=None,
            help='Nom du schéma du tenant à traiter (tous si omis)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simule le nettoyage sans supprimer (mode lecture seule)',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirme la suppression des doublons',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']
        tenant_filter = options.get('tenant')

        tenants = Tenant.objects.all()
        if tenant_filter:
            tenants = tenants.filter(schema_name=tenant_filter)

        if not tenants.exists():
            self.stdout.write(self.style.ERROR("Aucun tenant trouvé."))
            return

        total_deleted = 0

        for tenant in tenants:
            self.stdout.write(f"\n{'=' * 60}")
            self.stdout.write(f"** Tenant : {tenant.schema_name} ({tenant.name})")
            self.stdout.write(f"{'=' * 60}")

            with tenant_context(tenant):
                # Trouver les employee_id qui apparaissent plusieurs fois
                duplicates = (
                    EmploymentScheme.objects.all_with_deleted()
                    .values('employee_id')
                    .annotate(cnt=Count('id'))
                    .filter(cnt__gt=1)
                )

                duplicate_count = duplicates.count()
                if duplicate_count == 0:
                    self.stdout.write(self.style.SUCCESS("  ++ Aucun doublon trouve."))
                    continue

                self.stdout.write(
                    self.style.WARNING(f"  !! {duplicate_count} employe(s) avec des affectations en double.")
                )

                for dup in duplicates:
                    employee_id = dup['employee_id']
                    schemes = EmploymentScheme.objects.all_with_deleted().filter(
                        employee_id=employee_id
                    ).order_by('-created_at', '-id')

                    self.stdout.write(f"\n  Employe ID : {employee_id}")
                    self.stdout.write(f"     {schemes.count()} affectations trouvees :")

                    for i, scheme in enumerate(schemes):
                        self.stdout.write(
                            f"       [{i + 1}] ID={scheme.id} | "
                            f"valid_from={scheme.valid_from} | "
                            f"valid_until={scheme.valid_until} | "
                            f"policy={scheme.policy.name} | "
                            f"created_at={scheme.created_at.isoformat() if hasattr(scheme, 'created_at') and scheme.created_at else 'N/A'}"
                        )

                    # Garder la première (la plus récente), supprimer les autres
                    keep = schemes.first()
                    to_delete = list(schemes.exclude(id=keep.id))
                    self.stdout.write(f"     ->  Conserver : ID={keep.id}")
                    self.stdout.write(f"     Supprimer : {[str(s.id) for s in to_delete]}")

                    if not dry_run and confirm:
                        with transaction.atomic():
                            for scheme in to_delete:
                                scheme.delete(force_policy=HARD_DELETE)
                        self.stdout.write(self.style.SUCCESS(f"     ++ {len(to_delete)} doublon(s) supprime(s)."))
                    else:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(f"     (dry-run) {len(to_delete)} doublon(s) serait supprime(s)."))
                        else:
                            self.stdout.write(self.style.WARNING(f"     Ignore (pas de --confirm)."))
                    total_deleted += len(to_delete)

        self.stdout.write(f"\n{'=' * 60}")
        if dry_run:
            self.stdout.write(self.style.WARNING(f"DRY-RUN termine. {total_deleted} doublon(s) auraient ete supprimes."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Nettoyage termine. {total_deleted} doublon(s) supprime(s)."))
