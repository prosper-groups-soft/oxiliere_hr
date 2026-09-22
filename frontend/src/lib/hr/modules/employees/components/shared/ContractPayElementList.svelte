<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Switch } from '@/components/ui/switch';
  import { notification } from '@/hr/stores/notification.svelte';
  import { cn } from '@/hr/utilities/common/css';
  import type { ContractPayElementItem } from '@/hr/modules/employees/types/types';
  import type { PayrollAdjustmentConfig } from '@/hr/modules/payroll/types/types';
  import type { ContractPayElementInput } from '@/hr/modules/payroll/types/types';
  import PayElementPickerModal from '@/hr/modules/employees/components/shared/PayElementPickerModal.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';


  let {
    contractId,
    elements,
    catalog,
    isLoading = false,
    onAdd,
    onToggle,
    onDelete,
    variant = 'card',
    showToggle = true,
    catalogLoading = false,
    catalogError = false,
  } = $props<{
    contractId?: string;
    elements: ContractPayElementItem[];
    catalog: PayrollAdjustmentConfig[];
    isLoading?: boolean;
    /** Chargement du catalogue backend en cours */
    catalogLoading?: boolean;
    /** Échec du chargement du catalogue backend */
    catalogError?: boolean;
    onAdd: (payload: ContractPayElementInput) => Promise<void>;
    onToggle?: (element: ContractPayElementItem, active: boolean) => Promise<void>;
    onDelete: (element: ContractPayElementItem, index: number) => Promise<void>;
    /** 'card' = carte autonome (profil), 'section' = section intégrée (onboarding) */
    variant?: 'card' | 'section';
    showToggle?: boolean;
  }>();

  let pickerOpen = $state(false);
  let togglingId = $state<string | null>(null);
  let deletingId = $state<string | null>(null);

  const existingCodes = $derived<Set<string>>(
    new Set(elements.map((e: any) => e.catalog_code ?? e.id))
  );

  const activeCount = $derived(elements.filter((e: ContractPayElementItem) => e.is_active).length);

  const formattedValue = (el: ContractPayElementItem) => {
    if (el.custom_amount != null) return `${Number(el.custom_amount).toLocaleString('fr-FR')} CDF`;
    if (el.custom_percentage != null) return `${Number(el.custom_percentage)} %`;
    if (el.amount != null) return `${Number(el.amount).toLocaleString('fr-FR')} CDF`;
    return '—';
  };

  /** Formate une date ISO (YYYY-MM-DD ou datetime) en JJ/MM/AAAA, sans dépendance. */
  const formatDate = (d?: string | null): string => {
    if (!d) return 'Pas de date';
    const raw = String(d).slice(0, 10);
    const date = new Date(raw + 'T00:00:00');
    if (Number.isNaN(date.getTime())) return raw;
    return new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(date);
  };

  async function handleToggle(el: ContractPayElementItem, active: boolean) {
    if (!onToggle) return;
    togglingId = el.id;
    try {
      await onToggle(el, active);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible de mettre à jour l'élément");
    } finally {
      togglingId = null;
    }
  }

  async function handleDelete(el: ContractPayElementItem, index: number) {
    if (!confirm(`Retirer « ${el.label} » de ce contrat ?`)) return;
    deletingId = el.id;
    try {
      await onDelete(el, index);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible de retirer l'élément");
    } finally {
      deletingId = null;
    }
  }
</script>


