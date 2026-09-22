<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { WorkPolicy, DayPattern } from "../../../types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { fade } from 'svelte/transition';
  import { cn } from "@/hr/utilities/common/css";
  import { DAYS } from "../../../constants/attendance.constants";

  
  type Policy = WorkPolicy;

  let { policy, onEdit, onDelete, onViewDetails }: { 
    policy: Policy; 
    onEdit?: (policy: Policy) => void; 
    onDelete?: (policy: Policy) => void;
    onViewDetails?: (policy: Policy) => void;
  } = $props();

  // --- Helpers of logic ---
  function getDayStatus(dayPattern: DayPattern | undefined) {
    if (!dayPattern || dayPattern.isOff)
      return { bg: "bg-slate-50/60", text: "text-slate-400", dot: "bg-slate-200" };
    const workPeriods = dayPattern.periods?.filter(p => p.type === 'work') || [];
    if (workPeriods.length > 1)
      return { bg: "bg-emerald-50/70", text: "text-emerald-600", dot: "bg-emerald-500" };
    return { bg: "bg-blue-50/70", text: "text-blue-600", dot: "bg-blue-500" };
  }

  const activeDaysCount = $derived(
    Object.values(policy.pattern ?? {}).filter((p) => p && !p.isOff).length
  );

  function handleEdit() { if (onEdit) onEdit(policy); }
  function handleDelete() { if (onDelete) onDelete(policy); }
  function handleViewDetails() { if (onViewDetails) onViewDetails(policy); }
</script>


<div
  in:fade={{ duration: 250 }}
  onclick={handleViewDetails}
  role="none"
  class="group flex flex-col rounded-xl border border-slate-200 bg-white overflow-hidden transition-all duration-200 hover:border-slate-300 hover:shadow-sm cursor-pointer"
>
  <!-- Header -->
  <div class="px-5 pt-5 pb-4 border-b border-slate-100">
      <div class="flex items-start justify-between gap-4">
        <div class="flex flex-col min-w-0 flex-1">
          <span class="text-[0.95rem] font-semibold text-slate-900 leading-snug truncate tracking-tight group-hover:text-indigo-600 transition-colors">
            {policy.name}
          </span>
          {#if policy.description}
            <div class="text-[0.78rem] flex items-start justify-start gap-1 text-slate-500 leading-snug mt-0.5 line-clamp-2 h-8">
              <AppIcon name="info" size={16} class="text-slate-400 hover:text-slate-600 transition-colors cursor-help" />
              {policy.description}
            </div>
          {/if}
        </div>
        {@render Menu()}
      </div>
  </div>

  <!-- Body -->
  <div class="p-5 flex flex-col gap-5">
    <!-- Day indicators grid -->
    <div class="grid grid-cols-7 gap-1">
      {#each DAYS as day}
        {@const status = getDayStatus(policy.pattern?.[day.index])}
        <div class={cn(
          "flex flex-col items-center gap-1.5 py-2 rounded-lg transition-colors",
          status.bg
        )}>
          <span class={cn("text-[0.62rem] font-semibold uppercase tracking-tight", status.text)}>
            {day.short}
          </span>
          <div class={cn("h-1.5 w-1.5 rounded-full", status.dot)}></div>
        </div>
      {/each}
    </div>

    <!-- Period details -->
    <div class="space-y-1 max-h-44 overflow-y-auto custom-scrollbar pr-1">
      {#each DAYS as day}
        {@const pattern = policy.pattern?.[day.index]}
        {#if pattern && !pattern.isOff && pattern.periods?.length}
          <div class="flex items-start gap-3 py-1.5 px-2.5 rounded-lg border border-transparent hover:border-indigo-300 hover:bg-indigo-100/50 transition-all duration-150">
            <span class="text-[0.65rem] font-semibold text-indigo-600 uppercase tracking-wider w-7 pt-0.5 shrink-0">
              {day.short}
            </span>
            <div class="flex flex-wrap gap-1.5 flex-1">
              {#each pattern.periods as period}
                <div class={cn(
                  "flex w-[100%] items-center justify-between gap-0.5 px-2.5 py-1 rounded-md border transition-colors",
                  "bg-white border-slate-200"
                )}>
                  <div class="flex items-baseline gap-0 w-fit shrink-0">
                    <span class="text-[0.82rem] font-medium text-slate-700 tabular-nums">
                      {period.startTime}
                    </span>
                    {#if period.endTime}
                      <span class="text-[0.82rem] text-slate-400 mx-1">—</span>
                      <span class="text-[0.82rem] font-medium text-slate-700 tabular-nums">
                        {period.endTime}
                      </span>
                    {/if}
                  </div>
                  <span class={cn(
                    "text-[0.78rem] font-medium ml-0.5",
                    period.type === 'work' ? "text-slate-700" : "text-amber-600"
                  )}>
                    {period.name || (period.type === 'work' ? 'Travail' : 'Pause')}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/each}
    </div>
  </div>

  <!-- Footer -->
  <div class="mt-auto px-5 py-3 border-t border-slate-100 flex items-center justify-between">
    <div class="flex items-center gap-2 text-slate-500">
      <AppIcon name="calendar-days" size={16} class="text-slate-400" />
      <span class="text-[0.8rem] font-medium">
        {activeDaysCount} jour{activeDaysCount > 1 ? 's' : ''} actif{activeDaysCount > 1 ? 's' : ''}
      </span>
    </div>
    <button onclick={handleViewDetails} class="text-[0.78rem] font-medium text-blue-600 hover:text-blue-700 transition-colors cursor-pointer">
      Détails →
    </button>
  </div>
</div>


{#snippet Menu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="h-8 w-8 rounded-md text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors inline-flex items-center justify-center cursor-pointer border-none outline-none">
      <AppIcon name="more-horizontal" size={18} />
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" sideOffset={5} class="min-w-44 p-1 rounded-lg border border-slate-200 bg-white shadow-md z-50">
      <DropdownMenu.Item onSelect={handleEdit} class="flex items-center gap-2.5 px-3 py-1 rounded-md text-[0.85rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="edit" size={15} class="text-slate-400" />
        Modifier
      </DropdownMenu.Item>
      <DropdownMenu.Item onSelect={handleViewDetails} class="flex items-center gap-2.5 px-3 py-1 rounded-md text-[0.85rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="eye" size={15} class="text-slate-400" />
        Consulter
      </DropdownMenu.Item>
      <DropdownMenu.Separator class="my-1 bg-slate-100" />
      <DropdownMenu.Item onSelect={handleDelete} class="flex items-center gap-2.5 px-3 py-1 rounded-md text-[0.85rem] text-red-600! hover:bg-red-50! cursor-pointer outline-none transition-colors">
        <AppIcon name="trash" size={15} class="text-red-500" />
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}



