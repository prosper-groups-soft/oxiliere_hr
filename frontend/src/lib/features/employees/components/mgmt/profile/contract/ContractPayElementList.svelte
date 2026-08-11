<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
  } from '@/components/ui/card';
  import { Switch } from '@/components/ui/switch';
  import { notification } from '@/stores/notification.svelte';
  import { cn } from '@/utilities/common/css';
  import type { ContractPayElementItem } from '@/features/employees/types/types';
  import type { PayrollAdjustmentConfig } from '@/features/payroll/types/types';
  import type { ContractPayElementInput } from '@/features/payroll/types/types';
  import PayElementPickerModal from './PayElementPickerModal.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';


  let {
    contractId,
    elements,
    catalog,
    isLoading,
    onAdd,
    onToggle,
    onDelete,
  } = $props<{
    contractId: string;
    elements: ContractPayElementItem[];
    catalog: PayrollAdjustmentConfig[];
    isLoading: boolean;
    onAdd: (payload: ContractPayElementInput) => Promise<void>;
    onToggle: (element: ContractPayElementItem, active: boolean) => Promise<void>;
    onDelete: (element: ContractPayElementItem) => Promise<void>;
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

  async function handleToggle(el: ContractPayElementItem, active: boolean) {
    togglingId = el.id;
    try {
      await onToggle(el, active);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible de mettre à jour l'élément");
    } finally {
      togglingId = null;
    }
  }

  async function handleDelete(el: ContractPayElementItem) {
    if (!confirm(`Retirer « ${el.label} » de ce contrat ?`)) return;
    deletingId = el.id;
    try {
      await onDelete(el);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible de retirer l'élément");
    } finally {
      deletingId = null;
    }
  }
</script>


<Card class="shadow-none py-4">
  <CardHeader class="flex-row items-center justify-between space-y-0">
    <CardTitle class="flex items-center gap-2 text-[0.98rem]">
      <AppIcon name="list-plus" size={18} />
      Éléments de paie
    </CardTitle>
    <Button
      size="sm"
      variant="outline"
      class="gap-1.5 h-8 text-[0.78rem]"
      onclick={() => (pickerOpen = true)}
      disabled={!contractId || catalog.length === 0}
    >
      <AppIcon name="plus" size={14} />
      Ajouter
    </Button>
  </CardHeader>

  <CardContent class="space-y-3">
    <div class="flex items-center justify-between">
      <p class="text-[0.82rem] text-slate-400">
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
        <div class="text-slate-300 mx-auto w-fit mb-2">
          <AppIcon name="package" size={28} />
        </div>
        <p class="text-[0.82rem] text-slate-400">Aucun élément de paie assigné à ce contrat.</p>
        <button
          type="button"
          class="mt-2 text-[0.78rem] text-primary font-medium hover:underline cursor-pointer"
          onclick={() => (pickerOpen = true)}
          disabled={catalog.length === 0}
        >
          Ajouter un élément depuis le catalogue
        </button>
      </div>
    {:else}
      <div class="overflow-hidden rounded-lg border border-slate-100">
        <table class="w-full text-left">
          <thead class="bg-slate-50">
            <tr>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Code</th>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Libellé</th>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Montant / Taux</th>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Période</th>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-center">Actif</th>
              <th class="px-3.5 py-2.5 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50">
            {#each elements as el}
              <tr class="hover:bg-slate-50/50 transition-colors">
                <td class="px-3.5 py-2.5">
                  <span class="text-[0.72rem] font-mono font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                    {el.catalog_code ?? '—'}
                  </span>
                </td>
                <td class="px-3.5 py-2.5">
                  <div class="flex items-center gap-2">
                    <span class="text-[0.82rem] font-medium text-slate-700">{el.label}</span>
                    {#if el.is_taxable}
                      <span title="Imposable IRPP">
                        <AppIcon name="shield" size={13} class="text-amber-500" />
                      </span>
                    {/if}
                  </div>
                </td>
                <td class="px-3.5 py-2.5 text-[0.82rem] text-slate-600">{formattedValue(el)}</td>
                <td class="px-3.5 py-2.5 text-[0.72rem] text-slate-400 whitespace-nowrap">
                  {el.start_period ? el.start_period.slice(0, 10) : '—'}
                  {#if el.end_period} → {el.end_period.slice(0, 10)}{/if}
                </td>
                <td class="px-3.5 py-2.5 text-center">
                  <Switch
                    checked={el.is_active}
                    onCheckedChange={(v) => handleToggle(el, v)}
                    disabled={togglingId === el.id}
                    class="cursor-pointer scale-90"
                    aria-label={`Activer ${el.label}`}
                  />
                </td>
                <td class="px-3.5 py-2.5 text-right">
                  <button
                    type="button"
                    title="Retirer du contrat"
                    onclick={() => handleDelete(el)}
                    disabled={deletingId === el.id}
                    class={cn(
                      "text-slate-400 hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40",
                    )}
                  >
                    <AppIcon name="trash-2" size={14} />
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

<PayElementPickerModal
  open={pickerOpen}
  {catalog}
  {existingCodes}
  onOpenChange={(v) => (pickerOpen = v)}
  onConfirm={onAdd}
/>
