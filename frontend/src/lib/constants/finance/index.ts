// Constants for finance/currency module

/**
 * Supported currencies
 */
export const CURRENCIES = {
  USD: 'USD' as const,
  CDF: 'CDF' as const,
  EUR: 'EUR' as const,
};

export type Currency = typeof CURRENCIES[keyof typeof CURRENCIES];

/**
 * Default currency
 */
export const DEFAULT_CURRENCY: Currency = 'USD';

/**
 * Social contribution types
 */
export const CONTRIBUTION_TYPES = {
  CNSS: 'CNSS' as const,
  ONEM: 'ONEM' as const,
  INPP: 'INPP' as const,
  AMO: 'AMO' as const,
};

export type ContributionType = typeof CONTRIBUTION_TYPES[keyof typeof CONTRIBUTION_TYPES];

/**
 * Payment methods
 */
export const PAYMENT_METHODS = {
  BANK_TRANSFER: 'bank_transfer' as const,
  CASH: 'cash' as const,
  CHECK: 'check' as const,
};

export type PaymentMethod = typeof PAYMENT_METHODS[keyof typeof PAYMENT_METHODS];

