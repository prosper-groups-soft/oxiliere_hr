/**
 * Types pour la configuration globale des pointages (AttendanceSettings)
 * API Endpoints: GET/PATCH /api/attendance/settings
 *
 * Les champs timedelta (late_grace_period, partial_absence_threshold)
 * sont représentés en minutes côté frontend pour une meilleure UX.
 */


// Attendance Settings entity (GET response)
export interface AttendanceSettings {
  /** Tolérance avant d'être considéré en retard (en minutes) */
  late_grace_period: number;
  /** Précision d'arrondi des heures (en minutes) */
  rounding_precision: number;
  /** Seuil de temps manquant pour classer "présence partielle" (en minutes) */
  partial_absence_threshold: number;
}


// Update payload (PATCH body — all fields optional)
export interface AttendanceSettingsUpdate {
  late_grace_period?: number;
  rounding_precision?: number;
  partial_absence_threshold?: number;
}


// Store state
export interface AttendanceSettingsStoreState {
  settings: AttendanceSettings;
  isLoading: boolean;
  isSaving: boolean;
  error: Error | null;
  isDirty: boolean;
}

