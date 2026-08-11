"""
Bases de calcul — Étape 4 du pipeline de paie.

Conforme à :
- metamodel.md §Concept : Base de calcul
- semantics.md §Concept : Construction des bases de calcul
- catalogue.md §4. Catalogue des bases de calcul

Chaque base est un objet explicite avec :
- type_base, montant, éléments contributeurs, règle de filtrage.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Any

from hr.payroll.enums import CalculationBasisType


@dataclass
class PayElementRef:
    """Référence légère vers un élément de paie contributeur."""
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
    """
    Base de calcul intermédiaire — conforme à metamodel.md §Concept : Base de calcul.

    Attributs :
    - identifiant_base : identifiant unique pour le bulletin
    - type_base : brut, cnss, imposable, inpp, onem
    - montant : résultat de l'accumulation
    - elements_contribuant : références vers les éléments qui la composent
    - regle_filtrage : description de la règle de filtrage
    """
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
    """
    Constructeur des 5 bases de calcul — Étape 4 du pipeline.

    Ordre de construction (obligatoire, cf. catalogue.md §4.1) :
    1. BASE_BRUT       = Σ(tous les gains)
    2. BASE_CNSS       = Σ(gains où soumis_cnss = vrai)
    3. BASE_INPP       = Σ(gains où soumis_inpp = vrai)
    4. BASE_ONEM       = Σ(gains où soumis_onem = vrai)
    5. BASE_IMPOSABLE  = Σ(gains où est_imposable = vrai)
                         - exonération logement (plafond 30% du salaire de base)
                         - exonération transport (frais professionnels)
                         - CNSS salariale (5% de BASE_CNSS)
    """

    ZERO = Decimal("0.00")

    @classmethod
    def _safe_sum(cls, iterable) -> Decimal:
        """Somme de Decimals avec start=Decimal('0.00') pour éviter int(0)."""
        return sum(iterable, start=cls.ZERO)

    @classmethod
    def build_all(
        cls,
        elements: List[PayElementRef],
        cnss_salariale: Decimal = Decimal("0.00"),
        exoneration_logement: Decimal = Decimal("0.00"),
        exoneration_transport: Decimal = Decimal("0.00"),
    ) -> Dict[CalculationBasisType, CalculationBasis]:
        """
        Construit les 5 bases de calcul dans l'ordre prescrit.

        Args:
            elements: Liste des éléments de paie avec leurs flags.
            cnss_salariale: CNSS salariale déjà calculée (BASE_CNSS x 5%).
            exoneration_logement: Montant exonéré au titre du logement.
            exoneration_transport: Montant exonéré au titre du transport.

        Returns:
            Dictionnaire des 5 bases {type: CalculationBasis}.
        """
        bases: Dict[CalculationBasisType, CalculationBasis] = {}

        # --- BASE_BRUT : Σ tous les gains, sans exception ---
        # Invariant métamodèle R3 : "la base brut est la somme de tous les éléments"
        brut_elements = list(elements)
        bases[CalculationBasisType.BRUT] = CalculationBasis(
            type_base=CalculationBasisType.BRUT,
            montant=cls._safe_sum(e.montant for e in brut_elements),
            elements_contribuant=brut_elements,
            regle_filtrage="Σ(tous les gains) — sans exception",
        )

        # --- BASE_CNSS : Σ(gains où soumis_cnss = vrai) ---
        # Inclut l'indemnité logement (pratique sociale RDC)
        # PAS DE PLAFOND en RDC (semantics.md §Propriété : soumis_cnss)
        cnss_elements = [e for e in elements if e.soumis_cnss]
        bases[CalculationBasisType.CNSS] = CalculationBasis(
            type_base=CalculationBasisType.CNSS,
            montant=cls._safe_sum(e.montant for e in cnss_elements),
            elements_contribuant=cnss_elements,
            regle_filtrage="Σ(gains où soumis_cnss = vrai) — pas de plafond en RDC",
        )

        # --- BASE_INPP : Σ(gains où soumis_inpp = vrai) ---
        # Généralement identique à BASE_CNSS
        inpp_elements = [e for e in elements if e.soumis_inpp]
        bases[CalculationBasisType.INPP] = CalculationBasis(
            type_base=CalculationBasisType.INPP,
            montant=cls._safe_sum(e.montant for e in inpp_elements),
            elements_contribuant=inpp_elements,
            regle_filtrage="Σ(gains où soumis_inpp = vrai)",
        )

        # --- BASE_ONEM : Σ(gains où soumis_onem = vrai) ---
        onem_elements = [e for e in elements if e.soumis_onem]
        bases[CalculationBasisType.ONEM] = CalculationBasis(
            type_base=CalculationBasisType.ONEM,
            montant=cls._safe_sum(e.montant for e in onem_elements),
            elements_contribuant=onem_elements,
            regle_filtrage="Σ(gains où soumis_onem = vrai)",
        )

        # --- BASE_IMPOSABLE : cf. semantics.md §Construction des bases ---
        # Étape 1 : Σ(gains où est_imposable = vrai)
        # Étape 2 : − exonération logement (plafonnée 30% du brut imposable avant exonération)
        # Étape 3 : − exonération transport (frais professionnels)
        # Étape 4 : − CNSS salariale (5% de BASE_CNSS)
        imposable_elements = [e for e in elements if e.est_imposable]
        brut_imposable_avant = cls._safe_sum(e.montant for e in imposable_elements)

        base_imposable_nette = (
            brut_imposable_avant
            - exoneration_logement
            - exoneration_transport
            - cnss_salariale
        )
        # La base imposable ne peut jamais être négative
        if base_imposable_nette < cls.ZERO:
            base_imposable_nette = cls.ZERO

        bases[CalculationBasisType.IMPOSABLE] = CalculationBasis(
            type_base=CalculationBasisType.IMPOSABLE,
            montant=base_imposable_nette,
            elements_contribuant=imposable_elements,
            regle_filtrage=(
                "Σ(gains où est_imposable = vrai)"
                " - exonération_logement(plafond 30% brut_imposable)"
                " - exonération_transport"
                " - CNSS_salariale(5% x BASE_CNSS)"
            ),
        )

        return bases
