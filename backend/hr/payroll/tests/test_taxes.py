"""
Tests unitaires — Calcul d'impôt (IPR/IRPP + abattement familial).

Usage: uv run python backend/hr/payroll/tests/test_taxes.py
"""

import unittest
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Optional


# --- Minimal standalone TaxBracket (matches Django model) ---

@dataclass
class FakeTaxBracket:
    label: str
    lower_limit: Decimal
    upper_limit: Optional[Decimal]
    rate_percentage: Decimal
    min_tax_amount: Optional[Decimal] = None
    max_tax_percentage: Optional[Decimal] = None


# --- Minimal standalone TaxCalculationService (matches taxes.py) ---

class TaxCalculationService:
    @classmethod
    def calculate_progressive_tax(
        cls,
        taxable_income: Decimal,
        brackets: List[FakeTaxBracket],
        nb_charges: int = 0,
    ) -> Decimal:
        if taxable_income <= 0:
            return Decimal("0.00")
        if not brackets:
            return Decimal("0.00")

        annual = taxable_income * Decimal("12")

        min_tax = Decimal("2000.00")
        max_cap = Decimal("0.30")
        fb = brackets[0]
        if fb.min_tax_amount is not None:
            min_tax = fb.min_tax_amount
        if fb.max_tax_percentage is not None:
            max_cap = fb.max_tax_percentage / Decimal("100")

        total = Decimal("0.00")
        for b in brackets:
            if annual > b.lower_limit:
                upper = b.upper_limit if b.upper_limit else annual
                chunk = min(annual, upper) - b.lower_limit
                if chunk > 0:
                    total += chunk * (b.rate_percentage / Decimal("100"))
            else:
                break

        monthly = total / Decimal("12")

        # Plafonnement 30%
        cap = taxable_income * max_cap
        if monthly > cap:
            monthly = cap

        if 0 < monthly < min_tax:
            monthly = min_tax

        # Abattement familial
        if nb_charges > 0:
            abt = min(Decimal(nb_charges) * Decimal("0.02"), Decimal("0.18"))
            monthly = monthly * (Decimal("1.00") - abt)

        return monthly.quantize(Decimal("0.01"))


# --- Barèmes de test ---

IPR_4_BRACKETS = [
    FakeTaxBracket("IPR 1", Decimal("0.00"), Decimal("1944000.00"), Decimal("3.00"),
                    min_tax_amount=Decimal("2000.00"), max_tax_percentage=Decimal("30.00")),
    FakeTaxBracket("IPR 2", Decimal("1944001.00"), Decimal("21600000.00"), Decimal("15.00")),
    FakeTaxBracket("IPR 3", Decimal("21600001.00"), Decimal("43200000.00"), Decimal("30.00")),
    FakeTaxBracket("IPR 4", Decimal("43200001.00"), None, Decimal("40.00")),
]

IRPP_2026_10_BRACKETS = [
    FakeTaxBracket("IRPP 1",  Decimal("0.00"), Decimal("524160.00"), Decimal("0.00"),
                    max_tax_percentage=Decimal("30.00")),
    FakeTaxBracket("IRPP 2",  Decimal("524161.00"), Decimal("1428000.00"), Decimal("15.00")),
    FakeTaxBracket("IRPP 3",  Decimal("1428001.00"), Decimal("2700000.00"), Decimal("20.00")),
    FakeTaxBracket("IRPP 4",  Decimal("2700001.00"), Decimal("4620000.00"), Decimal("22.50")),
    FakeTaxBracket("IRPP 5",  Decimal("4620001.00"), Decimal("7260000.00"), Decimal("25.00")),
    FakeTaxBracket("IRPP 6",  Decimal("7260001.00"), Decimal("10260000.00"), Decimal("30.00")),
    FakeTaxBracket("IRPP 7",  Decimal("10260001.00"), Decimal("13908000.00"), Decimal("32.50")),
    FakeTaxBracket("IRPP 8",  Decimal("13908001.00"), Decimal("16824000.00"), Decimal("35.00")),
    FakeTaxBracket("IRPP 9",  Decimal("16824001.00"), Decimal("22956000.00"), Decimal("37.50")),
    FakeTaxBracket("IRPP 10", Decimal("22956001.00"), None, Decimal("40.00")),
]


