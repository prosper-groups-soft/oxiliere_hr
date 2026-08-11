"""
Prorata calendaire pour les entrees/sorties en cours de periode.

Conforme a semantics.md §Mecanisme : Proratisation des entrees et sorties
  - Unite : jours calendaires (pas jours ouvres)
  - Formule : salaire_proratise = salaire_de_base x (nb_jours_travailles / nb_jours_calendaires_periode)
  - Perimetre : seul le salaire de base est proratise. Les indemnites et HS restent intactes.
"""

from datetime import date
from decimal import Decimal


def calculate_prorata_ratio(
    contract_start: date,
    contract_end: date | None,
    period_start: date,
    period_end: date,
) -> Decimal:
    """
    Calcule le ratio de prorata pour un salarie.

    Args:
        contract_start: Date de debut du contrat.
        contract_end: Date de fin du contrat (None si CDI).
        period_start: Debut de la periode de paie.
        period_end: Fin de la periode de paie.

    Returns:
        Ratio entre 0.0 et 1.0.
        1.0 = mois complet (pas de prorata).

    Examples:
        Embauche le 15 janvier (periode 01/01-31/01):
          ratio = 17/31 ≈ 0.5484

        Sortie le 20 mars (periode 01/03-31/03):
          ratio = 20/31 ≈ 0.6452

        CDI present tout le mois:
          ratio = 1.0
    """
    # Jours calendaires totaux dans la periode
    nb_jours_calendaires = (period_end - period_start).days + 1

    # Periode d'activite dans le mois
    debut_activite = max(contract_start, period_start)

    fin_contrat = contract_end if contract_end else period_end
    fin_activite = min(fin_contrat, period_end)

    # Employe pas encore arrive ou deja parti
    if debut_activite > period_end or fin_activite < period_start:
        return Decimal("0.00")

    nb_jours_travailles = (fin_activite - debut_activite).days + 1

    # Pas de prorata si presence complete
    if nb_jours_travailles >= nb_jours_calendaires:
        return Decimal("1.00")

    ratio = (
        Decimal(nb_jours_travailles)
        / Decimal(nb_jours_calendaires)
    )

    return ratio

