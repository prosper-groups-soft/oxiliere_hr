<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Label } from "@/components/ui/label";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { slide } from "svelte/transition";
  import type { User } from "../../types/user.types";
  import { Badge } from "@/components/ui/badge";
  import PermissionMatrix from "../../../access/components/PermissionMatrix.svelte";
  import { getAvatarColors } from "../../utilities/avatar.utils";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";

  interface Props {
    user: User;
    onClose?: () => void;
    onSave?: (userId: string | number, data: { isActive: boolean }) => void;
  }

  let { user, onClose, onSave }: Props = $props();

  let isActive = $state(true);
  let hasChanges = $state(false);

  // Sync local state when user prop changes
  $effect(() => {
    isActive = user.isActive;
    hasChanges = false;
  });

  function handleSave() {
    onSave?.(user.id, { isActive });
    hasChanges = false;
  }

  $effect(() => {
    if (isActive !== user.isActive) {
      hasChanges = true;
    }
  });

  // Helper for avatar initials
  const initials = $derived(`${user.firstName?.[0] || ''}${user.lastName?.[0] || ''}` || 'U');
  const avatarColors = $derived(getAvatarColors('EMPLOYEE')); // Defaulting for now
</script>


<div class="h-full flex flex-col">
  <!-- Header -->
  <div class="flex items-center justify-between p-2 border-b border-slate-100 shrink-0 sticky top-0 bg-white z-10">
    <div class="flex items-center gap-3">
      <div class="w-12 h-12 rounded-full {avatarColors.bg} {avatarColors.text} {avatarColors.border} border flex items-center justify-center font-semibold text-[0.9rem]">
        {initials}
      </div>
      <div>
        <h3 class="font-semibold text-slate-900 text-[0.875rem]">{user.firstName} {user.lastName}</h3>
        <p class="text-[0.84rem] text-slate-500">{user.email}</p>
      </div>
    </div>
    <button
      onclick={onClose}
      class="w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center text-slate-500 transition-colors cursor-pointer"
    >
      <AppIcon name="x" size={18} />
    </button>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-y-auto p-4">
    <div class="grid grid-cols-2 gap-6">
      <!-- Left Column - Base Config -->
      <div class="space-y-6">
        <!-- Status -->
        <div class="space-y-2">
          <Label class="text-[0.75rem] font-bold text-slate-700 uppercase tracking-wider">
            Statut du compte
          </Label>
          <div class="flex items-center gap-3 p-3 rounded-xl border border-slate-200 bg-white shadow-fine">
            <button
              aria-label={isActive ? "Désactiver le compte" : "Activer le compte"}
              class={`
                relative w-10 h-5.5 rounded-full transition-colors cursor-pointer
                ${isActive ? 'bg-indigo-600' : 'bg-slate-300'}
              `}
              onclick={() => isActive = !isActive}
            >
              <span
                class={`
                  absolute top-0.75 left-0.75 w-4 h-4 bg-white rounded-full shadow-sm transition-transform
                  ${isActive ? 'translate-x-4.5' : 'translate-x-0'}
                `}
              >
              </span>
            </button>
            <div>
              <div class="font-semibold text-slate-900 text-[0.85rem]">{isActive ? 'Actif' : 'Inactif'}</div>
              <div class="text-[0.8rem] text-slate-500">
                {isActive ? 'Connexion autorisée' : 'Connexion bloquée'}
              </div>
            </div>
          </div>
        </div>

        <!-- Groups -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
             <Label class="text-[0.75rem] font-bold text-slate-700 uppercase tracking-wider">Groupes de Permissions</Label>
             <button class="text-[0.7rem] text-indigo-600 font-medium hover:underline">Gérer</button>
          </div>
          <div class="flex flex-wrap gap-2">
             {#each user.groups as group}
               <Badge class="bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-indigo-100 px-3 py-1">
                 {group}
               </Badge>
             {/each}
             {#if user.groups.length === 0}
               <div class="w-full">
                 <Empty 
                    title="Aucun groupe" 
                    description="Cet utilisateur n'appartient à aucun groupe." 
                    icon="users"
                    iconSize={24}
                 />
               </div>
             {/if}
          </div>
        </div>

        <!-- Meta Info -->
        <div class="space-y-2 pt-2 border-t border-slate-100">
           <div class="flex justify-between text-[0.8rem]">
              <span class="text-slate-500">Créé le :</span>
              <span class="text-slate-700 font-medium">{typeof user.createdAt === 'string' ? new Date(user.createdAt).toLocaleDateString() : user.createdAt?.toLocaleDateString() || '-'}</span>
           </div>
           <div class="flex justify-between text-[0.8rem]">
              <span class="text-slate-500">Dernière connexion :</span>
              <span class="text-slate-700 font-medium">{typeof user.lastLogin === 'string' ? new Date(user.lastLogin).toLocaleDateString() : user.lastLogin?.toLocaleDateString() || 'Jamais'}</span>
           </div>
        </div>
      </div>

      <!-- Right Column - Permissions Matrix -->
      <div class="flex flex-col h-full min-h-[400px]">
        <div class="flex items-center gap-2 mb-3">
           <Label class="text-[0.75rem] font-bold text-slate-700 uppercase tracking-wider">Matrice des Permissions</Label>
           <div class="h-px flex-1 bg-slate-100"></div>
        </div>
        
        <div class="flex-1 min-w-0">
           <PermissionMatrix {user} />
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  {#if hasChanges}
    <div 
      transition:slide={{ duration: 200 }}
      class="p-4 py-3 border-t border-slate-200 bg-slate-50 flex justify-end gap-3 shrink-0 sticky bottom-0"
    >
      <Button variant="outline" onclick={() => { isActive = user.isActive; hasChanges = false; }} class="h-9">
        Annuler
      </Button>
      <Button onclick={handleSave} class="h-9 bg-indigo-600 hover:bg-indigo-700 shadow-sm">
        <AppIcon name="check" size={16} class="mr-2" />
        Enregistrer les modifications
      </Button>
    </div>
  {/if}
</div>

