<script lang="ts">
  import { calendarStore } from "@/hr/modules/calendar/stores/calendar.svelte";

  let view = $derived(calendarStore.view);

  function setView(v: 'month' | 'year') {
    calendarStore.view = v;
  }
</script>


<div class="flex items-center gap-1 bg-slate-100/80 p-1 rounded-lg relative">
  <!-- Magic Background Slider -->
  <div 
    class="absolute bg-white shadow-sm rounded-md transition-all duration-300 ease-in-out pointer-events-none h-[calc(100%-8px)] top-1"
    style="width: 60px; left: {view === 'month' ? '4px' : '68px'};"
  ></div>

  <button 
    class="w-[60px] h-7.5 text-xs font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'month' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
    onclick={() => setView('month')}
  >
    Mois
  </button>
  <button 
    class="w-[60px] h-7.5 text-xs font-medium rounded-md cursor-pointer transition-colors relative z-10 {view === 'year' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'}"
    onclick={() => setView('year')}
  >
    Année
  </button>
</div>

