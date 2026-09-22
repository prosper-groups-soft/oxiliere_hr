<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import type { JobPosition } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import PositionService from "../../../../services/positionService";
  import { fade } from "svelte/transition";
  import { payrollConfigStore } from "@/hr/modules/payroll/stores/configuration/payrollConfigStore.svelte";
  import { CURRENCIES } from "@/hr/constants/finance";
  import { fromCDF, formatCurrency } from "@/hr/utilities/common/currency";
  import { ORG_UNIT_ICONS } from "../../../../constants/orgUnit.constants";

  let { pos, index = 0, onEdit, onDelete } = $props<{
    pos: JobPosition;
    index?: number;
    onEdit?: (pos: JobPosition) => void;
    onDelete?: (pos: JobPosition) => void;
  }>();

  const orgUnit = $derived(pos.org_unit);
  const allRequirements = $derived(pos.requirements || []);
  const allSkills = $derived(pos.skills || []);

  // --- Currency ---
  const currency = $derived(payrollConfigStore.configuration?.currency ?? 'CDF');
  const currencySymbol = $derived(currency === CURRENCIES.USD ? '$' : 'FC');

  const seniorityDisplay = $derived(PositionService.formatSeniorityLevelsForDisplay(pos, 5));
</script>


<div 
  transition:fade={{ duration: 300 }}
  class="group flex items-center py-2.5 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
  role="none"
  onclick={() => onEdit?.(pos)}
>

  <!-- Seniority Levels -->
  <div class="w-[25%] flex items-center">
    {#if seniorityDisplay.levels.length > 0}
      <div class="grid grid-cols-2 gap-0.5 w-full">
        {#each seniorityDisplay.levels as seniorityLink}
          <div class="flex flex-col gap-1">
            <Badge 
              variant="outline"
              class="{jobsStore.getSeniorityColor(seniorityLink.seniority_level.level)} border text-[0.77rem] font-medium px-2 py-0.5 shadow-none bg-slate-100 rounded-full border-white/20 whitespace-nowrap"
            >
              Niveau {seniorityLink.rank} : {SENIORITY_LABELS[seniorityLink.seniority_level.level as keyof typeof SENIORITY_LABELS] || seniorityLink.seniority_level.level}
            </Badge>
            {#if seniorityLink.salary_min > 0 && seniorityLink.salary_max > 0}
              <div class="text-[0.77rem] text-slate-500 leading-tight">
                {formatCurrency(fromCDF(seniorityLink.salary_min, currency), currency)} - {formatCurrency(fromCDF(seniorityLink.salary_max, currency), currency)}
              </div>
            {/if}
          </div>
        {/each}
        {#if seniorityDisplay.hasMore}
          <div class="col-span-2 text-center">
            <span class="text-slate-400 text-[0.77rem]">+{seniorityDisplay.remainingCount} autres</span>
          </div>
        {/if}
      </div>
    {:else}
      <span class="text-slate-300 text-[0.82rem] bg-slate-300 rounded-full h-0.5 w-4"></span>
    {/if}
  </div>

  <!-- Poste / Famille -->
  <div class="w-[20%] flex flex-col justify-center gap-1.5">
    <div class="flex items-center gap-2">
      <span class="text-[0.85rem] font-medium text-slate-800 truncate">
        {pos.name}
      </span>
      {#if pos.job_family?.name}
        <span class="text-[0.84rem] text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded-full">
          {pos.job_family.name}
        </span>
      {/if}
    </div>
    {#if orgUnit}
      <div class="flex items-center gap-1.5 text-slate-400 text-[0.85rem]">
        <AppIcon name={ORG_UNIT_ICONS[orgUnit.type] ?? 'business'} size={17} class="text-slate-500" />
        <span class="truncate text-[0.85rem]">{orgUnit.name}</span>
      </div>
    {/if}
  </div>

  <!-- Skills -->
  <div class="w-[27.5%] flex flex-wrap items-center gap-1.5 px-2">
    {#if allSkills.length > 0}
      {#each allSkills.slice(0, 3) as skill}
        <span class="text-[0.82rem] bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5 whitespace-nowrap">
          <AppIcon name="tag" size={14} />
          {skill.name}
        </span>
      {/each}
      {#if allSkills.length > 3}
        <span class="text-slate-400 text-[0.82rem]">+{allSkills.length - 3}</span>
      {/if}
    {:else}
      <span class="text-slate-300 text-[0.82rem] bg-slate-300 rounded-full h-0.5 w-4"></span>
    {/if}
  </div>

  <!-- Requirements -->
  <div class="w-[27.5%] flex flex-wrap items-center gap-1.5 px-2">
    {#if allRequirements.length > 0}
      {#each allRequirements.slice(0, 3) as req}
        <span class="text-[0.82rem] bg-emerald-50 text-emerald-600 px-2 py-0.5 rounded-full font-medium flex items-center gap-1.5 whitespace-nowrap">
          <AppIcon name="circle-check" size={14} class="text-emerald-500" strokeWidth={1.7} />
          {req}
        </span>
      {/each}
      {#if allRequirements.length > 3}
        <span class="text-slate-400 text-[0.82rem]">+{allRequirements.length - 3}</span>
      {/if}
    {:else}
      <span class="text-slate-300 text-[0.82rem] bg-slate-300 rounded-full h-0.5 w-4"></span>
    {/if}
  </div>

  <!-- Actions -->
  <div class="w-[5%] flex items-center justify-end gap-1">
    <button 
      onclick={(e) => { e.stopPropagation(); onEdit?.(pos); }}
      class="p-1.5 rounded text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors cursor-pointer"
      title="Modifier"
    >
      <AppIcon name="edit" size={17} />
    </button>
    <button 
      onclick={(e) => { e.stopPropagation(); onDelete?.(pos); }}
      class="p-1.5 rounded text-red-400 hover:text-red-600 hover:bg-red-50 transition-colors cursor-pointer"
      title="Supprimer"
    >
      <AppIcon name="trash-2" size={17} />
    </button>
  </div>

</div>

