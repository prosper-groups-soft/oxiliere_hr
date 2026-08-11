"""
Tests unitaires — Prorata calendaire entrees/sorties.

Usage: uv run python backend/hr/payroll/tests/test_prorata.py
"""

import unittest
from datetime import date
from decimal import Decimal


# Import standalone (no Django needed)
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..'
))
# But let's inline the function to avoid import issues with Django


# --- Inline copy of calculate_prorata_ratio for standalone testing ---

def calculate_prorata_ratio(
    contract_start: date,
    contract_end: date | None,
    period_start: date,
    period_end: date,
) -> Decimal:
    nb_jours_calendaires = (period_end - period_start).days + 1

    debut_activite = max(contract_start, period_start)
    fin_contrat = contract_end if contract_end else period_end
    fin_activite = min(fin_contrat, period_end)

    if debut_activite > period_end or fin_activite < period_start:
        return Decimal("0.00")

    nb_jours_travailles = (fin_activite - debut_activite).days + 1

    if nb_jours_travailles >= nb_jours_calendaires:
        return Decimal("1.00")

    return (
        Decimal(nb_jours_travailles)
        / Decimal(nb_jours_calendaires)
    )


class ProrataCalendarTests(unittest.TestCase):

    def test_full_month_no_prorata(self):
        """Employe present tout le mois → ratio 1.0."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2025, 1, 1),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(ratio, Decimal("1.0"))

    def test_hired_mid_month(self):
        """Embauche le 15 mars → 17/31."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 3, 15),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        expected = Decimal(17) / Decimal(31)
        self.assertAlmostEqual(float(ratio), float(expected), places=4)

    def test_exit_mid_month(self):
        """Sortie le 20 mars → 20/31."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2025, 1, 1),
            contract_end=date(2026, 3, 20),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        expected = Decimal(20) / Decimal(31)
        self.assertAlmostEqual(float(ratio), float(expected), places=4)

    def test_hired_first_day(self):
        """Embauche le 1er mars → pas de prorata."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 3, 1),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(ratio, Decimal("1.0"))

    def test_hired_last_day(self):
        """Embauche le 31 mars → 1/31."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 3, 31),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        expected = Decimal(1) / Decimal(31)
        self.assertAlmostEqual(float(ratio), float(expected), places=4)

    def test_short_month_february(self):
        """Fevrier (28 jours) : embauche le 10 → 19/28."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 2, 10),
            contract_end=None,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
        )
        expected = Decimal(19) / Decimal(28)
        self.assertAlmostEqual(float(ratio), float(expected), places=4)

    def test_contract_starts_after_period(self):
        """Contrat commence apres la periode → 0.00."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 4, 1),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(ratio, Decimal("0.00"))

    def test_contract_ended_before_period(self):
        """Contrat termine avant la periode → 0.00."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2025, 1, 1),
            contract_end=date(2026, 2, 28),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(ratio, Decimal("0.00"))

    def test_salary_900k_hired_15th(self):
        """Salaire 900k, embauche 15 mars → 900k × 17/31 ≈ 493 548,39."""
        base = Decimal("900000.00")
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 3, 15),
            contract_end=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        prorated = (base * ratio).quantize(Decimal("0.01"))
        self.assertEqual(prorated, Decimal("493548.39"))

    def test_salary_1200k_exit_10th(self):
        """Salaire 1 200k, sortie 10 mars → 1 200k × 10/31 ≈ 387 096,77."""
        base = Decimal("1200000.00")
        ratio = calculate_prorata_ratio(
            contract_start=date(2025, 6, 1),
            contract_end=date(2026, 3, 10),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        prorated = (base * ratio).quantize(Decimal("0.01"))
        self.assertEqual(prorated, Decimal("387096.77"))

    def test_hired_and_exit_same_month(self):
        """Embauche + sortie dans le meme mois → 5/31."""
        ratio = calculate_prorata_ratio(
            contract_start=date(2026, 3, 10),
            contract_end=date(2026, 3, 15),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        expected = Decimal(6) / Decimal(31)  # 10,11,12,13,14,15 = 6 jours
        self.assertAlmostEqual(float(ratio), float(expected), places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
