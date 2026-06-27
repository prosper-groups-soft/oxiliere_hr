import logging
from uuid   import UUID
from io     import BytesIO
import pandas as pd
from injector    import inject
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from ninja.files import UploadedFile
from typing import Optional
from ninja import File, Query
from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_put,
    http_patch,
    http_delete,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
)

from oxutils.permissions.perms import ScopePermission

from hr.banking.services import BankingService, BankFileGenerator
from hr.banking.models   import Bank, BankAccount
from hr.banking.schemas  import (
    BankCreateIn, 
    BankUpdateIn, 
    BankOut,
    BankSeedIn,
    BankSeedInstitution,
    BankSeedOut,
    BankAccountCreateIn, 
    BankAccountUpdateIn, 
    BankAccountOut,
    BankAccountFilterIn,
    BankAccountHistoryOut
)
from hr.services.cache_helpers import cache_api_response


logger = logging.getLogger(__name__)


@api_controller("/banking", tags=["Banking"])
class BankingController(ControllerBase):
    """ Manages banking institutions and employee payment accounts. """

    @inject
    def __init__(self, banking_service: BankingService):
        self.banking_service = banking_service

    # --- Bank Management ---

    @http_post("/banks", response={201: BankOut}, permissions=[ScopePermission('banking:w')])
    def create_bank(self, payload: BankCreateIn):
        """ Registers a new financial institution in the system. """
        try:
            bank = self.banking_service.create_bank(payload.model_dump(exclude_none=True))
            logger.info(f"Bank created: {bank.code}")
            return 201, bank
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_get("/banks", response=PaginatedResponseSchema[BankOut], permissions=[ScopePermission('banking:r')])
    @paginate(PageNumberPaginationExtra)
    @cache_api_response(timeout=60*60*24, key_prefix="bank_list", user_specific=False)
    def list_banks(self):
        """ Lists all registered banks and mobile money providers. """
        return Bank.objects.order_by('name')

    @http_get("/banks/seed/list", response=list[BankSeedInstitution], permissions=[ScopePermission('banking:r')])
    def list_seedable_banks(self):
        """ Returns the list of institutions available for seeding from the fixture. """
        return self.banking_service.list_seedable_banks()

    @http_post("/banks/seed", response=BankSeedOut, permissions=[ScopePermission('banking:w')])
    def seed_default_banks(self, payload: BankSeedIn = None):
        """ Bulk-creates default DRC financial institutions. Accepts optional list of codes to seed only selected ones. """
        codes = payload.codes if payload and payload.codes else None
        result = self.banking_service.seed_default_banks(codes=codes)
        if result['created_count'] > 0:
            from hr.services.cache_helpers import invalidate_cache_prefix
            invalidate_cache_prefix("bank_list")
        logger.info(f"Seed banks: {result['created_count']} created, {result['skipped_count']} skipped")
        return result

    @http_put("/banks/{bank_id}", response=BankOut, permissions=[ScopePermission('banking:w')])
    def update_bank(self, bank_id: UUID, payload: BankUpdateIn):
        """ Updates metadata for a specific bank institution. """
        try:
            return self.banking_service.update_bank(
                bank_id, 
                payload.model_dump(exclude_unset=True)
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_delete("/banks/{bank_id}", response={204: None}, permissions=[ScopePermission('banking:w')])
    def delete_bank(self, bank_id: UUID):
        """ Removes a bank provider from the system. """
        try:
            self.banking_service.delete_bank(bank_id)
            logger.info(f"Bank deleted: {bank_id}")
            return 204, None
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_post("/banks/{bank_id}/upload-logo", response={200: BankOut}, permissions=[ScopePermission('banking:w')])
    def upload_bank_logo(self, bank_id: UUID, logo: UploadedFile = File(...)):
        """ Uploads a logo image for a financial institution. """
        bank = get_object_or_404(Bank, id=bank_id)
        bank.logo = logo
        bank.full_clean()
        bank.save()
        logger.info(f"Bank logo uploaded: {bank_id}")
        return bank

    # --- Bank Account Management ---

    @http_post("/accounts", response={201: BankAccountOut}, permissions=[ScopePermission('banking:w')])
    def create_account(self, payload: BankAccountCreateIn):
        """ Registers a new payment account for an employee. """
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

    @http_get("/accounts", response=PaginatedResponseSchema[BankAccountOut], permissions=[ScopePermission('banking:r')])
    @paginate(PageNumberPaginationExtra)
    def list_accounts(
        self,
        filters: BankAccountFilterIn = Query(...),
        ordering: Optional[str] = Query(None, description="Sort by: account_name, -account_name, created_at, -created_at, employee_name, -employee_name")
    ):
        """ Lists employee bank accounts with optional filtering and sorting. """
        qs = BankAccount.objects.select_related('bank', 'employee').all()
        qs = filters.filter(qs).distinct()
        qs = filters.apply_ordering(qs, ordering)
        return qs

    @http_put("/accounts/{account_id}", response=BankAccountOut, permissions=[ScopePermission('banking:u')])
    def update_account(self, account_id: UUID, payload: BankAccountUpdateIn):
        """ Modifies existing bank account settings. (Full replacement) """
        try:
            return self.banking_service.update_account(
                account_id=account_id,
                data=payload.model_dump(exclude_unset=True),
                actor=self.context.request.user
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_patch("/accounts/{account_id}", response=BankAccountOut, permissions=[ScopePermission('banking:u')])
    def partial_update_account(self, account_id: UUID, payload: BankAccountUpdateIn):
        """ Partial update of bank account settings — only sends changed fields. """
        try:
            return self.banking_service.update_account(
                account_id=account_id,
                data=payload.model_dump(exclude_unset=True),
                actor=self.context.request.user
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    # --- Account Actions ---

    @http_post("/accounts/{account_id}/verify", response=BankAccountOut, permissions=[ScopePermission('banking:a')])
    def verify_account(self, account_id: UUID):
        """ Formally validates an account for payroll use. """
        return self.banking_service.verify_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/unverify", response=BankAccountOut, permissions=[ScopePermission('banking:a')])
    def unverify_account(self, account_id: UUID):
        """ Revokes the validation status of a payment account. """
        return self.banking_service.unverify_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/primary", response=BankAccountOut, permissions=[ScopePermission('banking:u')])
    def set_primary_account(self, account_id: UUID):
        """ Sets an account as the main salary destination for its currency. """
        return self.banking_service.set_primary_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/activate", response=BankAccountOut, permissions=[ScopePermission('banking:u')])
    def activate_account(self, account_id: UUID):
        """ Restores a suspended account to active status. """
        return self.banking_service.activate_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_post("/accounts/{account_id}/deactivate", response=BankAccountOut, permissions=[ScopePermission('banking:u')])
    def deactivate_account(self, account_id: UUID):
        """ Suspends an account from payroll distribution. """
        return self.banking_service.deactivate_account(
            account_id, 
            actor=self.context.request.user
        )

    @http_delete("/accounts/{account_id}", response={204: None}, permissions=[ScopePermission('banking:d')])
    def delete_account(self, account_id: UUID):
        """ Formally removes a bank account record. """
        self.banking_service.delete_account(
            account_id, 
            actor=self.context.request.user
        )
        return 204, None

    @http_get("/accounts/{account_id}/history", response=PaginatedResponseSchema[BankAccountHistoryOut])
    @paginate(PageNumberPaginationExtra)
    @cache_api_response(timeout=60*10, key_prefix="account_history", user_specific=False)
    def account_history(self, account_id: UUID):
        """ Retrieves the full audit trail for a specific account. """
        account = get_object_or_404(BankAccount, id=account_id)
        return account.history.select_related('changed_by').all()

    @http_get("/export/payroll-file", permissions=[ScopePermission('banking:r')])
    def download_payroll_file(self, run_id: str, bank_code: str = None, currency: str = "CDF"):
        """ Generates and downloads the Excel transfer file for a specific payroll run. """
        data = BankFileGenerator.generate_listing(run_id, bank_code, currency)
        df = pd.DataFrame(data)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Virements')
            worksheet = writer.sheets['Virements']
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)
        
        output.seek(0)

        filename = f"virements_{currency}_{bank_code or 'ALL'}_{timezone.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"
        
        logger.info(f"Payroll file generated for run {run_id}") 
        return response

