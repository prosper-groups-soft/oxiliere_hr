import os
from datetime          import timedelta
from decimal           import Decimal
from unittest.mock     import patch
from uuid              import uuid4

from django.conf       import settings
from django.core.cache import cache
from django.utils      import timezone

from hr.enums          import Currency
from hr.payroll.models import PayrollConfiguration


try:
    import requests
    from bcc_rates import BCCBankSource, OXRBankSource
    from oxutils.currency.models import CurrencyState
    from oxutils.currency.utils import update_rates
    from oxutils.currency.schemas import CurrencyStateDetailSchema
    OXUTILS_CURRENCY_AVAILABLE = True
except ImportError:
    OXUTILS_CURRENCY_AVAILABLE = False


class ExchangeRateService:
    """ 
        Handles currency conversions using oxutils.currency live rates, 
        with fallback to manual config. 
    """

    # Default fallback rate
    DEFAULT_USD_TO_CDF = Decimal('2300.0')

    # How fresh a synced CurrencyState must be to be reused (6h).
    # Sync attempts are also throttled with the same window.
    SYNC_CACHE_TTL = 6 * 60 * 60  # seconds

    # Cache key guarding the "last sync attempt" so we don't hammer BCC.
    SYNC_CACHE_KEY = 'oxutils.currency.last_sync_attempt'

    @classmethod
    def _latest_state(cls):
        """ Returns the latest CurrencyState or None. """
        try:
            return CurrencyState.objects.latest()
        except Exception:
            return None

    @classmethod
    def _state_is_fresh(cls, state) -> bool:
        if state is None or state.created_at is None:
            return False
        return state.created_at >= timezone.now() - timedelta(seconds=cls.SYNC_CACHE_TTL)

    @classmethod
    def _persist_rates(cls, rates, source: str) -> bool:
        """
        Persists a set of SourceValue rates (1 unit of currency = X CDF)
        into a new CurrencyState via oxutils' update_rates().
        """
        try:
            state = CurrencyStateDetailSchema(
                id=uuid4(),
                source=source,
                currencies={r.currency: float(r.amount) for r in rates},
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            update_rates(state)
            return True
        except Exception:
            return False

    @classmethod
    def _sync_from_sources(cls) -> bool:
        """
        Attempts to fetch live rates and persist them.

        1. BCC (primary) — converts rates into '1 currency = X CDF' form.
        2. OXR (fallback, if OXR_API_KEY is set) — converts to CDF base too.
        """
        # 1. BCC
        try:
            bcc = BCCBankSource()
            if os.environ.get('OXI_BCC_SSL_VERIFY', '').lower() in ('0', 'false', 'off', 'no'):
                # Dev workaround: bcc.cd presents a certificate that requests
                # cannot verify. Disable verification ONLY for BCC fetches.
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                real_get = requests.get

                def _insecure_get(*args, **kwargs):
                    kwargs['verify'] = False
                    return real_get(*args, **kwargs)

                with patch('requests.get', new=_insecure_get):
                    rates = bcc.sync(cache=True)
            else:
                rates = bcc.sync(cache=True)
            return cls._persist_rates(rates, 'BCC')
        except Exception:
            pass

        # 2. OXR fallback
        if not getattr(settings, 'OXI_BCC_FALLBACK_ON_OXR', False):
            return False
        try:
            oxr = OXRBankSource()
            rates = oxr.sync(cache=True)
            oxr.set_cdf_as_base()
            rates = oxr.get_values()
            return cls._persist_rates(rates, 'OXR')
        except Exception:
            return False

    @classmethod
    def _ensure_live_state(cls) -> bool:
        """
        Ensures a live CurrencyState exists and is reasonably fresh.

        If the latest state is missing or older than the TTL, triggers a sync
        from BCC (with OXR fallback when enabled). A short-lived cache prevents
        stampeding the external source.
        """
        if not OXUTILS_CURRENCY_AVAILABLE:
            return False

        # Fast path: a fresh state exists → nothing to do.
        if cls._state_is_fresh(cls._latest_state()):
            cache.set(cls.SYNC_CACHE_KEY, True, cls.SYNC_CACHE_TTL)
            return True

        # Throttle: if we already tried very recently, don't retry yet.
        if cache.get(cls.SYNC_CACHE_KEY) is not None:
            return False

        # Remember the attempt (success or failure) before hitting the network.
        cache.set(cls.SYNC_CACHE_KEY, True, cls.SYNC_CACHE_TTL)
        return cls._sync_from_sources()

    @classmethod
    def get_live_rate(cls, currency_code: str) -> Decimal | None:
        """ Tries to get the latest rate from oxutils.currency (BCC-synced). """
        if not OXUTILS_CURRENCY_AVAILABLE:
            return None
        try:
            if not cls._ensure_live_state():
                return None
            state = cls._latest_state()
            rate = state.currencies.filter(code=currency_code.upper()).first()
            return Decimal(str(rate.rate)) if rate else None
        except Exception:
            return None

    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Decimal:
        """ Retrieves the active exchange rate between two currencies. """
        if from_currency == to_currency:
            return Decimal('1.0')

        if from_currency == Currency.USD and to_currency == Currency.CDF:
            # 1. Try live rate from oxutils.currency (BCC-synced)
            live = cls.get_live_rate("USD")
            if live is not None:
                return live

            # 2. Fallback: manual rate from payroll configuration
            config = PayrollConfiguration.objects.first()
            if config and config.exchange_rate_usd_cdf:
                return config.exchange_rate_usd_cdf

            # 3. Hardcoded default
            return cls.DEFAULT_USD_TO_CDF

        if from_currency == Currency.CDF and to_currency == Currency.USD:
            return Decimal('1.0') / cls.get_exchange_rate(Currency.USD, Currency.CDF)

        raise ValueError(f"Conversion from {from_currency} to {to_currency} not supported yet.")

    @classmethod
    def get_exchange_rate_with_source(cls, from_currency: str, to_currency: str) -> tuple[Decimal, str]:
        """
        Returns (rate, source) in a single resolution so the caller never
        calls get_live_rate twice (and never sees inconsistent rate/source).

        Source is one of: 'bcc' (live BCC/oxutils), 'config' (manual), 'default'.
        """
        if from_currency == to_currency:
            return Decimal('1.0'), 'config'

        if from_currency == Currency.USD and to_currency == Currency.CDF:
            live = cls.get_live_rate("USD")
            if live is not None:
                return live, 'bcc'

            config = PayrollConfiguration.objects.first()
            if config and config.exchange_rate_usd_cdf:
                return config.exchange_rate_usd_cdf, 'config'

            return cls.DEFAULT_USD_TO_CDF, 'default'

        raise ValueError(f"Conversion from {from_currency} to {to_currency} not supported yet.")

    @classmethod
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """ Converts an amount between currencies using the active exchange rate. """
        if amount is None:
            return Decimal('0.00')
        rate = cls.get_exchange_rate(from_currency, to_currency)
        return (amount * rate).quantize(Decimal('0.01'))