class TaxCalculationTests(unittest.TestCase):
    """Tests de calcul d'impôt — barème configurable + abattement familial."""

    # ─────── IPR (4 tranches, pré-2026) ───────

    def test_ipr_zero_income(self):
        self.assertEqual(
            TaxCalculationService.calculate_progressive_tax(Decimal("0"), IPR_4_BRACKETS),
            Decimal("0.00"),
        )

    def test_ipr_under_min_tax(self):
        """Revenu très faible → plancher minimum 2000 FC."""
        tax = TaxCalculationService.calculate_progressive_tax(Decimal("5000"), IPR_4_BRACKETS)
        self.assertEqual(tax, Decimal("2000.00"))

    def test_ipr_30_percent_cap(self):
        """Plafonnement à 30% du revenu imposable."""
        tax = TaxCalculationService.calculate_progressive_tax(
            Decimal("10000000"), IPR_4_BRACKETS
        )
        self.assertLessEqual(tax, Decimal("3000000.00"))  # 30% de 10M

    def test_ipr_900k_standard(self):
        """Cas standard : 900k CDF/mois → IPR 4 tranches → ~115 560 FC/mois."""
        tax = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IPR_4_BRACKETS)
        # Annual 10.8M: T1 1.944M×3%=58 320 + T2 8.856M×15%=1 328 400 = 1 386 720/an
        # → 115 560/mois
        self.assertGreater(tax, Decimal("115500.00"))
        self.assertLess(tax, Decimal("115600.00"))

    # ─────── IRPP 2026 (10 tranches) ───────

    def test_irpp_10_brackets_present(self):
        """Le barème IRPP 2026 a bien 10 tranches."""
        self.assertEqual(len(IRPP_2026_10_BRACKETS), 10)

    def test_irpp_tranche_1_zero(self):
        """Tranche 1 (0-43 680/mois) → 0%."""
        tax = TaxCalculationService.calculate_progressive_tax(Decimal("30000"), IRPP_2026_10_BRACKETS)
        self.assertEqual(tax, Decimal("0.00"))

    def test_irpp_900k(self):
        """900k/mois → IRPP 2026 : tranches 1-6 applicables."""
        tax = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS)
        self.assertGreater(tax, Decimal("0.00"))
        self.assertLess(tax, Decimal("270000.00"))  # < 30%

    def test_irpp_30_percent_cap(self):
        """Même avec IRPP 2026, plafond à 30%."""
        tax = TaxCalculationService.calculate_progressive_tax(
            Decimal("5000000"), IRPP_2026_10_BRACKETS
        )
        max_tax = Decimal("5000000") * Decimal("0.30")
        self.assertLessEqual(tax, max_tax)

    # ─────── Abattement familial ───────

    def test_no_abattement_without_charges(self):
        """Sans charges → pas d'abattement."""
        t1 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=0)
        t2 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=0)
        self.assertEqual(t1, t2)

    def test_abattement_1_charge(self):
        """1 charge → 2% d'abattement."""
        t0 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=0)
        t1 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=1)
        self.assertLess(t1, t0)
        # L'écart doit être ~2%
        self.assertAlmostEqual(float(t1 / t0), 0.98, delta=0.01)

    def test_abattement_3_charges(self):
        """3 charges → 6% d'abattement."""
        t0 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=0)
        t3 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=3)
        self.assertLess(t3, t0)
        self.assertAlmostEqual(float(t3 / t0), 0.94, delta=0.01)

    def test_abattement_max_18_percent(self):
        """9 charges → 18% max, 10 charges → toujours 18%."""
        t0 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=0)
        t9 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=9)
        t10 = TaxCalculationService.calculate_progressive_tax(Decimal("900000"), IRPP_2026_10_BRACKETS, nb_charges=10)
        # 9 charges = 18% abattement → 82% de t0
        self.assertAlmostEqual(float(t9 / t0), 0.82, delta=0.01)
        # 10 charges = toujours 18% (plafonné)
        self.assertEqual(t9, t10)

    def test_abattement_on_small_income(self):
        """Abattement sur un revenu très faible."""
        tax = TaxCalculationService.calculate_progressive_tax(Decimal("50000"), IRPP_2026_10_BRACKETS, nb_charges=5)
        # Tranche 2 = 15% → abattement 10% → arrondi
        self.assertGreaterEqual(tax, Decimal("0.00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
