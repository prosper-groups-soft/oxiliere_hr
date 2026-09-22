import type { AdvanceStatus } from "../types/types";

/**
 * Onglets de statut des avances (remplacent les colonnes kanban).
 * 'Tous' affiche toutes les avances ; les autres filtrent par statut.
 */
export type AdvanceStatusTab = 'Tous' | AdvanceStatus;


export const ADVANCE_STATUS_TABS: { key: AdvanceStatusTab; label: string }[] = [
  { key: 'Tous', label: 'Toutes' },
  { key: 'DRAFT', label: 'Brouillons' },
  { key: 'PENDING', label: 'En attente' },
  { key: 'APPROVED', label: 'Approuvées' },
  { key: 'ACTIVE', label: 'Actives' },
  { key: 'REJECTED', label: 'Rejetées' },
  { key: 'CLOSED', label: 'Soldées' },
];

