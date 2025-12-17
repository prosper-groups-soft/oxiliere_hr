from enum import Enum


class PaymentMethod(str, Enum):
    BANK = 'bank transfer'
    CASH = 'cash'
    CHECK = 'check'


class BonusTypes(str, Enum):
    TRANSPORT_ALLOWANCE = 'Indemnité de transport'
    HOUSING_ALLOWANCE = 'Indemnité de logement'
    REMOTE_WORK_ALLOWANCE = 'Indemnité de télétravail'
    MEAL_ALLOWANCE = 'Indemnité repas'
    COMPANY_HEALTH_INSURANCE = 'Mutuelle d\'entreprise'
    DISABILITY_INSURANCE = 'Assurance prévoyance'
    TRAVEL_EXPENSES = 'Frais de mission'
    BACK_TO_SCHOOL_ALLOWANCE = 'Allocation de rentrée scolaire'
    CHILDCARE_ALLOWANCE = 'Allocation de garde d\'enfants'
    HOUSING_AID = 'Aide au logement'
    THIRTEENTH_MONTH = '13e mois'
    HEALTH_INSURANCE = 'Assurance santé'
    TRANSPORT_BONUS = 'Primes de transport'
    SENIORITY_BONUS = 'Prime d\'ancienneté'
    OTHER = 'Autre'

