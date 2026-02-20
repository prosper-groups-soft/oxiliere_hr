<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { formatDate } from '@/utilities/common/date';
  import type { TimelineEvent } from '../../../types/types';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import Badge from '@/components/ui/badge/badge.svelte';

  let { events = [] } = $props<{ events: TimelineEvent[] }>();
</script>


<Card class="bg-white h-full flex flex-col overflow-hidden p-0 shadow-none">
  <CardHeader class="pb-4 shrink-0 border-b border-slate-50 p-0! py-3.5!">
    <CardTitle class="text-[1rem] font-bold text-slate-800 flex items-center gap-2">
      <AppIcon name="history" size={18} class="text-primary" />
      Parcours Collaborateur
    </CardTitle>
  </CardHeader>
  
  <CardContent class="flex-1 overflow-y-auto custom-scrollbar p-6">
    <div class="relative space-y-8 before:absolute before:inset-0 before:ml-2.75 before:-translate-x-px before:h-full before:w-0.5 before:bg-linear-to-b before:from-primary/40 before:via-slate-100 before:to-transparent">
      {#each events as event, i}
        <div class="relative flex flex-col pl-10 group">
          <div class="absolute left-0 top-1 w-6 h-6 translate-x-0 rounded-full bg-white border-2 border-primary flex items-center justify-center z-10 shadow-sm group-hover:scale-110 transition-transform">
             <div class="w-2 h-2 rounded-full bg-primary"></div>
          </div>
          
          <div class="flex flex-col gap-1">
            <div class="flex items-center justify-between">
              <p class="text-[0.85rem] font-extrabold text-slate-800">{event.label}</p>
              <time class="text-[0.8rem] font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded uppercase tracking-tighter">
                {formatDate(event.date, false, true)}
              </time>
            </div>
            
            <div class="flex items-center gap-2">
               <span class="text-[0.8rem] text-slate-500 font-medium">{event.status}</span>
               {#if i === 0}
                 <Badge class="h-4 text-[0.6rem] bg-emerald-500 text-white border-none">Actuel</Badge>
               {/if}
            </div>
          </div>
        </div>
      {:else}
        <div class="flex flex-col items-center justify-center py-10 opacity-50">
           <AppIcon name="clock" size={32} class="text-slate-300 mb-2" />
           <p class="text-xs text-slate-400 italic">Aucun historique disponible</p>
        </div>
      {/each}
      
    </div>
  </CardContent>
</Card>

