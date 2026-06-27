/**
 * Constants for Organizational Units (OrgUnit, NodeType)
 * Centralized configuration for org unit types, icons, and styling
 */

/**
 * Icons for organizational unit types (OrgUnit, NodeType)
 * Centralized to avoid duplication across components
 */
export const ORG_UNIT_ICONS: Record<string, string> = {
	DEPARTMENT: 'business',
	DIVISION: 'corporate_fare',
	TEAM: 'team',
	FUNCTION: 'settings',
	BRANCH: 'store',
	PROJECT: 'folder'
};

/**
 * Get icon for an organizational unit type
 * @param type - The org unit type (e.g., 'DEPARTMENT', 'TEAM')
 * @returns The icon name, defaults to 'business' if type not found
 */
export function getOrgUnitIcon(type: string): string {
	return ORG_UNIT_ICONS[type] ?? 'business';
}
