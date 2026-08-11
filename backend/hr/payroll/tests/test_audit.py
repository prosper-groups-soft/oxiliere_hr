"""
Tests unitaires — Snapshot d'audit + Signature SHA-256.

Usage: uv run python backend/hr/payroll/tests/test_audit.py
"""

import unittest
import hashlib
import json
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


# --- Minimal standalone classes (matches models.py + orchestrator.py) ---

class CalculationBasisType(str, Enum):
    BRUT = "brut"
    CNSS = "cnss"
    INPP = "inpp"
    ONEM = "onem"
    IMPOSABLE = "imposable"


@dataclass
class CalculationBasis:
    type_base: CalculationBasisType
    montant: Decimal = Decimal("0.00")


@dataclass
class FakeBracket:
    label: str
    lower_limit: Decimal
    upper_limit: Decimal | None = None
    rate_percentage: Decimal = Decimal("0.00")
    max_tax_percentage: Decimal | None  = None


@dataclass
class FakeSmig:
    daily_rate: Decimal = Decimal("14500.00")


@dataclass
class FakeRun:
    code: str = "RUN-2026-01"
    start_date: str = "2026-01-01"
    end_date: str = "2026-01-31"
    params_snapshot: Dict[str, Any] = field(default_factory=dict)

    def save(self, **kwargs):
        pass  # no-op for tests


@dataclass
class FakePayslip:
    id: int = 1
    payroll_run: FakeRun = field(default_factory=FakeRun)
    contract_id: int = 42
    gross_amount: Decimal = Decimal("1221000.00")
    taxable_base: Decimal = Decimal("859950.00")
    net_amount: Decimal = Decimal("1018000.00")
    cnss_amount: Decimal = Decimal("61050.00")
    ipr_amount: Decimal = Decimal("90420.00")
    housing_allowance: Decimal = Decimal("270000.00")
    transport_allowance: Decimal = Decimal("42000.00")
    signature_hash: str = ""


