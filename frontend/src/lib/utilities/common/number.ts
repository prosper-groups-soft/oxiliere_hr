/**
 * Keyboard event handler to prevent non-numeric input.
 * Allows: 0-9, ., -, Backspace, Tab, Enter, Escape, Arrow keys, Delete, Home, End
 * Also allows Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X for copy/paste operations
 * 
 * Usage: <input type="number" onkeydown={preventNonNumeric} />
 * 
 * @param e - KeyboardEvent from the input element
 */
export function preventNonNumeric(e: KeyboardEvent): void {
	const allowedKeys = [
		'Backspace',
		'Tab',
		'Enter',
		'Escape',
		'ArrowLeft',
		'ArrowRight',
		'ArrowUp',
		'ArrowDown',
		'Delete',
		'Home',
		'End',
	];
	const isNumber = /^[0-9]$/.test(e.key);
	const isDecimal = e.key === '.' || e.key === ',';
	const isNegative = e.key === '-';

	if (isNumber || isDecimal || isNegative || allowedKeys.includes(e.key)) {
		return; // Allow
	}

	// Allow Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
	if (e.ctrlKey || e.metaKey) {
		return;
	}

	e.preventDefault(); // Block letter keys
}

/**
 * Parses a string input to a number, returning NaN for empty/invalid values.
 * This is useful for validation where empty inputs should show validation errors
 * rather than defaulting to 0.
 * 
 * Usage: parseNumericInput(e.currentTarget.value) // returns number | NaN
 * 
 * @param value - The string value from an input element
 * @returns The parsed number or NaN if empty/invalid
 */
export function parseNumericInput(value: string): number {
	return value === '' ? NaN : parseFloat(value);
}

/**
 * Parses a string input to an integer, returning NaN for empty/invalid values.
 * 
 * Usage: parseIntegerInput(e.currentTarget.value) // returns number | NaN
 * 
 * @param value - The string value from an input element
 * @returns The parsed integer or NaN if empty/invalid
 */
export function parseIntegerInput(value: string): number {
	return value === '' ? NaN : parseInt(value, 10);
}
