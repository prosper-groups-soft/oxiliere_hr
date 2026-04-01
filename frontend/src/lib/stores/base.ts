import type { CurrentOrganization } from '@/types/organization';
import { writable, type Writable } from 'svelte/store';
import { browser } from '$app/environment';


/**
 * Retrieves the organization slug to serve as a namespace.
 */
export function get_application_namespace(org?: CurrentOrganization): string | undefined {
  return org?.slug ? org?.slug : undefined;
}

/**
 * Generates a unique key prefixed by the namespace (e.g., "my-org:user-prefs").
 */
function get_storage_key(key: string, org?: CurrentOrganization): string {
  const namespace = get_application_namespace(org);
  return namespace ? `${namespace}:${key}` : key;
}

/**
 * Creates a persistent Svelte store synchronized across tabs.
 */
export function createPersistentStore<T>(
  key: string, 
  initialValue: T, 
  org?: CurrentOrganization
): Writable<T> {
  // Initialize standard Svelte store
  const wstore: Writable<T> = writable(initialValue);

  if (browser) {
    const fullKey = get_storage_key(key, org);

    // 1. Load value from localStorage on startup
    try {
      const storedValue = localStorage.getItem(fullKey);
      if (storedValue !== null) {
        wstore.set(JSON.parse(storedValue));
      }
    } catch (err) {
      console.warn(`localStorage read error for "${fullKey}":`, err);
    }

    // 2. Listen for changes from other tabs (Multi-tab sync)
    const onStorageChange = (event: StorageEvent) => {
      if (event.key === fullKey && event.newValue !== null) {
        try {
          wstore.set(JSON.parse(event.newValue));
        } catch (err) {
          console.error("Multi-tab sync error:", err);
        }
      }
    };

    window.addEventListener('storage', onStorageChange);

    // 3. Automatically save every store change to localStorage
    wstore.subscribe((value) => {
      try {
        localStorage.setItem(fullKey, JSON.stringify(value));
      } catch (err) {
        console.error(`localStorage write error for "${fullKey}":`, err);
      }
    });
  }

  return wstore;
}

