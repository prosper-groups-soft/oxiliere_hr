<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import type { Transition, JobPosition } from "../../../types/types";
  import { fade } from "svelte/transition";
  import { 
    getTransitionConfig 
  } from "../../../constants/transition.constants";
  import { buildFullName } from "@/hr/utilities/common/employee.utils";
  import { ORG_UNIT_ICONS } from "../../../constants/orgUnit.constants";

  let { 
    transition,
    index = 0,
    onEdit,
    onDelete
  } = $props<{ 
    transition: Transition,
    onEdit?: (trans: Transition) => void;
    onDelete?: (trans: Transition) => void;
    index?: number;
  }>();

  // Use full position objects from API if available, otherwise fallback
  function getPositionData(position?: JobPosition | null): { name: string | null; orgUnit: string | null; orgUnitType: string | null } {
    if (!position) return { name: null, orgUnit: null, orgUnitType: null };
    return {
      name: position.name || "Poste inconnu",
      orgUnit: position.org_unit?.name || null,
      orgUnitType: position.org_unit?.type || null
    };
  }

  // --- Derived State ---
  const isHire = $derived(transition.transition_type === 'HIRE');
  const isOffboard = $derived(transition.transition_type === 'OFFBOARD');

  // Build employee name from nested employee data
  const employeeName = $derived(
    transition.employee?.name ||
    buildFullName(transition.employee) ||
    "Employé inconnu"
  );
  const cfg = $derived(getTransitionConfig(transition.transition_type));

  // Use API-provided full position objects
  const fromData = $derived(getPositionData(transition.from_position));
  const toData = $derived(getPositionData(transition.to_position));
  
  const displayDate = $derived(
    new Date(transition.date).toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short', 
      year: 'numeric' 
    })
  );
</script>


<div 
  in:fade={{ duration: 300 }}
  class="group flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
  role="none"
  onclick={() => onEdit?.(transition)}
>
  <!-- Type Badge (colonne étroite) -->
  <div class="w-[10%] flex items-center">
    <Badge 
      variant="outline"
      class="{cfg.bg} {cfg.color} {cfg.hoverBg} border-0 text-[0.84rem] font-semibold px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors"
    >
      <AppIcon name={cfg.icon} size={15} />
      {cfg.label}
    </Badge>
  </div>

  <!-- Employee (colonne employé) -->
  <div class="w-[16%] flex flex-col justify-center gap-0.5">
    <span class="text-[0.85rem] font-medium text-slate-800 truncate">
      {employeeName}
    </span>
    <span class="text-[0.84rem] text-slate-400">
    </span>
  </div>

  <!-- From Position (colonne origine) -->
  <div class="w-[20%] flex flex-col justify-center gap-0.5">
    {#if isHire}
      <span class="text-[0.85rem] text-slate-400">Recrutement externe</span>
    {:else}
      <div class="flex items-center gap-1.5">
        <AppIcon name="arrow-up-left" size={15} class="text-slate-400" />
        <span class="text-[0.85rem] font-medium text-slate-700 truncate">
          {fromData.name ?? '-'}
        </span>
      </div>
      {#if transition.from_seniority_level}
        <div class="flex items-center gap-1.5 text-slate-400 text-[0.85rem] pl-5">
          <Badge variant="outline" class="text-[0.75rem] px-2 py-0.5 border-slate-200 bg-slate-50">
            {transition.from_seniority_level.label}
          </Badge>
        </div>
      {/if}
      {#if fromData.orgUnit}
        <div class="flex items-center gap-1.5 text-slate-400 text-[0.85rem] pl-5">
          <AppIcon name={ORG_UNIT_ICONS[fromData.orgUnitType ?? 'DEPARTMENT']} size={15} />
          <span class="truncate text-[0.85rem]">{fromData.orgUnit}</span>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Arrow indicator -->
  <div class="w-[2%] flex justify-center">
    <div class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center group-hover:bg-indigo-100 transition-colors">
      <AppIcon name="arrow-right" size={15} class="text-slate-400 group-hover:text-indigo-500" />
    </div>
  </div>

  <!-- To Position (colonne destination) -->
  <div class="w-[20%] flex flex-col justify-center gap-0.5">
    {#if isOffboard}
      <span class="text-[0.84rem] text-red-500 font-medium">
        Fin de contrat
      </span>
    {:else}
      <div class="flex items-center gap-1.5">
        <AppIcon name="arrow-down-right" size={15} class={cfg.color} />
        <span class="text-[0.84rem] font-semibold {cfg.color} truncate">
          {toData.name ?? '-'}
        </span>
      </div>
      {#if transition.to_seniority_level}
        <div class="flex items-center gap-1.5 text-slate-400 text-[0.85rem] pl-5">
          <Badge variant="outline" class="{cfg.color} text-[0.75rem] px-2 py-0.5 border-current bg-opacity-10" style="background-color: {cfg.bg};">
            {transition.to_seniority_level.label}
          </Badge>
        </div>
      {/if}
      {#if toData.orgUnit}
        <div class="flex items-center gap-1.5 text-slate-400 text-[0.84rem] pl-5">
          <AppIcon name={ORG_UNIT_ICONS[toData.orgUnitType ?? 'DEPARTMENT']} size={15} />
          <span class="truncate text-[0.84rem]">{toData.orgUnit}</span>
        </div>
      {/if}
    {/if}
  </div>

  <!-- Reason / Motif (colonne variable) -->
  <div class="w-[14%] flex items-center px-2">
    {#if transition.reason}
      <div class="flex items-center gap-1.5 min-w-0">
        <AppIcon name="quote" size={15} class="text-slate-400 shrink-0" />
        <span class="text-[0.85rem] text-slate-600 truncate">{transition.reason}</span>
      </div>
    {:else}
      <span class="text-slate-300 text-[0.85rem]">-</span>
    {/if}
  </div>

  <!-- Date (colonne date) -->
  <div class="w-[12%] text-right flex flex-col justify-center pr-4">
    <span class="text-[0.84rem] font-medium text-slate-700">
      {displayDate}
    </span>
  </div>

  <!-- Actions (colonne actions) -->
  <div class="w-[6%] flex items-center justify-end gap-1">
    <button 
      onclick={(e) => { e.stopPropagation(); onEdit?.(transition); }}
      class="p-1.5 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors cursor-pointer"
      title="Modifier"
    >
      <AppIcon name="edit" size={17} />
    </button>
    {#if onDelete}
      <button 
        onclick={(e) => { e.stopPropagation(); onDelete?.(transition); }}
        class="p-1.5 rounded text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer hidden"
        title="Supprimer"
      >
        <AppIcon name="trash-2" size={17} />
      </button>
    {/if}
  </div>
</div>

