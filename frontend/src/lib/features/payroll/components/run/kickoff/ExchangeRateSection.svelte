<script lang="ts">
  import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import type { ExchangeRateResponse } from "@/features/payroll/queries/payroll";


  interface Props {
    rateSource: 'auto' | 'manual';
    manualRate: number;
    exchangeRateInfo: ExchangeRateResponse | null;
    onRateSourceChange: (source: 'auto' | 'manual') => void;
    onManualRateChange: (value: number) => void;
    onRefresh: () => void;
  }

  let {
    rateSource,
    manualRate,
    exchangeRateInfo,
    onRateSourceChange,
    onManualRateChange,
    onRefresh
  }: Props = $props();
</script>


<Card class="border-slate-200 shadow-sm rounded-2xl">
  <CardHeader class="px-5 pt-5 pb-0">
    <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
      Taux de change
    </CardTitle>
    <CardDescription class="text-[0.875rem]">
      Taux USD → CDF applicable (officiel BCC ou manuel).
    </CardDescription>
  </CardHeader>
  <CardContent class="px-5 py-5 space-y-4">
    <div class="grid grid-cols-2 gap-2">
      <Button type="button" variant="ghost" onclick={() => onRateSourceChange('auto')}
        class="h-10 rounded-lg border-2 text-[0.875rem] font-medium transition-all flex items-center justify-center gap-1.5
                {rateSource === 'auto' ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-transparent'}">
        <AppIcon name="zap" size={14} />
        Automatique (BCC)
      </Button>
      <Button type="button" variant="ghost" onclick={() => onRateSourceChange('manual')}
        class="h-10 rounded-lg border-2 text-[0.875rem] font-medium transition-all flex items-center justify-center gap-1.5
                {rateSource === 'manual' ? 'border-indigo-500 bg-indigo-50 text-indigo-700' : 'border-slate-200 text-slate-500 hover:border-slate-300 hover:bg-transparent'}">
        <AppIcon name="pen-line" size={14} />
        Manuel
      </Button>
    </div>

    {#if rateSource === 'auto'}
      {#if exchangeRateInfo}
        <div class="flex items-center gap-2 flex-wrap">
          <Button type="button" variant="outline" size="sm"
            class="h-8 px-2.5 text-[0.875rem] text-slate-600 hover:text-slate-900 shadow-fine"
            onclick={onRefresh}
            aria-label="Recharger le taux de change"
            title="Recharger le taux de change">
            <AppIcon name="refresh-cw" size={15} class="shrink-0" />
            Recharger
          </Button>
          <div class="flex gap-1.5">
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[0.85rem] font-medium
                        {exchangeRateInfo.source === 'bcc'
                          ? 'bg-emerald-50 border border-emerald-100 text-emerald-700'
                          : 'bg-amber-50 border border-amber-100 text-amber-700'}">
              <AppIcon name={exchangeRateInfo.source === 'bcc' ? 'zap' : 'settings'} size={12} />
              {exchangeRateInfo.source === 'bcc'
                ? 'Taux officiel BCC (en direct)'
                : 'Taux manuel (configuration)'}
            </span>
            <span class="inline-flex items-center gap-1.5 text-[0.85rem] text-slate-600">
              <AppIcon name="banknote" size={14} class="text-slate-400" />
              1 USD = {Number(exchangeRateInfo.rate).toLocaleString('fr-FR')} CDF
            </span>
          </div>
        </div>
      {:else}
        <div class="flex items-center gap-2 px-3.5 py-2.5 bg-slate-50 rounded-lg border border-slate-100 text-[0.85rem] text-slate-500">
          <AnimateSpin text="Chargement du taux officiel BCC" class="size-3.5 border-slate-400" textPosition="right" />
        </div>
      {/if}
    {:else}
      <div class="space-y-1.5">
        <Label for="exchange-rate" class="text-[0.85rem] text-slate-900 font-medium">
          Taux de change USD → CDF *
        </Label>
        <div class="relative">
          <Input
            id="exchange-rate"
            type="number"
            min="0"
            step="0.01"
            value={manualRate}
            oninput={(e) => onManualRateChange(Number((e.currentTarget as HTMLInputElement).value))}
            class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine pr-20 text-right text-base font-semibold"
          />
          <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium text-sm">
            CDF/USD
          </span>
        </div>
        <p class="text-[0.85rem] text-slate-500">
          Saisissez le taux à figer pour cette exécution.
        </p>
      </div>
    {/if}
  </CardContent>
</Card>

