from decimal import Decimal
from hr.payroll.enums import CalculationMode


class PayrollCalculatorService:
    """
    Service responsible for core mathematical payroll calculations.
    Does not interact with the database directly.
    """

    @staticmethod
    def calculate_adjustment_value(mode: str, base_value: Decimal, 
                                 config_amount: Decimal = None, 
                                 config_percentage: Decimal = None) -> Decimal:
        """
        Calculates the actual value of an adjustment based on its mode (Fixed or Percentage).
        
        Args:
            mode: CalculationMode choice (FIXED or PERCENTAGE).
            base_value: The reference amount (usually base salary) for percentage calculations.
            config_amount: The fixed amount defined in settings.
            config_percentage: The percentage value defined in settings (0-100).
        """
        if mode == CalculationMode.FIXED:
            return config_amount or Decimal('0.00')
        
        if mode == CalculationMode.PERCENTAGE:
            percentage = config_percentage or Decimal('0.00')
            return (base_value * (percentage / Decimal('100'))).quantize(Decimal('0.01'))
        
        return Decimal('0.00')

    @staticmethod
    def calculate_hourly_gross(hourly_rate: Decimal, hours_worked: float, 
                              overtime_hours: float, multiplier: Decimal) -> Decimal:
        """
        Calculates gross pay for hourly contracts including overtime.
        """
        regular_pay = hourly_rate * Decimal(str(hours_worked))
        overtime_pay = (hourly_rate * multiplier) * Decimal(str(overtime_hours))
        return (regular_pay + overtime_pay).quantize(Decimal('0.01'))

