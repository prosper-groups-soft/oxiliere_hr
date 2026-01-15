import traceback
from uuid import uuid4
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from hr.employees.models import Employee
from hr.employees.services import EmployeeProfileService, EmployeeQueryService
from hr.enums import GenderStatus, MaritalStatus, CountryCode


User = get_user_model()


class Command(BaseCommand):
    help = "Generates a test environment: User (UUID) + Employee + Service Linking."

    def add_arguments(self, parser):
        parser.add_argument(
            '--username', 
            type=str, 
            default='test_employee', 
            help='Username of the worker'
        )
        parser.add_argument(
            '--email', 
            type=str, 
            help='Optional: Specific email (defaults to username@oxiliere.com)'
        )
        parser.add_argument(
            '--admin', 
            action='store_true', 
            help='Give superuser and staff permissions to the user'
        )

    def handle(self, *args, **options):
        # 1. Dynamic data initialization
        username = options['username'].lower().strip()
        
        # If email is not provided, generate it from the username
        email = options['email']
        if not email:
            email = f"{username}@oxiliere.com"
        else:
            email = email.lower().strip()
        
        # Manual service injection
        self.profile_service = EmployeeProfileService(query_service=EmployeeQueryService())

        self.stdout.write(self.style.MIGRATE_LABEL(f"--- Starting setup for {email} ---"))

        try:
            with transaction.atomic():
                # Step A: Create/Retrieve the Django User
                user = self._get_or_create_user(email, username, options['admin'])
                
                # Step B: Create/Retrieve the Employee profile via Service
                employee = self._get_or_onboard_employee(email, username)
                
                # Step C: Link both accounts via Service
                self._link_account(employee, user)

                # Final summary
                self._print_summary(employee, user)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Setup failed: {str(e)}"))
            self.stdout.write(traceback.format_exc())

    def _get_or_create_user(self, email, username, is_admin):
        """Handles user account creation with UUID management."""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': "Test",
                'last_name': username.upper(),
                'is_active': True,
                'is_staff': True,
                'is_superuser': is_admin,
                'oxi_id': uuid4(),
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✔ User created (UUID: {user.id})"))
        else:
            # Update admin status if necessary even if the user exists
            if is_admin and not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
            self.stdout.write(self.style.WARNING(f"ℹ User already exists (UUID: {user.id})"))
        
        return user

    def _get_or_onboard_employee(self, email, username):
        """Handles employee profile creation via the business service."""
        employee = Employee.objects.filter(email=email).first()
        
        if employee:
            self.stdout.write(self.style.WARNING(f"ℹ Employee already exists (ID: {employee.matricule})"))
            return employee

        onboarding_data = {
            "first_name": username.title(),
            "middle_name": "TEST",
            "last_name": "WORKER",
            "email": email,
            "gender": GenderStatus.MALE,
            "marital_status": MaritalStatus.SINGLE,
            "birthdate": "2000-05-15",
            "nationality": CountryCode.DRC,
            "phone": "+243812345678",
            "hire_date": timezone.now().date(),
        }
        
        # Use service to ensure matricule and initial status are correctly generated
        employee = self.profile_service.onboard_employee(data=onboarding_data)
        self.stdout.write(self.style.SUCCESS(f"✔ Employee onboarded (ID: {employee.matricule})"))
        return employee

    def _link_account(self, employee, user):
        """Uses the service to link the employee to the user."""
        # The service will enable can_connect=True and link the OneToOneField
        self.profile_service.assign_user_account(
            employee_id=employee.id,
            user_id=user.id,
            actor=None
        )
        self.stdout.write(self.style.SUCCESS(f"✔ Employee and User linked successfully"))

    def _print_summary(self, employee, user):
        """Displays a visual block for easier testing."""
        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS(f"  SUCCESSFULLY CONFIGURED"))
        self.stdout.write(f"  Employee ID : {employee.matricule}")
        self.stdout.write(f"  Login       : {user.email}")
        self.stdout.write(f"  Password    : password123")
        self.stdout.write("=" * 50)

