"""
Tests unitaires — Deduction des absences non payees (mode exclusif).

Couvre les 4 modes de LeaveDeductionMode (RDC) :
  - DISABLED       : aucune deduction
  - DAILY_RATE     : salaire ÷ diviseur fixe (26 jours legal RDC)
  - CALENDAR_DAYS  : salaire ÷ jours calendaires reels du mois
  - FIXED_AMOUNT   : montant forfaitaire par jour

Usage: uv run python backend/hr/payroll/tests/test_absence.py
"""

import unittest
from datetime import date
from decimal import Decimal


# --- Inline copy of the absence deduction logic (orchestrator _step2) ---
# This mirrors the exact computation in orchestrator.py so the test runs
# standalone (no Django import needed), following test_prorata.py pattern.

def compute_absence_deduction(
    mode: str,
    unpaid_leave_days: Decimal,
    base_amount: Decimal,
    leave_deduction_divisor: Decimal,
    fixed_deduction_per_absent_day: Decimal | None,
    period_start: date,
    period_end: date,
) -> Decimal:
    """
    Calcule la deduction d'absence selon le mode exclusif.

    Identique a _step2_calculate_earnings de l'orchestrator.
    """
    absence_deduction = Decimal('0.00')

    if unpaid_leave_days > 0:
        if mode == 'DAILY_RATE':
            divisor = leave_deduction_divisor or Decimal('26')
            per_day = base_amount / divisor
            absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
        elif mode == 'CALENDAR_DAYS':
            divisor = Decimal((period_end - period_start).days + 1)
            per_day = base_amount / divisor
            absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
        elif mode == 'ATTENDANCE_DAYS':
            # Le diviseur est le nombre de jours théoriques de presence (planning).
            # Fourni via leave_deduction_divisor dans ce test (le backend l'obtient
            # via SchedulingService.count_working_days_for_employee).
            divisor = leave_deduction_divisor if leave_deduction_divisor and leave_deduction_divisor > 0 else Decimal((period_end - period_start).days + 1)
            per_day = base_amount / divisor
            absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))
        elif mode == 'FIXED_AMOUNT':
            per_day = fixed_deduction_per_absent_day or Decimal('0')
            absence_deduction = (per_day * unpaid_leave_days).quantize(Decimal('0.01'))

    # Garde-fou : la deduction ne peut pas depasser le salaire de base
    absence_deduction = min(absence_deduction, base_amount)

    return absence_deduction


class AbsenceDeductionDisabledTests(unittest.TestCase):
    """Mode DISABLED (defaut) : aucune deduction, meme avec des absences."""

    def test_disabled_no_deduction(self):
        deduction = compute_absence_deduction(
            mode='DISABLED',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('0.00'))

    def test_disabled_no_absences(self):
        deduction = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('0'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('0.00'))


