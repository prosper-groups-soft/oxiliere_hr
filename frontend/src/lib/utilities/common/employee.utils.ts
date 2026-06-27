/**
 * Utility functions for employee-related operations
 */


/**
 * Construit le nom complet d'un employé à partir de ses prénoms et nom
 * 
 * @param employee - Objet employé avec first_name, middle_name (optionnel), last_name
 * @returns Nom complet formaté ou null
 */
export function buildFullName(employee: {
	first_name?: string;
	middle_name?: string | null;
	last_name?: string;
} | null | undefined): string | null {
	if (!employee) return null;
	
	const parts: string[] = [];
	
	if (employee.last_name) {
		parts.push(employee.last_name);
	}
	
	
	if (employee.middle_name) {
		parts.push(employee.middle_name);
	}

	if (employee.first_name) {
		parts.push(employee.first_name);
	}
	
	return parts.length > 0 ? parts.join(' ') : null;
}


/**
 * Formate le nom d'un employé pour affichage (nom complet avec initiales optionnelles)
 * 
 * @param firstName - Prénom
 * @param lastName - Nom de famille
 * @param middleName - Deuxième prénom (optionnel)
 * @returns Nom formaté
 */
export function formatEmployeeName(
	firstName: string,
	lastName: string,
	middleName?: string | null
): string;

/**
 * Formate le nom d'un employé pour affichage (à partir d'un objet employé)
 * 
 * @param employee - Objet employé avec first_name, last_name, middle_name
 * @returns Nom formaté
 */
export function formatEmployeeName(employee: {
	first_name?: string;
	middle_name?: string | null;
	last_name?: string;
} | null | undefined): string;

export function formatEmployeeName(
	arg1: string | { first_name?: string; middle_name?: string | null; last_name?: string } | null | undefined,
	arg2?: string,
	arg3?: string | null
): string {
	// Cas objet employé
	if (typeof arg1 === 'object') {
		if (!arg1) return '';
		const { first_name, last_name, middle_name } = arg1;
		if (!first_name || !last_name) return '';
		if (middle_name) {
			return `${last_name} ${middle_name} ${first_name}`;
		}
		return `${last_name} ${first_name}`;
	}

	// Cas arguments individuels
	const firstName = arg1;
	const lastName = arg2!;
	const middleName = arg3;

	if (middleName) {
		return `${lastName} ${middleName} ${firstName}`;
	}
	return `${lastName} ${firstName}`;
}


/**
 * Retourne les initiales d'un employé
 * 
 * @param firstName - Prénom
 * @param lastName - Nom de famille
 * @returns Initiales (ex: "JD" pour John Doe)
 */
export function getEmployeeInitials(firstName: string, lastName: string): string {
	const first = firstName.charAt(0).toUpperCase();
	const last = lastName.charAt(0).toUpperCase();
	return `${last}${first}`;
}

