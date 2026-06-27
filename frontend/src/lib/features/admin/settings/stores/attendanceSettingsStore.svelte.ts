import type { AttendanceSettings, AttendanceSettingsUpdate } from '../types/attendance.types';
import { attendanceSettingsService } from '../services/attendance.service';


/**
 * Interface locale pour représenter un champ en édition.
 * late_grace_period et partial_absence_threshold sont en minutes.
 * rounding_precision est un entier.
 */
interface SettingsFormFields {
  late_grace_period: number;
  partial_absence_threshold: number;
  rounding_precision: number;
}


/** Valeurs par défaut du modèle Django (tirées de AttendanceSettings) */
const DEFAULT_VALUES: AttendanceSettings = {
  late_grace_period: 5,
  partial_absence_threshold: 30,
  rounding_precision: 1,
};


export class AttendanceSettingsStore {
  // PUBLIC STATE
  settings = $state<AttendanceSettings>({
    late_grace_period: 5,
    partial_absence_threshold: 30,
    rounding_precision: 1,
  });

  formFields = $state<SettingsFormFields>({
    late_grace_period: 5,
    partial_absence_threshold: 30,
    rounding_precision: 1,
  });

  isLoading = $state(false);
  isSaving = $state(false);
  error = $state<Error | null>(null);

  // DERIVED
  isDirty = $derived(
    this.formFields.late_grace_period !== this.settings.late_grace_period ||
    this.formFields.partial_absence_threshold !== this.settings.partial_absence_threshold ||
    this.formFields.rounding_precision !== this.settings.rounding_precision
  );

  /** Vrai si les valeurs actuelles diffèrent des valeurs par défaut */
  isNotDefault = $derived(
    this.settings.late_grace_period !== DEFAULT_VALUES.late_grace_period ||
    this.settings.partial_absence_threshold !== DEFAULT_VALUES.partial_absence_threshold ||
    this.settings.rounding_precision !== DEFAULT_VALUES.rounding_precision
  );

  // METHODS

  /**
   * Charge les paramètres depuis l'API et met à jour le store.
   */
  async load(): Promise<void> {
    this.isLoading = true;
    this.error = null;
    try {
      const data = await attendanceSettingsService.getSettings();
      this.settings = data;
      this.formFields = {
        late_grace_period: data.late_grace_period,
        partial_absence_threshold: data.partial_absence_threshold,
        rounding_precision: data.rounding_precision,
      };
    } catch (err: any) {
      this.error = err;
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Sauvegarde les champs modifiés via l'API.
   */
  async save(): Promise<void> {
    if (!this.isDirty) return;

    this.isSaving = true;
    this.error = null;
    try {
      const payload: AttendanceSettingsUpdate = {};

      if (this.formFields.late_grace_period !== this.settings.late_grace_period) {
        payload.late_grace_period = this.formFields.late_grace_period;
      }
      if (this.formFields.partial_absence_threshold !== this.settings.partial_absence_threshold) {
        payload.partial_absence_threshold = this.formFields.partial_absence_threshold;
      }
      if (this.formFields.rounding_precision !== this.settings.rounding_precision) {
        payload.rounding_precision = this.formFields.rounding_precision;
      }

      const updated = await attendanceSettingsService.updateSettings(payload);
      this.settings = updated;
      this.formFields = {
        late_grace_period: updated.late_grace_period,
        partial_absence_threshold: updated.partial_absence_threshold,
        rounding_precision: updated.rounding_precision,
      };
    } catch (err: any) {
      this.error = err;
    } finally {
      this.isSaving = false;
    }
  }

  /**
   * Remet les champs du formulaire à la dernière version sauvegardée.
   */
  reset() {
    this.formFields = {
      late_grace_period: this.settings.late_grace_period,
      partial_absence_threshold: this.settings.partial_absence_threshold,
      rounding_precision: this.settings.rounding_precision,
    };
  }

  /**
   * Réinitialise tous les paramètres aux valeurs par défaut via l'API.
   */
  async resetToDefaults(): Promise<void> {
    this.isSaving = true;
    this.error = null;
    try {
      const updated = await attendanceSettingsService.updateSettings({
        late_grace_period: DEFAULT_VALUES.late_grace_period,
        partial_absence_threshold: DEFAULT_VALUES.partial_absence_threshold,
        rounding_precision: DEFAULT_VALUES.rounding_precision,
      });
      this.settings = updated;
      this.formFields = {
        late_grace_period: updated.late_grace_period,
        partial_absence_threshold: updated.partial_absence_threshold,
        rounding_precision: updated.rounding_precision,
      };
    } catch (err: any) {
      this.error = err;
    } finally {
      this.isSaving = false;
    }
  }
}


// Singleton export
export const attendanceSettingsStore = new AttendanceSettingsStore();
