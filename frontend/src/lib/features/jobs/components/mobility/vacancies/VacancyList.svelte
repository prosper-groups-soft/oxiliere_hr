<script lang="ts">
  import type { Vacancy } from "../../../types/types";
  import VacancyItem from "./VacancyItem.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";

  let { 
    vacancies = [],
    onEdit,
    onNew
  } = $props<{ 
    vacancies: Vacancy[],
    onEdit: (vac: Vacancy) => void,
    onNew?: () => void
  }>();
</script>


<div class="bg-white overflow-hidden flex flex-col h-full flex-1">
  {#each vacancies as vac (vac.id)}
    <VacancyItem vacancy={vac} {onEdit} />
  {:else}
    <div class="flex flex-col items-center justify-center flex-1">
      <Empty 
        title="Aucun besoin identifié" 
        description="Tous les postes critiques sont actuellement pourvus." 
        icon="inbox" 
        iconStrokeWidth={1}
        iconClass="text-primary"
      >
        {#if onNew}
          <EmptyButton labelElement="un besoin" {onNew} />
        {/if}
      </Empty>
    </div>
  {/each}
</div>