class SnapshotHelper:
    """Minimal standalone version of _build_snapshot and _sign_payslip."""

    @staticmethod
    def build_snapshot(run: FakeRun, brackets: List[FakeBracket], smig: FakeSmig,
                       currency: str = "CDF", rate: Decimal = Decimal("1")) -> Dict:
        if run.params_snapshot and run.params_snapshot.get('date_generation'):
            return run.params_snapshot  # deja capture

        snapshot = {
            "date_generation": "2026-01-31T18:00:00Z",
            "run_code": run.code,
            "periode": {"debut": run.start_date, "fin": run.end_date},
            "parametres_legaux": {
                "SMIG": {
                    "valeur": str(smig.daily_rate),
                    "devise": "CDF/jour",
                },
                "bareme_IRPP": [
                    {
                        "label": b.label,
                        "lower_limit": str(b.lower_limit),
                        "upper_limit": str(b.upper_limit) if b.upper_limit else None,
                        "rate": str(b.rate_percentage) + "%",
                    }
                    for b in brackets
                ],
                "taux_CNSS_salarial": "5%",
                "taux_change": {"devise": currency, "taux": str(rate)},
            },
            "formules_appliquees": {
                "cnss_salariale": "base_cnss x 0.05",
                "irpp": "bareme progressif -> plafonnement 30% -> abattement familial",
                "logement_exoneration": "min(indemnite, brut_imposable x 30%)",
            },
        }
        run.params_snapshot = snapshot
        return snapshot

    @staticmethod
    def sign_payslip(payslip: FakePayslip, bases: Dict[CalculationBasisType, CalculationBasis]) -> str:
        canonical = json.dumps({
            "payslip_id": payslip.id,
            "run_code": payslip.payroll_run.code,
            "contract_id": payslip.contract_id,
            "gross": str(payslip.gross_amount),
            "taxable": str(payslip.taxable_base),
            "net": str(payslip.net_amount),
            "cnss": str(payslip.cnss_amount),
            "ipr": str(payslip.ipr_amount),
            "housing": str(payslip.housing_allowance),
            "transport": str(payslip.transport_allowance),
            "bases": {
                bt.value: str(basis.montant)
                for bt, basis in bases.items()
            },
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


# --- Test data ---

BRACKETS = [
    FakeBracket("IRPP 2026 T1", Decimal("0.00"), Decimal("524160.00"), Decimal("0.00"), Decimal("30.00")),
    FakeBracket("IRPP 2026 T2", Decimal("524161.00"), Decimal("1428000.00"), Decimal("15.00")),
    FakeBracket("IRPP 2026 T10", Decimal("22956001.00"), Decimal("0.00"), Decimal("40.00")),
]

SMIG = FakeSmig(Decimal("14500.00"))

BASES = {
    CalculationBasisType.BRUT: CalculationBasis(CalculationBasisType.BRUT, Decimal("1221000.00")),
    CalculationBasisType.CNSS: CalculationBasis(CalculationBasisType.CNSS, Decimal("1221000.00")),
    CalculationBasisType.INPP: CalculationBasis(CalculationBasisType.INPP, Decimal("1221000.00")),
    CalculationBasisType.ONEM: CalculationBasis(CalculationBasisType.ONEM, Decimal("1221000.00")),
    CalculationBasisType.IMPOSABLE: CalculationBasis(CalculationBasisType.IMPOSABLE, Decimal("859950.00")),
}


class AuditSnapshotTests(unittest.TestCase):

    def test_snapshot_structure(self):
        """Le snapshot contient toutes les sections requises."""
        run = FakeRun()
        snap = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        self.assertIn("date_generation", snap)
        self.assertIn("run_code", snap)
        self.assertIn("periode", snap)
        self.assertIn("parametres_legaux", snap)
        self.assertIn("formules_appliquees", snap)

    def test_snapshot_smig(self):
        run = FakeRun()
        snap = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        self.assertEqual(snap["parametres_legaux"]["SMIG"]["valeur"], "14500.00")
        self.assertEqual(snap["parametres_legaux"]["SMIG"]["devise"], "CDF/jour")

    def test_snapshot_brackets_count(self):
        run = FakeRun()
        snap = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        self.assertEqual(len(snap["parametres_legaux"]["bareme_IRPP"]), 3)

    def test_snapshot_has_formulas(self):
        run = FakeRun()
        snap = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        self.assertIn("cnss_salariale", snap["formules_appliquees"])
        self.assertIn("irpp", snap["formules_appliquees"])

    def test_snapshot_idempotent(self):
        """Appeler build_snapshot 2x ne change rien."""
        run = FakeRun()
        s1 = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        s2 = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG)
        self.assertEqual(s1["date_generation"], s2["date_generation"])

    def test_snapshot_currency_rate(self):
        run = FakeRun()
        snap = SnapshotHelper.build_snapshot(run, BRACKETS, SMIG, currency="USD", rate=Decimal("2850"))
        self.assertEqual(snap["parametres_legaux"]["taux_change"]["devise"], "USD")
        self.assertEqual(snap["parametres_legaux"]["taux_change"]["taux"], "2850")

    def test_signature_length(self):
        """SHA-256 produit un hash de 64 caracteres hex."""
        payslip = FakePayslip()
        sig = SnapshotHelper.sign_payslip(payslip, BASES)
        self.assertEqual(len(sig), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in sig))

    def test_signature_deterministic(self):
        """Meme donnees → meme signature."""
        p1 = FakePayslip()
        p2 = FakePayslip()
        s1 = SnapshotHelper.sign_payslip(p1, BASES)
        s2 = SnapshotHelper.sign_payslip(p2, BASES)
        self.assertEqual(s1, s2)

    def test_signature_changes_with_data(self):
        """Modifier un montant change la signature."""
        p1 = FakePayslip()
        s1 = SnapshotHelper.sign_payslip(p1, BASES)

        p2 = FakePayslip()
        p2.net_amount = Decimal("999999.00")
        s2 = SnapshotHelper.sign_payslip(p2, BASES)
        self.assertNotEqual(s1, s2)

    def test_signature_changes_with_bases(self):
        """Modifier une base de calcul change la signature."""
        p1 = FakePayslip()
        bases1 = dict(BASES)

        p2 = FakePayslip()
        bases2 = dict(BASES)
        bases2[CalculationBasisType.IMPOSABLE] = CalculationBasis(
            CalculationBasisType.IMPOSABLE, Decimal("500000.00")
        )

        s1 = SnapshotHelper.sign_payslip(p1, bases1)
        s2 = SnapshotHelper.sign_payslip(p2, bases2)
        self.assertNotEqual(s1, s2)

    def test_signature_hex_format(self):
        """La signature est bien du hexadecimal."""
        payslip = FakePayslip()
        sig = SnapshotHelper.sign_payslip(payslip, BASES)
        # hexdigest ne contient que [0-9a-f]
        self.assertTrue(all(c in "0123456789abcdef" for c in sig))


if __name__ == "__main__":
    unittest.main(verbosity=2)
