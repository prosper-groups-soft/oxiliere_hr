"""
Banking caching services.

Handles caching of bank and account-related queries.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.banking.models import Bank, BankAccount


class BankingCacheService:
    """Cache operations for banking module."""
    
    @staticmethod
    def get_bank(bank_id):
        """Get bank by ID (stable - long cache)."""
        cache_key = generate_cache_key("hr:banking:bank", bank_id)
        bank = cache.get(cache_key)
        
        if bank is None:
            bank = Bank.objects.filter(id=bank_id).first()
            
            if bank:
                cache.set(cache_key, bank, timeout=60*60*24*7)  # 7 days
        
        return bank
    
    @staticmethod
    def get_bank_by_code(bank_code):
        """Get bank by code (stable - long cache)."""
        cache_key = generate_cache_key("hr:banking:bank_code", bank_code)
        bank = cache.get(cache_key)
        
        if bank is None:
            bank = Bank.objects.filter(
                code=bank_code
            ).first()
            
            if bank:
                cache.set(cache_key, bank, timeout=60*60*24*7)  # 7 days
        
        return bank
    
    @staticmethod
    def get_all_banks():
        """Get all banks (stable - long cache)."""
        cache_key = "hr:banking:all_banks"
        banks = cache.get(cache_key)
        
        if banks is None:
            banks = list(Bank.objects.all().order_by('name'))
            cache.set(cache_key, banks, timeout=60*60*24*7)  # 7 days
        
        return banks
    
    @staticmethod
    def get_bank_account(account_id):
        """Get bank account by ID."""
        cache_key = generate_cache_key("hr:banking:account", account_id)
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(
                id=account_id
            ).first()
            
            if account:
                cache.set(cache_key, account, timeout=60*60)  # 1h
        
        return account
    
    @staticmethod
    def get_bank_account_by_iban(iban):
        """
        Get bank account by IBAN (frequently used).
        
        Args:
            iban: IBAN string
        
        Returns:
            BankAccount instance or None
        """
        cache_key = CacheKeys.bank_account_by_iban(iban)
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(
                iban=iban
            ).first()
            
            if account:
                cache.set(cache_key, account, timeout=60*60)  # 1h
        
        return account
    
    @staticmethod
    def get_active_bank_accounts():
        """
        Get all active bank accounts (short cache due to changes).
        
        Returns:
            List of active BankAccount instances
        """
        cache_key = CacheKeys.active_bank_accounts()
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                status='active'
            ).order_by('bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)  # 1h
        
        return accounts
    
    @staticmethod
    def get_employee_bank_accounts(employee):
        """
        Get all bank accounts for an employee.
        
        Args:
            employee: Employee instance
        
        Returns:
            List of BankAccount instances
        """
        cache_key = generate_cache_key(
            "hr:banking:employee_accounts", employee.id
        )
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                employee=employee
            ).order_by('-is_primary', 'bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)  # 1h
        
        return accounts
    
    @staticmethod
    def get_employee_primary_account(employee):
        """Get primary bank account for employee."""
        cache_key = generate_cache_key(
            "hr:banking:primary_account", employee.id
        )
        account = cache.get(cache_key)
        
        if account is None:
            account = BankAccount.objects.filter(
                employee=employee,
                is_primary=True,
                status='active'
            ).first()
            
            if account:
                cache.set(cache_key, account, timeout=60*60)  # 1h
        
        return account
    
    @staticmethod
    def get_accounts_by_currency(currency_code):
        """Get all active accounts for a currency."""
        cache_key = generate_cache_key(
            "hr:banking:accounts_currency", currency_code
        )
        accounts = cache.get(cache_key)
        
        if accounts is None:
            accounts = list(BankAccount.objects.filter(
                currency=currency_code,
                status='active'
            ).order_by('bank__name'))
            
            cache.set(cache_key, accounts, timeout=60*60)  # 1h
        
        return accounts
    
    @staticmethod
    def clear_account_cache(account):
        """Clear cache for a bank account."""
        if isinstance(account, BankAccount):
            account_id = account.id
            iban = account.iban
            employee_id = account.employee.id if account.employee else None
        else:
            account_id = account
            iban = None
            employee_id = None
        
        # Clear specific caches
        cache.delete(generate_cache_key("hr:banking:account", account_id))
        
        if iban:
            cache.delete(CacheKeys.bank_account_by_iban(iban))
        
        # Clear list caches
        cache.delete(CacheKeys.active_bank_accounts())
        
        if employee_id:
            cache.delete(generate_cache_key(
                "hr:banking:employee_accounts", employee_id
            ))
            cache.delete(generate_cache_key(
                "hr:banking:primary_account", employee_id
            ))
    
    @staticmethod
    def clear_all_banking_cache():
        """Clear all banking cache."""
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        pattern = "*hr:banking*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
