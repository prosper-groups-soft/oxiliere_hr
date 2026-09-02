import os
import re
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
    from bs4 import BeautifulSoup
    from bcc_rates import OXRBankSource
    from bcc_rates.base import SourceValue
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
    def _sync_from_sources(cls, force: bool = False) -> bool:
        """
        Attempts to fetch live rates and persist them.

        1. BCC (primary) — parses the SSR HTML of bcc.cd (Next.js).
        2. OXR (fallback, if OXR_API_KEY is set) — converts to CDF base too.
        """
        # 1. BCC
        try:
            rates = cls._fetch_bcc_rates()
            if rates:
                return cls._persist_rates(rates, 'BCC')
            if not force:
                return False
        except Exception:
            if not force:
                return False

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
    def _fetch_bcc_rates(cls) -> list:
        """
        Récupère les taux de change depuis le site bcc.cd.

        Le site est une app Next.js (SSR) : les taux sont rendus dans des
        <span> avec les classes CSS :
          - devise : `font-semibold uppercase tracking-wide text-[#005CA9]`
          - valeur : `font-bold tabular-nums text-[#005CA9]`

        L'ancien sélecteur `div.changes_row` du package bcc_rates ne
        correspond plus à cette structure (retournait 0 taux).
        """
        url = 'https://www.bcc.cd/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/125.0.0.0 Safari/537.36'
        }
        kwargs_ct = {'headers': headers, 'timeout': 20}
        if os.environ.get('OXI_BCC_SSL_VERIFY', '').lower() in ('0', 'false', 'off', 'no'):
            kwargs_ct['verify'] = False

        resp = requests.get(url, **kwargs_ct)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        rates: list = []
        # Couples devise/taux : <span>DEV/DEV</span><span>Taux</span>
        for pair in soup.select(r'span.font-semibold.uppercase.tracking-wide.text-\[\#005CA9\]'):
            label = pair.get_text(strip=True).upper()
            if '/' not in label:
                continue
            base, quote = label.split('/', 1)
            # Le span suivant contient le taux (ex: « 2 265,5600 »)
            value_el = pair.find_next_sibling('span')
            if value_el is None:
                continue
            raw = value_el.get_text(strip=True)
            raw = re.sub(r'[^0-9.,]', '', raw).replace(' ', '').replace(',', '.')
            try:
                amount = Decimal(raw)
            except Exception:
                continue
            if amount <= 0:
                continue
            # La devise est au format BASE/QUOTE — la valeur = 1 BASE en QUOTE
            if quote.upper() == 'CDF':
                rates.append(SourceValue(currency=base, amount=amount))
            else:
                rates.append(SourceValue(currency=quote, amount=amount))
        return rates

    @classmethod
    def _ensure_live_state(cls, force: bool = False) -> bool:
        """
        Ensures a live CurrencyState exists and is reasonably fresh.

        If the latest state is missing or older than the TTL, triggers a sync
        from BCC (with OXR fallback when enabled). A short-lived cache prevents
        stampeding the external source.
        """
        if not OXUTILS_CURRENCY_AVAILABLE:
            return False

        # Forced refresh (bouton « Recharger ») : toujours re-synchroniser.
        if force:
            ok = cls._sync_from_sources(force=True)
            if ok:
                cache.set(cls.SYNC_CACHE_KEY, True, cls.SYNC_CACHE_TTL)
            else:
                cache.delete(cls.SYNC_CACHE_KEY)
            return ok

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
    def get_live_rate(cls, currency_code: str, force: bool = False) -> Decimal | None:
        """ Tries to get the latest rate from oxutils.currency (BCC-synced). """
        if not OXUTILS_CURRENCY_AVAILABLE:
            return None
        try:
            if not cls._ensure_live_state(force=force):
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
    def get_exchange_rate_with_source_forced(cls, from_currency: str, to_currency: str) -> tuple[Decimal, str]:
        """
        Résolution du taux avec synchronisation BCC forcée
        (bouton « Recharger » de l'UI kickoff).

        Retourne (rate, source) exactement comme get_exchange_rate_with_source,
        mais force toujours un re-fetch BCC + persistance avant la lecture.
        """
        if from_currency == to_currency:
            return Decimal('1.0'), 'config'

        if from_currency == Currency.USD and to_currency == Currency.CDF:
            live = cls.get_live_rate("USD", force=True)
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

