<script lang="ts">
  import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import type { DashboardConfig } from "../core/dashboard";

  let { dashboard }: { dashboard: DashboardConfig & { visibleWidgets: any[] } } = $props();
</script>

<div class="space-y-6">
  <div>
    <h1 class="text-2xl font-bold text-slate-900">Tableau de bord {dashboard.role === 'admin' ? 'Direction' : dashboard.role === 'hr' ? 'RH' : 'Collaborateur'}</h1>
    <p class="text-sm text-slate-500">Bienvenue dans votre centre de gestion d'entreprise.</p>
  </div>

  <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
    {#each dashboard.visibleWidgets as widget (widget.id)}
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
</div>
