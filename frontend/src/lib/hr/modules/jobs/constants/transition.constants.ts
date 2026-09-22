/**
 * Constants for Employee Transitions (Mobility)
 * Centralized configuration for transition types, colors, and icons
 */

import type { TransitionType } from '../types/types';


/**
 * UI configuration for each transition type
 * Used for badges, icons, and styling across components
 */
export const TRANSITION_TYPE_CONFIG: Record<TransitionType, {
  label: string;
  icon: string;
  color: string;
  bg: string;
  hoverBg: string;
  border: string;
  description: string;
}> = {
  PROMOTION: {
    label: 'Promotion',
    icon: 'trending-up',
    color: 'text-emerald-600',
    bg: 'bg-emerald-50',
    hoverBg: 'hover:bg-emerald-100/50',
    border: 'border-emerald-100',
    description: 'Avancement vers un poste supérieur'
  },
  TRANSFER: {
    label: 'Mutation',
    icon: 'refresh-cw',
    color: 'text-blue-600',
    bg: 'bg-blue-50',
    hoverBg: 'hover:bg-blue-100/50',
    border: 'border-blue-100',
    description: 'Changement de poste ou d\'unité'
  },
  HIRE: {
    label: 'Embauche',
    icon: 'circle-plus',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
    hoverBg: 'hover:bg-purple-100/50',
    border: 'border-purple-100',
    description: 'Nouvelle entrée dans l\'entreprise'
  },
  OFFBOARD: {
    label: 'Départ',
    icon: 'user-minus',
    color: 'text-red-600',
    bg: 'bg-red-50',
    hoverBg: 'hover:bg-red-100/50',
    border: 'border-red-100',
    description: 'Sortie de l\'entreprise'
  }
};


/**
 * Icons for transition type selector in forms
 */
export const TRANSITION_TYPE_ICONS: Record<TransitionType, string> = {
  PROMOTION: 'trending-up',
  TRANSFER: 'refresh-cw',
  HIRE: 'circle-plus',
  OFFBOARD: 'user-minus'
};


/**
 * All transition types as array for iteration
 */
export const TRANSITION_TYPES: TransitionType[] = ['PROMOTION', 'TRANSFER', 'HIRE', 'OFFBOARD'];


/**
 * Transition type options for dropdowns/filters
 * Includes value, label and icon for each type
 */
export const TRANSITION_TYPE_OPTIONS: { 
  value: TransitionType; 
  label: string; 
  icon: string;
  color: string;
}[] = [
  { value: 'PROMOTION', label: 'Promotion', icon: 'trending-up', color: 'text-emerald-600' },
  { value: 'TRANSFER', label: 'Mutation', icon: 'refresh-cw', color: 'text-blue-600' },
  { value: 'HIRE', label: 'Embauche', icon: 'circle-plus', color: 'text-purple-600' },
  { value: 'OFFBOARD', label: 'Départ', icon: 'user-minus', color: 'text-red-600' }
];


/**
 * Helper to get transition config safely
 */
export function getTransitionConfig(type: TransitionType | string) {
  return TRANSITION_TYPE_CONFIG[type as TransitionType] ?? TRANSITION_TYPE_CONFIG.TRANSFER;
}

