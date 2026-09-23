<script lang="ts">
  let { title, bars }: { title: string; bars: { label: string; value: number; width: number }[] } = $props();
</script>

<div class="rounded-xl border border-slate-200 bg-white p-4">
  <h3 class="text-sm font-semibold text-slate-800 mb-3">{title}</h3>
  {#if bars.length === 0}
    <p class="text-sm text-slate-400">Aucune donnée</p>
  {:else}
    <div class="space-y-2">
      {#each bars as bar}
        <div class="flex items-center gap-3">
          <span class="w-24 text-xs text-slate-600 truncate">{bar.label}</span>
          <div class="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div class="h-full bg-primary rounded-full transition-all" style="width: {bar.width}%"></div>
          </div>
          <span class="w-8 text-xs font-medium text-slate-700 text-right">{bar.value}</span>
        </div>
      {/each}
    </div>
  {/if}
</div>
