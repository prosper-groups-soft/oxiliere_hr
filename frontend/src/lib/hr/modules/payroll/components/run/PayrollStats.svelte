<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { payrollStore } from "../../stores/payroll.svelte";

  const stats = $derived([
    {
      label: 'Masse salariale nette',
      value: payrollStore.totalNetPay,
      currency: 'USD',
      icon: 'wallet',
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50'
    },
    {
      label: 'Cotisations sociales',
      value: payrollStore.totalContributions,
      currency: 'USD',
      icon: 'users',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      label: 'Salaire brut total',
      value: payrollStore.totalGrossPay,
      currency: 'USD',
      icon: 'trending-up',
      color: 'text-amber-600',
      bgColor: 'bg-amber-50'
    },
    {
      label: 'Taux de change',
      value: payrollStore.exchangeRate,
      currency: 'CDF/USD',
      icon: 'refresh',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      isRate: true
    }
  ]);

  function formatCurrency(value: number, currency: string, isRate = false) {
    if (isRate) {
      return value.toLocaleString('fr-FR');
    }
    return value.toLocaleString('fr-FR', {
      style: 'currency',
      currency,
      maximumFractionDigits: 0
    });
  }
</script>


<div class="grid grid-cols-4 gap-4 px-6 py-5 bg-slate-50/50">
  {#each stats as stat}
    <div class="bg-white rounded-xl border border-slate-200/60 p-3.5 shadow-sm hover:shadow-fine transition-all duration-200">
      <div class="flex items-center gap-3">
        <div class={cn("w-9 h-9 rounded-lg flex items-center justify-center shrink-0", stat.bgColor)}>
          <AppIcon name={stat.icon} size={18} class={stat.color} />
        </div>
        <div class="min-w-0">
          <p class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider truncate mb-0.5">{stat.label}</p>
          <p class="text-[1.05rem] font-bold text-slate-800 tracking-tight flex items-baseline gap-1">
            {formatCurrency(stat.value, stat.currency, stat.isRate)}
            {#if stat.isRate}
              <span class="text-[0.6rem] text-slate-400 font-bold"> {stat.currency}</span>
            {/if}
          </p>
        </div>
      </div>
    </div>
  {/each}
</div>

