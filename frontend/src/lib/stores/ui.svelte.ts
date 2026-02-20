import { settings } from "./settings.svelte";
import { type Snippet } from "svelte";


// --- VOLATILE STATES (Reset on page refresh) ---
class UiStore {
  // Selected menu ID (updated by the Root Layout based on the URL)
  selectedMenuItem = $state<string | null>("home");
  // Global title actions
  pageActions = $state<Snippet | null>(null);
  
  // Initial application loading state
  initialLoading = $state(true);

  // --- PERSISTENT STATES (Shortcuts to the settings store) ---
  
  /**
   * Getter to retrieve the sidebar expansion state
   */
  get isExpanded() {
    return settings.current.sidebarExpanded;
  }

  /**
   * Setter to modify the expansion state (auto-saved via settings)
   */
  setExpanded(val: boolean) {
    settings.update('sidebarExpanded', val);
  }

  /**
   * Setter to modify the global actions shown in page title
   */
  setActions(actions: Snippet | null) {
    this.pageActions = actions;
  }
}


export const ui = new UiStore();
