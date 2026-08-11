<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import type { ExchangeRateInfo } from '@/features/payroll/types/types';

  interface Props {
    exchangeRate: ExchangeRateInfo;
  }

  let { exchangeRate }: Props = $props();
</script>


<div
  class="relative overflow-hidden rounded-xl border border-amber-200/70 bg-linear-to-br from-amber-50 via-white to-amber-50/80 px-4 py-3 shadow-xs"
>
  <!-- Decorative background accent -->
  <div class="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-amber-200/30 blur-xl"></div>
  <div class="pointer-events-none absolute -bottom-4 -left-4 h-14 w-14 rounded-full bg-amber-300/20 blur-lg"></div>

  <div class="flex items-start gap-3">
    <!-- Icon col -->
    <div class="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-700 shadow-xs">
      <AppIcon name="refresh-cw" size={15} strokeWidth={2} />
    </div>

    <!-- Content col -->
    <div class="min-w-0 flex-1 space-y-2">
      <!-- Title row -->
      <div class="flex items-center justify-between gap-2">
        <span class="text-[0.8rem] font-semibold text-amber-800">
          Conversion de devise
        </span>
        {#if exchangeRate.isLocked}
          <span class="inline-flex items-center gap-1 rounded-md bg-amber-200/60 px-2 py-0.5 text-[0.65rem] font-medium text-amber-800">
            <AppIcon name="lock" size={10} strokeWidth={2.5} />
            Verrouillé
          </span>
        {:else}
          <span class="inline-flex items-center gap-1 rounded-md bg-emerald-100/60 px-2 py-0.5 text-[0.65rem] font-medium text-emerald-700">
            <AppIcon name="refresh-cw" size={10} strokeWidth={2.5} />
            Flottant
          </span>
        {/if}
      </div>

      <!-- Rate row -->
      <div class="flex flex-wrap items-baseline gap-x-4 gap-y-1 text-[0.8rem]">
        <span class="text-slate-600">1 $US =</span>
        <span class="font-semibold text-slate-800">
          {exchangeRate.rate.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} FC
        </span>
        <span class="text-xs text-slate-400">•</span>
        <span class="text-xs text-slate-500">
          Source : {{ 'bcc': 'BCC', 'transferwise': 'TransferWise', 'manual': 'Manuelle' }[exchangeRate.source] ?? exchangeRate.source}
        </span>
      </div>

      <!-- Meta row -->
      <div class="flex flex-wrap items-center gap-x-3 gap-y-0.5 text-[0.7rem] text-slate-400">
        <span class="inline-flex items-center gap-1">
          <AppIcon name="clock" size={10} class="text-slate-400" />
          {new Date(exchangeRate.fetchedAt).toLocaleDateString('fr-FR', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
        {#if exchangeRate.isLocked}
          <span class="inline-flex items-center gap-1 text-amber-500">
            <AppIcon name="check-circle" size={10} />
            Taux gelé pour cette période
          </span>
        {:else}
          <span class="inline-flex items-center gap-1 text-slate-400">
            <AppIcon name="alert-circle" size={10} />
            Mis à jour automatiquement
          </span>
        {/if}
      </div>
    </div>
  </div>
</div>

