<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { fade } from "svelte/transition";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { useGroupForm } from "./useGroupForm.svelte";
  import RoleItem from "./RoleItem.svelte";
  import MemberManager from "./MemberManager.svelte";
  import type { Group } from "../../../types/access.types";
  import ValidationError from "@/components/ui/validation-error/ValidationError.svelte";
  import { 
    useRolesQuery, 
    useCreateGroupMutation, 
    useUpdateGroupMutation 
  } from "../../../queries/accessQueries.svelte";


  interface Props {
    open: boolean;
    group?: Group | null;
  }

  
  let { open = $bindable(false), group }: Props = $props();

  // TanStack Queries & Mutations
  const rolesQuery = useRolesQuery();
  const createGroupMutation = useCreateGroupMutation();
  const updateGroupMutation = useUpdateGroupMutation();

  // Derived
  const isEdit = $derived(!!group);
  const roles = $derived($rolesQuery.data ?? []);

  // Form logic with mutations (dereferenced stores)
  const form = useGroupForm({
    onSuccess: () => { open = false; },
    createMutation: $createGroupMutation,
    updateMutation: $updateGroupMutation
  });

  // UI State
  let expandedRoles = $state<Set<string>>(new Set());
  let expandedScopes = $state<Set<string>>(new Set());
  let wasOpen = $state(false);

  // Handle sheet open/close
  $effect(() => {
    if (open && !wasOpen) {
      wasOpen = true;
      form.resetForm(group);
    } else if (!open) {
      wasOpen = false;
    }
  });

  function toggleRoleExpanded(roleSlug: string, e: Event) {
    e.stopPropagation();
    const newSet = new Set(expandedRoles);
    if (newSet.has(roleSlug)) {
      newSet.delete(roleSlug);
    } else {
      newSet.add(roleSlug);
    }
    expandedRoles = newSet;
  }

  async function handleSubmit() {
    await form.submit(group?.slug);
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-2.5 border-b border-b-slate-100 bg-slate-50/60">
      <Sheet.Title class="text-[1rem] font-bold">
        {isEdit ? 'Gérer le groupe' : 'Nouveau groupe'}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar">
      <!-- Group Info Form -->
      <div class="space-y-4">
        <!-- Name Field -->
        <div class="space-y-1.5">
          <div class="flex items-end justify-between">
            <Label for="group-name">Nom du groupe</Label>
            <ValidationError errors={form.validationErrors as Record<string, string>} field="name" />
          </div>
          <Input 
            id="group-name" 
            value={form.name}
            oninput={(e) => { form.name = e.currentTarget.value; form.clearError('name'); }}
            placeholder="ex: Managers RH" 
            class="h-10 text-[0.88rem] bg-white shadow-fine {form.validationErrors.name ? 'border-red-400 focus:border-red-400 focus:ring-red-400/20' : ''}"
          />
        </div>

        <!-- Slug Field -->
        <div class="space-y-1.5">
          <div class="flex items-end justify-between">
            <Label for="group-slug">Identifiant (Slug)</Label>
            <ValidationError errors={form.validationErrors as Record<string, string>} field="slug" />
          </div>
          <div class="relative">
            <Input 
              id="group-slug" 
              value={form.slug}
              oninput={(e) => { form.slug = e.currentTarget.value; form.clearError('slug'); }}
              disabled={isEdit} 
              placeholder="ex: hr_managers" 
              class="h-10 text-[0.85rem] bg-white shadow-fine {form.validationErrors.slug ? 'border-red-400 focus:border-red-400 focus:ring-red-400/20' : ''}"
            />
            {#if isEdit}
              <div class="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                <AppIcon name="lock" size={15} class="text-slate-500" />
              </div>
            {/if}
          </div>
          {#if !isEdit}
            <p class="text-[0.85rem] text-slate-500 flex items-center gap-1.5 mt-1 ml-1" transition:fade={{ duration: 300 }}>
              <AppIcon name="alert-circle" size={14} />
              L'identifiant unique ne peut plus être modifié après la création.
            </p>
          {/if}
        </div>
      </div>

      <!-- Roles -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <Label>Rôles assignés</Label>
          {#if $rolesQuery.isLoading}
            <span class="text-[0.8rem] text-slate-400 flex items-center gap-1.5" transition:fade={{ duration: 300 }}>
              <AnimateSpin text="Chargement des rôles" class="border-slate-400 size-3" />
            </span>
          {/if}
        </div>
        
        {#if roles.length > 0}
          <div class="border border-slate-50/0 flex flex-col gap-1.5 rounded-lg overflow-hidden bg-slate-50/30" transition:fade={{ duration: 300 }}>
            {#each roles as role, index}
              <RoleItem 
                {role}
                isSelected={form.selectedRoles.includes(role.slug)}
                isExpanded={expandedRoles.has(role.slug)}
                {expandedScopes}
                onToggle={() => form.toggleRole(role.slug)}
                onToggleExpand={(e) => toggleRoleExpanded(role.slug, e)}
              />
            {/each}
          </div>
        {:else if !$rolesQuery.isLoading}
          <div class="text-[0.9rem] text-slate-500 bg-slate-50/50 border rounded-lg p-4" transition:fade={{ duration: 300 }}>
            Aucun rôle disponible.
          </div>
        {/if}
      </div>

      <!-- Members Section -->
      {#if isEdit && group}
        <MemberManager {group} />
      {:else}
        <div class="space-y-4" transition:fade={{ duration: 300 }}>
          <Label class="flex items-center gap-2">
            <AppIcon name="users" size={16} class="text-slate-400" />
            Membres du groupe
          </Label>
          <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/50 text-center">
            <AppIcon name="info" size={26} iconStrokeWidth={1} class="text-slate-500 mx-auto mb-2" />
            <p class="text-[0.88rem] text-slate-600">Créez d'abord le groupe pour pouvoir ajouter des membres.</p>
            <p class="text-[0.875rem] text-slate-400">Les membres pourront être gérés après la création.</p>
          </div>
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-2.5 border-t border-t-slate-100 flex flex-row gap-3 bg-slate-50/60">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9">
          <AppIcon name="x" size={17} class="text-slate-300" />
          Annuler
        </Button>
      </Sheet.Close>
      <Button 
        onclick={handleSubmit} 
        disabled={form.isSubmitting}
        class="flex-1 h-9 bg-primary text-white font-medium"
      >
        {#if form.isSubmitting}
          <AnimateSpin text="" class="size-3 border-white!" />
        {:else}
          <AppIcon name="check" size={17} />
        {/if}
        {isEdit ? 'Enregistrer' : 'Créer le groupe'}
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




