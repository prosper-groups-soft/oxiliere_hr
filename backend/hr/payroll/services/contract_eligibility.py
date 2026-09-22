"""
Éligibilité d'un contrat sur une période de paie.

Règle : un employé est payé si son contrat de travail est **valide sur la
période du run**, c.-à-d. que l'intervalle de validité du contrat chevauche
[period_start, period_end] :

    contract.start_date <= period_end
    AND (contract.end_date IS NULL OR contract.end_date >= period_start)

Un contrat qui commence ou se termine en cours de période est éligible ; la
proratisation (calculations/prorata.py) réduit alors le salaire aux jours
effectivement couverts dans la période.
"""
from django.db.models import Q


def contract_active_on_period(period_start, period_end) -> Q:
    """Q filter sélectionnant les contrats valides sur [period_start, period_end]."""
    return Q(start_date__lte=period_end) & (
        Q(end_date__isnull=True) | Q(end_date__gte=period_start)
    )
