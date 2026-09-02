<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  
  const formattedDate = $derived(new Date(payrollStore.currentRun?.paidAt ?? '').toLocaleDateString('fr-FR'));
  const periodLabel = $derived(new Date(payrollStore.currentPeriod + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }));
  const today = new Date().toLocaleDateString('fr-FR');

  type StatusAlertProps = { color: string; icon: string; title: string; text: string };
  type SummaryCardProps = { color: string; icon: string; label: string; value: string; subtext: string };
  type PaymentOptionProps = { icon: string; title: string; desc: string; checked: boolean; extraClass?: string };
</script>


<div class="space-y-3 mt-2">
  
  {#if currentStatus === 'approved'}
    {@render StatusAlert({ 
      color: 'purple', 
      icon: 'credit-card', 
      title: 'Prêt pour exécution', 
      text: "La paie a été approuvée. Utilisez le bouton Payer pour valider." 
    })}
  {:else if currentStatus === 'paid'}
    <div class="bg-emerald-50 border border-emerald-100 rounded-xl p-2 flex items-center gap-4 shadow-fine">
      <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center">
        <AppIcon name="circle-check" size={24} class="text-emerald-600" />
      </div>
      <div>
        <p class="text-[0.875rem] font-bold text-emerald-900">Paiement complété</p>
        <p class="text-[0.75rem] text-emerald-600 font-medium">Exécuté le {formattedDate}</p>
      </div>
    </div>
  {/if}

  <section class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-fine">
    <header class="px-4 py-3 bg-slate-50 border-b border-slate-100">
      <h3 class="text-sm font-bold text-slate-700">Résumé du paiement</h3>
    </header>
    
    <div class="p-4 py-2 grid grid-cols-2 gap-10">
      {@render SummaryCard({
        color: 'emerald',
        icon: 'banknote',
        label: 'Montant total',
        value: payrollStore.totalNetPay.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' }),
        subtext: `${payrollStore.payslips.length} employés`
      })}
      {@render SummaryCard({
        color: 'blue',
        icon: 'calendar',
        label: 'Période',
        value: periodLabel,
        subtext: `Date: ${today}`
      })}
    </div>
  </section>

  <section class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-fine">
    <header class="px-4 py-3 bg-slate-50 border-b border-slate-100">
      <h3 class="text-sm font-bold text-slate-700">Méthode de paiement</h3>
    </header>
    <div class="p-4 space-y-3">
      {@render PaymentOption({ icon: 'finance', title: 'Virement bancaire', desc: 'Paiement direct vers les comptes', checked: true })}
      {@render PaymentOption({ icon: 'mobile', title: 'Mobile Money', desc: 'Orange Money, M-Pesa ou Airtel Money', checked: false, extraClass: 'opacity-60' })}
    </div>
  </section>
</div>


{#snippet StatusAlert({ color, icon, title, text }: StatusAlertProps)}
  <div class="bg-{color}-50 border border-{color}-100 rounded-xl p-6 flex gap-4">
    <div class="w-12 h-12 rounded-full bg-{color}-100 flex items-center justify-center shrink-0">
      <AppIcon name={icon} size={24} class="text-{color}-600" />
    </div>
    <div class="flex-1">
      <h3 class="font-medium text-{color}-900 mb-1">{title}</h3>
      <p class="text-sm text-{color}-700">{text}</p>
    </div>
  </div>
{/snippet}


{#snippet SummaryCard({ color, icon, label, value, subtext }: SummaryCardProps)}
  <div class="bg-{color}-50/50 rounded-lg p-4 py-2 border border-{color}-100">
    <div class="flex items-center gap-3 mb-2">
      <div class="w-8 h-8 rounded-full bg-{color}-100 flex items-center justify-center">
        <AppIcon name={icon} size={18} class="text-{color}-600" />
      </div>
      <span class="text-[0.78rem] text-{color}-600 font-bold uppercase tracking-wider">{label}</span>
    </div>
    <p class="text-[1rem] font-medium text-{color}-700">{value}</p>
    <p class="text-[0.8rem] text-{color}-600 font-medium mt-1">{subtext}</p>
  </div>
{/snippet}


{#snippet PaymentOption({ icon, title, desc, checked, extraClass = '' }: PaymentOptionProps)}
  <label class="flex items-center gap-3 p-3 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-all group {extraClass}">
    <input type="radio" name="payment-method" {checked} class="w-4 h-4 text-primary border-slate-300" />
    <div class="flex-1">
      <div class="flex items-center gap-2">
        <AppIcon name={icon} size={16} class="text-slate-600 group-hover:text-primary" />
        <span class="font-bold text-sm text-slate-700">{title}</span>
      </div>
      <p class="text-sm text-slate-500 mt-0.5">{desc}</p>
    </div>
  </label>
{/snippet}

