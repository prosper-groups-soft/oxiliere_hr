import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { attendanceSettingsEndpoint } from '../api/attendanceSettings.endpoints';
import type { AttendanceSettings, AttendanceSettingsUpdate } from '../types/attendanceSettings.types';


/**
 * Convertit une chaîne ISO 8601 duration en minutes.
 * Gère les formats :
 *   - Django : "P0DT00H11M00S" (avec jours)
 *   - Notre envoi : "PT5M" (sans jours)
 * Si la valeur est déjà un nombre, on la retourne telle quelle.
 */
function parseTimedeltaMinutes(value: unknown): number {
  if (typeof value === 'number') return value;
  if (typeof value !== 'string') return 0;

  // Format ISO 8601: P{n}DT{n}H{n}M{n}S ou PT{n}H{n}M{n}S
  const match = value.match(/P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return 0;

  const days = parseInt(match[1] || '0', 10);
  const hours = parseInt(match[2] || '0', 10);
  const minutes = parseInt(match[3] || '0', 10);
  const seconds = parseInt(match[4] || '0', 10);
  return days * 24 * 60 + hours * 60 + minutes + (seconds >= 30 ? 1 : 0);
}


/**
 * Convertit un nombre de minutes en chaîne ISO 8601 duration (ex: 5 → "PT5M").
 */
function toTimedeltaISO(minutes: number): string {
  return `PT${minutes}M`;
}


/**
 * Normalise les données de l'API : convertit les timedelta en minutes.
 */
function normalizeSettings(raw: any): AttendanceSettings {
  return {
    late_grace_period: parseTimedeltaMinutes(raw.late_grace_period),
    rounding_precision: typeof raw.rounding_precision === 'number'
      ? raw.rounding_precision
      : parseInt(raw.rounding_precision) || 1,
    partial_absence_threshold: parseTimedeltaMinutes(raw.partial_absence_threshold),
  };
}


/**
 * Service pour la configuration globale des pointages (AttendanceSettings).
 * Utilise les endpoints dédiés dans le dossier api/.
 * Aligné avec la documentation API /api/attendance/settings
 */
class AttendanceSettingsService {
  /**
   * GET /api/attendance/settings
   * Récupère les paramètres (timedelta → minutes)
   */
  async getSettings(): Promise<AttendanceSettings> {
    try {
      const raw = await attendanceSettingsEndpoint.getSettings();
      return normalizeSettings(raw);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/attendance/settings
   * Met à jour les paramètres (minutes → timedelta ISO)
   */
  async updateSettings(data: AttendanceSettingsUpdate): Promise<AttendanceSettings> {
    try {
      // Convertir les minutes en timedelta ISO 8601 pour l'API
      const payload: Record<string, unknown> = {};
      if (data.late_grace_period !== undefined) {
        payload.late_grace_period = toTimedeltaISO(data.late_grace_period);
      }
      if (data.rounding_precision !== undefined) {
        payload.rounding_precision = data.rounding_precision;
      }
      if (data.partial_absence_threshold !== undefined) {
        payload.partial_absence_threshold = toTimedeltaISO(data.partial_absence_threshold);
      }

      const raw = await attendanceSettingsEndpoint.updateSettings(payload as AttendanceSettingsUpdate);
      notification.toast.success('Paramètres de pointage mis à jour');
      return normalizeSettings(raw);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const attendanceSettingsService = new AttendanceSettingsService();
