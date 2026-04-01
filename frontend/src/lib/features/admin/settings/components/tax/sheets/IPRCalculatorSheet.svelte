<script lang="ts">
  import { Button } from "@/components/ui/button";
  import * as Sheet from "@/components/ui/sheet";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../../stores/taxSettingsStore.svelte";

  interface Props {
    open: boolean;
  }

  let { open = $bindable(false) }: Props = $props();

  // Form state
  let salary = $state(100000);
  let children = $state(0);

  // Calculator result
  const result = $derived.by(() => {
    if (salary <= 0) return null;
    return taxSettingsStore.calculateIPR(salary, children);
  });

  const config = $derived(taxSettingsStore.config);

  function formatCurrency(value: number): string {
    return `${value.toFixed(2)} ${config.currency}`;
  }

  function handleReset() {
    salary = 100000;
    children = 0;
  }

  function handleClose() {
    open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem] flex items-center gap-2">
        Simulateur IPR
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 pb-6 space-y-5 custom-scrollbar">
      <p class="text-[0.85rem] text-slate-500">
        Calculez l'Impôt sur le Revenu des Personnes Physiques (IPR) selon la législation fiscale RDC.
      </p>

      <!-- Salary Input -->
      <div class="space-y-1.5">
        <Label for="salary">Salaire brut mensuel</Label>
        <div class="flex items-center gap-2">
          <Input
            id="salary"
            type="number"
            bind:value={salary}
            min={0}
            step={1000}
            class="h-10 bg-white shadow-fine text-right"
          />
          <span class="text-[0.85rem] text-slate-500 font-medium min-w-12">{config.currency}</span>
        </div>
      </div>

      <!-- Children Input -->
      <div class="space-y-1.5">
        <Label for="children">Nombre d'enfants à charge</Label>
        <Input
          id="children"
          type="number"
          bind:value={children}
          min={0}
          max={15}
          class="h-10 bg-white shadow-fine"
        />
        <p class="text-[0.8rem] text-slate-400">
          Maximum {config.familyDeduction.maxChildren} enfants pris en compte pour la déduction
        </p>
      </div>

      <!-- Quick Amount Buttons -->
      <div class="flex flex-wrap gap-2">
        {#each [50000, 100000, 200000, 500000, 1000000] as amount}
          <button
            onclick={() => salary = amount}
            class="px-3 py-1.5 text-[0.84rem] bg-slate-100 hover:bg-slate-200 rounded-md transition-colors text-slate-600"
          >
            {amount.toLocaleString()}
          </button>
        {/each}
      </div>

      <!-- Results -->
      {#if result}
        <div class="space-y-3">
          <div class="p-4 bg-white rounded-lg border border-slate-200 shadow-fine space-y-3">
            <h4 class="font-medium text-slate-900 text-[0.9rem] mb-3">Détail du calcul</h4>

            <div class="flex justify-between">
              <span class="text-slate-500 text-[0.85rem]">Salaire brut:</span>
              <span class="font-medium text-[0.85rem]">{formatCurrency(result.grossSalary)}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500 text-[0.85rem]">Abattement professionnel (20%):</span>
              <span class="text-slate-600 text-[0.85rem]">-{formatCurrency(result.professionalAllowance)}</span>
            </div>
            <div class="h-px bg-slate-100"></div>
            <div class="flex justify-between">
              <span class="text-slate-500 text-[0.85rem]">Base imposable:</span>
              <span class="font-medium text-[0.85rem]">{formatCurrency(result.taxableBase)}</span>
            </div>
          </div>

          <div class="p-4 bg-white rounded-lg border border-slate-200 shadow-fine space-y-3">
            <h4 class="font-medium text-slate-900 text-[0.9rem] mb-3">Calcul de l'IPR</h4>

            <div class="flex justify-between">
              <span class="text-slate-500 text-[0.85rem]">IPR brut:</span>
              <span class="text-[0.85rem]">{formatCurrency(result.totalTaxBeforeDeductions)}</span>
            </div>
            {#if result.familyDeduction > 0}
              <div class="flex justify-between">
                <span class="text-slate-500 text-[0.85rem]">Déduction enfants ({children} enfant{children > 1 ? 's' : ''}):</span>
                <span class="text-green-600 text-[0.85rem]">-{formatCurrency(result.familyDeduction)}</span>
              </div>
            {/if}
            {#if result.globalCapApplied}
              <div class="flex items-center gap-2 text-[0.8rem] text-amber-600 bg-amber-50 p-2 rounded">
                <AppIcon name="alert-triangle" size={14} />
                <span>Plafond 30% appliqué (limite légale atteinte)</span>
              </div>
            {/if}
          </div>

          <div class="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
            <div class="flex items-center justify-between">
              <span class="font-semibold text-indigo-900 text-[0.875rem]">IPR final:</span>
              <span class="text-[0.9rem] font-bold text-indigo-600">{formatCurrency(result.finalTax)}</span>
            </div>
            <div class="flex justify-between mt-2 pt-2 border-t border-indigo-200">
              <span class="text-[0.85rem] text-indigo-700">Taux effectif:</span>
              <span class="font-medium text-[0.85rem] text-indigo-700">{(result.effectiveRate * 100).toFixed(2)}%</span>
            </div>
          </div>

          <!-- Bracket breakdown -->
          {#if result.brackets && result.brackets.length > 0}
            <div class="p-4 bg-white rounded-lg border border-slate-200 shadow-fine">
              <h4 class="font-medium text-slate-900 text-[0.9rem] mb-3">Détail par tranche</h4>
              <div class="space-y-2">
                {#each result.brackets as { bracket, taxInBracket }, index}
                  {@const colors = ['bg-emerald-500', 'bg-blue-500', 'bg-amber-500', 'bg-rose-500']}
                  <div class="flex justify-between items-center">
                    <div class="flex items-center gap-2">
                      <span class="w-2 h-2 rounded-full {colors[index % colors.length]}"></span>
                      <span class="text-slate-600 text-[0.85rem]">{bracket.label}</span>
                    </div>
                    <span class="font-medium text-[0.85rem]">{formatCurrency(taxInBracket)}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Button
        onclick={handleReset}
        variant="outline"
        class="flex-1 h-10 shadow-fine"
      >
        <AppIcon name="rotate-ccw" size={16} />
        Réinitialiser
      </Button>
      <Sheet.Close class="flex-1">
        <Button class="w-full h-10 bg-indigo-600 hover:bg-indigo-700 shadow-fine">
          <AppIcon name="x" size={16} />
          Fermer
        </Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
</style>

