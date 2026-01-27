from decimal import Decimal
from django.core.management.base import BaseCommand
from hr.payroll.services.calculations.taxes import TaxCalculationService
from hr.payroll.services.calculations.contributions import SocialContributionService
from hr.payroll.services.calculations.legal_allowances import LegalAllowanceService


class Command(BaseCommand):
    help = 'Tests the DRC payroll calculation logic with sample data.'

    def add_arguments(self, parser):
        parser.add_argument('--base', type=float, default=195000.0, help='Monthly base salary (default: 195,000 FC)')
        parser.add_argument('--days', type=int, default=26, help='Worked days (default: 26)')
        parser.add_argument('--children', type=int, default=1, help='Number of children (default: 1)')
        parser.add_argument('--housing', type=float, default=50000.0, help='Housing allowance (default: 50,000 FC)')
        parser.add_argument('--ceiling', type=float, default=None, help='CNSS Ceiling amount (optional)')
        parser.add_argument('--paid-leaves', type=float, default=0.0, help='Number of paid leave days')
        parser.add_argument('--unpaid-leaves', type=float, default=0.0, help='Number of unpaid leave days')
        parser.add_argument('--currency', type=str, default='CDF', help='Contract currency (CDF or USD)')

    def handle(self, *args, **options):
        base_salary = Decimal(str(options['base']))
        worked_days = options['days']
        child_count = options['children']
        ceiling = Decimal(str(options['ceiling'])) if options['ceiling'] else None
        paid_leave_days = Decimal(str(options['paid_leaves']))
        unpaid_leave_days = Decimal(str(options['unpaid_leaves']))
        currency = options['currency']
        
        # --- Currency Conversion Simulation ---
        rate = Decimal('2850.0') # Simulation rate matching default config
        if currency == 'USD':
             base_salary_cdf = (base_salary * rate).quantize(Decimal('0.01'))
             self.stdout.write(self.style.WARNING(f"Converting Contract: {base_salary} USD -> {base_salary_cdf} CDF (Rate: {rate})"))
             base_salary = base_salary_cdf
        
        # Pro-rating logic (simplified for test)
        days_in_month = Decimal('26.0')
        deduction = (base_salary / days_in_month) * unpaid_leave_days
        base_salary_after_absences = base_salary - deduction
        
        # Gross = Base + Overtime (0)
        gross_salary = base_salary_after_absences

        self.stdout.write(self.style.SUCCESS(f"--- DRC Payroll Calculation Test (Leave Integration) ---"))
        self.stdout.write(f"Parameters: Base={base_salary} FC, Days={worked_days}, Paid Leaves={paid_leave_days}, Unpaid Leaves={unpaid_leave_days}")
        if unpaid_leave_days > 0:
            self.stdout.write(self.style.WARNING(f"  - Deduction for unpaid absences: -{deduction:.2f} FC"))
            self.stdout.write(f"  - Gross after absences: {gross_salary:.2f} FC")
        self.stdout.write("-" * 40)

        # 1. Social Contributions (CNSS, ONEM, INPP)
        social = SocialContributionService.calculate_contributions(
            gross_amount=gross_salary, 
            base_salary=base_salary_after_absences, 
            company_size=10
        )
        
        cnss_employee = Decimal('0.00')
        self.stdout.write(self.style.MIGRATE_HEADING("1. Déductions Sociales (Travailleur):"))
        for detail in social['details']:
            amt = detail['employee_amount']
            if detail['type'] == 'CNSS' and ceiling and gross_salary > ceiling:
                amt = (ceiling * Decimal('0.05')).quantize(Decimal('0.01'))
                self.stdout.write(f"  - {detail['label']} (Ceiling Applied: {ceiling}): {amt} FC")
            else:
                if detail['employee_amount'] > 0:
                    self.stdout.write(f"  - {detail['label']}: {detail['employee_amount']} FC")
            
            if detail['type'] == 'CNSS':
                cnss_employee = amt

        self.stdout.write(self.style.MIGRATE_HEADING("Charges Patronales (Non déduites du net):"))
        for detail in social['details']:
            if detail['employer_amount'] > 0:
                self.stdout.write(f"  - {detail['label']}: {detail['employer_amount']} FC")

        # 2. IPR Tax
        taxable_base = gross_salary - cnss_employee
        ipr = TaxCalculationService.calculate_progressive_tax(taxable_base)
        self.stdout.write(self.style.MIGRATE_HEADING("2. Impôts (IPR):"))
        self.stdout.write(f"  - Base imposable: {taxable_base} FC")
        self.stdout.write(f"  - IPR calculé: {ipr} FC")

        # 3. Legal Allowances
        # Paid leaves are counted as worked days for allowances
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=worked_days + int(paid_leave_days), 
            child_count=child_count, 
            gross_salary=gross_salary,
            base_salary=base_salary_after_absences
        )
        self.stdout.write(self.style.MIGRATE_HEADING("3. Avantages Légaux:"))
        self.stdout.write(f"  - Allocations Familiales: {allowances['family_allowance']} FC")
        self.stdout.write(f"  - Indemnité de Transport: {allowances['transport_allowance']} FC")
        self.stdout.write(f"  - Contre-valeur Logement: {allowances['housing_allowance']} FC")

        # 4. Final Net
        net = (gross_salary + allowances['total_allowances']) - (cnss_employee + ipr)

        self.stdout.write("-" * 40)
        self.stdout.write(self.style.SUCCESS(f"SALAIRE NET FINAL: {net:.2f} FC"))
        self.stdout.write("-" * 40)
        self.stdout.write(self.style.NOTICE("Note: Ce calcul intègre les congés payés et les déductions pour absences injustifiées."))

