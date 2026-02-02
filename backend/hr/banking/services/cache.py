import logging
from django.core.cache import cache
from django_redis      import get_redis_connection
from hr.banking.models import Bank, BankAccount
# Cache integration
from hr.services.cache_helpers import (
    invalidate_cache_prefix,
    generate_cache_key,
    CacheKeys
)

        
logger = logging.getLogger(__name__)


class BankingCacheService:
    """ Performance optimization and data caching for the banking module. """
    
    @staticmethod
    def get_bank(bank_id):
        """ Retrieves a cached bank instance. """
        cache_key = generate_cache_key("hr:banking:bank", bank_id)
        bank = cache.get(cache_key)
        
        if bank is None:
            bank = Bank.objects.filter(id=bank_id).first()
            if bank:
                cache.set(cache_key, bank, timeout=60*60*24*7)
        
        return bank
    
    @staticmethod
    def get_bank_by_code(bank_code):
        """ Retrieves a bank by its unique identifier code. """
        cache_key = generate_cache_key("hr:banking:bank_code", bank_code)
        bank = cache.get(cache_key)
        
        if bank is None:
            bank = Bank.objects.filter(code=bank_code).first()
            if bank:
                cache.set(cache_key, bank, timeout=60*60*24*7)
        
        return bank
    
    @staticmethod
    def get_all_banks():
        """ Provides an optimized list of all registered banks. """
        cache_key = "hr:banking:all_banks"
        banks = cache.get(cache_key)
        
        if banks is None:
            banks = list(Bank.objects.all().order_by('name'))
            cache.set(cache_key, banks, timeout=60*60*24*7)
        
        return banks
    
    @staticmethod
    def get_bank_account(account_id):
        """ Retrieves cached details for a specific bank account. """
        cache_key = generate_cache_key("hr:banking:account", account_id)
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(id=account_id).first()
            if account:
                cache.set(cache_key, account, timeout=60*60)
        
        return account
    
    @staticmethod
    def get_bank_account_by_iban(iban):
        """ Finds a bank account using its International Bank Account Number. """
        cache_key = CacheKeys.bank_account_by_iban(iban)
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(iban=iban).first()
            if account:
                cache.set(cache_key, account, timeout=60*60)
        
        return account
    
    @staticmethod
    def get_active_bank_accounts():
        """ Lists all verified and active bank accounts. """
        cache_key = CacheKeys.active_bank_accounts()
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                is_active=True,
                verified=True
            ).order_by('bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)
        
        return accounts
    
    @staticmethod
    def get_employee_bank_accounts(employee):
        """ Retrieves all payment accounts associated with an employee. """
        cache_key = generate_cache_key("hr:banking:employee_accounts", employee.id)
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                employee=employee
            ).order_by('-is_primary', 'bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)
        
        return accounts
    
    @staticmethod
    def get_employee_primary_account(employee):
        """ Identifies the primary salary account for an employee. """
        cache_key = generate_cache_key("hr:banking:primary_account", employee.id)
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(
                employee=employee,
                is_primary=True,
                is_active=True
            ).first()
            
            if account:
                cache.set(cache_key, account, timeout=60*60)
        
        return account
    
    @staticmethod
    def get_accounts_by_currency(currency_code):
        """ Lists all active accounts filtered by currency. """
        cache_key = generate_cache_key("hr:banking:accounts_currency", currency_code)
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                currency=currency_code,
                is_active=True
            ).order_by('bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)
        
        return accounts
    
    @staticmethod
    def clear_account_cache(account):
        """ Invalidates all cached records for a bank account and its owner. """
        if isinstance(account, BankAccount):
            account_id = account.id
            iban = account.iban
            employee_id = account.employee.id if account.employee else None
        else:
            account_id = account
            iban = None
            employee_id = None
        
        cache.delete(generate_cache_key("hr:banking:account", account_id))
        
        if iban:
            cache.delete(CacheKeys.bank_account_by_iban(iban))
        
        cache.delete(CacheKeys.active_bank_accounts())
        
        if employee_id:
            cache.delete(generate_cache_key("hr:banking:employee_accounts", employee_id))
            cache.delete(generate_cache_key("hr:banking:primary_account", employee_id))
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """ Clears specific API response caches. """
        invalidate_cache_prefix(prefix)
    
    @staticmethod
    def clear_all_banking_cache():
        """ Performs a global cleanup of all banking-related cache data. """
        redis_conn = get_redis_connection("default")
        
        pattern = "*hr:banking*"
        keys = list(redis_conn.scan_iter(match=pattern, count=100))
        if keys:
            redis_conn.delete(*keys)
        
        BankingCacheService.clear_api_cache_prefix("bank_list")
        BankingCacheService.clear_api_cache_prefix("account_list")
        BankingCacheService.clear_api_cache_prefix("account_history")
        
        logger.info("All banking cache cleared.")

