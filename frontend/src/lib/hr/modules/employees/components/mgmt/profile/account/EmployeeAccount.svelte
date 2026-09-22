<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  import type { EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  import { cn } from '@/hr/utilities/common/css';

  
  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  const hasUserAccount = $derived(!!employee.user);
  const userAccount = $derived(employee.user);

  const accountStatus = $derived(() => {
    if (!hasUserAccount) return 'non_existent';
    return userAccount?.is_active ? 'active' : 'inactive';
  });

  const statusLabel = $derived(() => {
    switch (accountStatus()) {
      case 'active': return 'Actif';
      case 'inactive': return 'Inactif';
      case 'non_existent': return 'Non créé';
      default: return '-';
    }
  });

  const statusColor = $derived(() => {
    switch (accountStatus()) {
      case 'active': return 'bg-emerald-500';
      case 'inactive': return 'bg-slate-400';
      case 'non_existent': return 'bg-amber-500';
      default: return 'bg-slate-400';
    }
  });
</script>


{#snippet Field(label: string, value: string)}
  <div class="space-y-1">
    <div class="text-[0.8rem] font-bold uppercase tracking-widest text-slate-400">{label}</div>
    <p class="text-[0.86rem] font-medium text-slate-900 leading-snug wrap-break-word">{value}</p>
  </div>
{/snippet}


<div class="space-y-4">
  <!-- Statut du compte -->
  <Card class="rounded-xl border-slate-200 bg-white overflow-hidden shadow-none border-0">
    <CardHeader class="pb-3 border-b border-slate-50 shadow-none border-0">
      <div class="flex items-center justify-between gap-3">
        <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
          <span class="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
            <AppIcon name="shield" size={16} class="text-indigo-600" />
          </span>
          Accès au compte
        </CardTitle>
        {#if !hasUserAccount}
          <Button variant="outline" size="sm" class="h-8 px-3.5 rounded-full border-slate-200 bg-white hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-700 text-[0.84rem] font-medium shadow-fine">
            <AppIcon name="plus" size={18} />
            Créer un compte
          </Button>
        {/if}
      </div>
    </CardHeader>
    <CardContent class="pt-1 shadow-none border-0">
      <div class="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50/50">
        <div class="flex items-center gap-3.5">
          <div class={cn(
            "h-12 w-12 rounded-xl flex items-center justify-center border shrink-0",
            hasUserAccount && userAccount?.is_active 
              ? "bg-emerald-50 text-emerald-600 border-emerald-100" 
              : hasUserAccount
                ? "bg-slate-100 text-slate-400 border-slate-200"
                : "bg-amber-50 text-amber-600 border-amber-100"
          )}>
            <AppIcon name={hasUserAccount ? "user-check" : "user-minus"} size={20} />
          </div>
          <div>
            <div class="text-[0.88rem] font-bold text-slate-900 tracking-tight leading-tight">Compte utilisateur</div>
            <div class="text-[0.82rem] text-slate-500 mt-0.5">Accès à la plateforme et aux services</div>
          </div>
        </div>
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-white border border-slate-200 rounded-full shadow-fine">
          <span class={cn("h-2 w-2 rounded-full", statusColor())}></span>
          <span class="text-[0.84rem] font-medium text-slate-700">{statusLabel()}</span>
        </div>
      </div>
    </CardContent>
  </Card>

  {#if hasUserAccount && userAccount}
    <!-- Informations du compte -->
    <Card class="rounded-xl border-slate-200 bg-white border-0 shadow-none overflow-hidden">
      <CardHeader class="pb-3 border-b border-slate-50">
        <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
          <span class="h-8 w-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0">
            <AppIcon name="user" size={18} class="text-emerald-600" />
          </span>
          Détails de connexion
        </CardTitle>
      </CardHeader>
      <CardContent class="pt-1.5 border-0 shadow-none">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {@render Field("Email de connexion", userAccount.email || '-')}
          <div class="space-y-1">
            <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">ID Système</div>
            <p class="text-[0.82rem] font-mono font-medium text-slate-500 leading-snug wrap-break-word">{userAccount.id || '-'}</p>
          </div>
          {@render Field("Utilisateur", `${userAccount.first_name ?? ''} ${userAccount.last_name ?? ''}`.trim() || '-')}
          {@render Field("Dernière connexion", '-')}
          <div class="hidden lg:block"></div>
        </div>
      </CardContent>
    </Card>

    <!-- Actions -->
    <Card class="rounded-xl border-slate-200 bg-white border-0 shadow-none overflow-hidden">
      <CardHeader class="pb-3 border-b border-slate-50 border-0 shadow-none">
        <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
          <span class="h-8 w-8 rounded-lg bg-amber-50 border border-amber-100 flex items-center justify-center shrink-0">
            <AppIcon name="settings-2" size={18} class="text-amber-600" />
          </span>
          Sécurité et Actions
        </CardTitle>
      </CardHeader>
      <CardContent class="pt-1.5 space-y-2.5 border-0 shadow-none">
        <div class="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50/60 hover:border-slate-200 transition-colors">
          <div class="flex items-center gap-3">
            <span class="h-9 w-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100 shrink-0">
              <AppIcon name="lock" size={18} />
            </span>
            <div>
              <div class="text-[0.86rem] font-bold text-slate-900 leading-tight">Révoquer l'accès</div>
              <div class="text-[0.8rem] text-slate-500">Désactiver temporairement le compte</div>
            </div>
          </div>
          <Button variant="ghost" size="sm" class="h-8 rounded-full px-3.5 text-amber-600 hover:text-amber-700 hover:bg-amber-50 border border-transparent hover:border-amber-100 text-[0.84rem] font-medium">
            Désactiver
          </Button>
        </div>

        <div class="flex items-center justify-between p-3.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50/60 hover:border-slate-200 transition-colors">
          <div class="flex items-center gap-3">
            <span class="h-9 w-9 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100 shrink-0">
              <AppIcon name="key" size={18} />
            </span>
            <div>
              <div class="text-[0.86rem] font-bold text-slate-900 leading-tight">Réinitialiser le mot de passe</div>
              <div class="text-[0.8rem] text-slate-500">Envoyer un lien sécurisé par email</div>
            </div>
          </div>
          <Button variant="ghost" size="sm" class="h-8 rounded-full px-3.5 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 border border-transparent hover:border-indigo-100 text-[0.84rem] font-medium">
            Réinitialiser
          </Button>
        </div>
      </CardContent>
    </Card>
  {/if}
</div>

