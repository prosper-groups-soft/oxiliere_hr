<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import type { JobPosition } from "../../../../types/types";
  import { fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";

  let { pos, index = 0, onEdit, onDelete } = $props<{
    pos: JobPosition;
    index?: number;
    onEdit?: (pos: JobPosition) => void;
    onDelete?: (pos: JobPosition) => void;
  }>();

  const dept = $derived(jobsStore.getDepartmentById(pos.departmentId));
  const seniorityDef = $derived(jobsStore.seniorityLevels.find(l => l.name === pos.seniority));
  const allRequirements = $derived([...(seniorityDef?.requirements || []), ...pos.requirements]);
</script>


<div 
  in:fly={{ y: 20, duration: 400, delay: index * 80, easing: cubicOut }}
  class="group relative bg-white/80 backdrop-blur-2xl border border-slate-50 rounded-xl p-5 shadow-fine hover:shadow-sm transition-all duration-300 cursor-default ring-1 ring-slate-200/40 flex flex-col gap-5"
>
  <!-- Glass reflection effect -->
  <div class="absolute inset-0 bg-linear-to-br from-white/60 to-transparent pointer-events-none rounded-xl"></div>

  <div class="relative z-10 flex flex-col h-full">
    <!-- Header: Icon, Actions, Title -->
    <div class="flex items-start justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="p-4 rounded-full bg-slate-50/90 group-hover:bg-primary/5 text-slate-500 group-hover:text-primary transition-all shadow-none border border-slate-200">
          <AppIcon name="briefcase" size={26} strokeWidth={1} class="text-primary"  />
        </div>
        <div>
          <h3 class="text-[0.78rem] text-medium mb-1.5 text-slate-800 uppercase">
            Fiche de poste
          </h3>
          <Badge 
            variant="outline"
            class="{jobsStore.getSeniorityColor(pos.seniority)} border text-[0.6rem] font-black uppercase tracking-widest px-2 py-0.5 shadow-none bg-slate-100 rounded-full border-white/20"
          >
            {jobsStore.seniorityLabels[pos.seniority]}
          </Badge>
        </div>
      </div>

      <div class="flex items-center gap-1">
        <button 
          onclick={() => onEdit?.(pos)}
          class="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-all border border-transparent cursor-pointer shadow-none"
          title="Modifier le poste"
        >
          <AppIcon name="edit" size={17} />
        </button>
        <button 
          onclick={() => onDelete?.(pos)}
          class="p-2 hover:bg-red-50/60 rounded-lg text-red-400 hover:text-red-600 transition-all border border-transparent cursor-pointer shadow-none"
          title="Supprimer le poste"
        >
          <AppIcon name="trash-2" size={17} />
        </button>
      </div>
    </div>

    <!-- Title & Department -->
    <div class="mb-5 flex justify-between items-center">
      <h4 class="text-[1.05rem] font-bold mb-1.5">
        {pos.title}
      </h4>
      {#if dept}
        <div class="flex items-center gap-1.5 text-slate-700 text-[0.8rem]">
          <AppIcon name="network" size={16} class="text-slate-400/80" />
          {dept.name}
        </div>
      {/if}
    </div>

    <!-- Skills Section -->
    {#if pos.skills.length > 0}
      <div class="space-y-2.5 mb-5">
        <h5 class="text-[0.78rem] text-medium mb-1.5 text-slate-800 uppercase">
          Compétences clés
        </h5>
        <div class="flex flex-wrap gap-1.5 ml-3.5 mt-1.5">
          {#each pos.skills as skill}
            <div class="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-blue-50/40 border border-blue-100 text-[0.72rem] font-medium text-blue-600 transition-colors group-hover:bg-blue-50/60 w-fit">
              <AppIcon name="tag" size={14} strokeWidth={1.7} class="opacity-80" />
              {skill.name} 
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Requirements List -->
    <div class="space-y-2.5 mb-6 flex-1">
      <span class="text-[0.78rem] text-medium text-slate-800 uppercase">
        Exigences & Profil
      </span>
      <div class="flex flex-wrap gap-1.5 ml-3.5 mt-1.5">
        {#each allRequirements as req}
          <div class="flex items-center gap-2 bg-slate-50/60 px-2 py-1 rounded-full border border-slate-200 text-[0.78rem] text-slate-700 group-hover:bg-indigo-50/60 group-hover:border-indigo-100/40 transition-colors w-fit">
            <AppIcon name="circle-check" size={15} class="text-emerald-500/80" strokeWidth={1.7} />
            {req}
          </div>
        {:else}
          <div class="w-full flex justify-center items-center py-4 bg-slate-50/40 rounded-2xl border border-dashed border-slate-200/60">
            <p class="text-[0.7rem] text-slate-400 font-medium">
              Aucune exigence spécifiée
            </p>
          </div>
        {/each}
      </div>
    </div>

    <!-- Footer: Salary Budget -->
    <div class="pt-4 border-t border-slate-100/40 flex items-center justify-between">
        <span class="text-[0.78rem] text-medium mb-1.5 text-slate-800 uppercase">
          Estimation Mensuelle
        </span>
        <div class="flex items-baseline gap-1.5">
          <span class="text-[0.82rem] tabular-nums">
            {pos.salaryRange.min.toLocaleString('fr-FR')}
          </span>
          <span class="text-[0.82rem]">à</span>
          <span class="text-[0.82rem] tabular-nums">
            {pos.salaryRange.max.toLocaleString('fr-FR')}
          </span>
          <span class="text-[0.82rem]">FC</span>
        </div>
    </div>
  </div>
</div>

