<script lang="ts">
  import { calendarStore } from "@/features/calendar/stores/calendar.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { fade } from "svelte/transition";

  const stats = $derived(calendarStore.monthStats);
</script>


<div class="flex items-center gap-0.5 py-1" in:fade>
  <!-- Working Days -->
  <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-md hover:bg-slate-50 transition-colors cursor-pointer">
    <div class="h-5 w-5 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center border border-emerald-100/50">
      <AppIcon name="calendar" size={12} />
    </div>
    <div class="flex items-baseline gap-1.5 leading-none">
      <span class="text-[0.75rem]">{stats.workingDays}</span>
      <span class="text-[0.75rem]">Ouvrés</span>
    </div>
  </div>

  <div class="h-4 w-px bg-slate-200"></div>

  <!-- Holidays -->
  <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-md hover:bg-slate-50 transition-colors cursor-pointer">
    <div class="h-5 w-5 rounded-full bg-red-50 text-red-600 flex items-center justify-center border border-red-100/50">
      <AppIcon name="activity" size={12} />
    </div>
    <div class="flex items-baseline gap-1.5 leading-none">
      <span class="text-[0.75rem]">{stats.holidaysCount}</span>
      <span class="text-[0.75rem]">Fériés</span>
    </div>
  </div>

  {#if stats.closuresCount > 0}
    <div class="h-4 w-px bg-slate-200"></div>
    <!-- Closures -->
    <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-md hover:bg-slate-50 transition-colors cursor-pointer">
      <div class="h-5 w-5 rounded-full bg-amber-50 text-amber-600 flex items-center justify-center border border-amber-100/50">
        <AppIcon name="close" size={12} />
      </div>
      <div class="flex items-baseline gap-1.5 leading">
        <span class="text-[0.75rem]">{stats.closuresCount}</span>
        <span class="text-[0.75rem]">Fermé</span>
      </div>
    </div>
  {/if}
</div>

