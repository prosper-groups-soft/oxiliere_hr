<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { taxSettingsStore } from "../../stores/taxSettingsStore.svelte";
  import { cn } from "@/utilities/common/css";
  import IPRCalculatorSheet from "./sheets/IPRCalculatorSheet.svelte";

  const config = $derived(taxSettingsStore.config);
  const isSaving = $derived(taxSettingsStore.isSaving);
  const hasChanges = $derived(taxSettingsStore.hasChanges);
  const calculatorResult = $derived(taxSettingsStore.calculatorResult);

  let showLegalBanner = $state(true);
  let showCalculatorSheet = $state(false);

  function handleSave() {
    taxSettingsStore.saveSettings();
  }

  function handleReset() {
    taxSettingsStore.resetToDefaults();
  }

  function formatCurrency(value: number): string {
    return `${value.toFixed(2)} ${config.currency}`;
  }
</script>


{#snippet Header()}
  <div class="flex items-center justify-between px-6 py-3 pr-8 border-b border-slate-100">
    <div class="flex items-center gap-3">
      <div>
        <h3 class="font-semibold text-slate-900 text-[0.96rem]">
          Configuration fiscale IPR & Social
        </h3>
        <p class="text-[0.8rem] text-slate-500">
          Barème progressif IPR selon la législation fiscale RDC
        </p>
      </div>
      {#if hasChanges}
        <span class="flex items-center gap-1.5 text-[0.8rem] text-amber-600 bg-amber-50 px-2.5 py-1 rounded-full">
          <AppIcon name="circle-alert" size={14} />
          Modifications non sauvegardées
        </span>
      {/if}
    </div>
    <div class="flex gap-2">
      {#if hasChanges}
        <Button variant="outline" onclick={handleReset} disabled={isSaving} class="h-7.5 shadow-fine">
          <AppIcon name="rotate-ccw" size={16} />
          Réinitialiser
        </Button>
        <Button onclick={handleSave} disabled={isSaving} class="bg-indigo-600 hover:bg-indigo-700 shadow-fine h-7.5">
          {#if isSaving}
            <AppIcon name="loader-2" size={17} class="animate-spin" />
          {:else}
            <AppIcon name="save" size={17} />
          {/if}
          Enregistrer
        </Button>
      {/if}
    </div>
  </div>
{/snippet}


{#snippet LegalInfoBanner()}
  {#if showLegalBanner}
    <div 
      class="bg-amber-50/80 border-b border-amber-100 px-6 pr-8 py-2.5 flex items-center justify-start gap-3"
    >
      <button
        aria-label="Fermer la bannière"
        onclick={() => showLegalBanner = false}
        class="shrink-0 p-1 text-amber-400 hover:text-amber-600 hover:bg-amber-100 rounded transition-all cursor-pointer"
      >
        <AppIcon name="x" size={17} />
      </button>
      <div class="flex items-center gap-3 flex-1 justify-start">
        <AppIcon name="scale" size={18} class="text-amber-500 shrink-0" />
        <span class="text-[0.82rem] text-amber-900 leading-relaxed">
          L'Impôt sur le Revenu des Personnes Physiques (IPR) est régi par l'Ordonnance n°69-102 du 10 février 1969.
          Le barème comporte 4 tranches : 3%, 15%, 30% et 40%. L'IPR ne peut excéder <span class="font-semibold text-[0.82rem]">30% du revenu net imposable</span>.
        </span>
      </div>
    </div>
  {/if}
{/snippet}


{#snippet IPRBracketsSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h5 class="font-medium text-slate-900 text-[0.94rem]">Barème IPR Progressif</h5>
        <p class="text-[0.84rem] text-slate-500">Tranches d'imposition (Impôt sur le Revenu des Personnes Physiques)</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-[0.84rem] text-slate-500">Devise:</span>
        <Select.Root type="single" bind:value={config.currency}>
          <Select.Trigger class="h-7! w-20 shadow-fine text-[0.84rem] cursor-pointer">
            {config.currency}
          </Select.Trigger>
          <Select.Content class="z-100 shadow-fine">
            <Select.Item value="USD" class="text-[0.84rem]">USD</Select.Item>
            <Select.Item value="CDF" class="text-[0.84rem]">CDF</Select.Item>
          </Select.Content>
        </Select.Root>
      </div>
    </div>

    <div class="overflow-hidden rounded-lg border border-slate-200">
      <table class="w-full text-[0.85rem]">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-3 py-2.5 text-left font-medium text-slate-700 text-[0.85rem]">Tranche</th>
            <th class="px-3 py-2.5 text-right font-medium text-slate-700 text-[0.85rem]">Revenu imposable</th>
            <th class="px-3 py-2.5 text-right font-medium text-slate-700 text-[0.85rem]">Taux</th>
            <th class="px-3 py-2.5 text-center font-medium text-slate-700 text-[0.85rem]">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#each config.iprBrackets as bracket, index (bracket.id)}
            {@const isEditing = taxSettingsStore.editingBracketId === bracket.id}
            <tr class="hover:bg-slate-50/50">
              <td class="px-3 py-2.5">
                {#if isEditing}
                  <Input
                    value={taxSettingsStore.bracketEditForm.label}
                    oninput={(e) => taxSettingsStore.bracketEditForm = { ...taxSettingsStore.bracketEditForm, label: e.currentTarget.value }}
                    class="h-7 text-[0.85rem] shadow-fine"
                  />
                {:else}
                  <span class="font-medium text-slate-900 text-[0.87rem]">{index + 1}</span>
                  <span class="text-slate-500 ml-2 text-[0.87rem]">{bracket.label}</span>
                {/if}
              </td>
              <td class="px-3 py-2.5 text-right">
                {#if isEditing}
                  <div class="flex items-center gap-1 justify-end">
                    <Input
                      type="number"
                      value={taxSettingsStore.bracketEditForm.min}
                      oninput={(e) => taxSettingsStore.bracketEditForm = { ...taxSettingsStore.bracketEditForm, min: parseFloat(e.currentTarget.value) || 0 }}
                      class="h-7 w-20 text-[0.85rem] text-right shadow-fine"
                    />
                    <span class="text-slate-400">-</span>
                    <Input
                      type="number"
                      value={taxSettingsStore.bracketEditForm.max ?? ''}
                      placeholder="∞"
                      oninput={(e) => taxSettingsStore.bracketEditForm = { ...taxSettingsStore.bracketEditForm, max: e.currentTarget.value ? parseFloat(e.currentTarget.value) : null }}
                      class="h-7 w-20 text-[0.85rem] text-right shadow-fine"
                    />
                  </div>
                {:else}
                  <span class="text-slate-700 text-[0.87rem]">
                    {bracket.min} - {bracket.max ?? '∞'} {config.currency}
                  </span>
                {/if}
              </td>
              <td class="px-3 py-2.5 text-right">
                {#if isEditing}
                  <div class="flex items-center gap-1 justify-end">
                    <Input
                      type="number"
                      value={(taxSettingsStore.bracketEditForm.rate || 0) * 100}
                      oninput={(e) => taxSettingsStore.bracketEditForm = { ...taxSettingsStore.bracketEditForm, rate: (parseFloat(e.currentTarget.value) || 0) / 100 }}
                      class="h-7 w-16 text-[0.85rem] text-right shadow-fine"
                      min={0}
                      max={100}
                      step={0.1}
                    />
                    <span class="text-slate-500 text-[0.84rem]">%</span>
                  </div>
                {:else}
                  <span class={cn(
                    "font-medium text-[0.87rem]",
                    bracket.rate <= 0.05 ? "text-green-600" :
                    bracket.rate <= 0.15 ? "text-yellow-600" :
                    bracket.rate <= 0.30 ? "text-orange-600" : "text-red-600"
                  )}>
                    {(bracket.rate * 100).toFixed(0)}%
                  </span>
                {/if}
              </td>
              <td class="px-3 py-2.5 flex justify-center">
                {#if isEditing}
                  <div class="flex items-center justify-end gap-1">
                    <button
                      onclick={() => taxSettingsStore.saveBracketEdit()}
                      class="w-7 h-7 rounded-md bg-green-100 text-green-600 flex items-center justify-center hover:bg-green-200 cursor-pointer"
                    >
                      <AppIcon name="check" size={16} />
                    </button>
                    <button
                      onclick={() => taxSettingsStore.cancelBracketEdit()}
                      class="w-7 h-7 rounded-md bg-slate-200 text-slate-600 flex items-center justify-center hover:bg-slate-300 cursor-pointer"
                    >
                      <AppIcon name="x" size={16} />
                    </button>
                  </div>
                {:else}
                  <button
                    onclick={() => taxSettingsStore.startEditingBracket(bracket.id)}
                    class="w-7 h-7 rounded-md hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors cursor-pointer"
                  >
                    <AppIcon name="edit" size={16} />
                  </button>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <p class="text-[0.85rem] text-slate-400 mt-2">
      * Le barème IPR est fixé par la législation fiscale de la RDC. Toute modification doit être conforme aux textes en vigueur.
    </p>
  </div>
{/snippet}


{#snippet FamilyDeductionsSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-start gap-4">
      <div class="w-12 h-12 rounded-xl bg-pink-50 flex items-center justify-center text-pink-600 shrink-0">
        <AppIcon name="users" size={24} />
      </div>
      <div class="flex-1">
        <div class="flex items-center justify-between mb-1">
          <h5 class="font-medium text-slate-900 text-[0.94rem]">Déductions pour charges de famille</h5>
          <button
            aria-label={config.familyDeduction.enabled ? "Désactiver déductions famille" : "Activer déductions famille"}
            class={cn("relative w-8 h-5 rounded-full transition-colors cursor-pointer", config.familyDeduction.enabled ? "bg-indigo-500" : "bg-slate-300")}
            onclick={() => taxSettingsStore.updateFamilyDeduction({ enabled: !config.familyDeduction.enabled })}
          >
            <span class={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform", config.familyDeduction.enabled ? "translate-x-3" : "translate-x-0")}></span>
          </button>
        </div>
        <p class="text-[0.84rem] text-slate-500 mb-4">
          Réduction d'impôt pour enfants à charge (max {config.familyDeduction.maxChildren} enfants)
        </p>
        {#if config.familyDeduction.enabled}
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Label class="text-[0.84rem] text-slate-500">Taux par enfant</Label>
              <div class="flex items-center gap-2 mt-1">
                <Input
                  type="number"
                  value={(config.familyDeduction.ratePerChild * 100).toFixed(0)}
                  oninput={(e) => taxSettingsStore.updateFamilyDeduction({ ratePerChild: (parseFloat(e.currentTarget.value) || 0) / 100 })}
                  class="w-20 text-right shadow-fine"
                  min={0}
                  max={10}
                  step={0.5}
                />
                <span class="text-[0.84rem] text-slate-500">%</span>
              </div>
            </div>
            <div>
              <Label class="text-[0.84rem] text-slate-500">Maximum d'enfants</Label>
              <Input
                type="number"
                value={config.familyDeduction.maxChildren}
                oninput={(e) => taxSettingsStore.updateFamilyDeduction({ maxChildren: parseInt(e.currentTarget.value) || 9 })}
                class="w-20 mt-1 shadow-fine"
                min={1}
                max={15}
              />
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/snippet}


{#snippet IPRCapSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-start gap-4">
      <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
        <AppIcon name="shield" size={24} />
      </div>
      <div class="flex-1">
        <h5 class="font-medium text-slate-900 text-[0.94rem] mb-1">Plafonnement IPR (30%)</h5>
        <p class="text-[0.84rem] text-slate-500 mb-4">
          L'IPR ne peut excéder 30% du revenu net imposable (conformément au Code fiscal RDC)
        </p>
        <div class="flex items-center gap-4">
          <div class="flex-1">
            <div class="h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-amber-500 rounded-full"
                style="width: {(config.iprConfig.globalCapRate * 100)}%"
              ></div>
            </div>
            <div class="flex justify-between mt-1">
              <span class="text-[0.84rem] text-slate-500">0%</span>
              <span class="text-[0.84rem] font-medium text-amber-700">
                {(config.iprConfig.globalCapRate * 100).toFixed(0)}% (plafond légal)
              </span>
              <span class="text-[0.84rem] text-slate-500">50%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
{/snippet}


{#snippet CNSSSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-start gap-4">
      <div class="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 shrink-0">
        <AppIcon name="office" size={24} />
      </div>
      <div class="flex-1">
        <div class="flex items-center justify-between mb-1">
          <h5 class="font-medium text-slate-900 text-[0.94rem]">Cotisations CNSS</h5>
          <button
            aria-label={config.cnss.enabled ? "Désactiver cotisations CNSS" : "Activer cotisations CNSS"}
            class={cn("relative w-8 h-5 rounded-full transition-colors cursor-pointer", config.cnss.enabled ? "bg-indigo-500" : "bg-slate-300")}
            onclick={() => taxSettingsStore.updateCNSS({ enabled: !config.cnss.enabled })}
          >
            <span class={cn("absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform", config.cnss.enabled ? "translate-x-3" : "translate-x-0")}></span>
          </button>
        </div>
        <p class="text-[0.84rem] text-slate-500 mb-4">
          Caisse Nationale de Sécurité Sociale - RDC
        </p>
        {#if config.cnss.enabled}
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-slate-50 rounded-lg">
              <div class="text-[0.84rem] text-slate-500 mb-1">Part patronale</div>
              <div class="flex items-center gap-2">
                <Input
                  type="number"
                  value={(config.cnss.employerRate * 100).toFixed(0)}
                  oninput={(e) => taxSettingsStore.updateCNSS({ employerRate: (parseFloat(e.currentTarget.value) || 0) / 100 })}
                  class="w-20 text-right h-8 shadow-fine"
                  min={0}
                  max={30}
                />
                <span class="text-[0.84rem] text-slate-500">%</span>
              </div>
              <div class="text-[0.84rem] text-slate-400 mt-1">Charge employeur</div>
            </div>
            <div class="p-3 bg-slate-50 rounded-lg">
              <div class="text-[0.84rem] text-slate-500 mb-1">Part ouvrière</div>
              <div class="flex items-center gap-2">
                <Input
                  type="number"
                  value={(config.cnss.employeeRate * 100).toFixed(0)}
                  oninput={(e) => taxSettingsStore.updateCNSS({ employeeRate: (parseFloat(e.currentTarget.value) || 0) / 100 })}
                  class="w-20 text-right h-8 shadow-fine"
                  min={0}
                  max={10}
                />
                <span class="text-[0.84rem] text-slate-500">%</span>
              </div>
              <div class="text-[0.84rem] text-slate-400 mt-1">Retenue sur salaire</div>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
{/snippet}


{#snippet CalculatorSection()}
  <div class="p-4 bg-slate-50 rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-white flex items-center justify-center text-slate-600">
          <AppIcon name="calculator" size={20} />
        </div>
        <div>
          <h5 class="font-medium text-slate-900 text-[0.94rem]">Simulateur IPR</h5>
          <p class="text-[0.84rem] text-slate-500">Estimez l'impôt sur un salaire</p>
        </div>
      </div>
      <Button
        onclick={() => showCalculatorSheet = true}
        variant="outline"
        class="h-8 shadow-fine"
      >
        <AppIcon name="calculator" size={16} />
        Ouvrir le simulateur
      </Button>
    </div>
  </div>
{/snippet}


<div class="pb-6">
  <div class="sticky top-0 z-10 bg-white">
    {@render Header()}
    {@render LegalInfoBanner()}
  </div>
  <div class="mt-6 space-y-6">
    {@render IPRBracketsSection()}
    {@render FamilyDeductionsSection()}
    {@render IPRCapSection()}
    {@render CNSSSection()}
    {@render CalculatorSection()}
  </div>
</div>


<!-- IPR Calculator Sheet -->
<IPRCalculatorSheet bind:open={showCalculatorSheet} />

