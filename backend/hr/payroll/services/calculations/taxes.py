from decimal import Decimal, ROUND_HALF_UP
from hr.payroll.services.cache import PayrollCacheService


class TaxCalculationService:
    """Handles calculation of progressive income tax (IPR / IRPP)."""

    @classmethod
    def calculate_progressive_tax(
        cls,
        taxable_income: Decimal,
        nb_charges: int = 0,
    ) -> Decimal:
        """
        Calcule l'impôt progressif mensuel (IPR ou IRPP selon le barème actif).

        Algorithme conforme à catalogue.md §2.3 :
          1. Appliquer le barème (nombre de tranches variable selon le barème)
          2. Plafonnement à 30% du revenu imposable
          3. Abattement familial : 2% par personne à charge, max 18%
          4. Arrondi à 0.01 FC

        Args:
            taxable_income: Revenu imposable net mensuel.
            nb_charges: Nombre de personnes à charge pour l'abattement familial.

        Returns:
            Impôt mensuel arrondi.
        """
        if taxable_income <= 0:
            return Decimal("0.00")

        # 1. Annualize + apply progressive brackets
        annual_income = taxable_income * Decimal("12")
        brackets = PayrollCacheService.get_tax_brackets()

        if not brackets:
            return Decimal("0.00")

        # Configuration system-wide (min tax, max tax cap rate)
        min_tax = Decimal("2000.00")
        max_tax_cap_rate = Decimal("0.30")
        first_bracket = brackets[0] if brackets else None
        if first_bracket:
            if first_bracket.min_tax_amount is not None:
                min_tax = first_bracket.min_tax_amount
            if first_bracket.max_tax_percentage is not None:
                max_tax_cap_rate = first_bracket.max_tax_percentage / Decimal("100")

        # Étape 1 : Barème progressif
        total_annual_tax = Decimal("0.00")
        for bracket in brackets:
            if annual_income > bracket.lower_limit:
                upper_limit = bracket.upper_limit if bracket.upper_limit else annual_income
                taxable_in_bracket = min(annual_income, upper_limit) - bracket.lower_limit
                if taxable_in_bracket > 0:
                    total_annual_tax += taxable_in_bracket * (
                        bracket.rate_percentage / Decimal("100")
                    )
            else:
                break

        monthly_tax = total_annual_tax / Decimal("12")

        # Étape 2 : Plafonnement à 30% du revenu imposable (Art. 84 DRC Tax Code)
        max_allowed_tax = taxable_income * max_tax_cap_rate
        if monthly_tax > max_allowed_tax:
            monthly_tax = max_allowed_tax

        # Minimum tax de 2000 FC (ou configuré)
        if monthly_tax < min_tax:
            monthly_tax = min_tax

        # --- Correction 0.3a : Abattement familial ---
        # Conforme à catalogue.md §2.3 Étape 3
        # "taux_abattement = min(nb_charges × 0,02, 0,18)"
        if nb_charges > 0:
            abattement_rate = min(
                Decimal(nb_charges) * Decimal("0.02"),
                Decimal("0.18"),
            )
            monthly_tax = monthly_tax * (Decimal("1.00") - abattement_rate)

        return monthly_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
