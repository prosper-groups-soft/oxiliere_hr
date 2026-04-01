<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Checkbox } from "@/components/ui/checkbox";
  import { accessStore } from "../../stores/accessStore.svelte";
  import type { Group } from "../../types/access.types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";

  interface Props {
    open: boolean;
    group?: Group | null;
  }

  let { open = $bindable(false), group }: Props = $props();

  let name = $state("");
  let slug = $state("");
  let selectedRoles = $state<string[]>([]);
  let isSubmitting = $state(false);

  const isEdit = $derived(!!group);

  // Sync state when dialog opens or group changes
  $effect(() => {
    if (open) {
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
  });

  function toggleRole(roleSlug: string) {
    if (selectedRoles.includes(roleSlug)) {
      selectedRoles = selectedRoles.filter(s => s !== roleSlug);
    } else {
      selectedRoles = [...selectedRoles, roleSlug];
    }
  }

  async function handleSubmit() {
    if (!name || (!isEdit && !slug)) {
      notification.toast.error("Veuillez remplir tous les champs obligatoires.");
      return;
    }

    isSubmitting = true;
    try {
      if (isEdit) {
        await accessStore.updateGroup(group!.slug, { name, roles: selectedRoles });
        notification.toast.success("Groupe mis à jour avec succès.");
      } else {
        await accessStore.createGroup({ name, slug, roles: selectedRoles });
        notification.toast.success("Groupe créé avec succès.");
      }
      open = false;
    } catch (e: any) {
      notification.toast.error(e.message || "Erreur lors de l'enregistrement du groupe.");
    } finally {
      isSubmitting = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold">
        {isEdit ? 'Modifier le groupe' : 'Nouveau groupe'}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar">
      <div class="space-y-4">
        <div class="space-y-4">
          <div class="space-y-1.5">
            <Label for="group-name">Nom du groupe</Label>
            <Input 
              id="group-name" 
              bind:value={name} 
              placeholder="ex: Managers RH" 
              class="h-10 bg-white shadow-fine"
            />
          </div>

          <div class="space-y-1.5">
            <Label for="group-slug">Identifiant (Slug)</Label>
            <div class="relative">
              <Input 
                id="group-slug" 
                bind:value={slug} 
                disabled={isEdit} 
                placeholder="ex: hr_managers" 
                class="h-10 text-[0.85rem] bg-white shadow-fine"
              />
              {#if isEdit}
                <div class="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                  <AppIcon name="lock" size={14} class="text-slate-400" />
                </div>
              {/if}
            </div>
            {#if !isEdit}
              <p class="text-[0.8rem] text-slate-500 flex items-center gap-1.5 mt-1 ml-1">
                <AppIcon name="alert-circle" size={14} />
                L'identifiant unique ne peut plus être modifié après la création.
              </p>
            {/if}
          </div>
        </div>
      </div>

      <!-- Roles Selection Section -->
      <div class="space-y-4">
        <Label>
          <AppIcon name="users" size={16} class="text-indigo-500" />
          Sélection des rôles
        </Label>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4 rounded-xl border border-slate-200 bg-slate-50/30 shadow-fine">
          {#each accessStore.roles as role}
            <div 
              class="flex items-center space-x-3 p-2.5 rounded-lg border transition-all cursor-pointer group"
              class:bg-indigo-50={selectedRoles.includes(role.slug)}
              class:border-indigo-200={selectedRoles.includes(role.slug)}
              class:border-transparent={!selectedRoles.includes(role.slug)}
              class:hover:bg-slate-100={!selectedRoles.includes(role.slug)}
              onclick={() => toggleRole(role.slug)}
              role="none"
            >
              <Checkbox 
                id="role-{role.slug}" 
                checked={selectedRoles.includes(role.slug)} 
                class="data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-600 h-4 w-4 rounded-sm"
              />
              <div class="space-y-0.5">
                <p class="text-[0.86rem] font-semibold text-slate-800 leading-none">
                  {role.name}
                </p>
                <p class="text-[0.82rem] text-slate-500">
                  {role.slug}
                </p>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-5 border-t flex flex-row gap-3">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9">Annuler</Button>
      </Sheet.Close>
      <Button 
        onclick={handleSubmit} 
        disabled={isSubmitting}
        class="flex-1 h-9 bg-primary text-white font-medium"
      >
        {#if isSubmitting}
          <div class="animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full"></div>
        {:else}
          <AppIcon name="check" size={17} />
        {/if}
        {isEdit ? 'Enregistrer' : 'Créer le groupe'}
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

