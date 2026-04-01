import {
	APP_STORAGE_KEY,
	DEFAULT_SETTINGS,
	type UserSettings
} from '@/constants/features/navigation';


class SettingsStore {
	// Reactive state initialized with default values
	current = $state<UserSettings>(DEFAULT_SETTINGS);

	constructor() {
		// Retrieval on startup (client-side only to avoid SSR errors)
		if (typeof window !== 'undefined') {
			const saved = localStorage.getItem(APP_STORAGE_KEY);
			if (saved) {
				try {
					// Merge saved settings with defaults (for safety)
					this.current = { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
				} catch (e) {
					console.error('Failed to parse settings', e);
				}
			}

			// Root effect: monitors any change in 'current' to persist data
			$effect.root(() => {
				$effect(() => {
					localStorage.setItem(APP_STORAGE_KEY, JSON.stringify(this.current));
				});
			});
		}
	}

	/**
	 * Updates a specific settings property
	 */
	update<K extends keyof UserSettings>(key: K, value: UserSettings[K]) {
		this.current[key] = value;
	}
}


export const settings = new SettingsStore();
