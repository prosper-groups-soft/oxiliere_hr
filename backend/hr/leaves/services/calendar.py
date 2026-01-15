import logging
from decimal import Decimal
from datetime import timedelta, date
from hr.enums import CountryCode
from hr.leaves.models import PublicHoliday, CompanyClosing

logger = logging.getLogger(__name__)


class CalendarService:

    @staticmethod
    def is_working_day(day: date, country_code: str = CountryCode.DRC) -> bool:
        """
        Checks if a given date is a working day by verifying:
        - weekends
        - public holidays
        - company closing periods
        """
        # Weekend
        if day.isoweekday() >= 6:
            return False

        # Public holiday
        if PublicHoliday.objects.filter(
            country_code=country_code,
            date=day
        ).exists():
            return False

        # Company closing
        if CompanyClosing.objects.filter(
            start_date__lte=day,
            end_date__gte=day
        ).exists():
            return False

        return True

    @staticmethod
    def get_working_days(start_date: date, end_date: date, country_code: str = CountryCode.DRC) -> Decimal:
        """
        Calculates the total number of working days between two dates, excluding 
        weekends, public holidays, and company closing periods.
        """
        if start_date > end_date:
            return Decimal("0")

        # 1. Retrieve all public holidays for the period in a SINGLE query
        holidays = set(
            PublicHoliday.objects.filter(
                country_code=country_code,
                date__range=(start_date, end_date)
            ).values_list("date", flat=True)
        )

        # 2. Retrieve company closings (handling overlaps)
        closings = CompanyClosing.objects.filter(
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        closing_dates = set()
        for c in closings:
            # Only calculate dates that fall within our start/end range
            curr = max(c.start_date, start_date)
            limit = min(c.end_date, end_date)
            while curr <= limit:
                closing_dates.add(curr)
                curr += timedelta(days=1)

        # 3. Calculate working days in memory
        total_working_days = 0
        current = start_date
        while current <= end_date:
            # Priority 1: Weekend (ISO 6=Saturday, 7=Sunday)
            if current.isoweekday() < 6:
                # Priority 2: Not a public holiday AND not a company closing
                if current not in holidays and current not in closing_dates:
                    total_working_days += 1
            current += timedelta(days=1)

        return Decimal(total_working_days)

    @staticmethod
    def get_working_days_per_year(start: date, end: date, country_code: str = CountryCode.DRC) -> dict[int, Decimal]:
        """
        Returns a dictionary {year: working_days} between start and end.
        Optimized by using get_working_days for each year and existing cached data.
        """
        days_per_year = {}
        for year in range(start.year, end.year + 1):
            year_start = max(start, date(year, 1, 1))
            year_end = min(end, date(year, 12, 31))
            days_per_year[year] = CalendarService.get_working_days(year_start, year_end, country_code)
        return days_per_year

