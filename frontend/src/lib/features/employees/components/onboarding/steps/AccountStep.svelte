<script lang="ts">
  import { onMount } from "svelte";
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { accessStore } from "../../../../admin/access/stores/accessStore.svelte";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";

  onMount(() => {
    accessStore.fetchGroups();
  });
</script>


<Card class="border-slate-200 shadow-none rounded-none py-0">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-md font-bold text-slate-900 tracking-tight">
      Compte & Accès Système
    </CardTitle>
    <CardDescription class="text-[0.835rem]">Configurez l'accès de l'employé aux outils de l'entreprise.</CardDescription>
  </CardHeader>
  <CardContent class="px-0 py-0 space-y-6">
    <!-- Toggle Section -->
    <div class="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-white shadow-fine transition-all">
      <div class="flex items-center gap-3">
        <div class={cn(
          "w-10 h-10 rounded-full flex items-center justify-center transition-colors",
          onboardingStore.data.account.createAccount ? "bg-indigo-100 text-indigo-600" : "bg-slate-100 text-slate-400"
        )}>
          <AppIcon name="user-check" size={20} />
        </div>
        <div>
          <Label class="text-[0.875rem] font-semibold text-slate-900 select-none">Créer un compte utilisateur</Label>
          <p class="text-[0.78rem] text-slate-500">Permet à l'employé de se connecter à la plateforme.</p>
        </div>
      </div>
      <Switch 
        bind:checked={onboardingStore.data.account.createAccount}
        class="data-[state=checked]:bg-indigo-600"
      />
    </div>

    {#if onboardingStore.data.account.createAccount}
      <div class="space-y-5 animate-in fade-in slide-in-from-top-2 duration-300">
        <!-- Group Selection -->
        <div class="space-y-2">
          <Label class="text-[0.8rem] font-bold text-slate-700 uppercase tracking-wider">
            Groupe de permissions
          </Label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            {#each accessStore.groups as group}
              <button
                class={cn(
                  "flex flex-col p-3 rounded-xl border text-left transition-all cursor-pointer",
                  onboardingStore.data.account.groupSlug === group.slug
                    ? "border-indigo-600 bg-indigo-50/50 ring-1 ring-indigo-600"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50"
                )}
                onclick={() => onboardingStore.data.account.groupSlug = group.slug}
              >
                <div class="flex justify-between items-center mb-1">
                  <span class="font-semibold text-slate-900 text-[0.85rem]">{group.name}</span>
                  {#if onboardingStore.data.account.groupSlug === group.slug}
                    <AppIcon name="check-circle" size={16} class="text-indigo-600" />
                  {/if}
                </div>
                <div class="flex flex-wrap gap-1">
                   {#each group.roles as role}
                     <span class="text-[0.65rem] bg-indigo-100/50 text-indigo-700 px-1.5 rounded-md font-medium">{role.name}</span>
                   {/each}
                </div>
              </button>
            {/each}
          </div>
        </div>

        <!-- Info Box -->
        <div class="p-3 bg-amber-50 border border-amber-100 rounded-lg flex gap-3">
          <AppIcon name="info" size={18} class="text-amber-600 shrink-0 mt-0.5" />
          <div class="text-[0.78rem] text-amber-800 leading-relaxed">
            <p class="font-semibold mb-0.5">Note sur l'identification</p>
            L'identifiant de connexion sera l'adresse email professionnelle de l'employé. 
            Le mot de passe par défaut sera son <strong>matricule</strong> généré lors de la validation.
          </div>
        </div>
      </div>
    {/if}
  </CardContent>
</Card>

