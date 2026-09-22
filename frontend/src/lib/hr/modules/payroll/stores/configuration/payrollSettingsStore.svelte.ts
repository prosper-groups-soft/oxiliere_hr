import { notification } from '@/hr/stores/notification.svelte';
import { payrollConfigStore } from './payrollConfigStore.svelte';
import type { PayrollConfiguration, PayrollAdjustmentConfig } from '../../types/types';


/** Type de champ éditable d'une configuration de paie */
export type EditableConfigField = keyof PayrollConfiguration;

/** État de chargement global de la page */
export type SettingsViewState = 'loading' | 'success' | 'error' | 'offline';


/**
 * Store dédié à l'écran "Paramètres de paie" (payroll-settings).
 *
 * Responsabilité unique : orchestrer l'édition locale, la sauvegarde et
 * l'annulation de la configuration de paie, en s'appuyant sur `payrollConfigStore`
 * (couche API + données partagées). La page ne fait que lire ce store et
 * déléguer les événements UI.
 */
class PayrollSettingsStore {
  /** Onglet actif */
  activeTab = $state<'general' | 'legal' | 'fiscal' | 'catalog'>('general');
  activeTabIndex = $state(0);

  /** État de chargement de la configuration */
  viewState = $state<SettingsViewState>('loading');

  /** État de sauvegarde en cours */
  isSaving = $state(false);

  /** Message d'erreur de sauvegarde (affiché en inline + toast) */
  saveError = $state<string | null>(null);

  /** Configuration locale en édition (les changements ne sont appliqués qu'à la sauvegarde) */
  draftConfig = $state<PayrollConfiguration | null>(null);

  /** Liste des onglets (label + icône) */
  readonly tabs = [
    { id: 'general' as const, label: 'Général', icon: 'settings' },
    { id: 'legal' as const, label: 'Paramètres légaux', icon: 'scale' },
    { id: 'fiscal' as const, label: 'Barème fiscal', icon: 'receipt' },
    { id: 'catalog' as const, label: 'Éléments de paie', icon: 'book-open' },
  ];

  /** SMIG actif (le plus récent marqué actif) */
  readonly activeSMIG = $derived(
    payrollConfigStore.smigRates.find((s) => s.is_active) ?? payrollConfigStore.smigRates[0] ?? null
  );

  /** Charge la configuration depuis l'API et initialise le brouillon local */
  async load(): Promise<void> {
    this.viewState = 'loading';
    try {
      await payrollConfigStore.syncConfiguration();
      this.draftConfig = payrollConfigStore.configuration
        ? { ...payrollConfigStore.configuration }
        : null;
      this.viewState = 'success';
    } catch {
      this.viewState = 'error';
    }
  }

  /** Met à jour un champ du brouillon local */
  updateDraft(field: keyof PayrollConfiguration, value: string | number | boolean | null): void {
    if (!this.draftConfig) return;
    this.draftConfig = { ...this.draftConfig, [field]: value as never };
  }

  /** Sauvegarde la configuration via PATCH /payroll/configuration */
  async save(): Promise<void> {
    if (!this.draftConfig) return;
    this.isSaving = true;
    this.saveError = null;
    try {
      const updated = await payrollConfigStore.saveConfiguration({
        currency: this.draftConfig.currency,
        default_payment_method: this.draftConfig.default_payment_method,
        work_hours_per_week: this.draftConfig.work_hours_per_week,
        exchange_rate_usd_cdf: this.draftConfig.exchange_rate_usd_cdf,
        // --- Déduction des absences (mode exclusif) ---
        leave_deduction_mode: this.draftConfig.leave_deduction_mode,
        leave_deduction_divisor: this.draftConfig.leave_deduction_divisor,
        fixed_deduction_per_absent_day:
          this.draftConfig.fixed_deduction_per_absent_day ?? null,
      });
      // Re-synchronise le brouillon avec la réponse backend (valeurs normalisées)
      if (updated) {
        this.draftConfig = { ...updated };
      }
      notification.toast.success('Paramètres de paie enregistrés');
    } catch (e: any) {
      this.saveError = e?.message ?? 'Une erreur est survenue lors de la sauvegarde.';
      notification.toast.error(
        this.saveError ?? 'Une erreur est survenue lors de la sauvegarde.'
      );
    } finally {
      this.isSaving = false;
    }
  }

