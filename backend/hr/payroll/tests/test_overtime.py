"""
Tests unitaires — HS_NUIT (×1.5) + multiplicateurs overtime.

Usage: uv run python backend/hr/payroll/tests/test_overtime.py
"""

import unittest
from decimal import Decimal


# --- Minimal standalone Overtime calculator ---

def calculate_overtime_pay(
    hourly_rate: Decimal,
    std_hours: float,
    hol_hours: float,
    weekend_hours: float = 0,
    night_hours: float = 0,
    multipliers: dict | None = None,
) -> Decimal:
    pay = Decimal("0.00")
    std = Decimal(str(std_hours))
    hol = Decimal(str(hol_hours))
    wknd = Decimal(str(weekend_hours))
    night = Decimal(str(night_hours))
    if multipliers is None:
        multipliers = {}

    # Standard (130% then 160%)
    if std > 0:
        m130 = multipliers.get("first_period", Decimal("1.30"))
        m160 = multipliers.get("subsequent", Decimal("1.60"))
        if std <= 6:
            pay += std * hourly_rate * m130
        else:
            pay += Decimal("6.0") * hourly_rate * m130
            pay += (std - Decimal("6.0")) * hourly_rate * m160

    # Weekend (200%)
    if wknd > 0:
        m200 = multipliers.get("weekend", Decimal("2.00"))
        pay += wknd * hourly_rate * m200

    # Holiday (200%)
    if hol > 0:
        m200 = multipliers.get("holiday", Decimal("2.00"))
        pay += hol * hourly_rate * m200

    # Night (150%) — Correction 0.6
    if night > 0:
        m150 = multipliers.get("night", Decimal("1.50"))
        pay += night * hourly_rate * m150

    return pay.quantize(Decimal("0.01"))


class OvertimeNightTests(unittest.TestCase):
    """Tests HS_NUIT (×1.5) + tous les paliers OT."""

    def setUp(self):
        self.rate = Decimal("5000.00")  # 5 000 FC/h

    def test_no_overtime(self):
        pay = calculate_overtime_pay(self.rate, 0, 0)
        self.assertEqual(pay, Decimal("0.00"))

    def test_night_2_hours(self):
        """2h de nuit → 2 × 5000 × 1.5 = 15 000."""
        pay = calculate_overtime_pay(self.rate, 0, 0, night_hours=2)
        self.assertEqual(pay, Decimal("15000.00"))

    def test_night_5_hours(self):
        """5h de nuit → 5 × 5000 × 1.5 = 37 500."""
        pay = calculate_overtime_pay(self.rate, 0, 0, night_hours=5)
        self.assertEqual(pay, Decimal("37500.00"))

    def test_night_multiplier_configurable(self):
        """Multiplicateur nuit override via config."""
        pay = calculate_overtime_pay(
            self.rate, 0, 0, night_hours=4,
            multipliers={"night": Decimal("1.60")},
        )
        self.assertEqual(pay, Decimal("32000.00"))  # 4 × 5000 × 1.6

    def test_standard_first_6_hours(self):
        """3h standard → ×1.3."""
        pay = calculate_overtime_pay(self.rate, 3, 0)
        self.assertEqual(pay, Decimal("19500.00"))  # 3 × 5000 × 1.3

    def test_standard_beyond_6_hours(self):
        """8h standard → 6×1.3 + 2×1.6."""
        pay = calculate_overtime_pay(self.rate, 8, 0)
        # 6 × 5000 × 1.3 = 39000 + 2 × 5000 × 1.6 = 16000 = 55000
        self.assertEqual(pay, Decimal("55000.00"))

    def test_weekend_200pct(self):
        pay = calculate_overtime_pay(self.rate, 0, 0, weekend_hours=4)
        self.assertEqual(pay, Decimal("40000.00"))  # 4 × 5000 × 2.0

    def test_holiday_200pct(self):
        pay = calculate_overtime_pay(self.rate, 0, 5)
        self.assertEqual(pay, Decimal("50000.00"))  # 5 × 5000 × 2.0

    def test_combined_standard_night(self):
        """3h standard + 2h nuit → 19500 + 15000 = 34500."""
        pay = calculate_overtime_pay(self.rate, 3, 0, night_hours=2)
        self.assertEqual(pay, Decimal("34500.00"))

    def test_combined_all_types(self):
        """2h std + 3h WE + 1h nuit + 2h hol."""
        pay = calculate_overtime_pay(
            self.rate, std_hours=2,
            hol_hours=2, weekend_hours=3, night_hours=1,
        )
        # std: 2×5000×1.3 = 13000
        # hol: 2×5000×2.0 = 20000
        # we: 3×5000×2.0 = 30000
        # night: 1×5000×1.5 = 7500
        # total = 70500
        self.assertEqual(pay, Decimal("70500.00"))

    def test_zero_night_is_safe(self):
        """night_hours=0 par defaut ne change rien."""
        pay_without = calculate_overtime_pay(self.rate, 5, 0)
        pay_with = calculate_overtime_pay(self.rate, 5, 0, night_hours=0)
        self.assertEqual(pay_without, pay_with)


if __name__ == "__main__":
    unittest.main(verbosity=2)
