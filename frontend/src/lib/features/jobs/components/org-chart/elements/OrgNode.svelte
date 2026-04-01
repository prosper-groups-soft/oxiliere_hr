<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import type { Department, NodeType } from "../../../types/types";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { slide } from "svelte/transition";

  let { 
    department, 
    isSelected = false,
    onClick,
    onAddChild
  } = $props<{
    department: Department,
    isSelected?: boolean,
    onClick?: (dept: Department) => void,
    onAddChild?: (parent: Department) => void
  }>();

  const memberCount = $derived(
    employeeStore.employees.filter(e => e.department === department.name || e.departmentId === department.id).length
  );

  const nodeTypeLabel = $derived.by(() => {
    const type = department.type as NodeType;
    const config: Record<NodeType, { label: string; icon: string }> = {
      'DEPARTMENT': { label: 'Département', icon: '🏢' },
      'TEAM': { label: 'Équipe', icon: '👥' },
      'FUNCTION': { label: 'Fonction', icon: '⚙️' }
    };
    return config[type];
  });
</script>


<div 
  role="button"
  tabindex="0"
  onclick={() => onClick?.(department)}
  onkeydown={(e) => e.key === 'Enter' && onClick?.(department)}
  class={cn(
    "relative flex flex-col w-57 bg-white border border-slate-200 rounded-xl p-4 pt-5 transition-all duration-200 cursor-pointer select-none",
    "hover:border-slate-300 hover:bg-slate-50 group shadow-soft",
    isSelected && "border-primary ring-2 ring-primary/10"
  )}
>
  <!-- Quick Action -->
  <button 
    onclick={(e) => { e.stopPropagation(); onAddChild?.(department); }}
    class="absolute -top-2 -right-2 w-8 h-8 rounded-full bg-primary text-white shadow-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all hover:scale-105 active:scale-95 z-20 cursor-pointer"
    title="Ajouter un enfant"
  >
    <AppIcon name="plus" size={18} />
  </button>

  <!-- Type Badge -->
  <div class="absolute -top-3 -left-5 px-2 py-1 rounded-full bg-white border border-slate-200 shadow-fine flex items-center gap-1 z-10">
    <span class="text-[0.75rem] font-medium text-slate-700">{nodeTypeLabel?.icon} {nodeTypeLabel?.label}</span>
  </div>
  <div class="flex items-center justify-between mb-3">
    <div class={cn(
      "p-1.5 rounded-lg transition-colors bg-slate-50 text-slate-400 group-hover:text-primary",
      isSelected && "bg-primary/10 text-primary"
    )}>
      <AppIcon name="network" size={22} />
    </div>
    <div class="space-y-1 text-right text-[0.7rem] font-bold text-slate-500 uppercase tracking-tighter">
      <div class="px-2 py-0.5 rounded-full bg-slate-50 border border-slate-100 flex items-center gap-1 whitespace-nowrap">
        <span>{memberCount}</span>
        <span class="text-[0.65rem]">/ {department.authorizedHeadcount}</span>
      </div>
    </div>
  </div>

  <div class="space-y-1">
    <div class="flex items-start justify-between gap-2">
      <h3 class="text-[0.87rem] font-bold text-slate-900 leading-tight flex-1 truncate" title={department.name}>
        {department.name}
      </h3>
    </div>
    <div class="flex items-center gap-1.5 text-slate-600">
      <AppIcon name="circle-user" size={24} class="opacity-60" />
      <span class="text-[0.81rem] font-medium truncate">{department.managerName || 'Aucun'}</span>
    </div>
    {#if department.affointName}
      <div class="flex items-center gap-1.5 text-slate-600">
        <AppIcon name="circle-user" size={24} class="opacity-40" />
        <span class="text-[0.81rem] font-medium truncate text-slate-500">{department.affointName}</span>
      </div>
    {/if}
  </div>

  {#if isSelected}
    <div transition:slide={{ duration: 250 }} class="overflow-hidden">
      <div class="mt-1 pt-2 border-t border-slate-100 flex justify-between items-center text-primary group-hover:text-primary">
        <span class="text-[0.65rem] font-bold uppercase tracking-wider">Voir détails</span>
        <AppIcon name="arrow-right" size={16} />
      </div>
    </div>
  {/if}
</div>

