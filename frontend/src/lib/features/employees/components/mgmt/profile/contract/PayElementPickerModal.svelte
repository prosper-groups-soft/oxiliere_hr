<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Switch } from '@/components/ui/switch';
  import { notification } from '@/stores/notification.svelte';
  import { cn } from '@/utilities/common/css';
  import type { PayrollAdjustmentConfig } from '@/features/payroll/types/types';
  import type { ContractPayElementInput } from '@/features/payroll/types/types';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  

  let {
    open,
    catalog,
    existingCodes,
    onOpenChange,
    onConfirm,
  } = $props<{
    open: boolean;
    catalog: PayrollAdjustmentConfig[];
    existingCodes: Set<string>;
    onOpenChange: (open: boolean) => void;
    onConfirm: (payload: ContractPayElementInput) => Promise<void>;
  }>();

  let search = $state('');
  let selectedId = $state('');
  let customAmount = $state('');
  let customPercentage = $state('');
  let startPeriod = $state('');
  let endPeriod = $state('');
  let isActive = $state(true);
  let submitting = $state(false);
  let fieldErrors = $state<Record<string, string>>({});

  // Reset internal state each time the dialog opens
  $effect(() => {
    if (open) {
      search = '';
      selectedId = '';
      customAmount = '';
      customPercentage = '';
      startPeriod = '';
      endPeriod = '';
      isActive = true;
      fieldErrors = {};
    }
  });

  const available: PayrollAdjustmentConfig[] = $derived(
    catalog
      .filter((a: PayrollAdjustmentConfig) => !existingCodes.has(a.code ?? a.id))
      .filter((a: PayrollAdjustmentConfig) => {
        const q = search.trim().toLowerCase();
        if (!q) return true;
        return (
          (a.name ?? '').toLowerCase().includes(q) ||
          (a.code ?? '').toLowerCase().includes(q)
        );
      })
  );

  const selected = $derived(
    available.find((a: PayrollAdjustmentConfig) => a.id === selectedId) ?? null
  );

  const isFixed = $derived(selected?.calculation_mode === 'FIXED');
  const isPercentage = $derived(selected?.calculation_mode === 'PERCENTAGE');

  const formattedDefault = $derived(() => {
    if (!selected) return '';
    if (isFixed) return `Défaut : ${Number(selected.amount ?? 0).toLocaleString('fr-FR')} CDF`;
    if (isPercentage) return `Défaut : ${Number(selected.percentage ?? 0)} %`;
    return 'Défaut : —';
  });

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!selectedId) errors.adjustment = 'Sélectionnez un élément du catalogue';
    if (!startPeriod) errors.start_period = 'Date de début requise';

    if (isFixed && customAmount.trim() !== '' && Number.isNaN(Number(customAmount))) {
      errors.custom_amount = 'Montant invalide';
    }
    if (isPercentage && customPercentage.trim() !== '' && Number.isNaN(Number(customPercentage))) {
      errors.custom_percentage = 'Taux invalide';
    }
    if (endPeriod && startPeriod && endPeriod < startPeriod) {
      errors.end_period = 'La date de fin est antérieure au début';
    }
    fieldErrors = errors;
    return Object.keys(errors).length === 0;
  }

  async function handleConfirm() {
    if (!validate() || !selected) return;
    submitting = true;
    try {
      await onConfirm({
        adjustment: selected.id,
        custom_amount: isFixed && customAmount.trim() !== '' ? Number(customAmount) : null,
        custom_percentage: isPercentage && customPercentage.trim() !== '' ? Number(customPercentage) : null,
        start_period: startPeriod,
        end_period: endPeriod || null,
        is_active: isActive,
      });
      onOpenChange(false);
    } catch (e: any) {
      notification.toast.error(e?.message ?? "Impossible d'ajouter l'élément de paie");
    } finally {
      submitting = false;
    }
  }
</script>


