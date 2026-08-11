"""
Tests unitaires — Bases de calcul (standalone, sans Django).

Usage: uv run python backend/hr/payroll/tests/test_bases.py
"""

import unittest
from decimal import Decimal
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any


# --- Minimal standalone classes (matches bases.py without Django imports) ---

class CalculationBasisType(str, Enum):
    BRUT = "brut"
    CNSS = "cnss"
    INPP = "inpp"
    ONEM = "onem"
    IMPOSABLE = "imposable"


@dataclass
class PayElementRef:
    code: str
    libelle: str
    montant: Decimal
    est_imposable: bool = True
    soumis_cnss: bool = True
    soumis_inpp: bool = True
    soumis_onem: bool = True
    est_exonere_logement: bool = False
    est_exonere_transport: bool = False


@dataclass
class CalculationBasis:
    type_base: CalculationBasisType
    montant: Decimal = Decimal("0.00")
    elements_contribuant: List[PayElementRef] = field(default_factory=list)
    regle_filtrage: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_base": self.type_base.value,
            "montant": str(self.montant),
            "regle_filtrage": self.regle_filtrage,
            "nb_elements": len(self.elements_contribuant),
            "elements": [
                {"code": e.code, "libelle": e.libelle, "montant": str(e.montant)}
                for e in self.elements_contribuant
            ],
        }


class CalculationBasisBuilder:
    ZERO = Decimal("0.00")

    @classmethod
    def _safe_sum(cls, iterable) -> Decimal:
        return sum(iterable, start=cls.ZERO)

    @classmethod
    def build_all(
        cls,
        elements: List[PayElementRef],
        cnss_salariale: Decimal = Decimal("0.00"),
        exoneration_logement: Decimal = Decimal("0.00"),
        exoneration_transport: Decimal = Decimal("0.00"),
    ) -> Dict[CalculationBasisType, CalculationBasis]:
        bases: Dict[CalculationBasisType, CalculationBasis] = {}

        # BASE_BRUT
        bases[CalculationBasisType.BRUT] = CalculationBasis(
            type_base=CalculationBasisType.BRUT,
            montant=cls._safe_sum(e.montant for e in elements),
            elements_contribuant=list(elements),
            regle_filtrage="Σ(tous les gains)",
        )

        # BASE_CNSS
        cnss_elts = [e for e in elements if e.soumis_cnss]
        bases[CalculationBasisType.CNSS] = CalculationBasis(
            type_base=CalculationBasisType.CNSS,
            montant=cls._safe_sum(e.montant for e in cnss_elts),
            elements_contribuant=cnss_elts,
            regle_filtrage="Σ(gains où soumis_cnss=vrai)",
        )

        # BASE_INPP
        inpp_elts = [e for e in elements if e.soumis_inpp]
        bases[CalculationBasisType.INPP] = CalculationBasis(
            type_base=CalculationBasisType.INPP,
            montant=cls._safe_sum(e.montant for e in inpp_elts),
            elements_contribuant=inpp_elts,
            regle_filtrage="Σ(gains où soumis_inpp=vrai)",
        )

        # BASE_ONEM
        onem_elts = [e for e in elements if e.soumis_onem]
        bases[CalculationBasisType.ONEM] = CalculationBasis(
            type_base=CalculationBasisType.ONEM,
            montant=cls._safe_sum(e.montant for e in onem_elts),
            elements_contribuant=onem_elts,
            regle_filtrage="Σ(gains où soumis_onem=vrai)",
        )

        # BASE_IMPOSABLE
        imp_elts = [e for e in elements if e.est_imposable]
        brut_imp = cls._safe_sum(e.montant for e in imp_elts)
        net = brut_imp - exoneration_logement - exoneration_transport - cnss_salariale
        if net < cls.ZERO:
            net = cls.ZERO
        bases[CalculationBasisType.IMPOSABLE] = CalculationBasis(
            type_base=CalculationBasisType.IMPOSABLE,
            montant=net,
            elements_contribuant=imp_elts,
            regle_filtrage="Σ(imposable) − exonérations − CNSS",
        )

        return bases


# --- Tests ---

