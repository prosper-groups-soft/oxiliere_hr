import { 
  validateGroup, 
  validateGroupUpdate 
} from "../../../schemas/schemas";
import { notification } from "@/hr/stores/notification.svelte";
import { getFriendlyErrorMessage } from "@/hr/constants/errors";
import type { Group, GroupCreate } from "../../../types/access.types";


interface ValidationErrors {
  name?: string;
  slug?: string;
  roles?: string;
}


interface UseGroupFormOptions {
  onSuccess: () => void;
  createMutation: { mutateAsync: (data: GroupCreate) => Promise<Group> };
  updateMutation: { mutateAsync: (variables: { slug: string; data: Partial<GroupCreate> }) => Promise<Group> };
}


export function useGroupForm(options: UseGroupFormOptions) {
  let name = $state("");
  let slug = $state("");
  let selectedRoles = $state<string[]>([]);
  let isSubmitting = $state(false);
  let validationErrors = $state<ValidationErrors>({});

  function clearError(field: keyof ValidationErrors) {
    if (validationErrors[field]) {
      validationErrors = { ...validationErrors, [field]: undefined };
    }
  }

  function toggleRole(roleSlug: string) {
    clearError('roles');
    if (selectedRoles.includes(roleSlug)) {
      selectedRoles = selectedRoles.filter(s => s !== roleSlug);
    } else {
      selectedRoles = [...selectedRoles, roleSlug];
    }
  }

  function resetForm(group?: { name: string; slug: string; roles: { slug: string }[] } | null) {
    validationErrors = {};
    if (group) {
      name = group.name;
      slug = group.slug;
      selectedRoles = group.roles.map(r => r.slug);
    } else {
      name = "";
      slug = "";
      selectedRoles = [];
    }
  }

  async function submit(groupSlug?: string) {
    const isEditing = !!groupSlug;
    // Validation avec Zod
    const validation = isEditing
      ? validateGroupUpdate({ name, roles: selectedRoles })
      : validateGroup({ name, slug, roles: selectedRoles });
    
    if (!validation.valid) {
      const errors: ValidationErrors = {};
      validation.errors.forEach(err => {
        if (err.toLowerCase().includes('nom')) errors.name = err;
        else if (err.toLowerCase().includes('identifiant') || err.toLowerCase().includes('slug')) errors.slug = err;
        else if (err.toLowerCase().includes('rôle')) errors.roles = err;
      });
      validationErrors = errors;
      return false;
    }

    validationErrors = {};
    isSubmitting = true;
    
    try {
      if (isEditing && groupSlug) {
        await options.updateMutation.mutateAsync({ 
          slug: groupSlug, 
          data: { name, roles: selectedRoles } 
        });
        notification.toast.success("Groupe mis à jour avec succès.");
      } else {
        await options.createMutation.mutateAsync({ 
          name, 
          slug, 
          roles: selectedRoles 
        });
        notification.toast.success("Groupe créé avec succès.");
      }
      options.onSuccess();
      return true;
    } catch (e: any) {
      notification.toast.error(getFriendlyErrorMessage(e));
      return false;
    } finally {
      isSubmitting = false;
    }
  }

  return {
    // State
    get name() { return name; },
    set name(value: string) { name = value; },
    get slug() { return slug; },
    set slug(value: string) { slug = value; },
    get selectedRoles() { return selectedRoles; },
    get isSubmitting() { return isSubmitting; },
    get validationErrors() { return validationErrors; },
    
    // Actions
    clearError,
    toggleRole,
    resetForm,
    submit
  };
}

