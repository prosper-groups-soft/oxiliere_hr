import { browser } from "$app/environment";
import { goto } from "$app/navigation";

/**
 * Extracts the tab parameter from the URL hash or returns the default value.
 * 
 * @param defaultTab - The default tab string to return if no tab parameter is found in the URL
 * @returns The tab string from the URL or the default value
 * 
 * @example
 * // URL: https://example.com/#tab=settings
 * getTab("general") // returns "settings"
 * 
 * // URL: https://example.com/
 * getTab("general") // returns "general"
 */
export function getTab(defaultTab: string): string {
    if (!browser) return defaultTab;
    
    const currentHash = window.location.hash || "";
    const match = currentHash.match(/[?&]?tab=([^&]+)/);
    
    return match ? match[1] : defaultTab;
}

/**
 * Sets the tab parameter in the URL hash while preserving other parameters.
 * 
 * @param tabValue - The value to set for the tab parameter
 * @returns The new URL hash string
 * 
 * @example
 * // URL: https://example.com/#view=list
 * setTab("settings") // sets URL to https://example.com/#view=list&tab=settings
 * 
 * // URL: https://example.com/#tab=general&view=list
 * setTab("settings") // sets URL to https://example.com/#view=list&tab=settings
 */
export function setTab(tabValue: string): string {
    // Get the current hash without the leading #
    const currentHash = window.location.hash.replace(/^#/, "");
    
    // Parse the current hash into a URLSearchParams-like object
    const params = new Map<string, string>();
    if (currentHash) {
        currentHash.split("&").forEach(param => {
            const [key, value] = param.split("=");
            if (key && value) {
                params.set(key, value);
            }
        });
    }
    
    // Set the tab parameter
    params.set("tab", tabValue);
    
    // Build the new hash string
    const newHash = Array.from(params.entries())
        .map(([key, value]) => `${key}=${value}`)
        .join("&");
    
    // Update the URL
    const newUrl = `${window.location.pathname}${window.location.search}#${newHash}`;
    
    goto(newUrl, {
        replaceState: true,
        noScroll: true,
        keepFocus: true
    });
    
    return newHash;
}
