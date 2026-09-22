<script lang="ts">
  import { calendarStore } from "@/hr/calendar/stores/calendar.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { fade } from "svelte/transition";
  import { TYPE_ICONS, TYPE_META, TYPE_OPTIONS } from "../../constants/event.constants";
  import { EVENT_TYPE_LABELS } from "../../types/types";
  import type { EventType } from "../../types/types";

  
  const stats = $derived(calendarStore.monthStats);
  let isMonthView = $derived(calendarStore.view === 'month');

  const typeDisplayOrder: EventType[] = $derived(TYPE_OPTIONS.map(o => o.value));
</script>


{#if isMonthView}
  <div class="flex items-center gap-0.5 py-1" in:fade={{ duration: 200 }} out:fade={{ duration: 150 }}>
    <!-- Working Days -->
    <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-md hover:bg-slate-50 transition-colors cursor-pointer">
      <div class="h-5 w-5 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100/50">
        <AppIcon name="calendar" size={12} />
      </div>
      <div class="flex items-baseline gap-1.5 leading-none">
        <span class="text-[0.75rem] font-semibold">{stats.workingDays}</span>
        <span class="text-[0.75rem] text-slate-500">Ouvrés</span>
      </div>
    </div>

    {#each typeDisplayOrder as type}
      {@const count = stats.typeCounts[type]}
      {@const meta = TYPE_META[type]}
      {#if count > 0}
        <div class="h-4 w-px bg-slate-200"></div>
        <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-md hover:bg-slate-50 transition-colors cursor-pointer">
          <div class="h-5 w-5 rounded-full {meta.bg} {meta.text} flex items-center justify-center border {meta.border}">
            <AppIcon name={TYPE_ICONS[type]} size={12} />
          </div>
          <div class="flex items-baseline gap-1 leading-none">
            <span class="text-[0.75rem] font-semibold">{count}</span>
            <span class="text-[0.75rem] text-slate-500">{EVENT_TYPE_LABELS[type]}</span>
          </div>
        </div>
      {/if}
    {/each}
  </div>
{/if}