{#if variant === 'card'}
  <Card class="shadow-none py-4">
    <CardHeader class="flex flex-row items-center justify-between space-y-0">
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="list-plus" size={18} />
        Éléments de paie
      </CardTitle>
      <Button
        size="sm"
        variant="default"
        class="gap-1.5 h-7.5 text-[0.8rem]"
        onclick={() => (pickerOpen = true)}
        disabled={!contractId}
      >
        <AppIcon name="plus" size={15} />
        Ajouter
      </Button>
    </CardHeader>

    <CardContent class="space-y-3">
      <div class="flex items-center justify-between">
        <p class="text-[0.85rem] text-slate-400">
          Primes, indemnités et retenues actives sur ce contrat.
        </p>
        <Badge variant="secondary" class="text-[0.68rem]">
          {activeCount}/{elements.length} actifs
        </Badge>
      </div>

      {#if isLoading}
        <div class="flex items-center justify-center py-10 text-[0.82rem] text-slate-400">
          <AnimateSpin class="size-4" textPosition="right" text="Chargement des éléments…" />
        </div>
      {:else if elements.length === 0}
        <div class="py-8 text-center rounded-lg border border-dashed border-slate-200">
          <div class="text-slate-400 mx-auto w-fit mb-2">
            <AppIcon name="box" size={28} />
          </div>
          <p class="text-[0.82rem] text-slate-600">Aucun élément de paie assigné à ce contrat.</p>
          <button
            type="button"
            class="mt-2 text-[0.82rem] text-primary font-medium hover:underline cursor-pointer"
            onclick={() => (pickerOpen = true)}
            disabled={!contractId}
          >
            Ajouter un élément depuis le catalogue
          </button>
        </div>
      {:else}
        <div class="overflow-hidden rounded-lg border border-slate-100">
          <table class="w-full text-left">
            <thead class="bg-slate-50">
              <tr>
                <th class="px-3.5 py-2.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Libellé</th>
                <th class="px-3.5 py-2.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Montant / Taux</th>
                <th class="px-3.5 py-2.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Période</th>
                {#if showToggle}
                  <th class="px-3.5 py-2.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider text-center">Actif</th>
                {/if}
                <th class="px-3.5 py-2.5 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              {#each elements as el, i}
                <tr class="hover:bg-slate-50/50 transition-colors">
                  <td class="px-3.5 py-2.5">
                    <div class="flex items-center gap-2">
                      <span class="text-[0.9rem] font-medium text-slate-700">{el.label}</span>
                      {#if !el.is_taxable}
                        <span title="Non imposable" class="text-[0.82rem] font-medium text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">
                          <AppIcon name="shield-check" size={16} class="text-emerald-500" />
                        </span>
                      {/if}
                    </div>
                  </td>
                  <td class="px-3.5 py-2.5 text-[0.9rem] text-slate-600">{formattedValue(el)}</td>
                  <td class="px-3.5 py-2.5 text-[0.82rem] text-slate-500 whitespace-nowrap">
                    {formatDate(el.start_period)}
                    {#if el.end_period} → {formatDate(el.end_period)}{/if}
                  </td>
                  {#if showToggle}
                    <td class="px-3.5 py-2.5 text-center">
                      <Switch
                        checked={el.is_active}
                        onCheckedChange={(v) => handleToggle(el, v)}
                        disabled={togglingId === el.id}
                        class="cursor-pointer scale-90"
                        aria-label={`Activer ${el.label}`}
                      />
                    </td>
                  {/if}
                  <td class="px-3.5 py-2.5 text-right">
                    <button
                      type="button"
                      title="Retirer du contrat"
                      onclick={() => handleDelete(el, i)}
                      disabled={deletingId === el.id}
                      class={cn(
                        "text-red-400 hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40",
                      )}
                    >
                      <AppIcon name="trash-2" size={18} />
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </CardContent>
  </Card>
{:else}
  <!-- variant='section' : intégré dans un formulaire (onboarding) -->
  <div class="pt-5 border-t border-slate-100 space-y-3">
    <div class="flex items-center justify-between">
      <div>
        <h4 class="text-[0.92rem] font-bold text-slate-900">Éléments de paie</h4>
        <p class="text-[0.85rem] text-slate-500">
          Primes et indemnités récurrentes appliquées automatiquement au bulletin.
        </p>
      </div>
      <Button
        type="button"
        size="sm"
        variant="default"
        class="gap-1.5 h-7.5 text-[0.82rem] border-slate-200 cursor-pointer"
        onclick={() => (pickerOpen = true)}
        disabled={catalog.length === 0}
      >
        <AppIcon name="plus" size={17} />
        Ajouter
      </Button>
    </div>

    {#if elements.length === 0}
      <div class="py-6 text-center rounded-lg border border-dashed border-slate-200">
        <div class="text-slate-400 mx-auto w-fit mb-2">
          <AppIcon name="box" size={24} />
        </div>
        <p class="text-[0.82rem] text-slate-600">
          Aucun élément de paie sélectionné. Ajoutez-en depuis le catalogue.
        </p>
      </div>
    {:else}
      <div class="overflow-hidden rounded-lg border border-slate-100">
        <table class="w-full text-left">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3.5 py-2 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Libellé</th>
              <th class="px-3.5 py-2 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Montant / Taux</th>
              <th class="px-3.5 py-2 text-[0.7rem] font-bold text-slate-400 uppercase tracking-wider">Période</th>
              <th class="px-3.5 py-2 text-right"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            {#each elements as el, i}
              <tr class="hover:bg-slate-50/50 transition-colors">
                <td class="px-3.5 py-2">
                  <div class="flex items-center gap-2">
                    <span class="text-[0.9rem] font-medium text-slate-700">{el.label}</span>
                    {#if !el.is_taxable}
                      <span title="Non imposable">
                        <AppIcon name="shield-check" size={16} class="text-emerald-500" />
                      </span>
                    {/if}
                  </div>
                </td>
                <td class="px-3.5 py-2 text-[0.9rem] text-slate-600">
                  {formattedValue(el)}
                </td>
                <td class="px-3.5 py-2 text-sm text-slate-600 whitespace-nowrap">
                  {formatDate(el.start_period)}
                  {#if el.end_period} → {formatDate(el.end_period)}{/if}
                </td>
                <td class="px-3.5 py-2 text-right">
                  <button
                    type="button"
                    title="Retirer"
                    onclick={() => handleDelete(el, i)}
                    disabled={deletingId === el.id}
                    class="text-red-400 hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40"
                  >
                    <AppIcon name="trash-2" size={18} />
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
{/if}


<PayElementPickerModal
  open={pickerOpen}
  {catalog}
  {existingCodes}
  {catalogLoading}
  {catalogError}
  onOpenChange={(v) => (pickerOpen = v)}
  onConfirm={onAdd}
/>

