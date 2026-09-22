<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { EmployeeEducation } from "@/hr/modules/employees/types/types";
  import { ACADEMIC_LEVELS } from "@/hr/modules/employees/constants/education";


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


<div class="group relative flex items-start gap-3.5 p-3.5 rounded-xl border border-slate-200 shadow-fine hover:border-violet-200 hover:shadow-sm transition-all">
  <span class="h-9 w-9 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center shrink-0 group-hover:bg-violet-100 transition-colors mt-0.5">
    <AppIcon name="graduation-cap" size={16} class="text-violet-600" />
  </span>

  <div class="flex-1 min-w-0">
    <div class="flex items-start justify-between gap-3">
      <div class="min-w-0">
        <h4 class="text-[0.88rem] font-bold text-slate-900 tracking-tight leading-tight">
          {ACADEMIC_LEVELS.find(l => l.value === ed.degree)?.label || ed.degree}
        </h4>
        <div class="flex items-center gap-2 mt-1.5 flex-wrap">
          <span class="inline-flex items-center gap-1.5 text-[0.85rem] font-medium text-slate-600">
            <AppIcon name="building" size={16} class="text-slate-400" />
            {ed.institute}
          </span>
          {#if ed.location}
            <span class="h-1 w-1 rounded-full bg-slate-300 shrink-0"></span>
            <span class="inline-flex items-center gap-1.5 text-[0.85rem] text-slate-500">
              <AppIcon name="map-pin" size={16} class="text-slate-400" />
              {ed.location}
            </span>
          {/if}
        </div>
        {#if ed.start_year || ed.end_year || ed.major}
          <div class="flex items-center gap-2 mt-1.5 flex-wrap">
            {#if ed.start_year || ed.end_year}
              <span class="inline-flex items-center gap-1 text-[0.85rem] font-medium text-slate-500 bg-slate-50 border border-slate-100 rounded-full px-2 py-0.5">
                <AppIcon name="calendar" size={16} class="text-slate-400" />
                {#if ed.start_year && ed.end_year}
                  {ed.start_year} – {ed.end_year}
                {:else if ed.start_year}
                  Depuis {ed.start_year}
                {:else if ed.end_year}
                  Jusqu'à {ed.end_year}
                {/if}
              </span>
            {/if}
            {#if ed.major}
              <span class="text-[0.85rem] text-slate-500">
                <span class="font-semibold text-slate-600 text-[0.85rem]">Spécialité:</span> {ed.major}
              </span>
            {/if}
          </div>
        {/if}
      </div>
      
      <div class="flex items-center gap-1 shrink-0">
        <button 
          onclick={() => onEdit(ed)}
          class="h-8 w-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-violet-600 hover:bg-violet-50 border border-transparent hover:border-violet-100 transition-colors cursor-pointer"
          title="Modifier"
        >
          <AppIcon name="edit" size={18} />
        </button>
        <button 
          onclick={() => onDelete(ed.id, ed.degree)}
          class="h-8 w-8 rounded-lg flex items-center justify-center text-red-400 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-100 transition-colors cursor-pointer"
          title="Supprimer"
        >
          <AppIcon name="trash-2" size={18} />
        </button>
      </div>
    </div>
  </div>
</div>

