<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import type { OnboardingEducationItem } from "@/hr/modules/employees/types/types";
  import { ACADEMIC_LEVELS } from "@/hr/modules/employees/constants/education";

  let {
    education,
    index,
    onEdit
  } = $props<{
    education: OnboardingEducationItem;
    index: number;
    onEdit: (index: number) => void;
  }>();

  function handleDelete() {
    onboardingStore.removeEducation(index);
  }

  function handleEdit() {
    onEdit(index);
  }
</script>


<div class="group relative flex items-start gap-4 p-3 rounded-lg bg-white border border-slate-200 hover:border-indigo-200 transition-all">
  <div class="mt-0.5 p-2.5 bg-indigo-50/50 text-indigo-500 rounded-lg border border-indigo-100/50 group-hover:scale-105 transition-transform shrink-0">
    <AppIcon name="graduation-cap" size={20} />
  </div>

  <div class="flex-1 min-w-0">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0 pr-4">
        <h4 class="text-[0.88rem] font-bold text-slate-800 flex items-center gap-2">
          {ACADEMIC_LEVELS.find(l => l.value === education.degree)?.label || education.degree}
        </h4>
        <div class="flex items-center gap-3 mt-1 text-slate-500">
          <span class="flex items-center gap-1.5 font-medium text-[0.84rem]">
            <AppIcon name="building" size={16} class="text-slate-400" />
            {education.institute}
          </span>
          {#if education.location}
            <span class="w-1 h-1 rounded-full bg-slate-300"></span>
            <span class="flex items-center gap-1.5 font-medium text-[0.84rem]">
              <AppIcon name="map-pin" size={16} class="text-slate-400" />
              {education.location}
            </span>
          {/if}
        </div>
        {#if education.start_year || education.end_year}
          <div class="flex items-center gap-3 mt-1.5 text-slate-400">
            <span class="flex items-center gap-1 text-[0.84rem]">
              <AppIcon name="calendar" size={16} />
              {#if education.start_year && education.end_year}
                {education.start_year} - {education.end_year}
              {:else if education.start_year}
                Depuis {education.start_year}
              {:else if education.end_year}
                Jusqu'à {education.end_year}
              {/if}
            </span>
            {#if education.major}
              <span class="w-1 h-1 rounded-full bg-slate-300"></span>
              <span class="font-medium text-slate-500 text-[0.84rem]">
                Spécialité: {education.major}
              </span>
            {/if}
          </div>
        {/if}
      </div>
      
      <div class="flex items-center gap-1">
        <button
          onclick={handleEdit}
          class="p-2 text-slate-500 hover:text-indigo-600 hover:bg-indigo-100 rounded-lg transition-colors cursor-pointer"
          title="Modifier"
        >
          <AppIcon name="edit" size={17} />
        </button>
        <button
          onclick={handleDelete}
          class="p-2 text-red-600 hover:text-red-600 hover:bg-red-100 rounded-lg transition-colors cursor-pointer"
          title="Supprimer"
        >
          <AppIcon name="trash-2" size={17} />
        </button>
      </div>
    </div>
  </div>
</div>

