<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import { currencySettingsStore } from "../../stores/currencySettingsStore.svelte";
  import type { CurrencyCode } from "../../types/currency.types";
  import { CURRENCIES } from "../../types/currency.types";
  import { cn } from "@/utilities/common/css";

  const config = $derived(currencySettingsStore.config);
  const currentRate = $derived(currencySettingsStore.currentRate);
  const isSaving = $derived(currencySettingsStore.isSaving);
  const hasChanges = $derived(currencySettingsStore.hasChanges);
  const history = $derived(currencySettingsStore.paginatedHistory);
  const showAddForm = $derived(currencySettingsStore.showAddRateForm);

  let showLegalBanner = $state(true);

  function handleSave() {
    currencySettingsStore.saveSettings();
  }

  function handleReset() {
    currencySettingsStore.resetToDefaults();
  }

  function handleAddRate() {
    if (currencySettingsStore.newRate.rate > 0) {
      currencySettingsStore.addExchangeRate({
        from: currencySettingsStore.newRate.from,
        to: currencySettingsStore.newRate.to,
        rate: currencySettingsStore.newRate.rate,
        source: 'MANUAL',
        notes: currencySettingsStore.newRate.notes
      });
    }
  }

  function formatDate(date: Date): string {
    return date.toLocaleDateString('fr-CD', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  function formatRate(rate: number): string {
    return rate.toLocaleString('fr-CD', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    });
  }
</script>


{#snippet Header()}
  <div class="flex items-center justify-between px-6 py-3 pr-8 border-b border-slate-100">
    <div class="flex items-center gap-3">
      <div>
        <h3 class="font-semibold text-slate-900 text-[0.96rem]">
          Paramètres régionaux et devises
        </h3>
        <p class="text-[0.8rem] text-slate-500">
          Configuration multi-devises CDF/USD pour la RDC
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
      class="bg-green-50/80 border-b border-green-100 px-6 pr-8 py-2.5 flex items-center justify-start gap-3"
    >
      <button
        aria-label="Fermer la bannière"
        onclick={() => showLegalBanner = false}
        class="shrink-0 p-1 text-green-400 hover:text-green-600 hover:bg-green-100 rounded transition-all cursor-pointer"
      >
        <AppIcon name="x" size={17} />
      </button>
      <div class="flex items-center gap-3 flex-1 justify-start">
        <AppIcon name="info" size={18} class="text-green-500 shrink-0" />
        <span class="text-[0.82rem] text-green-900 leading-relaxed">
          Le Franc Congolais (CDF) est la devise officielle de la RDC. Le Dollar américain (USD) est largement utilisé comme devise de référence.
        </span>
      </div>
    </div>
  {/if}
{/snippet}


{#snippet CurrencySection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <h5 class="font-medium text-slate-900 text-[0.94rem] mb-4">Configuration des devises</h5>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Primary Currency -->
      <div class="p-4 bg-slate-50 rounded-lg">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-lg bg-white flex items-center justify-center text-2xl shadow-sm">
            {config.currency.primaryCurrency.flag}
          </div>
          <div>
            <div class="font-medium text-slate-900 text-[0.9rem]">Devise principale</div>
            <div class="text-[0.75rem] text-slate-500">Pour les paiements internes</div>
          </div>
        </div>
        <Select.Root type="single" value={config.currency.primaryCurrency.code} onValueChange={(v) => currencySettingsStore.setPrimaryCurrency(v as 'CDF' | 'USD')}>
          <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
            <span class="text-[0.85rem]">{config.currency.primaryCurrency.code}</span>
          </Select.Trigger>
          <Select.Content>
            {#each CURRENCIES as currency}
              <Select.Item value={currency.code} class="cursor-pointer">
                <span class="text-[0.85rem]">{currency.flag} {currency.code} - {currency.name}</span>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <!-- Secondary Currency -->
      <div class="p-4 bg-slate-50 rounded-lg">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-10 h-10 rounded-lg bg-white flex items-center justify-center text-2xl shadow-sm">
            {config.currency.secondaryCurrency?.flag || '💱'}
          </div>
          <div>
            <div class="font-medium text-slate-900 text-[0.9rem]">Devise secondaire</div>
            <div class="text-[0.75rem] text-slate-500">Référence pour conversions</div>
          </div>
        </div>
        <Select.Root type="single" value={config.currency.secondaryCurrency?.code || ''} onValueChange={(v) => currencySettingsStore.setSecondaryCurrency(v as CurrencyCode | null)}>
          <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
            <span class="text-[0.85rem]">{config.currency.secondaryCurrency?.code || 'Aucune'}</span>
          </Select.Trigger>
          <Select.Content>
            <Select.Item value="" class="cursor-pointer">Aucune</Select.Item>
            {#each CURRENCIES.filter(c => c.code !== config.currency.primaryCurrency.code) as currency}
              <Select.Item value={currency.code} class="cursor-pointer">
                <span class="text-[0.85rem]">{currency.flag} {currency.code} - {currency.name}</span>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>
    </div>

    <!-- Display Options -->
    <div class="mt-4 flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
      <input
        type="checkbox"
        id="displayBoth"
        checked={config.currency.displayBoth}
        onchange={() => currencySettingsStore.toggleDisplayBoth()}
        class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
      />
      <label for="displayBoth" class="flex-1 cursor-pointer">
        <div class="font-medium text-slate-900 text-[0.9rem]">Afficher les deux devises</div>
        <div class="text-[0.75rem] text-slate-500">
          Montrer CDF et USD côte à côte dans les fiches de paie
        </div>
      </label>
    </div>
  </div>
{/snippet}


{#snippet ExchangeRateSection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center text-green-600">
          <AppIcon name="banknote" size={24} />
        </div>
        <div>
          <h5 class="font-medium text-slate-900 text-[0.94rem]">Taux de change actuel</h5>
          <p class="text-[0.84rem] text-slate-500">
            {#if currentRate}
              Mis à jour le {formatDate(currentRate.date)}
            {:else}
              Aucun taux actif
            {/if}
          </p>
        </div>
      </div>
      <Button
        variant="outline"
        onclick={() => currencySettingsStore.toggleAddRateForm()}
        class="h-8 shadow-fine"
      >
        <AppIcon name="plus" size={16} />
        Nouveau taux
      </Button>
    </div>

    {#if currentRate}
      <div class="flex items-center justify-center gap-6 py-6 bg-slate-50 rounded-lg">
        <div class="text-center">
          <div class="text-[1rem] font-bold text-slate-900">1</div>
          <div class="text-[0.85rem] text-slate-500">{currentRate.from}</div>
        </div>
        <div class="text-slate-400">
          <AppIcon name="arrow-right" size={24} />
        </div>
        <div class="text-center">
          <div class="text-[1rem] font-bold text-green-600">
            {formatRate(currentRate.rate)}
          </div>
          <div class="text-[0.85rem] text-slate-500">{currentRate.to}</div>
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center py-8 text-slate-400">
        <AppIcon name="alert-circle" size={24} />
        <span class="ml-2">Aucun taux de change configuré</span>
      </div>
    {/if}

    <!-- Add Rate Form -->
    {#if showAddForm}
      <div class="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <h5 class="font-medium text-slate-900 text-[0.9rem] mb-3">Ajouter un nouveau taux</h5>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
          <div>
            <Label class="text-[0.75rem] text-slate-500">De</Label>
            <select
              value={currencySettingsStore.newRate.from}
              onchange={(e) => currencySettingsStore.setNewRateField('from', e.currentTarget.value as 'CDF' | 'USD')}
              class="w-full h-9 px-2 rounded-md border border-slate-200 bg-white text-sm mt-1"
            >
              {#each CURRENCIES as currency}
                <option value={currency.code}>{currency.code}</option>
              {/each}
            </select>
          </div>
          <div>
            <Label class="text-[0.75rem] text-slate-500">Vers</Label>
            <select
              value={currencySettingsStore.newRate.to}
              onchange={(e) => currencySettingsStore.setNewRateField('to', e.currentTarget.value as 'CDF' | 'USD')}
              class="w-full h-9 px-2 rounded-md border border-slate-200 bg-white text-sm mt-1"
            >
              {#each CURRENCIES as currency}
                <option value={currency.code}>{currency.code}</option>
              {/each}
            </select>
          </div>
          <div>
            <Label class="text-[0.75rem] text-slate-500">Taux</Label>
            <Input
              type="number"
              step="0.01"
              value={currencySettingsStore.newRate.rate}
              oninput={(e) => currencySettingsStore.setNewRateField('rate', parseFloat(e.currentTarget.value) || 0)}
              class="mt-1 shadow-fine"
              placeholder="2800"
            />
          </div>
        </div>
        <div class="mb-3">
          <Label class="text-[0.75rem] text-slate-500">Notes (optionnel)</Label>
          <Input
            value={currencySettingsStore.newRate.notes}
            oninput={(e) => currencySettingsStore.setNewRateField('notes', e.currentTarget.value)}
            class="mt-1 shadow-fine"
            placeholder="Taux BCC du jour..."
          />
        </div>
        <div class="flex justify-end gap-2">
          <Button variant="outline" size="sm" onclick={() => currencySettingsStore.toggleAddRateForm()}>
            Annuler
          </Button>
          <Button size="sm" onclick={handleAddRate} class="bg-green-600 hover:bg-green-700">
            <AppIcon name="check" size={14} />
            Valider
          </Button>
        </div>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet HistorySection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <h5 class="font-medium text-slate-900 text-[0.94rem] mb-4">Historique des taux</h5>
    {#if history.length > 0}
      <div class="overflow-hidden rounded-lg border border-slate-200">
        <table class="w-full text-[0.85rem]">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3 py-2.5 text-left font-medium text-slate-700 text-[0.85rem]">
                Date
              </th>
              <th class="px-3 py-2.5 text-center font-medium text-slate-700 text-[0.85rem]">
                Paire
              </th>
              <th class="px-3 py-2.5 text-right font-medium text-slate-700 text-[0.85rem]">
                Taux
              </th>
              <th class="px-3 py-2.5 text-center font-medium text-slate-700 text-[0.85rem]">
                Source
              </th>
              <th class="px-3 py-2.5 text-center font-medium text-slate-700 text-[0.85rem]">
                Statut
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            {#each history as rate (rate.id)}
              <tr class="hover:bg-slate-50/50">
                <td class="px-3 py-2.5 text-slate-700 text-[0.83rem]">
                  {formatDate(rate.date)}
                </td>
                <td class="px-3 py-2.5 text-center">
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 rounded text-[0.83rem]">
                    {rate.from} → {rate.to}
                  </span>
                </td>
                <td class="px-3 py-2.5 text-right font-medium text-[0.83rem]">
                  {formatRate(rate.rate)}
                </td>
                <td class="px-3 py-2.5 text-center">
                  <span class={cn(
                    "px-2 py-0.5 rounded-full text-[0.83rem]",
                    rate.source === 'MANUAL' ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"
                  )}>
                    {rate.source === 'MANUAL' ? 'Manuel' : 'API'}
                  </span>
                </td>
                <td class="px-3 py-2.5 text-center">
                  {#if rate.isActive}
                    <span class="inline-flex items-center gap-1 text-[0.83rem] text-green-600">
                      <AppIcon name="check-circle" size={12} />
                      Actif
                    </span>
                  {:else}
                    <span class="inline-flex items-center gap-1 text-[0.83rem] text-slate-400">
                      <AppIcon name="archive" size={12} />
                      Archivé
                    </span>
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="mt-3">
        <DataPagination
          currentCount={history.length}
          totalCount={currencySettingsStore.filteredHistory.length}
          currentPage={currencySettingsStore.historyPage}
          totalPages={currencySettingsStore.historyTotalPages}
          perPage={currencySettingsStore.historyPerPage}
          onPageChange={(p) => currencySettingsStore.setHistoryPage(p)}
          onPerPageChange={(s) => currencySettingsStore.setHistoryPerPage(s)}
          onNext={() => currencySettingsStore.setHistoryPage(currencySettingsStore.historyPage + 1)}
          onPrev={() => currencySettingsStore.setHistoryPage(currencySettingsStore.historyPage - 1)}
          unitLabel="taux"
        />
      </div>
    {:else}
      <div class="flex items-center justify-center py-8 text-slate-400">
        <AppIcon name="inbox" size={24} />
        <span class="ml-2">Aucun historique disponible</span>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet CompanySection()}
  <div class="p-4 bg-white rounded-xl border border-slate-200 mx-6 mr-8">
    <h5 class="font-medium text-slate-900 text-[0.94rem] mb-4">Informations de l'entreprise</h5>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <Label class="text-[0.83rem]">Nom de l'entreprise</Label>
        <Input
          value={config.companyInfo.name}
          oninput={(e) => currencySettingsStore.updateCompanyInfo({ name: e.currentTarget.value })}
          class="mt-1 shadow-fine"
          placeholder="Oxilière SARL"
        />
      </div>
      <div>
        <Label class="text-[0.83rem]">ID National (ID.NAT)</Label>
        <Input
          value={config.companyInfo.idNat}
          oninput={(e) => currencySettingsStore.updateCompanyInfo({ idNat: e.currentTarget.value })}
          class="mt-1 shadow-fine"
          placeholder="ID National"
        />
      </div>
      <div>
        <Label class="text-[0.83rem]">RCCM</Label>
        <Input
          value={config.companyInfo.rccm}
          oninput={(e) => currencySettingsStore.updateCompanyInfo({ rccm: e.currentTarget.value })}
          class="mt-1 shadow-fine"
          placeholder="CD/..."
        />
      </div>
      <div>
        <Label class="text-[0.83rem]">Numéro d'impôt</Label>
        <Input
          value={config.companyInfo.taxNumber}
          oninput={(e) => currencySettingsStore.updateCompanyInfo({ taxNumber: e.currentTarget.value })}
          class="mt-1 shadow-fine"
          placeholder="Numéro d'impôt"
        />
      </div>
      <div class="md:col-span-2">
        <Label class="text-[0.83rem]">Adresse</Label>
        <Input
          value={config.companyInfo.address}
          oninput={(e) => currencySettingsStore.updateCompanyInfo({ address: e.currentTarget.value })}
          class="mt-1 shadow-fine"
          placeholder="123 Avenue..."
        />
      </div>
    </div>
  </div>
{/snippet}


<div class="pb-6">
  <div class="sticky top-0 z-10 bg-white">
    {@render Header()}
    {@render LegalInfoBanner()}
  </div>
  <div class="mt-6 space-y-6">
    {@render CurrencySection()}
    {@render ExchangeRateSection()}
    {@render HistorySection()}
    {@render CompanySection()}
  </div>
</div>

