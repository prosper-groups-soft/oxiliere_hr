<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { 
    DayOfWeek, 
    WorkPolicy, 
    DayPattern,
    WorkPeriod
  } from "../../../types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import PolicyDetailsSheet from "../sheets/policy/PolicyDetailsSheet.svelte";   
  import { fade } from 'svelte/transition';
  import { cn } from "@/utilities/common/css";

  type Policy = WorkPolicy;

  const days: { label: string; index: DayOfWeek }[] = [
    { label: "Lun", index: 1 },
    { label: "Mar", index: 2 },
    { label: "Mer", index: 3 },
    { label: "Jeu", index: 4 },
    { label: "Ven", index: 5 },
    { label: "Sam", index: 6 },
    { label: "Dim", index: 0 },
  ];

  // Get props with $props()
  let { policy, onEdit, onDelete }: { 
    policy: Policy; 
    onEdit?: (policy: Policy) => void; 
    onDelete?: (policy: Policy) => void; 
  } = $props();

  // --- Helpers of logic ---
  function getDayStatus(dayPattern: DayPattern | undefined) {
    if (!dayPattern || dayPattern.isOff) return { bg: "bg-slate-50", text: "text-slate-400", dot: "bg-slate-200" };
    const workPeriods = dayPattern.periods?.filter(p => p.type === 'work') || [];
    if (workPeriods.length > 1) return { bg: "bg-emerald-50", text: "text-emerald-600", dot: "bg-emerald-500" };
    return { bg: "bg-blue-50", text: "text-blue-600", dot: "bg-blue-500" };
  }

  const activeDaysCount = $derived(
    Object.values(policy.pattern).filter((p) => p && !p.isOff).length
  );

  let detailsSheetOpen = $state(false);

  function handleEdit() { if (onEdit) onEdit(policy); }
  function handleDelete() { if (onDelete) onDelete(policy); }
</script>


<div 
  in:fade={{ duration: 200 }}
  class="flex flex-col rounded-xl border border-slate-200 bg-white overflow-hidden transition-colors hover:border-slate-300 shadow-fine"
>
  <div class="p-5 bg-slate-50/50 border-b border-slate-100">
    <div class="flex items-start justify-between gap-4">
      <div class="flex flex-col min-w-0">
        <span class="text-[0.95rem] font-bold text-slate-900 leading-tight truncate">{policy.name}</span>
        <span class="mt-1.5 text-[0.85rem] text-slate-500 line-clamp-1 font-normal">{policy.description}</span>
      </div>
      {@render Menu()}
    </div>
  </div>

  <div class="p-5 flex flex-col gap-6">
    <div class="grid grid-cols-7 gap-1">
      {#each days as day}
        {@const status = getDayStatus(policy.pattern[day.index])}
        <div class={cn("flex flex-col items-center gap-1.5 py-2 rounded-md transition-colors", status.bg)}>
          <span class={cn("text-[0.65rem] font-bold uppercase tracking-tighter", status.text)}>{day.label}</span>
          <div class={cn("h-1.5 w-1.5 rounded-full", status.dot)}></div>
        </div>
      {/each}
    </div>
    
    <div class="space-y-1.5 max-h-44 overflow-y-auto custom-scrollbar pr-1">
      {#each days as day}
        {@const pattern = policy.pattern[day.index]}
        {#if pattern && !pattern.isOff && pattern.periods?.length}
          <div class="flex items-center gap-4 py-1 px-2 rounded-lg border border-transparent hover:border-slate-100 hover:bg-slate-50/50 transition-all">
            <span class="text-[0.7rem] font-bold text-slate-400 uppercase w-7">{day.label}</span>
            
            <div class="flex flex-wrap gap-2 flex-1">
              {#each pattern.periods as period}
                <div class="flex items-center bg-white border border-slate-100 rounded px-2 py-1">
                  <span class="text-[0.875rem] font-medium text-slate-700 tabular-nums">
                    {period.startTime}
                  </span>
                  <div class="mx-2 h-3 w-px bg-slate-200"></div>
                  <span class={cn(
                    "text-[0.65rem] font-bold uppercase tracking-tight",
                    period.type === 'work' ? 'text-blue-500' : 'text-amber-500'
                  )}>
                    {period.type === 'work' ? 'Travail' : 'Pause'}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {/each}
    </div>
  </div>

  <div class="mt-auto px-5 py-3 border-t border-slate-100 flex items-center justify-between bg-white">
    <div class="flex items-center gap-2 text-slate-500">
      <AppIcon name="calendar-days" size={16} />
      <span class="text-[0.8rem] font-medium">{activeDaysCount} jours actifs</span>
    </div>
    <button 
      onclick={() => detailsSheetOpen = true}
      class="text-[0.8rem] font-medium text-primary hover:text-blue-700 transition-colors uppercase tracking-tight hover:underline cursor-pointer"
    >
      Détails complets
    </button>
  </div>
</div>


<PolicyDetailsSheet bind:open={detailsSheetOpen} policy={policy} />


{#snippet Menu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class="h-8 w-8 rounded-md text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors inline-flex items-center justify-center cursor-pointer border-none outline-none">
      <AppIcon name="more-horizontal" size={18} />
    </DropdownMenu.Trigger>
    
    <DropdownMenu.Content align="end" sideOffset={5} class="min-w-44 p-1 rounded-lg border border-slate-200 bg-white shadow-md z-50">
      <DropdownMenu.Item onSelect={handleEdit} class="flex items-center gap-2.5 px-3 py-2 rounded-md text-[0.875rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="edit-3" size={16} class="text-slate-400" /> 
        Modifier
      </DropdownMenu.Item>
      
      <DropdownMenu.Item onSelect={() => detailsSheetOpen = true} class="flex items-center gap-2.5 px-3 py-2 rounded-md text-[0.875rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="eye" size={16} class="text-slate-400" /> 
        Consulter
      </DropdownMenu.Item>

      <DropdownMenu.Separator class="my-1 bg-slate-100" />
      
      <DropdownMenu.Item onSelect={handleDelete} class="flex items-center gap-2.5 px-3 py-2 rounded-md text-[0.875rem] text-red-600 hover:bg-red-50! hover:text-red-700! cursor-pointer outline-none transition-colors">
        <AppIcon name="trash" size={16} class="text-red-600"/> 
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
</style>

