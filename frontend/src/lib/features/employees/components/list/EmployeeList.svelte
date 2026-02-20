<script lang="ts">
  import { flip } from 'svelte/animate';
  import { fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Empty from '@/components/shared/containers/Empty.svelte';
  import EmployeeRow from "./EmployeeRow.svelte";

  let { employees } = $props();
</script>


<div class="flex flex-col h-full">
  {#if employees.length === 0}
    <div in:fade={{ duration: 200 }} class="h-full">
      <Empty 
        title="Aucun employé trouvé" 
        description="Nous n'avons trouvé aucun employé correspondant à vos critères de recherche ou filtres." 
        icon='no-user'
        iconSize={34}
        iconClass="text-slate-500"
      />
    </div>
  {:else}
    {#each employees as employee (employee.id)}
      <div 
        animate:flip={{ duration: 400, easing: cubicOut }}
        transition:fade={{ duration: 200 }}
      >
        <EmployeeRow {employee} />
      </div>
    {/each}
  {/if}
</div>

