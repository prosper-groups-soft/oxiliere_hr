import logging
from django.dispatch import receiver
from django.db       import transaction
from django.db.models.signals import post_save, post_delete
from .models   import Bank, BankAccount
from .services import BankingCacheService


logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Bank)
@receiver([post_save, post_delete], sender=BankAccount)
def invalidate_banking_cache(sender, instance, **kwargs):
    """ Automatically clears banking caches when institutions or accounts are modified. """
    
    def clear_cache():
        if sender is Bank:
            BankingCacheService.clear_all_banking_cache()
            logger.debug(f"Cache invalidated for Bank {instance.id}")
        
        elif sender is BankAccount:
            BankingCacheService.clear_account_cache(instance)
            logger.debug(f"Cache invalidated for BankAccount {instance.id}")
    
    transaction.on_commit(clear_cache)

