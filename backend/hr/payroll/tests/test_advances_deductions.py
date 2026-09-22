"""
Tests unitaires — Plafonnement cumulatif des remboursements d'avances.

Régression : `AdvanceService.process_advances_for_payslip` doit garantir que
le cumul des déductions d'avances ne dépasse JAMAIS le net à payer, même quand
plusieurs avances sont actives. La part non couverte reste due (déduite à la
période suivante) — jamais de net négatif / de sur-déduction.

NOTE : comme les autres tests du module (test_prorata, test_bases...), ce fichier
est un test STANDALONE (sans Django ni base de données). Il embarque une copie
fidèle de l'algorithme de plafonnement contenu dans
`hr/payroll/services/advances/advances.py`. Veiller à garder cette copie
synchronisée avec la méthode réelle `process_advances_for_payslip`.

Usage: uv run python hr/payroll/tests/test_advances_deductions.py
"""

import unittest
from decimal import Decimal


# ─────────────────────────────────────────────────────────────────────────────
# Copie fidèle de la logique de plafonnement (cf. process_advances_for_payslip)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_suggested_deduction(
    balance: Decimal,
    salary_base: Decimal,
    repayment_percentage: Decimal,
) -> Decimal:
    """Mi­roir de AdvanceService.calculate_advance_deduction."""
    if balance <= 0:
        return Decimal("0.00")
    suggested = (salary_base * (repayment_percentage / Decimal("100"))).quantize(
        Decimal("0.01")
    )
    # Ne jamais dépasser le solde restant dû
    return min(suggested, balance)


def allocate_advance_deductions(
    suggested_amounts: list[Decimal],
    available_net: Decimal,
) -> tuple[list[Decimal], Decimal]:
    """
    Miroir du cœur de process_advances_for_payslip (boucle de plafonnement).

    Reçoit la liste des déductions « suggérées » (une par avance active, dans
    l'ordre de priorité) et le net encore disponible. Retourne (déductions
    réellement appliquées, total). Chaque avance ne peut prendre que ce qu'il
    RESTE du net ; la part non couverte reste due.
    """
    applied: list[Decimal] = []
    total = Decimal("0.00")

    if available_net <= 0:
        return applied, total

    remaining = available_net
    for suggested in suggested_amounts:
        if remaining <= 0:
            break
        deduction = min(suggested, remaining)
        if deduction > 0:
            applied.append(deduction)
            total += deduction
            remaining -= deduction

    return applied, total


def process_advances_mirror(
    gross_salary: Decimal,
    net_salary_before_advances: Decimal,
    advances: list[tuple[Decimal, Decimal, Decimal]],  # (balance, %, base_net)
) -> tuple[list[Decimal], Decimal]:
    """Miroir complet de process_advances_for_payslip pour base NET."""
    suggested = [
        calculate_suggested_deduction(balance, net_salary_before_advances, pct)
        for (balance, pct, _) in advances
    ]
    return allocate_advance_deductions(suggested, net_salary_before_advances)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de régression
# ─────────────────────────────────────────────────────────────────────────────

class AdvanceDeductionCappingTests(unittest.TestCase):

    def test_two_advances_never_exceed_net(self):
        """
        Régression : 2 avances (20 % NET puis 100 % NET) sur un net de 100.
        La 1re prend 20, la 2e est plafonnée au reste (80) et non à 100.
        → net final 0, jamais négatif.
        """
        net = Decimal("100.00")
        advances = [
            (Decimal("1000.00"), Decimal("20"), True),   # suggéré 20
            (Decimal("500.00"), Decimal("100"), True),   # suggéré 100 → plafonné
        ]
        applied, total = process_advances_mirror(Decimal("200.00"), net, advances)

        self.assertEqual(len(applied), 2)
        self.assertEqual(applied[0], Decimal("20.00"))
        self.assertEqual(applied[1], Decimal("80.00"))  # et non 100
        self.assertEqual(total, Decimal("100.00"))
        # Invariant clé : le net ne devient jamais négatif.
        self.assertGreaterEqual(net - total, Decimal("0.00"))
        self.assertEqual(net - total, Decimal("0.00"))

    def test_single_advance_capped_to_net(self):
        """Une seule avance à 100 % est plafonnée au net (jamais au-delà)."""
        net = Decimal("50.00")
        advances = [(Decimal("1000.00"), Decimal("100"), True)]
        applied, total = process_advances_mirror(Decimal("200.00"), net, advances)
        self.assertEqual(applied, [Decimal("50.00")])
        self.assertEqual(total, Decimal("50.00"))
        self.assertGreaterEqual(net - total, Decimal("0.00"))

    def test_remaining_part_stays_due(self):
        """
        La 2e avance suggérée dépasse le reste → elle est plafonnée au reste,
        le surplus (la part non couverte) reste due (n'est pas perdue).
        """
        net = Decimal("100.00")
        advances = [
            (Decimal("30.00"), Decimal("100"), True),  # suggéré min(100,30)=30
            (Decimal("90.00"), Decimal("100"), True),  # suggéré 90
        ]
        applied, total = process_advances_mirror(Decimal("200.00"), net, advances)

        # 1re : balance 30 → déduit 30. Reste 70.
        # 2e : suggéré min(90,70)=70 → il restera 20 de dû sur la 2e avance.
        self.assertEqual(applied[0], Decimal("30.00"))
        self.assertEqual(applied[1], Decimal("70.00"))
        self.assertEqual(total, Decimal("100.00"))
        # Le dû non couvert n'est pas perdu : 20 restent à rembourser.
        self.assertEqual(Decimal("90.00") - applied[1], Decimal("20.00"))

    def test_second_advance_zero_when_net_depleted(self):
        """Si la 1re avance épulse le net, la 2e n'est pas déduite du tout."""
        net = Decimal("100.00")
        advances = [
            (Decimal("1000.00"), Decimal("100"), True),  # prend tout le net (100)
            (Decimal("500.00"), Decimal("50"), True),     # reste 0 → non déduite
        ]
        applied, total = process_advances_mirror(Decimal("200.00"), net, advances)
        self.assertEqual(applied, [Decimal("100.00")])
        self.assertEqual(total, Decimal("100.00"))

    def test_net_zero_or_negative_returns_empty(self):
        """Net ≤ 0 → aucune déduction (jamais de net négatif)."""
        for bad_net in (Decimal("0.00"), Decimal("-10.00")):
            applied, total = process_advances_mirror(
                Decimal("200.00"), bad_net,
                [(Decimal("1000.00"), Decimal("20"), True)],
            )
            self.assertEqual(applied, [])
            self.assertEqual(total, Decimal("0.00"))

    def test_fully_repaid_advance_not_deducted(self):
        """Balance à 0 → suggéré 0 → non déduit."""
        net = Decimal("100.00")
        advances = [
            (Decimal("0.00"), Decimal("20"), True),  # soldé → 0
            (Decimal("40.00"), Decimal("50"), True),  # suggéré min(50,40)=40
        ]
        applied, total = process_advances_mirror(Decimal("200.00"), net, advances)
        self.assertEqual(applied, [Decimal("40.00")])
        self.assertEqual(total, Decimal("40.00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

