<script lang="ts">
  import EmployeeRow from "./EmployeeRow.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  let { employees } = $props();
</script>


<div class="h-full">
  <div class="flex flex-col pb-0">
    {#if employees.length === 0}
      <div class="flex flex-col items-center justify-center py-24 px-4 text-center border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
        <div class="h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center mb-4">
          <AppIcon name="users" size={32} class="text-slate-400" />
        </div>
        <h3 class="text-lg font-bold text-slate-800 mb-1">Aucun résultat trouvé</h3>
        <p class="text-slate-500 max-w-[280px] text-sm leading-relaxed">
          Nous n'avons trouvé aucun employé correspondant à vos critères de recherche ou filtres.
        </p>
      </div>
    {:else}
      {#each employees as employee (employee.id)}
        <EmployeeRow {employee} />
      {/each}
    {/if}
  </div>
</div>

