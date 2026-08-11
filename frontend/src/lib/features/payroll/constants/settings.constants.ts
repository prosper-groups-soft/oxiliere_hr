/**
 * Options de configuration de paie — alignées sur les enums backend
 * (hr/payroll/enums.py) et les choix du formulaire.
 *
 * Conformité RDC : la paie est libellée en Francs Congolais (CDF),
 * la devise n'est donc pas configurable.
 */

/** Modes de paiement (PaymentMethod backend) */
export const CONFIG_PAYMENT_METHODS = [
  { value: 'BANK_TRANSFER', label: 'Virement bancaire' },
  { value: 'CASH', label: 'Espèces' },
  { value: 'MOBILE_MONEY', label: 'Mobile Money (M-Pesa, Orange Money)' },
  { value: 'CHECK', label: 'Chèque' },
] as const;

/** Règles d'arrondi (RoundingStrategy backend) */
export const CONFIG_ROUNDING_STRATEGIES = [
  { value: 'arithmetic', label: 'Arithmétique (ROUND_HALF_UP)' },
  { value: 'ceil', label: 'Supérieur (CEIL)' },
  { value: 'floor', label: 'Inférieur (FLOOR)' },
  { value: 'none', label: 'Aucun' },
] as const;

/**
 * Modes exclusifs de déduction des absences non payées.
 * Aligné sur l'enum backend `LeaveDeductionMode` (hr/payroll/enums.py).
 * Un seul mode est actif à la fois — les champs des autres modes sont ignorés.
 */
export const LEAVE_DEDUCTION_MODES = [
  {
    value: 'DISABLED',
    label: 'Désactivée — aucune déduction',
    description: "L'absence non payée n'est pas déduite du salaire.",
  },
  {
    value: 'DAILY_RATE',
    label: 'Salaire ÷ diviseur fixe (26 jours — légal RDC)',
    description: "Valeur d'un jour = salaire ÷ diviseur (26 jours de prestation par défaut).",
  },
  {
    value: 'CALENDAR_DAYS',
    label: 'Salaire ÷ jours calendaires du mois',
    description: "Valeur d'un jour = salaire ÷ nombre réel de jours du mois.",
  },
  {
    value: 'ATTENDANCE_DAYS',
    label: 'Salaire ÷ jours théoriques de présence (planning)',
    description: "Valeur d'un jour = salaire ÷ les jours de travail planifiés de l'employé (son planning d'attendance hebdomadaire, moins fériés et jours non travaillés).",
  },
  {
    value: 'FIXED_AMOUNT',
    label: 'Montant forfaitaire par jour',
    description: "Un montant fixe en CDF est déduit pour chaque jour d'absence.",
  },
] as const;

/** Libellés RDC des règles d'heures supplémentaires (OvertimeRuleType backend) */
export const OVERTIME_RULE_LABELS: Record<
  string,
  { label: string; short: string }
> = {
  FIRST_TIER: {
    label: '6 premières heures (au-delà de 45h/semaine)',
    short: '130 %',
  },
  SUBSEQUENT_HOURS: {
    label: 'Heures suivantes',
    short: '160 %',
  },
  WEEKEND: {
    label: 'Week-end / jour de repos',
    short: '200 %',
  },
  HOLIDAY: {
    label: 'Jour férié légal',
    short: '200 %',
  },
  NIGHT: {
    label: 'Travail de nuit',
    short: '150 %',
  },
};

/** Libellés français des allocations légales RDC (LegalAllowanceType backend) */
export const ALLOWANCE_TYPE_LABELS: Record<
  'HOUSING' | 'TRANSPORT',
  string
> = {
  HOUSING: 'Indemnité de Logement',
  TRANSPORT: 'Indemnité de Transport',
};

