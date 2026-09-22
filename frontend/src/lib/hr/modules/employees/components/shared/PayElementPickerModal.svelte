<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Switch } from '@/components/ui/switch';
  import { notification } from '@/hr/stores/notification.svelte';
  import { cn } from '@/hr/utilities/common/css';
  import type { PayrollAdjustmentConfig } from '@/hr/modules/payroll/types/types';
  import type { ContractPayElementInput } from '@/hr/modules/payroll/types/types';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';


  /** Couleurs des badges par type d'ajustement */
  const TYPE_STYLES: Record<string, { label: string; class: string }> = {
    BONUS: { label: 'Bonus', class: 'bg-emerald-50 text-emerald-700 border-emerald-100' },
    CONTRIBUTION: { label: 'Retenue', class: 'bg-rose-50 text-rose-700 border-rose-100' },
  };

  const getTypeStyle = (type: string) =>
    TYPE_STYLES[type] ?? { label: type, class: 'bg-slate-50 text-slate-600 border-slate-100' };

  /** Couleurs par mode de calcul */
  const MODE_STYLES: Record<string, string> = {
    FIXED: 'bg-slate-100 text-slate-600',
    PERCENTAGE: 'bg-indigo-50 text-indigo-600',
  };

  let {
    open,
    catalog,
    existingCodes,
    catalogLoading = false,
    catalogError = false,
    onOpenChange,
    onConfirm,
  } = $props<{
    open: boolean;
    catalog: PayrollAdjustmentConfig[];
    existingCodes: Set<string>;
    /** Chargement du catalogue backend en cours */
    catalogLoading?: boolean;
    /** Échec du chargement du catalogue backend */
    catalogError?: boolean;
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

  /** Placeholder de l'input : montre la valeur par défaut si elle est définie. */
  const defaultValuePlaceholder = $derived.by(() => {
    if (isFixed) {
      const amount = selected?.amount;
      return amount != null ? `Vide = ${Number(amount).toLocaleString('fr-FR')} CDF` : 'Aucune valeur par défaut';
    }
    if (isPercentage) {
      const pct = selected?.percentage;
      return pct != null ? `Vide = ${Number(pct)} %` : 'Aucune valeur par défaut';
    }
    return 'Laisser vide = défaut';
  });

  /** Valeur par défaut d'un item de la liste (avant sélection) */
  function formatItemDefault(item: PayrollAdjustmentConfig): string {
    if (item.calculation_mode === 'FIXED' && item.amount != null) {
      return `${Number(item.amount).toLocaleString('fr-FR')} CDF`;
    }
    if (item.calculation_mode === 'PERCENTAGE' && item.percentage != null) {
      return `${Number(item.percentage)} %`;
    }
    return '';
  }

  /** Libellé court du mode de calcul */
  function formatModeLabel(mode: string): string {
    if (mode === 'FIXED') return 'Montant';
    if (mode === 'PERCENTAGE') return 'Taux';
    return 'Défaut';
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!selectedId) errors.adjustment = 'Sélectionnez un élément du catalogue';
    if (!startPeriod) errors.start_period = 'Date de début requise';

    if (isFixed && String(customAmount ?? '').trim() !== '' && Number.isNaN(Number(customAmount))) {
      errors.custom_amount = 'Montant invalide';
    }
    if (isPercentage && String(customPercentage ?? '').trim() !== '' && Number.isNaN(Number(customPercentage))) {
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
        custom_amount: isFixed && String(customAmount ?? '').trim() !== '' ? Number(customAmount) : null,
        custom_percentage: isPercentage && String(customPercentage ?? '').trim() !== '' ? Number(customPercentage) : null,
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
  <DialogContent class="w-full max-w-[calc(100%-2rem)] sm:max-w-3xl">
    <DialogHeader>
      <DialogTitle class="flex items-center gap-2">
        <AppIcon name="list-plus" size={18} />
        Ajouter un élément de paie
      </DialogTitle>
      <DialogDescription>
        Sélectionnez un élément du catalogue, personnalisez le montant/taux si nécessaire.
      </DialogDescription>
    </DialogHeader>

    <div class="space-y-4 max-h-[65vh] overflow-y-auto pr-1">
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
          class="pl-9 my-2 ml-0.5 h-10 bg-white border-slate-200 rounded-full"
        />
      </div>

      <!-- Liste du catalogue -->
      {#if catalogLoading}
        <div class="py-8 text-center text-[0.82rem] text-slate-400 flex flex-col items-center justify-center gap-2">
          <AnimateSpin text="Chargement du catalogue" class="size-4" />
        </div>
      {:else if catalogError}
        <div class="py-8 text-center text-[0.82rem] text-slate-400 flex flex-col items-center justify-center gap-2">
          <AppIcon name="circle-alert" size={17} class="text-red-400" />
          <span class="text-center text-[0.82rem] text-slate-500">
            Impossible de charger le catalogue. Réessayez dans un instant.
          </span>
        </div>
      {:else if catalog.length === 0}
        <div class="py-8 text-center text-[0.82rem] text-slate-400 flex flex-col items-center justify-center gap-2">
          <AppIcon name="box" size={20} class="text-slate-400" />
          <span class="text-center text-[0.82rem]">
            Le catalogue des éléments de paie est vide.
          </span>
        </div>
      {:else if available.length === 0}
        <div class="py-8 text-center text-[0.82rem] text-slate-400 flex flex-col items-center justify-center gap-2">
          <AppIcon name="circle-check" size={17} class="text-emerald-400" />
          <span class="text-center text-[0.82rem]">
            Tous les éléments du catalogue sont déjà assignés à ce contrat.
          </span>
        </div>
      {:else}
        <div class="max-h-64 overflow-y-auto rounded-xl border border-slate-100">
          <Table>
            <TableHeader class="bg-slate-50">
              <TableRow>
                <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Libellé</TableHead>
                <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Catégorie</TableHead>
                <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Calcul</TableHead>
                <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Traitement</TableHead>
                <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500 text-center">Obligatoire</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {#each available as item (item.id)}
                <TableRow
                  class={cn(
                    "transition-colors cursor-pointer",
                    selectedId === item.id ? "bg-primary/5" : "hover:bg-slate-50/50"
                  )}
                  onclick={() => (selectedId = item.id)}
                >
                  <TableCell class="py-2.5 min-w-0 whitespace-normal">
                      <p class="text-[0.84rem] font-medium text-slate-700 wrap-break-word">{item.name}</p>

                  </TableCell>

                  <TableCell class="py-2.5">
                    {@const style = getTypeStyle(item.adjustment_type)}
                    <Badge variant="outline" class={cn('border-0 text-[0.7rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', style.class)}>
                      <AppIcon name={item.adjustment_type === 'BONUS' ? 'award' : 'circle-x'} size={13} />
                      {style.label}
                    </Badge>
                  </TableCell>

                  <TableCell class="py-2.5">
                    <span class={cn('text-[0.72rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md', MODE_STYLES[item.calculation_mode] ?? 'bg-slate-50 text-slate-500')}>
                      {formatItemDefault(item) || formatModeLabel(item.calculation_mode)}
                    </span>
                  </TableCell>

                  <TableCell class="py-2.5 whitespace-normal">
                    <div class="flex flex-wrap gap-1.5">
                      <Badge variant="outline" class={cn('border-0 text-[0.66rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', item.is_taxable ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700')}>
                        <AppIcon name={item.is_taxable ? 'receipt' : 'shield-check'} size={12} />
                        {item.is_taxable ? 'IRPP' : 'IRPP exclu'}
                      </Badge>
                      <Badge variant="outline" class={cn('border-0 text-[0.66rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', item.is_cnss_subject ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500')}>
                        <AppIcon name={item.is_cnss_subject ? 'shield' : 'circle-x'} size={12} />
                        {item.is_cnss_subject ? 'CNSS' : 'CNSS exclu'}
                      </Badge>
                    </div>
                  </TableCell>

                  <TableCell class="py-2.5 text-center">
                    {#if item.is_mandatory}
                      <Badge variant="outline" class="text-[0.66rem] font-semibold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap bg-amber-50 text-amber-700 border-amber-100">
                        <AppIcon name="shield-check" size={12} />
                        Obligatoire
                      </Badge>
                    {:else}
                      <Badge variant="outline" class="text-[0.66rem] font-medium uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap bg-slate-50 text-slate-400 border-slate-100">
                        Optionnel
                      </Badge>
                    {/if}
                  </TableCell>
                </TableRow>
              {/each}
            </TableBody>
          </Table>
        </div>
      {/if}

      <!-- Configuration du montant -->
      {#if selected}
        <div class="rounded-lg border border-slate-100 bg-slate-50/50 p-3.5 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-[0.86rem] font-semibold text-slate-800">{selected.name}</span>
                <Badge variant="outline" class="text-[0.86rem] text-slate-800 rounded-full">
                  {formatModeLabel(selected.calculation_mode)}
                </Badge>
              </div>
              <div class="text-[0.86rem] text-slate-400">{formattedDefault()}</div>
            </div>
            {#if selected.is_taxable}
              <Badge variant="outline" class="text-[0.86rem] rounded-full">Imposable</Badge>
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
                  placeholder={defaultValuePlaceholder}
                  bind:value={customAmount}
                  class="h-9 bg-white border-slate-200"
                />
                {#if fieldErrors.custom_amount}
                  <p class="text-[0.82rem] text-red-500">{fieldErrors.custom_amount}</p>
                {/if}
              </div>
            {:else if isPercentage}
              <div class="space-y-1">
                <Label for="pe-custom-percentage" class="text-[0.82rem] text-slate-500">Taux (% du salaire brut)</Label>
                <Input
                  id="pe-custom-percentage"
                  type="number"
                  min="0"
                  max="100"
                  placeholder={defaultValuePlaceholder}
                  bind:value={customPercentage}
                  class="h-9 bg-white border-slate-200"
                />
                <p class="text-[0.72rem] text-slate-400">Calculé sur le salaire brut mensuel.</p>
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
            <AnimateSpin class="border-white size-3" text="" />
        {:else}
          <AppIcon name="check" class="text-white" />
        {/if}
        Ajouter
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>