class AbsenceDeductionDailyRateTests(unittest.TestCase):
    """Mode DAILY_RATE : salaire ÷ 26 (reference legale RDC)."""

    def test_three_days_divisor_26(self):
        """Base 1 300 000 ÷ 26 = 50 000/jour ; 3 jours → 150 000."""
        deduction = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('150000.00'))

    def test_custom_divisor_30(self):
        """Diviseur personnalise 30 : 1 200 000 ÷ 30 = 40 000/jour ; 2 j → 80 000."""
        deduction = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1200000.00'),
            leave_deduction_divisor=Decimal('30'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('80000.00'))

    def test_one_day(self):
        """1 jour d'absence sur base 900 000 ÷ 26 → 34 615,38."""
        deduction = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('1'),
            base_amount=Decimal('900000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('34615.38'))


class AbsenceDeductionCalendarDaysTests(unittest.TestCase):
    """Mode CALENDAR_DAYS : salaire ÷ jours reels du mois."""

    def test_march_31_days(self):
        """Base 1 300 000 ÷ 31 = 41 935,48/jour ; 3 j → 125 806,45."""
        deduction = compute_absence_deduction(
            mode='CALENDAR_DAYS',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('125806.45'))

    def test_february_28_days(self):
        """Fevrier 28 jours : 1 300 000 ÷ 28 = 46 428,57 ; 2 j → 92 857,14."""
        deduction = compute_absence_deduction(
            mode='CALENDAR_DAYS',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 2, 1),
            period_end=date(2026, 2, 28),
        )
        self.assertEqual(deduction, Decimal('92857.14'))

    def test_divisor_ignored(self):
        """Le diviseur fixe est ignore en mode calendaire."""
        deduction_26 = compute_absence_deduction(
            mode='CALENDAR_DAYS',
            unpaid_leave_days=Decimal('1'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        deduction_99 = compute_absence_deduction(
            mode='CALENDAR_DAYS',
            unpaid_leave_days=Decimal('1'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('99'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction_26, deduction_99)


class AbsenceDeductionAttendanceDaysTests(unittest.TestCase):
    """Mode ATTENDANCE_DAYS : salaire ÷ jours theoriques de presence (planning)."""

    def test_attendance_days_22(self):
        """Base 1 300 000 ÷ 22 jours theoriques = 59 090,91/jour ; 2 j → 118 181,82."""
        deduction = compute_absence_deduction(
            mode='ATTENDANCE_DAYS',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('22'),  # jours theoriques du planning
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('118181.82'))

    def test_attendance_days_no_schedule_fallback(self):
        """Sans planning (0 jour theorique) → fallback sur les jours calendaires."""
        deduction = compute_absence_deduction(
            mode='ATTENDANCE_DAYS',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('0'),  # aucun planning
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        # Fallback : 31 jours calendaires → 41 935,48/jour × 2 = 83 870,97
        self.assertEqual(deduction, Decimal('83870.97'))


class AbsenceDeductionFixedAmountTests(unittest.TestCase):
    """Mode FIXED_AMOUNT : montant forfaitaire independant du salaire."""

    def test_fixed_amount_3_days(self):
        """3 jours × 20 000 = 60 000, quel que soit le salaire."""
        deduction = compute_absence_deduction(
            mode='FIXED_AMOUNT',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('5000000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=Decimal('20000'),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('60000.00'))

    def test_fixed_amount_low_salary(self):
        """Forfait qui depasse le salaire → plafonne au salaire de base."""
        deduction = compute_absence_deduction(
            mode='FIXED_AMOUNT',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('50000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=Decimal('20000'),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('50000.00'))

    def test_fixed_amount_null(self):
        """Forfait null → 0 (equivalent a pas de deduction)."""
        deduction = compute_absence_deduction(
            mode='FIXED_AMOUNT',
            unpaid_leave_days=Decimal('3'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction, Decimal('0.00'))


class AbsenceDeductionGuardTests(unittest.TestCase):
    """Garde-fous : deduction plafonnee au salaire de base."""

    def test_deduction_cannot_exceed_base(self):
        """DAILY_RATE avec base faible : la deduction est plafonnee."""
        deduction = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('30'),
            base_amount=Decimal('26000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=None,
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        # 26000/26 = 1000/jour × 30 = 30 000 > 26 000 → plafonne a 26 000
        self.assertEqual(deduction, Decimal('26000.00'))

    def test_exclusivity_semantics(self):
        """
        Exclusivite : le forfait et le diviseur ne sont jamais appliques
        simultanement (le mode determine le seul champ actif).
        """
        # Meme si les deux sont definis, seul le mode compte
        deduction_daily = compute_absence_deduction(
            mode='DAILY_RATE',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),
            fixed_deduction_per_absent_day=Decimal('100000'),  # ignore
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction_daily, Decimal('100000.00'))  # 1 300 000 ÷ 26 × 2

        deduction_fixed = compute_absence_deduction(
            mode='FIXED_AMOUNT',
            unpaid_leave_days=Decimal('2'),
            base_amount=Decimal('1300000.00'),
            leave_deduction_divisor=Decimal('26'),  # ignore
            fixed_deduction_per_absent_day=Decimal('100000'),
            period_start=date(2026, 3, 1),
            period_end=date(2026, 3, 31),
        )
        self.assertEqual(deduction_fixed, Decimal('200000.00'))  # 100 000 × 2


if __name__ == "__main__":
    unittest.main(verbosity=2)
