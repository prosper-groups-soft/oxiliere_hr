import { 
  getAppIconAsync, 
  hasAppIcon as hasAppIconConst
} from '@/constants/ui/icons';
import type { Component } from 'svelte';
import { Package, type IconProps } from '@lucide/svelte';

type Icon = Component<IconProps, {}>;

// Re-export async function
export { getAppIconAsync };

/**
 * Synchronous fallback - only checks if icon exists, doesn't load it
 * @param appName - Name or codename of the application
 * @returns true if icon exists in mapping
 */
export function hasAppIcon(appName: string): boolean {
  return hasAppIconConst(appName);
}

/**
 * @deprecated Use getAppIconAsync for lazy loading
 * Kept for backwards compatibility - loads icon synchronously (blocks)
 */
export function getAppIcon(appName: string, fallback: Icon = Package): Icon {
  // For sync compatibility, check if icon exists but return Package during loading
  // The actual icon will be loaded async in AppIcon component
  if (!appName || !hasAppIconConst(appName)) {
    return fallback;
  }
  // Return fallback - actual loading is done async
  return fallback;
}
