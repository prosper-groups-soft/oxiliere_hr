<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";

  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const payslips = $derived(payrollStore.payslips);

  const totalNet = $derived(payrollStore.totalNetPay);
  const totalGross = $derived(payrollStore.totalGrossPay);
  const totalTax = $derived(payrollStore.totalTax || 0);
  const totalSocialSecurity = $derived(payrollStore.totalSocialSecurity || 0);
  const totalContributions = $derived(totalTax + totalSocialSecurity);
  
  const employeeCount = $derived(payslips.length);

  type StatCardProps = {
    icon: string;
    iconColor: string;
    title: string;
    value: number;
    subtitle: string;
  };
</script>


<div class="mt-2 space-y-2 font-sans">
  
  <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
    {@render StatCard({ 
      icon: "banknote", 
      iconColor: "text-emerald-500", 
      title: "Total Net", 
      value: totalNet, 
      subtitle: `Basé sur ${employeeCount} bulletins` 
    })}
    {@render StatCard({ 
      icon: "trending-up", 
      iconColor: "text-blue-500", 
      title: "Total Brut", 
      value: totalGross, 
      subtitle: "Avant déductions" 
    })}
    {@render StatCard({ 
      icon: "shield", 
      iconColor: "text-blue-500", 
      title: "Cotisations", 
      value: totalContributions, 
      subtitle: "CNSS + IPR" 
    })}
    {@render StatCard({ 
      icon: "receipt", 
      iconColor: "text-amber-500", 
      title: "Taxes", 
      value: totalTax, 
      subtitle: "INPP" 
    })}
  </div>

  <!-- Status Cards -->
  {#if currentStatus === 'reviewed'}
    <div class="bg-amber-50/60 border border-amber-100 rounded-xl p-2 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center border border-amber-200">
            <AppIcon name="alert-circle" size={18} class="text-amber-600" />
        </div>
        <div class="flex-1">
          <h3 class="font-bold text-amber-900 text-sm">Prêt pour approbation</h3>
          <p class="text-sm text-amber-700 leading-relaxed mt-0.5">
            Vérifiez attentivement les montants ci-dessus. Une fois approuvée, la paie sera verrouillée pour le paiement.
          </p>
        </div>
      </div>
      <span class="text-[0.7rem] font-bold text-amber-600 bg-white px-2 py-1 rounded-full border border-amber-100 shadow-sm uppercase tracking-tighter">
        Étape 4/4
      </span>
    </div>
  {:else if currentStatus === 'approved' || currentStatus === 'paid'}
    <div class="bg-emerald-50/60 border border-emerald-100 rounded-xl p-2 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center border border-emerald-200">
            <AppIcon name="circle-check" size={18} class="text-emerald-600" />
        </div>
        <div>
          <h3 class="font-bold text-emerald-900 text-sm">Paie approuvée</h3>
          <p class="text-sm text-emerald-700 leading-relaxed mt-0.5">
            Approuvée le {new Date(payrollStore.currentRun?.approvedAt ?? '').toLocaleDateString('fr-FR')}
          </p>
        </div>
      </div>
      <span class="text-[0.7rem] font-medium text-emerald-600 bg-white px-2.5 py-0.5 rounded-full border border-emerald-100 shadow-fine uppercase tracking-tighter">
        Terminée
      </span>
    </div>
  {/if}

  <!-- Business Rules Section -->
  <div class="md:col-span-2 border border-slate-200 bg-white rounded-xl shadow-none overflow-hidden">
    <div class="p-3 border-b border-slate-100 bg-slate-50/50">
      <h3 class="text-sm font-bold text-slate-700">Règles métier (RDC)</h3>
    </div>
    <div class="p-4 space-y-3">
      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-slate-500 text-sm">
             <AppIcon name="check-circle-2" size={17} class="text-emerald-500" />
             Logement (max 30% Base)
          </div>
          <span class="font-semibold text-slate-700 text-sm">Exonéré</span>
        </div>
        <Separator class="opacity-50" />
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-slate-500 text-sm">
             <AppIcon name="check-circle-2" size={17} class="text-emerald-500" />
             Transport (Légal)
          </div>
          <span class="font-semibold text-slate-700 text-sm">Non Imp.</span>
        </div>
        <Separator class="opacity-50" />
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-slate-500 text-sm">
             <AppIcon name="info" size={17} class="text-blue-500" />
             ONEM & INPP
          </div>
          <span class="font-semibold text-slate-700 text-sm">Charge Patron.</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Compliance Info -->
  <div class="flex items-start gap-3 px-1 pt-2">
    <AppIcon name="lock" size={16} class="text-slate-400 mt-0.5" />
    <p class="text-[0.78rem] text-slate-500 leading-snug">
      Les calculs respectent le barème fiscal en vigueur. En cas de modification des lois sociales, veuillez contacter l'administrateur système pour mettre à jour les constantes.
    </p>
  </div>
</div>


{#snippet StatCard({ icon, iconColor, title, value, subtitle }: StatCardProps)}
  <Card class="border shadow-none border-slate-200 gap-2 h-29 py-2">
    <CardHeader class="py-2 pb-0">
      <CardTitle class="text-[0.75rem] font-semibold text-slate-500 uppercase flex items-center gap-2">
        <AppIcon name={icon} size={16} class={iconColor} /> {title}
      </CardTitle>
    </CardHeader>
    <CardContent class="py-2 pt-1">
      <p class="text-lg font-medium text-slate-900">
        {value.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' })}
      </p>
      <div class="mt-1 flex items-center gap-1 text-[0.7rem] text-slate-400 font-medium">
          {subtitle}
      </div>
    </CardContent>
  </Card>
{/snippet}

