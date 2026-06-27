<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { Vacancy } from "../../../types/types";
  import { cn } from "@/utilities/common/css";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { 
    getPriorityConfig, 
    getStatusConfig 
  } from "../../../constants/vacancy.constants";
  import { ORG_UNIT_ICONS } from "../../../constants/orgUnit.constants";

  let { 
    vacancy,
    onEdit,
    onDelete
  } = $props<{ 
    vacancy: Vacancy,
    onEdit?: (vac: Vacancy) => void;
    onDelete?: (vac: Vacancy) => void;
    index?: number;
  }>();

  // Use API-provided position data
  const pos = $derived(vacancy.position);
  const orgUnitName = $derived(pos?.org_unit?.name || null);
  const orgUnitType = $derived(pos?.org_unit?.type || null);
  const priCfg = $derived(getPriorityConfig(vacancy.priority));
  const stCfg = $derived(getStatusConfig(vacancy.status));
  
  // Format dates
  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  const isClosed = $derived(['FILLED', 'CANCELLED'].includes(vacancy.status));
</script>


{#snippet ItemActions()}
  <button
    onclick={(e) => { e.stopPropagation(); onEdit?.(vacancy); }}
    class="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-primary cursor-pointer outline-none"
    title="Modifier"
  >
    <AppIcon name="edit" size={18} />
  </button>
{/snippet}


<div 
  in:fly={{ y: 10, duration: 300, easing: cubicOut }}
  onclick={() => onEdit(vacancy)}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onEdit(vacancy)}
  class="group/row relative flex items-center w-full h-20 shrink-0 px-0 bg-white border-b border-slate-100 hover:bg-indigo-50/30 overtransition-colors duration-150 cursor-pointer overflow-hidden"
>
  <!-- Briefcase Icon + Position Title + Priority -->
  <div class="flex items-center w-[18%] shrink-0 pl-4 min-w-0 gap-3">
    <div class="flex flex-col min-w-0">
      <span class="font-semibold text-[0.87rem] text-slate-800 truncate leading-tight group-hover/row:text-primary transition-colors">
        {pos?.name || "-"}
      </span>
      <div class="flex items-center gap-1.5 mt-0.5">
        <span class={cn("inline-flex items-center justify-center gap-1 text-[0.85rem] font-medium", priCfg.color)}>
          <AppIcon name={priCfg.icon} size={16} />
          {priCfg.label}
        </span>
        {#if vacancy.status === 'RECRUITMENT'}
          <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-purple-100 text-purple-700 text-[0.85rem] font-semibold">
            <AppIcon name="users" size={15} />
            Rec. externe
          </span>
        {/if}
      </div>
    </div>
  </div>

  <!-- Org Unit -->
  <div class="flex flex-col min-w-0 flex-1 px-4 justify-center">
    {#if orgUnitName}
      <span class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Unité</span>
      <div class="flex items-center gap-1.5">
        <AppIcon name={ORG_UNIT_ICONS[orgUnitType ?? 'DEPARTMENT']} size={16} class="text-slate-400 shrink-0" />
        <span class="text-[0.86rem] font-medium text-slate-600 truncate">{orgUnitName}</span>
      </div>
    {:else}
      <span class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Unité</span>
      <span class="text-[0.85rem] flex items-center gap-1 font-medium text-slate-400">
        <AppIcon name="circle-x" size={15} class="text-slate-300" />
        Non assignée
      </span>
    {/if}
  </div>

  <!-- Status -->
  <div class="flex flex-col items-center shrink-0 w-[12%] justify-center">
    <span class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider mb-1">Statut</span>
    <div class={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full", stCfg.badgeClass)}>
      <AppIcon name={stCfg.icon} size={15} />
      <span class="text-[0.8rem] font-medium">{stCfg.label}</span>
    </div>
  </div>

  <!-- Reason / Motif -->
  <div class="flex items-center shrink-0 w-[28%] px-2">
    {#if vacancy.reason}
      <div class="flex items-center gap-1.5 min-w-0">
        <AppIcon name="quote" size={15} class="text-slate-400 shrink-0" />
        <span class="text-[0.85rem] text-slate-600 truncate">{vacancy.reason}</span>
      </div>
    {:else}
      <span class="text-slate-300 flex items-center justify-center gap-1">
        <AppIcon name="circle-x" size={15} class="text-slate-400" />
        <span class="text-inherit text-[0.85rem]">Aucun motif</span>
      </span>
    {/if}
  </div>

  <!-- Dates -->
  <div class="flex flex-col items-end shrink-0 w-[14%] pr-3 text-right justify-center gap-1">
    <!-- Date d'ouverture -->
    <div class="flex items-center gap-1.5">
      <span class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Ouvert</span>
      <span class="text-[0.85rem] font-medium text-slate-600">
        {formatDate(vacancy.openedDate)}
      </span>
    </div>
    <!-- Date cible -->
    {#if vacancy.targetDate}
      <div class="flex items-center gap-1.5">
        <span class="text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Cible</span>
        <span class="text-[0.85rem] font-medium text-slate-600">
          {formatDate(vacancy.targetDate)}
        </span>
      </div>
    {/if}
  </div>

  <!-- Actions -->
  <div class="flex items-center pr-6">
    {@render ItemActions()}
  </div>
</div>

