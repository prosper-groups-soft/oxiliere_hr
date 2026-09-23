<script lang="ts">
  import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import type { DashboardConfig } from "../core/dashboard";
  import ChartCanvas from "./ChartCanvas.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";

  let { dashboard, periodFilterState }: { dashboard: DashboardConfig & { visibleWidgets: any[] }; periodFilterState?: any } = $props();

  const periodFilterDefs = [{ key: 'period', label: 'Période', icon: 'calendar', mode: 'single' as const, options: [{ value: 'month', label: 'Mois en cours' }, { value: 'quarter', label: 'Trimestre' }, { value: 'year', label: 'Année' }] }];
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-slate-900">Tableau de bord {dashboard.role === 'admin' ? 'Direction' : dashboard.role === 'hr' ? 'RH' : 'Collaborateur'}</h1>
      <p class="text-sm text-slate-500">Bienvenue dans votre centre de gestion d'entreprise.</p>
    </div>
    <div class="flex items-center gap-2">
      {#if periodFilterState}<FilterMenu filterDefs={periodFilterDefs} filterState={periodFilterState} />{/if}
      <Button href={hr('/employees')} size="sm">Annuaire</Button>
      <Button href={hr('/recruitment')} variant="outline" size="sm">Recrutement</Button>
    </div>
  </div>

  <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
    {#each dashboard.visibleWidgets.filter((w: any) => w.kind !== 'chart') as widget (widget.id)}
      {@const res = useAsyncResource(widget.source, { mapData: widget.mapData })}
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">{res.data?.label ?? widget.metric}</CardTitle>
          <AppIcon name={res.data?.icon ?? widget.id} size={16} class={res.data?.color ?? 'text-slate-400'} />
        </CardHeader>
        <CardContent>
          {#if res.isLoading}
            <div class="h-7 w-16 bg-slate-100 animate-pulse rounded"></div>
          {:else if res.error}
            <p class="text-sm text-red-500">Erreur</p>
          {:else}
            <div class="text-2xl font-bold">{res.data?.value ?? '—'}</div>
            <p class="text-xs text-slate-500">{res.data?.sublabel ?? ''}</p>
          {/if}
        </CardContent>
      </Card>
    {/each}
  </div>

  <div class="grid gap-6 md:grid-cols-2">
    {#each dashboard.visibleWidgets.filter((w: any) => w.kind === 'chart') as widget (widget.id)}
      {@const res = useAsyncResource(widget.source, { mapData: widget.mapData })}
      {#if res.isLoading}
        <div class="h-48 bg-slate-50 animate-pulse rounded-xl border border-slate-200"></div>
      {:else if res.data}
        <div class="rounded-xl border border-slate-200 bg-white p-4">
          <h3 class="text-sm font-semibold text-slate-800 mb-3">{res.data.title}</h3>
          <ChartCanvas type={res.data.chartType ?? 'bar'} data={res.data.chartData} />
        </div>
      {/if}
    {/each}
  </div>

  <div class="grid gap-6 md:grid-cols-2">
    {#each dashboard.visibleWidgets.filter((w: any) => w.kind === 'list') as widget (widget.id)}
      {@const res = useAsyncResource(widget.source, { mapData: widget.mapData })}
      <div class="rounded-xl border border-slate-200 bg-white p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold text-slate-800">{res.data?.title ?? widget.metric}</h3>
          {#if res.data?.items?.length}<a href={res.data.items[0].href} class="text-xs text-primary hover:underline">Voir tout</a>{/if}
        </div>
        {#if res.isLoading}
          <div class="space-y-2"><div class="h-8 bg-slate-50 animate-pulse rounded"></div><div class="h-8 bg-slate-50 animate-pulse rounded"></div></div>
        {:else if !res.data || res.data.items.length === 0}
          <p class="text-sm text-slate-400">{res.data?.emptyText ?? 'Aucune donnée'}</p>
        {:else}
          <div class="space-y-2">
            {#each res.data.items as item}
              <a href={item.href} class="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-200 transition-colors">
                <div><p class="text-sm font-medium text-slate-800">{item.label}</p><p class="text-xs text-slate-500">{item.sublabel}</p></div>
                <AppIcon name="chevron-right" size={14} class="text-slate-400" />
              </a>
            {/each}
          </div>
        {/if}
      </div>
    {/each}
  </div>
</div>
