from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.enums import CalculationMode


class PayrollCalculatorService:
    """ Mathematical utility for payroll calculations. """

    @staticmethod
    def calculate_adjustment_value(mode: str, base_value: Decimal, config_amount: Decimal = None, config_percentage: Decimal = None) -> Decimal:
        """ Calculates an adjustment amount based on its calculation mode. """
        if mode == CalculationMode.FIXED:
            return config_amount or Decimal('0.00')
        
        if mode == CalculationMode.PERCENTAGE:
            percentage = config_percentage or Decimal('0.00')
            return (base_value * (percentage / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return Decimal('0.00')

    @staticmethod
    def calculate_overtime_pay(hourly_rate: Decimal, std_hours: float, hol_hours: float, weekend_hours: float = 0, multipliers: dict = None) -> Decimal:
        """ Calculates total overtime pay including statutory multipliers. """
        pay = Decimal('0.00')
        std_hours_dec = Decimal(str(std_hours))
        hol_hours_dec = Decimal(str(hol_hours))
        weekend_hours_dec = Decimal(str(weekend_hours))
        if multipliers is None:
            multipliers = {}
        
        # 1. Standard Overtime (Weekdays)
        if std_hours_dec > 0:
            m130 = multipliers.get('first_period', Decimal('1.30'))
            m160 = multipliers.get('subsequent', Decimal('1.60'))
            
            # DRC Rule: 130% for the first 6 hours, 160% beyond
            if std_hours_dec <= 6:
                pay += (std_hours_dec * hourly_rate * m130)
            else:
                pay += (Decimal('6.0') * hourly_rate * m130)
                pay += ((std_hours_dec - Decimal('6.0')) * hourly_rate * m160)
        
        # 2. Weekend Overtime (Sunday = 200% in DRC)
        if weekend_hours_dec > 0:
            m200 = multipliers.get('weekend', Decimal('2.00'))
            pay += (weekend_hours_dec * hourly_rate * m200)
        
        # 3. Holiday Overtime
        if hol_hours_dec > 0:
            m200 = multipliers.get('holiday', Decimal('2.00'))
            pay += (hol_hours_dec * hourly_rate * m200)
            
        return pay.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def calculate_hourly_rate(monthly_base_salary: Decimal, hours_per_month: float = 195.0) -> Decimal:
        """ Converts a monthly base salary to an hourly rate. """
        return (monthly_base_salary / Decimal(str(hours_per_month))).quantize(Decimal('0.01'))

