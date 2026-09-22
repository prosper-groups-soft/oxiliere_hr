<script lang="ts">
  import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
  let { config, field, form } = $props<{ config: FieldConfig; field: FieldInstance; form?: FormInstance<any> }>();
  // Valeur : { percentage, months, startMonth, refSalary, amount }
  let v = $derived((field.value as any) ?? { percentage: 20, months: 3, startMonth: '' });
  function update(patch: any) { field.setValue({ ...v, ...patch }); }
  const estimatedMonths = $derived(v.refSalary > 0 && v.amount > 0 ? Math.max(1, Math.ceil(v.amount / (v.refSalary * (v.percentage / 100)))) : null);
</script>

<div class="space-y-3">
  <div class="grid grid-cols-2 gap-3">
    <label class="space-y-1">
      <span class="text-[0.82rem] font-medium">% mensuel</span>
      <input type="number" min="1" max="100" value={v.percentage} onchange={(e) => update({ percentage: Math.min(100, Math.max(1, parseInt((e.target as HTMLInputElement).value) || 1)) })} class="h-8 w-full border rounded px-2 text-[0.85rem]" />
    </label>
    <label class="space-y-1">
      <span class="text-[0.82rem] font-medium">Mois</span>
      <input type="number" min="1" value={v.months} onchange={(e) => update({ months: Math.max(1, parseInt((e.target as HTMLInputElement).value) || 1) })} class="h-8 w-full border rounded px-2 text-[0.85rem]" />
    </label>
  </div>
  <label class="space-y-1">
    <span class="text-[0.82rem] font-medium">Mois de début</span>
    <input type="month" value={v.startMonth} onchange={(e) => update({ startMonth: (e.target as HTMLInputElement).value })} class="h-8 w-full border rounded px-2 text-[0.85rem]" />
  </label>
  {#if estimatedMonths}<p class="text-[0.82rem] text-slate-500">≈ {estimatedMonths} mois · {v.refSalary?.toLocaleString('fr-FR')} {v.currency ?? 'CDF'} de référence</p>{/if}
</div>
