<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";
  import { preventNonNumeric } from "@/utilities/common/number";
  import { cn } from "@/utilities/common/css";
  import ValidationError from "@/components/ui/validation-error";

  const config = $derived(taxSettingsStore.config);
  const validationErrors = $derived(taxSettingsStore.validationErrors);
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-violet-50 flex items-center justify-center text-violet-600 shrink-0">
      <AppIcon name="dollar-sign" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Configuration devise</h5>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-4">
        Taux de change et paramètres de paiement
      </p>

      <div class="grid grid-cols-2 gap-4">
        <div class="p-3 bg-slate-50 rounded-lg">
          <Label class="text-[0.87rem]">Taux USD/CDF</Label>
          <p class="text-[0.87rem] text-slate-400 mt-0.5 mb-2">Taux de conversion Dollar → Franc Congolais</p>
          <div class="flex items-center gap-2">
            <Input
              type="number"
              value={config.exchangeRateUsdCdf}
              onkeydown={preventNonNumeric}
              oninput={(e) => {
                const val = e.currentTarget.value;
                const num = val === '' ? NaN : parseFloat(val);
                taxSettingsStore.updateConfig({ exchangeRateUsdCdf: num });
              }}
              class={cn("w-full shadow-fine", validationErrors['exchangeRateUsdCdf'] && "border-red-500 focus:border-red-500 focus:ring-red-500")}
              min={1}
              step={0.0001}
            />
            <span class="text-[0.875rem]">CDF/USD</span>
          </div>
          <ValidationError errors={validationErrors} field="exchangeRateUsdCdf" />
        </div>

        <div class="p-3 bg-slate-50 rounded-lg">
          <Label class="text-[0.87rem]">Mode de paiement par défaut</Label>
          <p class="text-[0.87rem] text-slate-400 mt-0.5 mb-2">Méthode de paiement standard pour les salaires</p>
          <Select.Root type="single" value={config.defaultPaymentMethod} onValueChange={(val) => taxSettingsStore.updateConfig({ defaultPaymentMethod: val as typeof config.defaultPaymentMethod })}>
            <Select.Trigger class="w-full h-9 bg-white! shadow-fine">
              <span class="flex items-center gap-2 text-[0.88rem]">
                {#if config.defaultPaymentMethod === 'BANK_TRANSFER'}
                  Virement bancaire
                {:else if config.defaultPaymentMethod === 'CASH'}
                  Espèces
                {:else if config.defaultPaymentMethod === 'MOBILE_MONEY'}
                  Mobile Money
                {:else if config.defaultPaymentMethod === 'CHECK'}
                  Chèque
                {:else}
                  {config.defaultPaymentMethod}
                {/if}
              </span>
            </Select.Trigger>
            <Select.Content>
              <Select.Item value="BANK_TRANSFER">Virement bancaire</Select.Item>
              <Select.Item value="CASH">Espèces</Select.Item>
              <Select.Item value="MOBILE_MONEY">Mobile Money</Select.Item>
              <Select.Item value="CHECK">Chèque</Select.Item>
            </Select.Content>
          </Select.Root>
        </div>
      </div>
    </div>
  </div>
</div>

