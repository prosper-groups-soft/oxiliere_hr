<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { formatDate } from '@/utilities/common/date';
  import type { TimelineEvent } from '@/features/employees/types/types';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { cn } from '@/utilities/common/css';

  let { events = [] } = $props<{ events: TimelineEvent[] }>();

  // Configuration colors for status
  const statusConfig: Record<string, { label: string, color: string, bgColor: string }> = {
    'Senior Dev': { label: 'Senior Dev', color: 'text-emerald-700', bgColor: 'bg-emerald-50 border-emerald-200' },
    'Junior Dev': { label: 'Junior Dev', color: 'text-blue-700', bgColor: 'bg-blue-50 border-blue-200' },
    'Engineering': { label: 'Engineering', color: 'text-purple-700', bgColor: 'bg-purple-50 border-purple-200' },
    'Manager': { label: 'Manager', color: 'text-amber-700', bgColor: 'bg-amber-50 border-amber-200' },
    'Lead': { label: 'Lead', color: 'text-red-700', bgColor: 'bg-red-50 border-red-200' },
    'Intern': { label: 'Intern', color: 'text-slate-700', bgColor: 'bg-slate-50 border-slate-200' }
  };
</script>


<Card class="shadow-none">
  <CardHeader>
    <CardTitle class="flex items-center gap-2">
      <AppIcon name="clock" size={20} />
      Parcours collaborateur
    </CardTitle>
  </CardHeader>
  <CardContent class="space-y-3">
    {#if events.length === 0}
      <div class="text-center py-8">
        <AppIcon name="clock" size={32} class="text-primary mx-auto mb-3" />
        <p class="text-slate-500">Aucun historique disponible</p>
        <p class="text-sm text-slate-400 mt-1">Les événements apparaîtront ici une fois enregistrés</p>
      </div>
    {:else}
      {#each events as event (event.id)}
        <div class="flex gap-4 p-4 border-l-2 border-slate-200">
          <div class="flex-shrink-0">
            <div class="h-10 w-10 rounded-full bg-slate-100 border-2 border-slate-200 flex items-center justify-center">
              <AppIcon name="calendar" size={16} class="text-primary" />
            </div>
          </div>
          
          <div class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <h6 class="font-medium text-slate-900 text-[0.875rem]!">{event.label}</h6>
              <time class="text-sm text-slate-500">{formatDate(event.date, false, false)}</time>
            </div>
            
            <div class="flex items-center gap-2">
              <Badge 
                variant="outline" 
                class={cn(
                  "text-xs font-medium border",
                  statusConfig[event.status]?.bgColor || "bg-slate-50 border-slate-200",
                  statusConfig[event.status]?.color || "text-slate-700"
                )}
              >
                {statusConfig[event.status]?.label || event.status}
              </Badge>
              {#if event.description}
                <p class="text-sm text-slate-700 mt-1">{event.description}</p>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </CardContent>
</Card>

