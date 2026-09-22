import type { Component } from 'svelte';
import type { EmployeeFullProfile } from '@/hr/employees/types/types';
import EmployeeProfileForm from '../info/forms/EmployeeProfileForm.svelte';
import EmployeeContractForm from '../contract/forms/EmployeeContractForm.svelte';


/**
 * Configuration des formulaires d'édition accessibles depuis le header.
 * Chaque onglet du profil peut associer un formulaire (component + métadonnées).
 * Séparé du composant pour respecter le SRP : la config est testable et
 * indépendante de l'UI.
 */

export interface EditFormConfig {
  // Composant Svelte dynamique (formulaire d'édition). Component<any> car les
  // formulaires ont des signatures de props différentes (profil vs contrat).
  component: Component<any>;
  title: string;
  description: string;
  saveLabel: string;
  formId: string;
}

export type EditableTabId = 'profile' | 'contract';

export const EDIT_CONFIG: Record<EditableTabId, EditFormConfig> = {
  profile: {
    component: EmployeeProfileForm,
    title: 'Modifier le profil',
    description: "Mettez à jour les informations d'identité et de contact.",
    saveLabel: 'Enregistrer',
    formId: 'profile-form',
  },
  contract: {
    component: EmployeeContractForm,
    title: 'Modifier le contrat',
    description: "Modifiez les termes du contrat de l'employé.",
    saveLabel: 'Mettre à jour le contrat',
    formId: 'contract-form',
  },
};

/** Onglets qui disposent d'un formulaire d'édition. */
export const EDITABLE_TAB_IDS = Object.keys(EDIT_CONFIG) as EditableTabId[];

/**
 * Retourne la config du formulaire pour un onglet donné.
 * Retourne `undefined` si l'onglet n'a pas de formulaire (état "non disponible").
 */
export function getEditConfig(tabId: string): EditFormConfig | undefined {
  return EDIT_CONFIG[tabId as EditableTabId];
}

export interface EditFormProps {
  employee: EmployeeFullProfile;
  onSave: (data: unknown) => void;
}

