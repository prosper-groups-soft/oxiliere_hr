<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { formatDate } from '@/utilities/common/date';
  import type { TimelineEvent } from '@/features/employees/types/types';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { TRANSITION_TYPE_CONFIG } from '@/features/jobs/constants/transition.constants';
  import { getOrgUnitIcon } from '@/features/jobs/constants/orgUnit.constants';

  
  let { events = [] } = $props<{ events: TimelineEvent[] }>();

  /**
   * Get styling for an event based on its type and metadata
   */
  function getEventStyle(event: TimelineEvent) {
    if (event.type === 'transition' && event.metadata?.transition_type) {
      const config = TRANSITION_TYPE_CONFIG[event.metadata.transition_type as keyof typeof TRANSITION_TYPE_CONFIG];
      if (config) {
        return {
          icon: config.icon,
          iconClass: config.color,
          bgClass: config.bg,
          borderClass: config.border
        };
      }
    }
    
    // Default/Status style (Sober)
    return {
      icon: 'user-check',
      iconClass: 'text-slate-500',
      bgClass: 'bg-slate-50',
      borderClass: 'border-slate-200'
    };
  }
</script>


<Card class="shadow-none border-slate-200 rounded-none!">
  <CardHeader class="pb-4">
    <CardTitle class="flex items-center gap-2 text-slate-800">
      <AppIcon name="clock" size={18} class="text-slate-400" />
      Historique de carrière
    </CardTitle>
  </CardHeader>
  <CardContent class="pb-6">
    {#if events.length === 0}
      <div class="text-center py-12 border-2 border-dashed border-slate-100 rounded-lg">
        <AppIcon name="calendar" size={32} class="text-slate-200 mx-auto mb-3" />
        <p class="text-slate-400">Aucun événement enregistré</p>
      </div>
    {:else}
      <div class="relative ml-3 border-l border-slate-200 pl-8 space-y-8">
        {#each events as event (event.id)}
          {@const style = getEventStyle(event)}
          <div class="relative">
            <!-- Timeline dot/icon -->
            <div class={`absolute -left-[45px] top-0 h-8 w-8 rounded-full border flex items-center justify-center ${style.bgClass} ${style.borderClass}`}>
              <AppIcon name={style.icon} size={17} class={style.iconClass} />
            </div>

            <div class="space-y-1">
              <div class="flex items-center justify-between">
                <div class="text-[0.875rem] font-semibold uppercase tracking-wider text-slate-400">
                  {formatDate(event.date, false, false)}
                </div>
                <Badge variant="outline" class="font-normal text-[0.83rem] text-slate-500 border-slate-200 bg-white rounded-full">
                  {event.label}
                </Badge>
              </div>

              <div class="text-[0.85rem] font-medium text-slate-900">
                {event.status}
              </div>

              {#if event.metadata?.from && event.metadata?.to}
                <div class="flex items-center gap-2 mt-1 text-[0.875rem] text-slate-500">
                  <span class="line-through opacity-60 text-[0.875rem]">{event.metadata.from}</span>
                  <AppIcon name="arrow-right" size={17} class="text-slate-300" />
                  <span class="font-medium text-slate-700 text-[0.875rem]">{event.metadata.to}</span>
                </div>
              {:else if event.metadata?.seniority || event.metadata?.org_unit}
                <div class="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-[0.875rem] text-slate-500">
                  {#if event.metadata.seniority}
                    <div class="flex items-center gap-1">
                      <AppIcon name="trending-up" size={17} />
                      <span class="text-[0.875rem]">{event.metadata.seniority}</span>
                    </div>
                  {/if}
                  {#if event.metadata.org_unit}
                    <div class="flex items-center gap-1">
                      <AppIcon name={getOrgUnitIcon(event.metadata.org_unit_type ?? '')} size={17} />
                      <span class="text-[0.875rem]">{event.metadata.org_unit}</span>
                    </div>
                  {/if}
                </div>
              {/if}

              {#if event.description}
                <div class="text-[0.86rem] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100 mt-2">
                  {event.description}
                </div>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </CardContent>
</Card>

