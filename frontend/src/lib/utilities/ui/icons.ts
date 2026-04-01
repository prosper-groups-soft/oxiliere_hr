import { APPS_ICON } from '@/constants/ui/icons';
import type { Component } from 'svelte';
import { Package, type IconProps } from '@lucide/svelte';

type Icon = Component<IconProps, {}>;

/**
 *
 * Get the application icon by its name/codename
 * @param appName - Name or codename of the application
 * @param fallback - Default icon if matching is found
 * @returns Lucide icon matching
 */
export function getAppIcon(appName: string, fallback: Icon = Package): Icon {
	if (!appName) return fallback;

	// Normalize the name (miniscules, remplace spaces and spcial caracters by the hyphens)
	const normalizedName = appName
		.toLowerCase()
		.trim()
		.replace(/[\s_\.]+/g, '-')
		.replace(/[^\w-]/g, '');

	// Search first the corresponding name
	if (APPS_ICON[normalizedName]) {
		return APPS_ICON[normalizedName];
	}

	// Search the orginal name in minuscules
	const lowerName = appName.toLowerCase().trim();
	if (APPS_ICON[lowerName]) {
		return APPS_ICON[lowerName];
	}

	// Search the partials keys words
	const keywords = normalizedName.split('-');
	for (const keyword of keywords) {
		if (keyword.length > 2 && APPS_ICON[keyword]) {
			return APPS_ICON[keyword];
		}
	}

	// Return the default icon
	return fallback;
}

/**
 * Verify if the icon exists in a specific app
 * @param appName - Name or codename of the application
 * @returns true if the specific icon exists
 */
export function hasAppIcon(appName: string): boolean {
	if (!appName) return false;

	const normalizedName = appName
		.toLowerCase()
		.trim()
		.replace(/[\s_\.]+/g, '-')
		.replace(/[^\w-]/g, '');

	return !!(APPS_ICON[normalizedName] || APPS_ICON[appName.toLowerCase().trim()]);
}
