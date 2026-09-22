<script lang="ts">
  import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
  let { config, field, form } = $props<{ config: FieldConfig; field: FieldInstance; form?: FormInstance<any> }>();
  const data = $derived(field.value as any | null);
</script>

{#if data?.dayDetails?.length}
  <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
    <div class="px-4 py-2.5 flex items-center justify-between bg-slate-50/50 border-b">
      <span class="text-[0.85rem] font-semibold">Aperçu période</span>
      <span class="text-[0.85rem] font-bold text-primary">{data.workingDays} jour{data.workingDays>1?'s':''} ouvré{data.workingDays>1?'s':''}</span>
    </div>
    <div class="px-4 py-2 flex items-center gap-1.5 overflow-x-auto">
      {#each data.dayDetails as day}
        <div class="h-2 w-6 rounded-full shrink-0 {day.isWorking ? 'bg-emerald-500' : day.reason === 'public_holiday' ? 'bg-red-400' : 'bg-slate-200'}" title="{day.date} — {day.reason}"></div>
      {/each}
    </div>
    <div class="px-4 py-2 text-[0.82rem] text-slate-500 flex gap-3">
      <span>{data.workingDays} ouvrés</span>
      <span>{data.calendarDays} calendaires</span>
      {#if data.excluded?.totalExcluded}<span>{data.excluded.totalExcluded} exclus</span>{/if}
    </div>
  </div>
{:else}
  <p class="text-[0.82rem] text-slate-400">{config.placeholder ?? 'Sélectionnez une période pour voir l\'aperçu'}</p>
{/if}
