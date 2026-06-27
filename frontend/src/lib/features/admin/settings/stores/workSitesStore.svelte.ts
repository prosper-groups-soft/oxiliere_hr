import type { 
  WorkSite, 
  WorkSiteFormState 
} from '../types/workSites.types';


// Default form state
const DEFAULT_FORM_STATE: WorkSiteFormState = {
  name: '',
  latitude: null,
  longitude: null,
  allowed_radius: 100
};


export class WorkSitesStore {
  // PUBLIC STATE
  workSites = $state<WorkSite[]>([]);
  isLoading = $state(false);
  isSaving = $state(false);
  error = $state<Error | null>(null);
  
  // Pagination state
  currentPage = $state(1);
  perPage = $state(8);
  totalCount = $state(0);
  
  // UI state
  showAddForm = $state(false);
  
  // Form state
  formState = $state<WorkSiteFormState>({ ...DEFAULT_FORM_STATE });
  validationErrors = $state<Record<string, string>>({});
  
  // DERIVED STATE
  totalPages = $derived(Math.ceil(this.totalCount / this.perPage) || 1);
  hasWorkSites = $derived(this.workSites.length > 0);
  
  // Form validation
  isFormValid = $derived(() => {
    const errors: Record<string, string> = {};
    
    if (!this.formState.name?.trim()) {
      errors.name = 'Le nom du site est requis';
    }
    
    if (this.formState.latitude === null || isNaN(this.formState.latitude)) {
      errors.latitude = 'La latitude est requise';
    }
    
    if (this.formState.longitude === null || isNaN(this.formState.longitude)) {
      errors.longitude = 'La longitude est requise';
    }
    
    if (this.formState.allowed_radius < 10 || this.formState.allowed_radius > 1000) {
      errors.allowed_radius = 'Le rayon doit être entre 10 et 1000 mètres';
    }
    
    this.validationErrors = errors;
    return Object.keys(errors).length === 0;
  });
  
  // METHODS
  
  /**
   * Set work sites from API response
   */
  setWorkSites(sites: WorkSite[], total: number) {
    this.workSites = sites;
    this.totalCount = total;
  }
  
  /**
   * Add a new work site to the list
   */
  addWorkSite(site: WorkSite) {
    this.workSites = [site, ...this.workSites];
    this.totalCount++;
  }
  
  /**
   * Remove a work site from the list
   */
  removeWorkSite(siteId: string) {
    this.workSites = this.workSites.filter(s => s.id !== siteId);
    this.totalCount = Math.max(0, this.totalCount - 1);
  }
  
  /**
   * Update a work site in the list
   */
  updateWorkSite(siteId: string, updates: Partial<WorkSite>) {
    this.workSites = this.workSites.map(s => 
      s.id === siteId ? { ...s, ...updates } : s
    );
  }
  
  /**
   * Toggle add form visibility
   */
  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.resetForm();
    }
  }
  
  /**
   * Open add form
   */
  openAddForm() {
    this.showAddForm = true;
  }
  
  /**
   * Close add form
   */
  closeAddForm() {
    this.showAddForm = false;
    this.resetForm();
  }
  
  /**
   * Reset form to defaults
   */
  resetForm() {
    this.formState = { ...DEFAULT_FORM_STATE };
    this.validationErrors = {};
  }
  
  /**
   * Update form field
   */
  updateFormField<K extends keyof WorkSiteFormState>(field: K, value: WorkSiteFormState[K]) {
    this.formState = { ...this.formState, [field]: value };
    // Clear validation error for this field
    if (this.validationErrors[field]) {
      const { [field]: _, ...rest } = this.validationErrors;
      this.validationErrors = rest;
    }
  }
  
  /**
   * Get form data for API submission
   */
  getFormData() {
    return {
      name: this.formState.name,
      latitude: this.formState.latitude ?? 0,
      longitude: this.formState.longitude ?? 0,
      allowed_radius: this.formState.allowed_radius
    };
  }
  
  /**
   * Set loading state
   */
  setLoading(loading: boolean) {
    this.isLoading = loading;
  }
  
  /**
   * Set saving state
   */
  setSaving(saving: boolean) {
    this.isSaving = saving;
  }
  
  /**
   * Set error state
   */
  setError(error: Error | null) {
    this.error = error;
  }
  
  /**
   * Set pagination
   */
  setPagination(page: number, perPage: number) {
    this.currentPage = page;
    this.perPage = perPage;
  }
  
  /**
   * Refresh callback - called after pagination changes to trigger refetch
   */
  refreshCallback: (() => void) | null = null;
  
  setRefreshCallback(callback: () => void) {
    this.refreshCallback = callback;
  }
  
  /**
   * Go to next page
   */
  nextPage() {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.refreshCallback?.();
    }
  }
  
  /**
   * Go to previous page
   */
  prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.refreshCallback?.();
    }
  }
  
  /**
   * Go to specific page
   */
  goToPage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.refreshCallback?.();
    }
  }
  
  /**
   * Change per page and reset to page 1
   */
  changePerPage(perPage: number) {
    this.perPage = perPage;
    this.currentPage = 1;
    this.refreshCallback?.();
  }
}


// Singleton export
export const workSitesStore = new WorkSitesStore();

