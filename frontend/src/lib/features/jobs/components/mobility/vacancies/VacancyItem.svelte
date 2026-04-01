<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { jobsStore } from "$lib/features/jobs/stores/jobs.svelte";
  import type { Vacancy } from "../../../types/types";
  import { cn } from "@/utilities/common/css";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  let { 
    vacancy,
    onEdit
  } = $props<{ 
    vacancy: Vacancy,
    onEdit: (vac: Vacancy) => void
  }>();

  const priorityConfig: Record<string, { label: string, color: string }> = {
    'HIGH':   { label: 'Urgente', color: 'bg-red-50 text-red-600 border-red-100' },
    'MEDIUM': { label: 'Normale', color: 'bg-amber-50 text-amber-600 border-amber-100' },
    'LOW':    { label: 'Faible',  color: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
  };

  const statusConfig: Record<string, { label: string, icon: string, color: string }> = {
    'OPEN':        { icon: 'pin',         color: 'bg-blue-50 text-blue-600 border-blue-100',       label: 'Ouverte' },
    'IN_PROGRESS': { icon: 'rotate',      color: 'bg-amber-50 text-amber-600 border-amber-100',     label: 'En cours' },
    'RECRUITMENT': { icon: 'consulting',  color: 'bg-purple-50 text-purple-600 border-purple-100',  label: 'Réc. Externe' },
    'CANCELLED':   { icon: 'close',       color: 'bg-slate-50 text-slate-500 border-slate-100',     label: 'Annulée' }
  };

  const pos = $derived(jobsStore.positions.find(p => p.id === vacancy.positionId));
  const dept = $derived(pos?.departmentId ? jobsStore.getDepartmentById(pos.departmentId) : null);
  const priCfg = $derived(priorityConfig[vacancy.priority] ?? priorityConfig.MEDIUM);
  const stCfg = $derived(statusConfig[vacancy.status] ?? statusConfig.OPEN);
</script>


{#snippet ItemActions()}
  <div onclick={(e) => e.stopPropagation()} role="none">
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        {#snippet child({ props })}
          <button 
            {...props}
            class="p-1.5 hover:bg-slate-100 rounded-md transition-colors text-slate-400 hover:text-slate-700 cursor-pointer outline-none"
          >
            <AppIcon name="more-vertical" size={19} />
          </button>
        {/snippet}
      </DropdownMenu.Trigger>

      <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100 min-w-40">
        <DropdownMenu.Item onclick={() => onEdit(vacancy)} class="cursor-pointer gap-2 py-2 text-[0.85rem]!">
          <AppIcon name="edit" size={16} class="text-slate-500" />
          Modifier
        </DropdownMenu.Item>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}


<div 
  in:fly={{ y: 10, duration: 300, easing: cubicOut }}
  onclick={() => onEdit(vacancy)}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onEdit(vacancy)}
  class="group/row relative flex items-center w-full h-20 shrink-0 px-0 bg-white border-b border-slate-100 hover:bg-hover transition-colors duration-150 cursor-pointer overflow-hidden"
>
  <!-- Briefcase Icon + Position Title + Priority -->
  <div class="flex items-center w-[35%] shrink-0 pl-4 min-w-0 gap-3">
    <div class="h-10 w-10 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 shrink-0 group-hover/row:bg-primary group-hover/row:text-white group-hover/row:border-primary transition-all">
      <AppIcon name="briefcase" size={18} />
    </div>
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[0.88rem] text-slate-900 truncate leading-tight group-hover/row:text-primary transition-colors">
        {pos?.title || 'Poste inconnu'}
      </span>
      <div class="flex items-center gap-1.5 mt-0.5">
        <Badge variant="outline" class={cn("w-fit h-5 px-2 text-[0.6rem] font-bold uppercase tracking-widest border-none", priCfg.color)}>
          {priCfg.label}
        </Badge>
        {#if vacancy.status === 'RECRUITMENT'}
          <div class="flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-purple-500 text-white text-[0.55rem] font-bold uppercase tracking-wider">
            <AppIcon name="zap" size={9} />
            Externe
          </div>
        {/if}
      </div>
    </div>
  </div>

  <!-- Department -->
  <div class="flex flex-col min-w-0 flex-1 px-4">
    {#if dept}
      <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Unité</span>
      <div class="flex items-center gap-1.5">
        <AppIcon name="network" size={13} class="text-slate-400 shrink-0" />
        <span class="text-[0.82rem] font-medium text-slate-600 truncate">{dept.name}</span>
      </div>
    {/if}
  </div>

  <!-- Status -->
  <div class="flex flex-col items-center shrink-0 w-[14%]">
    <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-1">Statut</span>
    <Badge variant="outline" class={cn("h-5 px-2 text-[0.65rem] font-bold border-none", stCfg.color)}>
      <AppIcon name={stCfg.icon} size={10} class="mr-1" />
      {stCfg.label}
    </Badge>
  </div>

  <!-- Date -->
  <div class="flex flex-col items-end shrink-0 w-[12%] pr-3 text-right">
    <span class="text-[0.62rem] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Ouvert le</span>
    <span class="text-[0.8rem] font-medium text-slate-600">
      {new Date(vacancy.openedDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
    </span>
  </div>

  <!-- Actions -->
  <div class="flex items-center pr-2">
    {@render ItemActions()}
  </div>
</div>


  
