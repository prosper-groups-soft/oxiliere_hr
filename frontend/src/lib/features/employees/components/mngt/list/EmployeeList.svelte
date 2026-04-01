<script lang="ts">
  import { flip } from 'svelte/animate';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmployeeRow from "./views/EmployeeRow.svelte";
  import EmployeeCard from "./views/EmployeeCard.svelte";
  import { cn } from "@/utilities/common/css";

  let { employees, viewMode = 'list' } = $props();
</script>


<div class="flex flex-col h-full">
  {#if employees.length === 0}
    <div in:fade={{ duration: 200 }} class="h-full">
      <Empty 
        title="Aucun employé trouvé" 
        description="Nous n'avons trouvé aucun employé correspondant à vos critères de recherche ou filtres." 
        icon='no-user'
        iconSize={34}
        iconClass="text-primary"
      />
    </div>
  {:else}
    <div class="relative h-full">
      {#key viewMode}
        <div 
          in:fly={{ y: 20, duration: 400, delay: 200, easing: cubicOut }}
          out:fade={{ duration: 200 }}
          class={cn(
            "h-full w-full",
            viewMode === 'grid' 
              ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-0" 
              : "flex flex-col"
          )}
        >
          {#each employees as employee (employee.id)}
            <div 
              animate:flip={{ duration: 400, easing: cubicOut }}
              class={viewMode === 'grid' ? 'px-4' : ''}
            >
            {#if viewMode === 'list'}
              <EmployeeRow {employee} />
            {:else}
              <EmployeeCard {employee} />
            {/if}
          </div>
        {/each}
      </div>
      {/key}
    </div>
  {/if}
</div> 

