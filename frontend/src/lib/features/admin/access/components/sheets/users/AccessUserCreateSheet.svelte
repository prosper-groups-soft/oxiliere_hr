<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import * as Sheet from "@/components/ui/sheet";
  import { cn } from "@/utilities/common/css";
  import { accessStore } from "../../../stores/accessStore.svelte";


  interface Props {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onSubmit: (data: {
      email: string;
      first_name: string;
      last_name: string;
      password: string;
      is_active: boolean;
      is_admin: boolean;
      is_owner: boolean;
      groups: string[];
    }) => void;
  }

  
  let { open, onOpenChange, onSubmit }: Props = $props();

  // Form state
  let email = $state('');
  let firstName = $state('');
  let lastName = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let isActive = $state(true);
  let isAdmin = $state(false);
  let isOwner = $state(false);
  let selectedGroups = $state<string[]>([]);
  let isSubmitting = $state(false);

  const passwordsMatch = $derived(password === confirmPassword);
  const isValid = $derived(
    email && 
    firstName && 
    lastName && 
    password && 
    password.length >= 8 &&
    passwordsMatch
  );

  function toggleGroup(groupSlug: string) {
    if (selectedGroups.includes(groupSlug)) {
      selectedGroups = selectedGroups.filter(g => g !== groupSlug);
    } else {
      selectedGroups = [...selectedGroups, groupSlug];
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    if (!isValid) return;
    
    isSubmitting = true;
    try {
      await onSubmit({
        email,
        first_name: firstName,
        last_name: lastName,
        password,
        is_active: isActive,
        is_admin: isAdmin,
        is_owner: isOwner,
        groups: selectedGroups
      });
      // Reset form
      email = '';
      firstName = '';
      lastName = '';
      password = '';
      confirmPassword = '';
      isActive = true;
      isAdmin = false;
      isOwner = false;
      selectedGroups = [];
      onOpenChange(false);
    } finally {
      isSubmitting = false;
    }
  }
</script>


<Sheet.Root {open} onOpenChange={onOpenChange}>
  <Sheet.Content side="right" class="sm:max-w-md p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 text-left">
        Nouvel utilisateur
      </Sheet.Title>
    </Sheet.Header>

    <form onsubmit={handleSubmit} class="flex-1 overflow-hidden flex flex-col">
      <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
        <!-- Section: Informations -->
        <div class="space-y-4">
          <h3 class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Informations</h3>
          
          <div class="space-y-2">
            <Label for="email" class="text-[0.875rem]">Email <span class="text-rose-500">*</span></Label>
            <Input
              id="email"
              type="email"
              bind:value={email}
              placeholder="jean.mukendi@oxiliere.com"
              required
              class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <Label for="firstName" class="text-[0.875rem]">Prénom <span class="text-rose-500">*</span></Label>
              <Input
                id="firstName"
                type="text"
                bind:value={firstName}
                placeholder="Jean"
                required
                class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
              />
            </div>
            <div class="space-y-2">
              <Label for="lastName" class="text-[0.875rem]">Nom <span class="text-rose-500">*</span></Label>
              <Input
                id="lastName"
                type="text"
                bind:value={lastName}
                placeholder="Mukendi"
                required
                class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
              />
            </div>
          </div>
        </div>

        <!-- Section: Mot de passe -->
        <div class="space-y-4">
          <h3 class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Mot de passe</h3>
          
          <div class="space-y-2">
            <Label for="password" class="text-[0.875rem]">Mot de passe <span class="text-rose-500">*</span></Label>
            <Input
              id="password"
              type="password"
              bind:value={password}
              placeholder="••••••••"
              required
              class="h-10 border-slate-200 bg-white shadow-fine text-[0.88rem]"
            />
            {#if password && password.length < 8}
              <p class="text-[0.85rem] text-amber-600">
                Le mot de passe doit faire au moins 8 caractères
              </p>
            {/if}
          </div>

          <div class="space-y-2">
            <Label for="confirmPassword" class="text-[0.875rem] font-medium text-slate-700">Confirmer le mot de passe <span class="text-rose-500">*</span></Label>
            <Input
              id="confirmPassword"
              type="password"
              bind:value={confirmPassword}
              placeholder="••••••••"
              required
              class={cn(
                "h-10 bg-white shadow-fine text-[0.88rem]",
                confirmPassword && !passwordsMatch
                  ? "border-red-300 focus:border-red-500"
                  : "border-slate-200"
              )}
            />
            {#if confirmPassword && !passwordsMatch}
              <p class="text-[0.85rem] text-red-600">
                Les mots de passe ne correspondent pas
              </p>
            {/if}
          </div>
        </div>

        <!-- Section: Statut -->
        <div class="space-y-4">
          <h3 class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</h3>
          
          <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
            <div class="flex items-center gap-3">
              <div class={cn(
                "w-2 h-2 rounded-full",
                isActive ? "bg-emerald-500" : "bg-slate-400"
              )}></div>
              <span class="text-sm font-medium text-slate-700">
                Compte {isActive ? 'actif' : 'inactif'}
              </span>
            </div>
            <Switch 
              checked={isActive} 
              onCheckedChange={(v) => isActive = v}
              class="cursor-pointer"
            />
          </div>
        </div>

        <!-- Section: Permissions -->
        <div class="space-y-4">
          <h3 class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Permissions</h3>
          
          <div class="grid gap-3">
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div class="flex items-center gap-3">
                <AppIcon name="shield" size={18} class="text-indigo-500" />
                <div>
                  <span class="text-sm font-medium text-slate-800">Administrateur</span>
                  <p class="text-[0.8rem] text-slate-500">Accès complet à l'administration</p>
                </div>
              </div>
              <Switch 
                checked={isAdmin} 
                onCheckedChange={(v) => isAdmin = v}
                class="cursor-pointer"
              />
            </div>
            
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div class="flex items-center gap-3">
                <AppIcon name="crown" size={18} class="text-amber-500" />
                <div>
                  <span class="text-sm font-medium text-slate-800">Propriétaire</span>
                  <p class="text-[0.8rem] text-slate-500">Contrôle total du système</p>
                </div>
              </div>
              <Switch 
                checked={isOwner} 
                onCheckedChange={(v) => isOwner = v}
                class="cursor-pointer"
              />
            </div>
          </div>
        </div>

        <!-- Section: Groupes -->
        <div class="space-y-4">
          <h3 class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">
            Groupes ({selectedGroups.length} sélectionné{selectedGroups.length > 1 ? 's' : ''})
          </h3>
          
          <div class="flex flex-wrap gap-2">
            {#each accessStore.groups as group}
              <button
                type="button"
                onclick={() => toggleGroup(group.slug)}
                class={cn(
                  "px-3 py-1 text-[0.84rem] rounded-full border transition-all cursor-pointer shadow-fine",
                  selectedGroups.includes(group.slug)
                    ? "bg-indigo-50 text-indigo-700 border-indigo-200"
                    : "bg-white text-slate-800 border-slate-200 hover:bg-slate-50"
                )}
              >
                {group.name}
              </button>
            {/each}
          </div>
        </div>
      </div>

      <div class="px-6 py-4 border-t flex gap-3 bg-slate-50/30 shrink-0">
        <Button 
          type="button"
          variant="outline" 
          class="flex-1 h-9"
          onclick={() => onOpenChange(false)}
        >
          Annuler
        </Button>
        <Button 
          type="submit"
          class="flex-1 h-9 bg-indigo-600 hover:bg-indigo-700"
          disabled={!isValid || isSubmitting}
        >
          {#if isSubmitting}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          {:else}
            <AppIcon name="check" size={16} class="mr-2" />
          {/if}
          Créer
        </Button>
      </div>
    </form>
  </Sheet.Content>
</Sheet.Root>

