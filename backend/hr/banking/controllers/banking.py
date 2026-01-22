from oxutils.pagination.cursor import CursorPagination
import logging
from typing import List
from uuid import UUID

from injector import inject
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_put,
    http_delete,
    ControllerBase,
)

from django.http import HttpResponse
from io import BytesIO
import pandas as pd
from oxutils.pagination.cursor import CursorPagination

from hr.banking.services import BankingService
from hr.banking.models import Bank, BankAccount
from hr.banking.schemas import (
    BankCreateIn, 
    BankUpdateIn, 
    BankOut,
    BankAccountCreateIn, 
    BankAccountUpdateIn, 
    BankAccountOut,
    BankAccountHistoryOut
)


logger = logging.getLogger(__name__)


@api_controller("/banking", tags=["Banking"])
class BankingController(ControllerBase):
    """
    Controller for managing Banks and Bank Accounts.
    Follows project architectural patterns using dependency injection.
    """

    @inject
    def __init__(self, banking_service: BankingService):
        self.banking_service = banking_service

    # --- Bank Management ---

    @http_post("/banks", response={201: BankOut})
    def create_bank(self, payload: BankCreateIn):
        """Register a new bank."""
        try:
            bank = self.banking_service.create_bank(payload.model_dump(exclude_none=True))
            logger.info(f"Bank created via API: {bank.code}")
            return 201, bank
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_get("/banks", response=List[BankOut])
    @paginate(CursorPagination)
    def list_banks(self):
        """List all banks."""
        return Bank.objects.order_by('name')

    @http_put("/banks/{bank_id}", response=BankOut)
    def update_bank(self, bank_id: UUID, payload: BankUpdateIn):
        """Update bank details."""
        try:
            return self.banking_service.update_bank(
                bank_id, 
                payload.model_dump(exclude_unchanged=True)
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_delete("/banks/{bank_id}", response={204: None})
    def delete_bank(self, bank_id: UUID):
        """Delete a bank."""
        self.banking_service.delete_bank(bank_id)
        return 204, None

    # --- Bank Account Management ---

    @http_post("/accounts", response={201: BankAccountOut})
    def create_account(self, payload: BankAccountCreateIn):
        """Create a bank account for an employee."""
        try:
            data = payload.model_dump()
            employee_id = data.pop('employee_id')
            bank_id = data.pop('bank_id')
            
            account = self.banking_service.create_bank_account(
                employee_id=employee_id,
                bank_id=bank_id,
                account_data=data,
                actor=self.context.request.user
            )
            return 201, account
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_get("/accounts", response=List[BankAccountOut])
    @paginate(CursorPagination)
    def list_accounts(self, employee_id: UUID = None):
        """
        List bank accounts. 
        Optional: Filter by employee_id.
        """
        qs = BankAccount.objects.select_related('bank', 'employee').all()
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs

    @http_put("/accounts/{account_id}", response=BankAccountOut)
    def update_account(self, account_id: UUID, payload: BankAccountUpdateIn):
        """Update bank account details."""
        try:
            return self.banking_service.update_account(
                account_id=account_id,
                data=payload.model_dump(exclude_unchanged=True),
                actor=self.context.request.user
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    # --- Account Actions ---

    @http_post("/accounts/{account_id}/verify", response=BankAccountOut)
    def verify_account(self, account_id: UUID):
        return self.banking_service.verify_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/unverify", response=BankAccountOut)
    def unverify_account(self, account_id: UUID):
        return self.banking_service.unverify_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/primary", response=BankAccountOut)
    def set_primary_account(self, account_id: UUID):
        return self.banking_service.set_primary_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/activate", response=BankAccountOut)
    def activate_account(self, account_id: UUID):
        return self.banking_service.activate_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/deactivate", response=BankAccountOut)
    def deactivate_account(self, account_id: UUID):
        return self.banking_service.deactivate_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_delete("/accounts/{account_id}", response={204: None})
    def delete_account(self, account_id: UUID):
        self.banking_service.delete_account(
            account_id, 
            actor=self.context.request.user
        )
        return 204, None

    @http_get("/accounts/{account_id}/history", response=List[BankAccountHistoryOut])
    @paginate(CursorPagination)
    def account_history(self, account_id: UUID):
        """Retrieve audit history for a specific account."""
        account = get_object_or_404(BankAccount, id=account_id)
        return account.history.select_related('changed_by').all().order_by('-created_at')

    @http_get("/export/payroll-file")
    def download_payroll_file(self, bank_code: str = None, currency: str = "CDF"):
        # 1. Get data from service
        data = self.banking_service.generate_payroll_export(bank_code, currency)
        df = pd.DataFrame(data)

        # 2. Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Virements')
        
        output.seek(0)

        # 3. Prepare HTTP response
        filename = f"virements_{currency}_{bank_code or 'ALL'}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        
        logger.info(f"Payroll file generated for bank {bank_code} and currency {currency}") 
               
        return response

