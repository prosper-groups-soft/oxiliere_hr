from decimal           import Decimal
from hr.enums          import Currency
from hr.payroll.models import PayrollConfiguration

try:
    from oxutils.currency.models import CurrencyState
    OXUTILS_CURRENCY_AVAILABLE = True
except ImportError:
    OXUTILS_CURRENCY_AVAILABLE = False


class ExchangeRateService:
    """ Handles currency conversions using oxutils.currency live rates, with fallback to manual config. """

    # Default fallback rate
    DEFAULT_USD_TO_CDF = Decimal('2950.0')

    @classmethod
    def get_live_rate(cls, currency_code: str) -> Decimal | None:
        """ Tries to get the latest rate from oxutils.currency (BCC-synced). """
        if not OXUTILS_CURRENCY_AVAILABLE:
            return None
        try:
            state = CurrencyState.objects.latest()
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
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """ Converts an amount between currencies using the active exchange rate. """
        if amount is None:
            return Decimal('0.00')
        rate = cls.get_exchange_rate(from_currency, to_currency)
        return (amount * rate).quantize(Decimal('0.01'))