class CalculationBasisTests(unittest.TestCase):

    def test_all_bases_present(self):
        elts = [PayElementRef(code="A", libelle="Salaire", montant=Decimal("900000.00"))]
        bases = CalculationBasisBuilder.build_all(elts)
        self.assertCountEqual(bases.keys(), [
            CalculationBasisType.BRUT, CalculationBasisType.CNSS,
            CalculationBasisType.INPP, CalculationBasisType.ONEM,
            CalculationBasisType.IMPOSABLE,
        ])

    def test_base_brut_somme(self):
        elts = [
            PayElementRef(code="A", libelle="Salaire", montant=Decimal("100.00")),
            PayElementRef(code="B", libelle="Prime", montant=Decimal("50.00")),
        ]
        bases = CalculationBasisBuilder.build_all(elts)
        self.assertEqual(bases[CalculationBasisType.BRUT].montant, Decimal("150.00"))

    def test_base_cnss_filtre(self):
        elts = [
            PayElementRef(code="A", libelle="Ok", montant=Decimal("100.00"), soumis_cnss=True),
            PayElementRef(code="B", libelle="No", montant=Decimal("50.00"), soumis_cnss=False),
        ]
        bases = CalculationBasisBuilder.build_all(elts)
        self.assertEqual(bases[CalculationBasisType.CNSS].montant, Decimal("100.00"))

    def test_base_inpp_filtre(self):
        elts = [
            PayElementRef(code="A", libelle="Ok", montant=Decimal("100.00"), soumis_inpp=True),
            PayElementRef(code="B", libelle="No", montant=Decimal("50.00"), soumis_inpp=False),
        ]
        bases = CalculationBasisBuilder.build_all(elts)
        self.assertEqual(bases[CalculationBasisType.INPP].montant, Decimal("100.00"))

    def test_base_imposable_900k_cnss_45k(self):
        """900k − 45k CNSS = 855k imposable."""
        elts = [PayElementRef(code="A", libelle="Salaire", montant=Decimal("900000.00"))]
        bases = CalculationBasisBuilder.build_all(elts, cnss_salariale=Decimal("45000.00"))
        self.assertEqual(bases[CalculationBasisType.IMPOSABLE].montant, Decimal("855000.00"))

    def test_base_imposable_clamped_zero(self):
        elts = [PayElementRef(code="A", libelle="Salaire", montant=Decimal("100.00"))]
        bases = CalculationBasisBuilder.build_all(elts, cnss_salariale=Decimal("1000.00"))
        self.assertEqual(bases[CalculationBasisType.IMPOSABLE].montant, Decimal("0.00"))

    def test_logement_270k_deduit(self):
        """900k − 270k logement − 45k CNSS = 585k."""
        elts = [PayElementRef(code="A", libelle="Salaire", montant=Decimal("900000.00"))]
        bases = CalculationBasisBuilder.build_all(
            elts,
            cnss_salariale=Decimal("45000.00"),
            exoneration_logement=Decimal("270000.00"),
        )
        self.assertEqual(bases[CalculationBasisType.IMPOSABLE].montant, Decimal("585000.00"))

    def test_transport_100k_deduit(self):
        """900k − 100k transport − 45k CNSS = 755k."""
        elts = [PayElementRef(code="A", libelle="Salaire", montant=Decimal("900000.00"))]
        bases = CalculationBasisBuilder.build_all(
            elts,
            cnss_salariale=Decimal("45000.00"),
            exoneration_transport=Decimal("100000.00"),
        )
        self.assertEqual(bases[CalculationBasisType.IMPOSABLE].montant, Decimal("755000.00"))

    def test_empty_zero(self):
        bases = CalculationBasisBuilder.build_all([])
        for bt in CalculationBasisType:
            self.assertEqual(bases[bt].montant, Decimal("0.00"))

    def test_to_dict(self):
        basis = CalculationBasis(
            type_base=CalculationBasisType.BRUT,
            montant=Decimal("150.00"),
            elements_contribuant=[PayElementRef(code="A", libelle="Salaire", montant=Decimal("100.00"))],
            regle_filtrage="Σ",
        )
        d = basis.to_dict()
        self.assertEqual(d["type_base"], "brut")
        self.assertEqual(d["montant"], "150.00")
        self.assertEqual(d["nb_elements"], 1)

    def test_default_flags(self):
        ref = PayElementRef(code="X", libelle="Test", montant=Decimal("10.00"))
        self.assertTrue(ref.est_imposable)
        self.assertTrue(ref.soumis_cnss)
        self.assertFalse(ref.est_exonere_logement)


if __name__ == "__main__":
    unittest.main(verbosity=2)

