<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
  } from '@/components/ui/card';
  import { Button } from '@/components/ui/button';
  import type { EmployeeFullProfile } from '@/features/employees/types/types';
  import { cn } from '@/utilities/common/css';

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


<div class="space-y-0.5 px-2.5">
  <!-- Statut du compte -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center justify-between">
        <div class="flex items-center gap-2 text-[0.98rem] font-bold">
          <AppIcon name="shield" size={18} />
          Accès au compte
        </div>
        {#if !hasUserAccount}
          <Button variant="outline" size="sm" class="h-8 border-slate-200 bg-white hover:bg-slate-50 text-slate-800 text-[0.8rem] shadow-fine">
            <AppIcon name="plus" size={16} />
            Créer un compte
          </Button>
        {/if}
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-2.5">
      <div class="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50/30">
        <div class="flex items-center gap-4">
          <div class={cn(
            "w-12 h-12 rounded-lg flex items-center justify-center border",
            hasUserAccount && userAccount?.is_active 
              ? "bg-emerald-50 text-emerald-600 border-emerald-100" 
              : "bg-slate-100 text-slate-400 border-slate-200"
          )}>
            <AppIcon name={hasUserAccount ? "user-check" : "user-minus"} size={24} />
          </div>
          <div>
            <div class="text-[0.9rem] font-bold text-slate-900 tracking-tight">Compte utilisateur</div>
            <div class="text-[0.8rem] text-slate-500">Accès à la plateforme et aux services</div>
          </div>
        </div>
        <div class="flex items-center gap-2 px-3 py-1 bg-white border border-slate-200 rounded-full shadow-fine">
          <div class={cn("h-2 w-2 rounded-full", statusColor())}></div>
          <span class="text-[0.85rem] font-medium text-slate-700">{statusLabel()}</span>
        </div>
      </div>
    </CardContent>
  </Card>

  {#if hasUserAccount && userAccount}
    <!-- Informations du compte -->
    <Card class="shadow-none py-4">
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-[0.98rem]">
          <AppIcon name="user" size={18} />
          Détails de connexion
        </CardTitle>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4">
          <div>
            <div class="text-sm font-medium text-slate-500">Email de connexion</div>
            <p class="text-sm text-slate-900 mt-1 font-medium">{userAccount.email}</p>
          </div>
          <div>
            <div class="text-sm font-medium text-slate-500">ID Système</div>
            <p class="text-[0.78rem] text-slate-400 mt-1 font-mono">{userAccount.id}</p>
          </div>
          <div>
            <div class="text-sm font-medium text-slate-500">Utilisateur</div>
            <p class="text-sm text-slate-900 mt-1">{userAccount.first_name} {userAccount.last_name}</p>
          </div>
          <div>
            <div class="text-sm font-medium text-slate-500">Dernière connexion</div>
            <p class="text-sm text-slate-900 mt-1">-</p>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Actions -->
    <Card class="shadow-none py-4">
      <CardHeader>
        <CardTitle class="flex items-center gap-2 text-[0.98rem]">
          <AppIcon name="settings-2" size={18} />
          Sécurité et Actions
        </CardTitle>
      </CardHeader>
      <CardContent class="space-y-2">
        <div class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100">
              <AppIcon name="lock" size={16} />
            </div>
            <div>
              <div class="text-[0.85rem] font-bold text-slate-900">Révoquer l'accès</div>
              <div class="text-[0.75rem] text-slate-500">Désactiver temporairement le compte</div>
            </div>
          </div>
          <Button variant="ghost" size="sm" class="h-8 text-amber-600 hover:text-amber-700 hover:bg-amber-50">
            Désactiver
          </Button>
        </div>

        <div class="flex items-center justify-between p-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center border border-indigo-100">
              <AppIcon name="key" size={16} />
            </div>
            <div>
              <div class="text-[0.85rem] font-bold text-slate-900">Réinitialiser le mot de passe</div>
              <div class="text-[0.75rem] text-slate-500">Envoyer un lien sécurisé par email</div>
            </div>
          </div>
          <Button variant="ghost" size="sm" class="h-8 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50">
            Réinitialiser
          </Button>
        </div>
      </CardContent>
    </Card>
  {/if}
</div>
