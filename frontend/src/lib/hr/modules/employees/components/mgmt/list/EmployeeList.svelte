<script lang="ts">
  import { flip } from 'svelte/animate';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import EmployeeRow from './views/EmployeeRow.svelte';
  import EmployeeCard from './views/EmployeeCard.svelte';
  import { cn } from '@/hr/utilities/common/css';


  let { 
    employees, 
    viewMode = 'list'
  } = $props<{ employees: any[]; viewMode?: 'list' | 'grid' }>();
</script>


<div class="flex flex-col h-full">
  <div class="relative h-full">
    {#key viewMode}
      {#if viewMode === 'list'}
        <div class="sticky top-0 z-1001 flex items-center h-8 px-6 bg-white border-b border-slate-100">
          <span class="w-[28%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
          <span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Unité Org.</span>
          <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Contrat</span>
          <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Embauche</span>
          <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Localisation</span>
          <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-4">Statut</span>
          <span class="w-[5%]"></span>
        </div>
      {/if}
      <div
        in:fly={{ y: 20, duration: 400, delay: 200, easing: cubicOut }}
        out:fade={{ duration: 200 }}
        class={cn('w-full', viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-4 p-6' : 'flex flex-col')}
      >
        {#each employees as employee (employee.id)}
          <div animate:flip={{ duration: 400, easing: cubicOut }}>
            {#if viewMode === 'list'}<EmployeeRow {employee} />{:else}<EmployeeCard {employee} />{/if}
          </div>
        {/each}
      </div>
    {/key}
  </div>
</div>

