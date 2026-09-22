<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import * as Select from '@/components/ui/select';
  import type { PayrollConfiguration } from '@/hr/modules/payroll/types/types';
  import { CONFIG_PAYMENT_METHODS } from '../../../constants/settings.constants';
  import SettingSection from '../SettingSection.svelte';
  import SettingsField from '../SettingsField.svelte';

  
  let {
    config,
    onChange,
  }: {
    config: PayrollConfiguration | null;
    onChange: (field: keyof PayrollConfiguration, value: string | number | boolean) => void;
  } = $props();

  const selectClass =
    'h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer';
</script>


<SettingSection
  icon="settings"
  title="Paramètres généraux"
  description="Configuration globale de la paie — Code du travail congolais."
  iconClass="bg-slate-100"
>
  <div class="space-y-4">
    <SettingsField label="Mode de paiement par défaut" id="payment-method">
      <Select.Root
        type="single"
        value={config?.default_payment_method ?? 'BANK_TRANSFER'}
        onValueChange={(v) => onChange('default_payment_method', v)}
      >
        <Select.Trigger class={selectClass} id="payment-method">
          {CONFIG_PAYMENT_METHODS.find((m) => m.value === config?.default_payment_method)?.label ??
            'Virement bancaire'}
        </Select.Trigger>
        <Select.Content>
          {#each CONFIG_PAYMENT_METHODS as method}
            <Select.Item value={method.value} label={method.label}>{method.label}</Select.Item>
          {/each}
        </Select.Content>
      </Select.Root>
    </SettingsField>
  </div>

  <div class="mt-4 flex items-start gap-2 p-3 bg-slate-50/50 rounded-lg border border-slate-100">
    <AppIcon name="info" size={15} class="text-blue-500 mt-0.5 shrink-0" />
    <p class="text-[0.82rem] text-slate-500 leading-relaxed">
      La paie est libellée en Francs Congolais (CDF). Ces paramètres s'appliquent à toutes les
      exécutions de paie.
    </p>
  </div>
</SettingSection>

