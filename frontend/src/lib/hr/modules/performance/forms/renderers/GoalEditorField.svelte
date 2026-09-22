<script lang="ts">
  import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
  let { config, field, form } = $props<{ config: FieldConfig; field: FieldInstance; form?: FormInstance<any> }>();
  let goals = $derived((field.value as any[]) ?? []);
  function add() { field.setValue([...goals, { description: '', type: 'INDIVIDUAL', weight: 1 }]); }
  function remove(i: number) { field.setValue(goals.filter((_: any, idx: number) => idx !== i)); }
  function update(i: number, patch: any) { const next = [...goals]; next[i] = { ...next[i], ...patch }; field.setValue(next); }
</script>

<div class="space-y-2">
  {#each goals as g, i}
    <div class="flex gap-2 items-center p-2 border rounded-lg bg-white">
      <input type="text" value={g.description} placeholder="Objectif..." onchange={(e) => update(i, { description: (e.target as HTMLInputElement).value })} class="flex-1 h-8 border rounded px-2 text-[0.85rem]" />
      <input type="number" min="0" max="100" value={g.weight} onchange={(e) => update(i, { weight: Math.min(100, Math.max(0, parseInt((e.target as HTMLInputElement).value) || 0)) })} class="w-16 h-8 border rounded text-center text-[0.85rem]" />
      <span class="text-[0.75rem] text-slate-400">%</span>
      <button onclick={() => remove(i)} class="text-red-500 hover:text-red-700 p-1">×</button>
    </div>
  {/each}
  <button onclick={add} class="w-full py-1.5 text-[0.82rem] border-2 border-dashed rounded-lg text-slate-400 hover:border-primary/30 hover:text-primary">+ Ajouter un objectif</button>
</div>
