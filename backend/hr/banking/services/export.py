import pandas as pd
from typing import List, Dict
from django.utils import timezone
from hr.banking.models import BankAccount
from hr.payroll.models import EmployeePayslip, PayrollRun


class BankFileGenerator:
    """
    Generates bank transfer files (Excel/CSV) for a specific payroll run.
    """

    @classmethod
    def generate_listing(cls, run_id: str, bank_code: str = None, currency: str = "CDF") -> List[Dict]:
        """
        Creates a list of transfers by matching Payslip Net Amounts with Employee Bank Accounts.
        """
        run = PayrollRun.objects.get(id=run_id)
        
        # 1. Fetch valid payslips for this run
        payslips = EmployeePayslip.objects.filter(
            payroll_run=run,
            net_amount__gt=0
        ).select_related('contract__employee')

        # 2. Fetch active bank accounts for these employees
        employee_ids = [p.contract.employee.id for p in payslips]
        accounts = BankAccount.objects.filter(
            employee_id__in=employee_ids,
            is_active=True,
            verified=True,
            currency=currency
        ).select_related('bank', 'employee')
        
        if bank_code:
            accounts = accounts.filter(bank__code=bank_code)

        # Map employee_id -> account (prioritize primary if multiple?)
        # Simple map: last one wins or we filter for specific bank.
        # Ideally, we should filter for "is_primary=True" first.
        primary_accounts = accounts.filter(is_primary=True)
        account_map = {acc.employee_id: acc for acc in primary_accounts}
        
        # Fallback to any account if no primary found (optional logic)
        remaining_accounts = accounts.exclude(id__in=[a.id for a in primary_accounts])
        for acc in remaining_accounts:
            if acc.employee_id not in account_map:
                account_map[acc.employee_id] = acc

        export_data = []
        
        for slip in payslips:
            emp = slip.contract.employee
            account = account_map.get(emp.id)
            
            if not account:
                # Employee has no valid bank account for this currency
                continue
                
            export_data.append({
                "MATRICULE": emp.matricule,
                "NOM_COMPLET": f"{emp.last_name} {emp.first_name} {emp.middle_name or ''}".strip(),
                "BANQUE": account.bank.name,
                "CODE_BANQUE": account.bank.code,
                "COMPTE": account.account_number,
                "DEVISE": currency,
                "MONTANT": slip.net_amount,
                "MOTIF": f"SALAIRE {run.start_date.strftime('%m/%Y')}",
                "DATE_VALEUR": timezone.now().date()
            })
            
        return export_data

    @classmethod
    def to_excel(cls, data: List[Dict]) -> pd.DataFrame:
        """Converts the list to a DataFrame ready for Excel."""
        return pd.DataFrame(data)