<Dialog open={open} onOpenChange={onOpenChange}>
  <DialogContent class="max-w-lg">
    <DialogHeader>
      <DialogTitle class="flex items-center gap-2">
        <AppIcon name="list-plus" size={18} />
        Ajouter un élément de paie
      </DialogTitle>
      <DialogDescription>
        Sélectionnez un élément du catalogue, personnalisez le montant/taux si nécessaire.
      </DialogDescription>
    </DialogHeader>

    <div class="space-y-4">
      <!-- Recherche -->
      <div class="relative">
        <AppIcon
          name="search"
          size={15}
          class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
        <Input
          id="pay-element-search"
          placeholder="Rechercher par code ou libellé…"
          bind:value={search}
          class="pl-9 h-10 bg-white border-slate-200"
        />
      </div>

      <!-- Liste du catalogue -->
      <div class="max-h-56 overflow-y-auto rounded-lg border border-slate-100 divide-y divide-slate-50">
        {#if available.length === 0}
          <div class="py-8 text-center text-[0.82rem] text-slate-400">
            Aucun élément disponible — tous les éléments du catalogue sont déjà assignés.
          </div>
        {:else}
          {#each available as item}
            <button
              type="button"
              onclick={() => (selectedId = item.id)}
              class={cn(
                "w-full text-left px-3.5 py-2.5 flex items-center justify-between gap-3 transition-colors cursor-pointer",
                selectedId === item.id ? "bg-primary/5" : "hover:bg-slate-50"
              )}
            >
              <div class="flex items-center gap-3 min-w-0">
                <div class={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border",
                  selectedId === item.id
                    ? "bg-primary/10 text-primary border-primary/20"
                    : "bg-slate-50 text-slate-400 border-slate-100"
                )}>
                  <AppIcon name="award" size={15} />
                </div>
                <div class="min-w-0">
                  <div class="text-[0.86rem] font-medium text-slate-800 truncate">{item.name}</div>
                  <div class="text-[0.82rem] text-slate-400">{item.code ?? '—'}</div>
                </div>
              </div>
              {#if item.is_mandatory}
                <Badge variant="secondary" class="shrink-0 text-[0.82rem]">Légal</Badge>
              {/if}
            </button>
          {/each}
        {/if}
      </div>

      <!-- Configuration du montant -->
      {#if selected}
        <div class="rounded-lg border border-slate-100 bg-slate-50/50 p-3.5 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-[0.86rem] font-semibold text-slate-800">{selected.name}</div>
              <div class="text-[0.82rem] text-slate-400">{formattedDefault()}</div>
            </div>
            {#if selected.is_taxable}
              <Badge variant="outline" class="text-[0.82rem]">Imposable</Badge>
            {/if}
          </div>

          <div class="grid grid-cols-2 gap-3">
            {#if isFixed}
              <div class="space-y-1">
                <Label for="pe-custom-amount" class="text-[0.82rem] text-slate-500">Montant (CDF)</Label>
                <Input
                  id="pe-custom-amount"
                  type="number"
                  min="0"
                  placeholder="Laisser vide = défaut"
                  bind:value={customAmount}
                  class="h-9 bg-white border-slate-200"
                />
                {#if fieldErrors.custom_amount}
                  <p class="text-[0.82rem] text-red-500">{fieldErrors.custom_amount}</p>
                {/if}
              </div>
            {:else if isPercentage}
              <div class="space-y-1">
                <Label for="pe-custom-percentage" class="text-[0.82rem] text-slate-500">Taux (%)</Label>
                <Input
                  id="pe-custom-percentage"
                  type="number"
                  min="0"
                  max="100"
                  placeholder="Laisser vide = défaut"
                  bind:value={customPercentage}
                  class="h-9 bg-white border-slate-200"
                />
                {#if fieldErrors.custom_percentage}
                  <p class="text-[0.82rem] text-red-500">{fieldErrors.custom_percentage}</p>
                {/if}
              </div>
            {/if}

            <div class="space-y-1">
              <Label for="pe-start" class="text-[0.82rem] text-slate-500">Début d'application *</Label>
              <Input
                id="pe-start"
                type="date"
                bind:value={startPeriod}
                class="h-9 bg-white border-slate-200"
              />
              {#if fieldErrors.start_period}
                <p class="text-[0.82rem] text-red-500">{fieldErrors.start_period}</p>
              {/if}
            </div>

            <div class="space-y-1">
              <Label for="pe-end" class="text-[0.82rem] text-slate-500">Fin (optionnel)</Label>
              <Input
                id="pe-end"
                type="date"
                bind:value={endPeriod}
                class="h-9 bg-white border-slate-200"
              />
              {#if fieldErrors.end_period}
                <p class="text-[0.82rem] text-red-500">{fieldErrors.end_period}</p>
              {/if}
            </div>
          </div>

          <div class="flex items-center justify-between pt-1">
            <Label for="pe-active" class="text-[0.82rem] text-slate-600">Activer dès l'ajout</Label>
            <Switch id="pe-active" bind:checked={isActive} />
          </div>
        </div>
      {/if}
    </div>

    <DialogFooter>
      <Button variant="outline" onclick={() => onOpenChange(false)} disabled={submitting}>
        <AppIcon name="x" class="text-slate-400" />
        Annuler
      </Button>
      <Button onclick={handleConfirm} disabled={!selected || submitting}>
        {#if submitting}
          <AnimateSpin class="border-white size-3" />
        {:else}
          <AppIcon name="check" class="text-white" />
        {/if}
        Ajouter
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

