from decimal           import Decimal
from hr.enums          import Currency
from hr.payroll.models import PayrollConfiguration
from hr.payroll.enums  import ExchangeRateSource

try:
    from bcc_rates import BCCBankSource
    BCC_RATES_AVAILABLE = True
except ImportError:
    BCC_RATES_AVAILABLE = False


class ExchangeRateService:
    """
    Service responsible for handling currency conversions for Payroll.
    Specifically targets the USD -> CDF conversion common in DRC.
    """
    
    # Default fallback rate (example market rate)
    DEFAULT_USD_TO_CDF = Decimal('2100.0')

    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Decimal:
        """
        Retrieves the active exchange rate.
        For now, this returns a static/configured rate. 
        Ideally, this would fetch from a DailyRate model or external API.
        """
        if from_currency == to_currency:
            return Decimal('1.0')
        
        if from_currency == Currency.USD and to_currency == Currency.CDF:
            config = PayrollConfiguration.objects.filter(is_active=True).first()
            if config:
                # Check for BCC Source
                if config.exchange_rate_source == ExchangeRateSource.BCC and BCC_RATES_AVAILABLE:
                    try:
                        bcc = BCCBankSource()
                        # Assuming sync() returns list, or get_value returns rate object with amount
                        rate_obj = bcc.get_value("USD")
                        if rate_obj and rate_obj.amount:
                            return Decimal(str(rate_obj.amount))
                    except Exception as e:
                        # Log error and fallback to manual
                        print(f"Error fetching BCC rates: {e}. Falling back to manual configuration.")
                
                # Manual or Fallback
                if config.exchange_rate_usd_cdf:
                    return config.exchange_rate_usd_cdf
            return cls.DEFAULT_USD_TO_CDF
            
        if from_currency == Currency.CDF and to_currency == Currency.USD:
            return Decimal('1.0') / cls.DEFAULT_USD_TO_CDF
            
        raise ValueError(f"Conversion from {from_currency} to {to_currency} not supported yet.")

    @classmethod
    def convert(cls, amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
        """
        Converts an amount from one currency to another using the active rate.
        """
        if amount is None:
            return Decimal('0.00')
            
        rate = cls.get_exchange_rate(from_currency, to_currency)
        return (amount * rate).quantize(Decimal('0.01'))

