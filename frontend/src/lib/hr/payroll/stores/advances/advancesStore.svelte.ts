import type { Advance, AdvanceStatus, AdvanceRiskLevel, AdvanceCreatePayload, AdvanceUpdatePayload } from '../../types/types';
import { advancesApiStore } from './advances.client.svelte';


export class AdvancesStore {
  advances = $state<Advance[]>([]);
  loading = $state(false);
  error = $state<string | null>(null);

  // ── Recherche (débouncée côté UI, envoyée au backend)
  searchQuery = $state('');

  // ── Dérivés
  pendingAdvances = $derived(
    this.advances.filter(a => a.status === 'PENDING')
  );
  approvedAdvances = $derived(
    this.advances.filter(a => a.status === 'APPROVED' || a.status === 'ACTIVE')
  );
  rejectedAdvances = $derived(
    this.advances.filter(a => a.status === 'REJECTED')
  );
  completedAdvances = $derived(
    this.advances.filter(a => a.status === 'CLOSED')
  );

  pendingAdvancesCount = $derived(this.pendingAdvances.length);
  pendingAdvancesAmount = $derived(
    this.pendingAdvances.reduce((sum, a) => sum + a.amount, 0)
  );
  highRiskAdvancesCount = $derived(
    this.advances.filter(a => a.status === 'PENDING' && a.risk_level === 'HIGH').length
  );

  // ── Filtres (partagés entre la page et AdvanceActions) 
  riskLevelFilters = $state<AdvanceRiskLevel[]>([]);
  statusFilters = $state<AdvanceStatus[]>([]);

  toggleRiskLevel(level: AdvanceRiskLevel) {
    if (this.riskLevelFilters.includes(level)) {
      this.riskLevelFilters = this.riskLevelFilters.filter(l => l !== level);
    } else {
      this.riskLevelFilters = [...this.riskLevelFilters, level];
    }
  }

  toggleStatus(status: AdvanceStatus) {
    if (this.statusFilters.includes(status)) {
      this.statusFilters = this.statusFilters.filter(s => s !== status);
    } else {
      this.statusFilters = [...this.statusFilters, status];
    }
  }

  resetFilters() {
    this.riskLevelFilters = [];
    this.statusFilters = [];
  }

  resetStatusFilters() {
    this.statusFilters = [];
  }

  setSearchQuery(query: string) {
    this.searchQuery = query;
  }

  // Build API params from current store filters
  buildApiParams(): Record<string, string> {
    const params: Record<string, string> = {};
    if (this.searchQuery.trim()) params.search = this.searchQuery.trim();
    if (this.statusFilters.length > 0) params.status = this.statusFilters.join(',');
    if (this.riskLevelFilters.length > 0) params.risk_level = this.riskLevelFilters.join(',');
    return params;
  }

  // ── API 
  async syncFromApi(params?: Record<string, any>) {
    // Merge store filters with any explicit params
    const mergedParams = { ...this.buildApiParams(), ...(params ?? {}) };
    this.loading = true;
    this.error = null;
    try {
      const res = await advancesApiStore.fetchAdvances(mergedParams);
      if (res?.results) {
        this.advances = res.results as Advance[];
      } else {
        this.advances = [];
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors du chargement des avances';
      this.advances = [];
    } finally {
      this.loading = false;
    }
  }

  async requestAdvance(payload: AdvanceCreatePayload): Promise<Advance | null> {
    try {
      const created = await advancesApiStore.createAdvance(payload);
      if (created) {
        this.advances = [created, ...this.advances];
      }
      return created;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de la création de l\'avance';
      throw err;
    }
  }

  async approveAdvance(id: string): Promise<Advance | null> {
    try {
      const updated = await advancesApiStore.approveAdvance(id);
      const index = this.advances.findIndex(a => a.id === id);
      if (updated && index !== -1) {
        this.advances[index] = updated;
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de l\'approbation';
      throw err;
    }
  }

  async rejectAdvance(id: string, reason = ''): Promise<Advance | null> {
    try {
      const updated = await advancesApiStore.rejectAdvance(id, reason);
      const index = this.advances.findIndex(a => a.id === id);
      if (updated && index !== -1) {
        this.advances[index] = updated;
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors du rejet';
      throw err;
    }
  }

  async submitAdvance(id: string): Promise<Advance | null> {
    try {
      const updated = await advancesApiStore.submitAdvance(id);
      const index = this.advances.findIndex(a => a.id === id);
      if (updated && index !== -1) {
        this.advances[index] = updated;
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de la soumission';
      throw err;
    }
  }

  async activateAdvance(id: string): Promise<Advance | null> {
    try {
      const updated = await advancesApiStore.activateAdvance(id);
      const index = this.advances.findIndex(a => a.id === id);
      if (updated && index !== -1) {
        this.advances[index] = updated;
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de l\'activation';
      throw err;
    }
  }

  async updateAdvance(id: string, data: Partial<AdvanceCreatePayload>): Promise<Advance | null> {
    const index = this.advances.findIndex(a => a.id === id);

    try {
      const updated = await advancesApiStore.updateAdvance(id, data);
      if (updated && index !== -1) {
        this.advances[index] = { ...this.advances[index], ...updated };
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de la mise à jour de l\'avance';
      throw err;
    }
  }

  async updateAdvanceConfig(id: string, data: AdvanceUpdatePayload): Promise<Advance | null> {
    const index = this.advances.findIndex(a => a.id === id);

    try {
      const updated = await advancesApiStore.updateAdvanceConfig(id, data);
      if (updated && index !== -1) {
        this.advances[index] = { ...this.advances[index], ...updated };
      }
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Erreur lors de la mise à jour de la configuration';
      throw err;
    }
  }

  moveToStatus(id: string, status: AdvanceStatus) {
    const index = this.advances.findIndex(a => a.id === id);
    if (index === -1) return;
    this.advances[index] = { ...this.advances[index], status };
  }
}


export const advancesStore = new AdvancesStore();