  /** Annule les modifications : re-synchronise le brouillon depuis le store */
  cancel(): void {
    this.draftConfig = payrollConfigStore.configuration
      ? { ...payrollConfigStore.configuration }
      : null;
    this.saveError = null;
    notification.toast.info('Modifications annulées');
  }

  /** Bascule l'état actif d'un élément du catalogue */
  async toggleAdjustment(adjustment: PayrollAdjustmentConfig, isActive: boolean): Promise<void> {
    try {
      await payrollConfigStore.toggleAdjustmentActive(adjustment.id, isActive);
      notification.toast.success(isActive ? 'Élément activé' : 'Élément désactivé');
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de mettre à jour l'élément.";
      this.saveError = msg;
      notification.toast.error(msg);
    }
  }

  /** Crée un nouvel élément du catalogue */
  async createAdjustment(data: Partial<PayrollAdjustmentConfig>): Promise<boolean> {
    try {
      await payrollConfigStore.createAdjustment(data);
      notification.toast.success('Élément créé');
      return true;
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de créer l'élément.";
      this.saveError = msg;
      notification.toast.error(msg);
      return false;
    }
  }

  /** Met à jour un élément du catalogue */
  async updateAdjustment(adjustmentId: string, data: Partial<PayrollAdjustmentConfig>): Promise<boolean> {
    try {
      await payrollConfigStore.updateAdjustment(adjustmentId, data);
      notification.toast.success('Élément mis à jour');
      return true;
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de mettre à jour l'élément.";
      this.saveError = msg;
      notification.toast.error(msg);
      return false;
    }
  }

  /** Supprime un élément du catalogue */
  async deleteAdjustment(adjustmentId: string): Promise<boolean> {
    try {
      await payrollConfigStore.deleteAdjustment(adjustmentId);
      notification.toast.success('Élément supprimé');
      return true;
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de supprimer l'élément.";
      this.saveError = msg;
      notification.toast.error(msg);
      return false;
    }
  }

  /** Met à jour une règle d'heures supplémentaires */
  async updateOvertimeRule(ruleId: string, data: { multiplier: number }): Promise<void> {
    try {
      await payrollConfigStore.saveOvertimeRule(ruleId, data);
      notification.toast.success("Règle d'heures supplémentaires mise à jour");
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de mettre à jour la règle d'heures supplémentaires.";
      this.saveError = msg;
      notification.toast.error(msg);
    }
  }

  /** Met à jour une allocation légale (montant ou %) */
  async updateAllowance(allowanceId: string, data: { base_amount: number | null }): Promise<void> {
    try {
      await payrollConfigStore.saveLegalAllowance(allowanceId, data);
      notification.toast.success('Allocation mise à jour');
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de mettre à jour l'allocation.";
      this.saveError = msg;
      notification.toast.error(msg);
    }
  }

  /** Réinitialise les allocations légales depuis les fixtures */
  async resetAllowances(): Promise<void> {
    try {
      await payrollConfigStore.resetLegalAllowances();
      notification.toast.success('Allocations légales réinitialisées');
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de réinitialiser les allocations.";
      this.saveError = msg;
      notification.toast.error(msg);
    }
  }

  /** Réinitialise le catalogue d'éléments de paie depuis la fixture */
  async resetAdjustments(): Promise<void> {
    try {
      await payrollConfigStore.resetAdjustments();
      notification.toast.success('Catalogue d\'éléments de paie réinitialisé');
    } catch (e: any) {
      const msg = e?.message ?? "Impossible de réinitialiser le catalogue.";
      this.saveError = msg;
      notification.toast.error(msg);
    }
  }

  /** Force la valeur de l'onglet actif */
  setTab(value: string): void {
    this.activeTab = value as typeof this.activeTab;
    this.activeTabIndex = this.tabs.findIndex((t) => t.id === value);
  }
}


/** Instance singleton du store des paramètres de paie */
export const payrollSettingsStore = new PayrollSettingsStore();
