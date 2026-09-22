<script lang="ts">
  import type { Vacancy } from "../../../types/types";
  import VacancyItem from "./VacancyItem.svelte";
  import { fade } from "svelte/transition";

  let { 
    vacancies = [],
    onEdit,
    onDelete
  } = $props<{ 
    vacancies: Vacancy[];
    onEdit: (vac: Vacancy) => void;
    onDelete?: (vac: Vacancy) => void;
  }>();
</script>


<div class="flex flex-col h-full flex-1 overflow-hidden bg-white">
  <div class="flex-1 overflow-y-auto" in:fade={{ duration: 200 }}>
    {#each vacancies as vac (vac.id)}
      <VacancyItem vacancy={vac} {onEdit} {onDelete} />
    {/each}
  </div>
</div>

