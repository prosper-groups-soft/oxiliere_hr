<script lang="ts">
  import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
  import { DAYS } from '../../constants/attendance.constants';
  import type { DayOfWeek } from '../../types/types';

  let { config, field, form } = $props<{ config: FieldConfig; field: FieldInstance; form?: FormInstance<any> }>();

  // Valeur : WorkPolicy['pattern'] (Record<DayOfWeek, { isOff, periods }>)
  let pattern = $derived(field.value as any ?? {});

  function toggleDay(dayIndex: DayOfWeek) {
    const cur = pattern[dayIndex];
    const next = cur
      ? { ...cur, isOff: !cur.isOff, periods: !cur.isOff ? [] : [
          { id: crypto.randomUUID(), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: crypto.randomUUID(), startTime: "12:00", endTime: "14:00", type: "break", name: "Pause" },
          { id: crypto.randomUUID(), startTime: "14:00", endTime: "17:00", type: "work", name: "Après-midi" }
        ]}
      : { isOff: false, periods: [
          { id: crypto.randomUUID(), startTime: "08:00", endTime: "12:00", type: "work", name: "Matin" },
          { id: crypto.randomUUID(), startTime: "12:00", endTime: "14:00", type: "break", name: "Pause" },
          { id: crypto.randomUUID(), startTime: "14:00", endTime: "17:00", type: "work", name: "Après-midi" }
        ]};
    const updated = { ...pattern, [dayIndex]: next };
    field.setValue(updated);
  }

  function addPeriod(d: DayOfWeek) {
    const cur = pattern[d];
    if (!cur || cur.isOff) return;
    const updated = { ...pattern, [d]: { ...cur, periods: [...cur.periods, { id: Date.now().toString(), startTime: "08:00", endTime: "17:00", type: "work", name: "Nouvelle période" }] } };
    field.setValue(updated);
  }

  function removePeriod(d: DayOfWeek, id: string) {
    const cur = pattern[d];
    if (!cur) return;
    const updated = { ...pattern, [d]: { ...cur, periods: cur.periods.filter((p: any) => p.id !== id) } };
    field.setValue(updated);
  }
</script>

<div class="space-y-3">
  <div class="flex gap-1">
    {#each DAYS as day}
      {@const p = pattern[day.index]}
      <div class="h-2 flex-1 rounded-full {p && !p.isOff ? 'bg-primary/50' : 'bg-slate-200'}" title={day.label}></div>
    {/each}
  </div>
  {#each DAYS as day}
    {@const pat = pattern[day.index]}
    {@const active = pat && !pat.isOff}
    <div class="rounded-xl border {active ? 'border-primary/15 bg-white' : 'border-slate-100 bg-slate-50/40'} p-3 space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-[0.85rem] font-medium">{day.label}</span>
        <label class="flex items-center gap-2 cursor-pointer">
          <span class="text-[0.82rem] {active ? 'text-primary' : 'text-slate-400'}">{active ? 'Travaillé' : 'Repos'}</span>
          <input type="checkbox" checked={!!active} onchange={() => toggleDay(day.index)} class="size-4 accent-primary" />
        </label>
      </div>
      {#if active}
        {#each pat.periods as period}
          <div class="flex items-center gap-2 text-[0.82rem]">
            <span class="px-1.5 py-0.5 rounded text-[0.7rem] font-semibold uppercase {period.type === 'work' ? 'bg-primary/10 text-primary' : 'bg-amber-50 text-amber-600'}">{period.type}</span>
            <input type="time" value={period.startTime} onchange={(e) => { period.startTime = (e.target as HTMLInputElement).value; field.setValue({ ...pattern }); }} class="h-7 w-20 border rounded px-1" />
            <span class="text-slate-300">→</span>
            <input type="time" value={period.endTime} onchange={(e) => { period.endTime = (e.target as HTMLInputElement).value; field.setValue({ ...pattern }); }} class="h-7 w-20 border rounded px-1" />
            <input type="text" value={period.name} onchange={(e) => { period.name = (e.target as HTMLInputElement).value; field.setValue({ ...pattern }); }} placeholder="Libellé" class="h-7 flex-1 border rounded px-2" />
            <button onclick={() => removePeriod(day.index, period.id)} class="text-red-500 hover:text-red-700 p-1">×</button>
          </div>
        {/each}
        <button onclick={() => addPeriod(day.index)} class="w-full py-1.5 text-[0.82rem] border-2 border-dashed rounded-lg text-slate-400 hover:border-primary/30 hover:text-primary">+ Ajouter une période</button>
      {/if}
    </div>
  {/each}
</div>
