<script lang="ts">
  import { Switch } from "@/components/ui/switch";
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";
  import { fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { CURRENCIES } from "@/constants/finance";
  import ValidationError from "@/components/ui/validation-error";

  const legalAllowances = $derived(taxSettingsStore.legalAllowances);
  const config = $derived(taxSettingsStore.config);
  const validationErrors = $derived(taxSettingsStore.validationErrors);

  function translateAllowanceType(type: string): string {
    const translations: Record<string, string> = {
      'FAMILY': 'Famille',
      'HOUSING': 'Logement',
      'TRANSPORT': 'Transport',
      'OTHER': 'Autre'
    };
    return translations[type] || type;
  }

  function translateCalculationMode(mode: string): string {
    const translations: Record<string, string> = {
      'FIXED': 'Montant fixe',
      'PERCENTAGE': 'Pourcentage',
      'FORMULA': 'Formule'
    };
    return translations[mode] || mode;
  }
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center text-green-600 shrink-0">
      <AppIcon name="banknote" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Allocations légales</h5>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Allocations obligatoires selon le code du travail RDC
      </p>

      {#if legalAllowances.length > 0}
        <div class="space-y-3" transition:fade={{ duration: 300, easing: cubicOut }}>
          {#each legalAllowances as allowance}
            <div class="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div class="flex items-center gap-3">
                <Switch
                  checked={allowance.is_active}
                  onCheckedChange={(checked) => taxSettingsStore.updateLegalAllowance(allowance.id, { is_active: checked })}
                  class="data-[state=checked]:bg-green-600 cursor-pointer"
                />
                <div>
                  <span class="text-[0.88rem] font-medium text-slate-800">
                    {translateAllowanceType(allowance.allowance_type)}
                  </span>
                  <div class="text-[0.875rem] text-slate-500">
                    {translateCalculationMode(allowance.calculation_mode)} · Base: {taxSettingsStore.getDisplayValue(parseFloat(allowance.base_amount || '0')).toFixed(config.currency === CURRENCIES.USD ? 2 : 0)} {config.currency}
                  </div>
                </div>
              </div>
              {#if allowance.is_active}
                <div class="flex items-center gap-2">
                  <span class="text-[0.875rem] text-slate-500">Montant:</span>
                  <Input
                    type="number"
                    value={allowance.base_amount ? parseFloat(allowance.base_amount) : 0}
                    oninput={(e) => {
                      const val = e.currentTarget.value;
                      const num = val === '' ? 0 : parseFloat(val);
                      taxSettingsStore.updateLegalAllowance(allowance.id, { base_amount: num.toString() });
                    }}
                    class={cn("w-28 text-right h-8 text-[0.875rem] shadow-fine", validationErrors[`allowance-${allowance.id}-base_amount`] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
                    min={0}
                    step={allowance.calculation_mode === 'PERCENTAGE' ? 0.01 : 1}
                  />
                </div>
                <ValidationError errors={validationErrors} field={`allowance-${allowance.id}-base_amount`} />
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <div class="text-[0.875rem] text-slate-400" transition:fade={{ duration: 300, easing: cubicOut }}>
          Aucune allocation légale configurée
        </div>
      {/if}
    </div>
  </div>
</div>
