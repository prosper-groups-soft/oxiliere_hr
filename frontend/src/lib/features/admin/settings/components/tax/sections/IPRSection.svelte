<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";


  const config = $derived(taxSettingsStore.config);

  let showCalculatorSheet = $state(false);

  function calculateBracketAmount(min: number, max: number | null): string {
    const maxVal = max ?? Infinity;
    const minDisplay = taxSettingsStore.getDisplayValue(min);
    if (maxVal === Infinity) return `> ${minDisplay.toFixed(0)}`;
    const maxDisplay = taxSettingsStore.getDisplayValue(maxVal);
    return `${minDisplay.toFixed(0)} - ${maxDisplay.toFixed(0)}`;
  }

  // Calculate max rate from brackets
  const maxRate = $derived(
    config.iprBrackets.length > 0 
      ? Math.max(...config.iprBrackets.map(b => b.rate)) 
      : 0
  );
</script>


<div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
  <div class="flex items-start gap-4">
    <div class="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 shrink-0">
      <AppIcon name="receipt" size={24} />
    </div>
    <div class="flex-1">
      <div class="flex items-center justify-between mb-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Barème progressif IPR</h5>
        <button 
          onclick={() => showCalculatorSheet = true}
          class="text-[0.85rem] text-indigo-600 hover:text-indigo-700 font-medium items-center gap-1 hidden"
        >
          <AppIcon name="calculator" size={16} />
          Simuler
        </button>
      </div>
      <p class="text-[0.875rem] text-slate-500 mb-3">
        Tranches d'imposition progressives selon le barème fiscal RDC
      </p>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-200">
              <th class="text-left py-2 px-2 text-slate-600 font-medium text-[0.87rem] w-16">Tranche</th>
              <th class="text-right py-2 px-2 text-slate-600 font-medium text-[0.87rem] w-1/2">Revenu imposable</th>
              <th class="text-right py-2 px-2 text-slate-600 font-medium text-[0.87rem] w-20">Taux</th>
            </tr>
          </thead>
          <tbody>
            {#each config.iprBrackets as bracket, i}
              <tr class={cn(
                "border-b border-slate-100 last:border-0"
              )}>
                <td class="py-2 px-2 w-16">
                  <span class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-100 text-slate-600 text-[0.875rem] font-medium">
                    {i + 1}
                  </span>
                </td>
                <td class="py-2 px-2 text-right text-slate-700 text-[0.88rem] w-1/2">
                  {calculateBracketAmount(bracket.min, bracket.max)} {config.currency}
                </td>
                <td class="py-2 px-2 text-right w-20">
                  <span class="font-medium text-slate-800 text-[0.88rem]">{(bracket.rate * 100).toFixed(1)}%</span>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="mt-3 flex items-center justify-between text-[0.88rem]">
        <span class="text-slate-500 text-[0.88rem]">
          Taux max: <span class="font-medium text-slate-700 text-[0.88rem]">{(maxRate * 100).toFixed(1)}%</span>
        </span>
        <span class="text-slate-500 text-[0.88rem]">
          {config.iprBrackets.length} tranches
        </span>
      </div>
    </div>
  </div>
</div>

<!-- Calculator Sheet -->
{#if showCalculatorSheet}
  <div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
    <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-slate-900">Simulateur IPR</h3>
        <button onclick={() => showCalculatorSheet = false} class="text-slate-400 hover:text-slate-600">
          <AppIcon name="x" size={20} />
        </button>
      </div>
      <!-- Calculator content would go here -->
      <p class="text-slate-500 text-sm">Fonctionnalité de simulation à implémenter</p>
    </div>
  </div>
{/if}

