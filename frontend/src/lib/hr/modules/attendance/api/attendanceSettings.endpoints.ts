import APIEndPoint from '@/hr/utilities/http/rest';
import type { AttendanceSettings, AttendanceSettingsUpdate } from '../types/attendanceSettings.types';


/**
 * Endpoints API pour les paramètres globaux des pointages
 * Base path: /api/attendance/settings
 *
 * Le singleton AttendanceSettings est accessible via:
 *   GET  /api/attendance/settings  → lit la config
 *   PATCH /api/attendance/settings  → met à jour partiellement
 */
export const attendanceSettingsEndpoint = {
  /**
   * GET /api/attendance/settings
   * Récupère les paramètres globaux des pointages
   */
  getSettings: async (): Promise<AttendanceSettings> => {
    const endpoint = new APIEndPoint(
      '/api/attendance/settings',
      '/api/attendance/settings'
    );
    return await endpoint.list() as unknown as AttendanceSettings;
  },

  /**
   * PATCH /api/attendance/settings
   * Met à jour partiellement les paramètres
   */
  updateSettings: async (data: AttendanceSettingsUpdate): Promise<AttendanceSettings> => {
    const endpoint = new APIEndPoint(
      '/api/attendance/settings',
      '/api/attendance/settings'
    );
    return await endpoint.partial_update(data) as unknown as AttendanceSettings;
  }
};

