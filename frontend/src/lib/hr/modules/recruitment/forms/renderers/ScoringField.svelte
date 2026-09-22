<script lang="ts">
  import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
  let { config, field, form } = $props<{ config: FieldConfig; field: FieldInstance; form?: FormInstance<any> }>();

  // Valeur : Record<string, number> (criterionName -> score 0-100)
  // Config attend `config.dataSource` avec les critères [{ value: name, label, weight, source }]
  let scores = $derived((field.value as Record<string, number> ?? {}));
  let criteria = $derived((config.dataSource as any)?.values ?? []);
</script>

<div class="space-y-3">
  {#if criteria.length === 0}
    <p class="text-[0.82rem] text-slate-400">Aucun critère défini</p>
  {:else}
    {#each criteria as c}
      <div class="flex items-center gap-3">
        <span class="flex-1 text-[0.85rem] font-medium truncate">{c.label}
          <span class="ml-1 text-[0.7rem] px-1 py-0.5 rounded {c.source === 'requirement' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}">{c.source}</span>
          <span class="ml-1 text-[0.75rem] text-slate-400">{c.weight}%</span>
        </span>
        <input type="number" min="0" max="100" value={scores[c.value] ?? 0} onchange={(e) => field.setValue({ ...scores, [c.value]: Math.min(100, Math.max(0, parseInt((e.target as HTMLInputElement).value) || 0)) })} class="h-8 w-20 border rounded text-center text-[0.85rem]" />
        <span class="text-[0.75rem] text-slate-400">/100</span>
      </div>
    {/each}
  {/if}
</div>
