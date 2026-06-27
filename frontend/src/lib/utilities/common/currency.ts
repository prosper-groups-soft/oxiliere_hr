/**
 * Currency conversion utilities
 * All values are stored in CDF (Francs Congolais) in the database
 * Display/conversion happens on the frontend based on selected currency
 */

import { CURRENCIES, type Currency } from '@/constants/finance';


// Default exchange rate (should be fetched from config)
let currentExchangeRate = 2850; // 1 USD = 2850 CDF

/**
 * Set the current exchange rate for conversions
 */
export function setExchangeRate(rate: number): void {
	currentExchangeRate = rate;
}

/**
 * Get the current exchange rate
 */
export function getExchangeRate(): number {
	return currentExchangeRate;
}

/**
 * Convert a value from CDF (database storage) to the target currency for display
 * @param valueInCDF - Value stored in database (always CDF)
 * @param targetCurrency - Currency to display in
 * @returns Converted value for display
 */
export function fromCDF(valueInCDF: number | null | undefined, targetCurrency: Currency): number {
	if (valueInCDF === null || valueInCDF === undefined) return 0;
	if (targetCurrency === CURRENCIES.CDF) return valueInCDF;
	return valueInCDF / currentExchangeRate;
}

/**
 * Convert a value from display currency to CDF for database storage
 * @param displayValue - Value entered by user in display currency
 * @param displayCurrency - Currency being displayed
 * @returns Value in CDF for database storage
 */
export function toCDF(displayValue: number | null | undefined, displayCurrency: Currency): number {
	if (displayValue === null || displayValue === undefined) return 0;
	if (displayCurrency === CURRENCIES.CDF) return displayValue;
	return displayValue * currentExchangeRate;
}

/**
 * Format a value for display with currency symbol
 */
export function formatCurrency(
	value: number | null | undefined,
	currency: Currency,
	options?: { decimals?: number; compact?: boolean }
): string {
	if (value === null || value === undefined) return '-';

	const { decimals = 2, compact = false } = options || {};

	const formatter = new Intl.NumberFormat('fr-FR', {
		style: 'currency',
		currency: currency,
		minimumFractionDigits: decimals,
		maximumFractionDigits: decimals,
		notation: compact ? 'compact' : 'standard',
	});

	return formatter.format(value);
}

/**
 * Parse a currency string to number
 */
export function parseCurrency(value: string): number {
	// Remove currency symbols and spaces, replace comma with dot
	const cleaned = value
		.replace(/[^\d.,-]/g, '')
		.replace(',', '.');
	return parseFloat(cleaned) || 0;
}

/**
 * Round to specified decimals
 */
export function round(value: number, decimals: number = 2): number {
	const multiplier = Math.pow(10, decimals);
	return Math.round(value * multiplier) / multiplier;
}

/**
 * Input handler for currency fields - converts display value to CDF
 * Usage in oninput: oninput={(e) => handleCurrencyInput(e, config.currency, (v) => updateValue(v))}
 */
export function handleCurrencyInput(
	event: Event,
	displayCurrency: Currency,
	onConvert: (valueInCDF: number) => void
): void {
	const input = event.currentTarget as HTMLInputElement;
	const displayValue = parseFloat(input.value) || 0;
	const cdfValue = toCDF(displayValue, displayCurrency);
	onConvert(cdfValue);
}

/**
 * Get display value from CDF storage
 * Usage: value={displayValue(config.storedValue, config.currency)}
 */
export function displayValue(valueInCDF: number | null | undefined, displayCurrency: Currency): number {
	return fromCDF(valueInCDF, displayCurrency);
}
