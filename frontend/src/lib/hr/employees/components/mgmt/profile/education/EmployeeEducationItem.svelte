<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { EmployeeEducation } from "@/hr/employees/types/types";
  import { ACADEMIC_LEVELS } from "@/hr/employees/constants/education";

  let { 
    ed, 
    isLast = false,
    onEdit,
    onDelete
  } = $props<{
    ed: EmployeeEducation;
    isLast?: boolean;
    onEdit: (ed: EmployeeEducation) => void;
    onDelete: (id: string, degree: string) => void;
  }>();

</script>

<div class="group relative flex items-start gap-4 p-2 rounded-lg hover:cursor-pointer hover:bg-indigo-50/30 border border-transparent hover:border-indigo-100 transition-all {isLast ? '' : 'border-b-slate-100/50'}">
  <div class="mt-0.5 p-2.5 bg-indigo-50/50 text-indigo-500 rounded-lg border border-indigo-100/50 group-hover:scale-105 transition-transform shrink-0">
    <AppIcon name="graduation-cap" size={20} />
  </div>

  <div class="flex-1 min-w-0">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0 pr-4">
        <h4 class="text-[0.88rem] font-bold text-slate-800 flex items-center gap-2">
          {ACADEMIC_LEVELS.find(l => l.value === ed.degree)?.label || ed.degree}
        </h4>
        <div class="flex items-center gap-3 mt-1 text-slate-500">
          <span class="flex items-center gap-1.5 font-medium text-[0.84rem]">
            <AppIcon name="building" size={16} class="text-slate-400" />
            {ed.institute}
          </span>
          {#if ed.location}
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span class="flex items-center gap-1.5 font-medium text-[0.84rem]">
              <AppIcon name="map-pin" size={16} class="text-slate-400" />
              {ed.location}
            </span>
          {/if}
        </div>
        {#if ed.start_year || ed.end_year}
          <div class="flex items-center gap-3 mt-1.5 text-slate-400">
            <span class="flex items-center gap-1 text-[0.84rem]">
              <AppIcon name="calendar" size={16} />
              {#if ed.start_year && ed.end_year}
                {ed.start_year} - {ed.end_year}
              {:else if ed.start_year}
                Depuis {ed.start_year}
              {:else if ed.end_year}
                Jusqu'à {ed.end_year}
              {/if}
            </span>
            {#if ed.major}
              <span class="w-1 h-1 rounded-full bg-slate-300"></span>
              <span class="font-medium text-slate-500 text-[0.84rem]">
                Spécialité: {ed.major}
              </span>
            {/if}
          </div>
        {/if}
      </div>
      
      <div class="flex items-center gap-1">
        <button 
          onclick={() => onEdit(ed)}
          class="p-2 text-slate-400 hover:text-indigo-600 hover:bg-indigo-100 rounded-lg transition-colors cursor-pointer"
          title="Modifier"
        >
          <AppIcon name="edit" size={17} />
        </button>
        <button 
          onclick={() => onDelete(ed.id, ed.degree)}
          class="p-2 text-red-600 hover:text-red-600 hover:bg-red-100 rounded-lg transition-colors cursor-pointer"
          title="Supprimer"
        >
          <AppIcon name="trash-2" size={17} />
        </button>
      </div>
    </div>
  </div>
</div>

