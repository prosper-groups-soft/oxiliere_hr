<script lang="ts">
  import { onMount } from "svelte";
  import { fade } from "svelte/transition";
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { accessStore } from "../../../../admin/access/stores/accessStore.svelte";
  import { Label } from "@/components/ui/label";
  import { Switch } from "@/components/ui/switch";
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/hr/utilities/common/css";
  

  onMount(() => {
    accessStore.fetchGroups();
  });
</script>


<Card class="border-slate-200 shadow-none rounded-none py-0">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
      Compte & Accès Système
    </CardTitle>
    <CardDescription class="text-[0.835rem]">
      Configurez l'accès de l'employé aux outils de l'entreprise.
    </CardDescription>
  </CardHeader>
  <CardContent class="px-0 py-0 space-y-6">
    <!-- Toggle Section -->
    <div class="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-white shadow-fine transition-all">
      <div class="flex items-center gap-3">
        <div class={cn(
          "w-10 h-10 rounded-full flex items-center justify-center transition-colors",
          onboardingStore.data.account.create_account ? "bg-indigo-100 text-indigo-600" : "bg-slate-100 text-slate-400"
        )}>
          <AppIcon name="user-check" size={20} />
        </div>
        <div>
          <Label class="text-[0.875rem] font-semibold text-slate-900 select-none">Créer un compte utilisateur</Label>
          <p class="text-[0.78rem] text-slate-500">Permet à l'employé de se connecter à la plateforme.</p>
        </div>
      </div>
      <Switch 
        onchange={() => onboardingStore.setAccountField('create_account', onboardingStore.data.account.create_account)}
        class="data-[state=checked]:bg-indigo-600"
      />
    </div>

    {#if onboardingStore.data.account.create_account}
      <div class="space-y-5 animate-in fade-in slide-in-from-top-2 duration-300">
        <!-- Group Selection -->
        <div class="space-y-3">
          <Label class="text-[0.8rem] font-bold text-slate-700 uppercase tracking-wider">
            Groupe de permissions
          </Label>
          <div class="space-y-2">
            {#each accessStore.groups as group (group.slug)}
              <div 
                transition:fade={{ duration: 200 }}
                class={cn(
                  "group flex items-center py-3 px-4 rounded-xl border cursor-pointer transition-all",
                  onboardingStore.data.account.group_slug === group.slug
                    ? "border-indigo-600 bg-indigo-50/30 hover:bg-indigo-50/50"
                    : "border-slate-200 hover:border-slate-300 hover:bg-slate-50/30"
                )}
                onclick={() => onboardingStore.setAccountField('group_slug', group.slug)}
                role="none"
              >
                <!-- Icon and Name Section -->
                <div class="flex items-center gap-3 flex-1">
                  <div class={cn(
                    "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                    onboardingStore.data.account.group_slug === group.slug
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-100 text-slate-400 group-hover:bg-slate-200"
                  )}>
                    <AppIcon name="shield" size={16} />
                  </div>
                  <div class="flex-1">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="font-semibold text-slate-900 text-[0.85rem]">{group.name}</span>
                      {#if onboardingStore.data.account.group_slug === group.slug}
                        <div class="flex items-center gap-1">
                          <AppIcon name="circle-check" size={14} class="text-indigo-600" />
                          <span class="text-[0.82rem] text-indigo-600 font-medium">Sélectionné</span>
                        </div>
                      {/if}
                    </div>
                    <div class="flex flex-wrap gap-1">
                      {#if group.roles && group.roles.length > 0}
                        {#each group.roles.slice(0, 3) as role}
                          <span class="text-[0.82rem] bg-slate-50 text-slate-600 px-2 py-0.5 rounded-full font-medium border border-slate-200">
                            {role.name}
                          </span>
                        {/each}
                        {#if group.roles.length > 3}
                          <span class="text-[0.82rem] text-slate-400 px-2 py-0.5 rounded-full">
                            +{group.roles.length - 3} autres
                          </span>
                        {/if}
                      {:else}
                        <span class="text-[0.82rem] text-slate-400 px-2 py-0.5 rounded-full">
                          Aucun rôle
                        </span>
                      {/if}
                    </div>
                  </div>
                </div>
                
                <!-- Selection Indicator -->
                <div class="ml-3">
                  {#if onboardingStore.data.account.group_slug === group.slug}
                    <div class="w-5 h-5 rounded-full bg-indigo-600 flex items-center justify-center">
                      <AppIcon name="check" size={12} strokeWidth={2} class="text-white" />
                    </div>
                  {:else}
                    <div class="w-5 h-5 rounded-full border-2 border-slate-300 group-hover:border-slate-400 transition-colors"></div>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Info Box -->
        <div class="p-2 bg-amber-50 border border-amber-100 rounded-lg flex gap-3">
          <AppIcon name="info" size={18} class="text-amber-600 shrink-0 mt-0.5" />
          <div class="text-amber-800 leading-relaxed text-[0.86rem]">
            <p class="font-semibold mb-0.5 text-[0.86rem]">Note sur l'identification</p>
            L'identifiant de connexion sera l'adresse email professionnelle de l'employé. 
            Le mot de passe par défaut sera son <strong class="text-[0.86rem] font-bold">matricule</strong> généré lors de la validation.
          </div>
        </div>
      </div>
    {/if}
  </CardContent>
</Card>

