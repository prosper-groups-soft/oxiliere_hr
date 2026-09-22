"""
Tests unitaires — Règle de finalisation de la présence pour la paie.

Garantit que l'agrégation d'un registre de présence (TimeSheet) ne compte un
jour comme travaillé / absent QUE si le registre est FINALISÉ, et qu'un registre
non finalisé est renvoyé à part (`unfinalized_days`) sans alimenter le calcul.

Miroir exact des filtres de AttendanceSummaryService.get_attendance_summary
(suite à la correction « seuls les registres finalisés alimentent la paie »).

Usage: uv run python backend/hr/payroll/tests/test_presence_preview.py
"""

import unittest

# Statuts considérés comme « travaillés » par l'orchestrateur (worked).
WORKED_STATUSES = ('PRESENT', 'PARTIAL', 'LATE')


def aggregate_attendance(days):
    """
    Miroir des agrégats de AttendanceSummaryService : reçoit une liste de jours
    `{finalized: bool, status: str}` et renvoie les compteurs paie.
    Un jour non finalisé n'est NI travaillé NI absent : il est compté dans
    `unfinalized_days` et exclu du calcul.
    """
    worked_days = 0
    absence_days = 0
    unfinalized_days = 0

    for day in days:
        if not day['finalized']:
            unfinalized_days += 1
            continue
        if day['status'] in WORKED_STATUSES:
            worked_days += 1
        elif day['status'] == 'ABSENT':
            absence_days += 1

    return {
        'worked_days': worked_days,
        'absence_days': absence_days,
        'unfinalized_days': unfinalized_days,
    }


class FinalizationCountTests(unittest.TestCase):
    """Seules les présences finalisées alimentent le calcul de paie."""

    def test_finalized_absent_counts_as_absence(self):
        result = aggregate_attendance([
            {'finalized': True, 'status': 'ABSENT'},
        ])
        self.assertEqual(result['absence_days'], 1)
        self.assertEqual(result['worked_days'], 0)
        self.assertEqual(result['unfinalized_days'], 0)

    def test_unfinalized_present_does_not_count_as_worked(self):
        # Un pointage PRESENT mais dont le registre n'est pas finalisé ne doit
        # PAS gonfler les jours travaillés (il est encore susceptible d'évoluer).
        result = aggregate_attendance([
            {'finalized': False, 'status': 'PRESENT'},
        ])
        self.assertEqual(result['worked_days'], 0)
        self.assertEqual(result['unfinalized_days'], 1)

    def test_finalization_makes_day_count(self):
        # Le même jour devient compté une fois son registre finalisé.
        before = aggregate_attendance([{'finalized': False, 'status': 'PRESENT'}])
        after = aggregate_attendance([{'finalized': True, 'status': 'PRESENT'}])
        self.assertEqual(before['worked_days'], 0)
        self.assertEqual(after['worked_days'], 1)
        self.assertEqual(before['unfinalized_days'], 1)
        self.assertEqual(after['unfinalized_days'], 0)

    def test_mixed_period(self):
        result = aggregate_attendance([
            {'finalized': True, 'status': 'PRESENT'},
            {'finalized': True, 'status': 'LATE'},
            {'finalized': True, 'status': 'ABSENT'},
            {'finalized': False, 'status': 'PRESENT'},
            {'finalized': False, 'status': 'ABSENT'},
        ])
        self.assertEqual(result['worked_days'], 2)       # PRESENT + LATE
        self.assertEqual(result['absence_days'], 1)      # ABSENT finalisé
        self.assertEqual(result['unfinalized_days'], 2)  # les 2 non finalisés


if __name__ == "__main__":
    unittest.main(verbosity=2)
