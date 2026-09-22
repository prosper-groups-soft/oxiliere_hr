<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import { Badge } from '@/components/ui/badge';
  import { Button } from '@/components/ui/button';
  import { Switch } from '@/components/ui/switch';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
  import { Select, SelectContent, SelectItem,SelectTrigger} from '@/components/ui/select';
  import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
  import { cn } from '@/hr/utilities/common/css';
  import { notification } from '@/hr/stores/notification.svelte';
  import type { PayrollAdjustmentConfig } from '@/hr/modules/payroll/types/types';
  import SettingSection from '../SettingSection.svelte';


  let {
    adjustments = [],
    isLoading = false,
    onToggle,
    onCreate,
    onUpdate,
    onDelete,
    onReset,
  }: {
    adjustments?: PayrollAdjustmentConfig[];
    isLoading?: boolean;
    onToggle?: (adjustment: PayrollAdjustmentConfig, isActive: boolean) => void;
    onCreate?: (data: Partial<PayrollAdjustmentConfig>) => Promise<boolean> | boolean;
    onUpdate?: (id: string, data: Partial<PayrollAdjustmentConfig>) => Promise<boolean> | boolean;
    onDelete?: (id: string) => Promise<boolean> | boolean;
    onReset?: () => Promise<void> | void;
  } = $props();

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

  /* ── Recherche & filtre ── */
  let searchQuery = $state('');
  let typeFilter = $state<'ALL' | 'BONUS' | 'CONTRIBUTION'>('ALL');

  const filteredAdjustments = $derived(
    adjustments.filter((a) => {
      const q = searchQuery.trim().toLowerCase();
      const matchesSearch =
        !q ||
        a.name.toLowerCase().includes(q) ||
        (a.formula_description ?? '').toLowerCase().includes(q);
      const matchesType = typeFilter === 'ALL' || a.adjustment_type === typeFilter;
      return matchesSearch && matchesType;
    })
  );

  /* ── Formulaire création / édition ── */
  type FormState = {
    name: string;
    adjustment_type: 'BONUS' | 'CONTRIBUTION';
    calculation_mode: 'FIXED' | 'PERCENTAGE';
    amount: string;
    percentage: string;
    is_mandatory: boolean;
    is_active: boolean;
    is_taxable: boolean;
    is_cnss_subject: boolean;
    formula_description: string;
  };

  const emptyForm = (): FormState => ({
    name: '',
    adjustment_type: 'BONUS',
    calculation_mode: 'FIXED',
    amount: '',
    percentage: '',
    is_mandatory: false,
    is_active: true,
    is_taxable: false,
    is_cnss_subject: false,
    formula_description: '',
  });

  let dialogOpen = $state(false);
  let editingId = $state<string | null>(null);
  let form = $state<FormState>(emptyForm());
  let submitting = $state(false);

  const openCreate = () => {
    editingId = null;
    form = emptyForm();
    dialogOpen = true;
  };

  const openEdit = (adj: PayrollAdjustmentConfig) => {
    editingId = adj.id;
    form = {
      name: adj.name,
      adjustment_type: (adj.adjustment_type as 'BONUS' | 'CONTRIBUTION') ?? 'BONUS',
      calculation_mode: (adj.calculation_mode as 'FIXED' | 'PERCENTAGE') ?? 'FIXED',
      amount: adj.amount != null ? String(adj.amount) : '',
      percentage: adj.percentage != null ? String(adj.percentage) : '',
      is_mandatory: adj.is_mandatory,
      is_active: adj.is_active,
      is_taxable: adj.is_taxable,
      is_cnss_subject: adj.is_cnss_subject,
      formula_description: adj.formula_description ?? '',
    };
    dialogOpen = true;
  };

  const closeDialog = () => {
    dialogOpen = false;
    editingId = null;
    form = emptyForm();
  };

  const submitForm = async () => {
    if (!form.name.trim()) return;
    submitting = true;
    try {
      const payload: Partial<PayrollAdjustmentConfig> = {
        name: form.name.trim(),
        adjustment_type: form.adjustment_type,
        calculation_mode: form.calculation_mode,
        is_mandatory: form.is_mandatory,
        is_active: form.is_active,
        is_taxable: form.is_taxable,
        is_cnss_subject: form.is_cnss_subject,
        formula_description: form.formula_description.trim(),
        amount: form.calculation_mode === 'FIXED' && form.amount !== '' ? Number(form.amount) : null,
        percentage:
          form.calculation_mode === 'PERCENTAGE' && form.percentage !== '' ? Number(form.percentage) : null,
      };
      const ok = editingId
        ? await onUpdate?.(editingId, payload)
        : await onCreate?.(payload);
      if (ok) closeDialog();
    } finally {
      submitting = false;
    }
  };

  /* ── Suppression avec confirmation ── */
  const requestDelete = (adj: PayrollAdjustmentConfig) => {
    notification.confirm({
      title: 'Supprimer cet élément ?',
      message:
        '<strong style="font-size: 0.85rem">' + (adj.name ?? 'Cet élément') +
        '</strong> sera supprimé du catalogue. Cette action est irréversible.',
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: () => onDelete?.(adj.id),
    });
  };

  /* ── Réinitialisation avec confirmation ── */
  const requestReset = () => {
    notification.confirm({
      title: 'Réinitialiser le catalogue ?',
      message:
        'Tous les éléments de paie seront réinitialisés aux valeurs par défaut de la loi. Vos modifications seront écrasées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      noText: 'Annuler',
      onYes: () => onReset?.(),
    });
  };
</script>


<SettingSection
  icon="book-open"
  title="Catalogue des éléments de paie"
  description="Primes et bonus conventionnels de l'entreprise, activables par contrat."
  iconClass="bg-rose-50"
>
  <!-- Barre d'outils : recherche + filtre + nouvel élément (toujours visible) -->
  <div class="mb-4 flex flex-wrap items-center gap-2">
    <div class="relative min-w-0 flex-1 basis-52">
      <AppIcon
        name="search"
        size={15}
        class="text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none"
      />
      <Input
        type="text"
        placeholder="Rechercher..."
        bind:value={searchQuery}
        class="h-9 w-full pl-8 pr-3 text-[0.84rem] bg-white border-slate-200 rounded-md shadow-fine focus:ring-1 focus:ring-primary focus:border-primary"
      />
    </div>

    <Select
      type="single"
      value={typeFilter}
      onValueChange={(v) => (typeFilter = v as 'ALL' | 'BONUS' | 'CONTRIBUTION')}
    >
      <SelectTrigger class="h-9 w-40 text-[0.82rem] bg-white border-slate-200 rounded-md shadow-fine">
        {typeFilter === 'ALL' ? 'Tous' : typeFilter === 'BONUS' ? 'Bonus' : 'Retenues'}
      </SelectTrigger>
      <SelectContent class="z-9999">
        <SelectItem value="ALL">Tous</SelectItem>
        <SelectItem value="BONUS">Bonus</SelectItem>
        <SelectItem value="CONTRIBUTION">Retenues</SelectItem>
      </SelectContent>
    </Select>

    <Button
      size="sm"
      class="h-9 px-3 text-[0.82rem] bg-primary text-white hover:text-white shadow-fine rounded-lg"
      onclick={openCreate}
    >
      <AppIcon name="plus" size={15} />
      Nouvel élément
    </Button>

    <Button
      size="sm"
      variant="outline"
      class="h-9 px-2.5 text-[0.82rem] text-slate-500 hover:text-rose-600 hover:border-rose-200"
      onclick={requestReset}
    >
      <AppIcon name="rotate-ccw" size={15} />
      Réinitialiser
    </Button>
  </div>

  {#if isLoading && adjustments.length === 0}
    <div class="py-10">
      <AnimateSpin text="Chargement du catalogue" class="border-primary text-slate-500" />
    </div>
  {:else if adjustments.length === 0}
    <div class="py-10 text-center">
      <AppIcon name="book-open" size={28} class="text-slate-300 mx-auto mb-2" strokeWidth={1.3} />
      <p class="text-[0.85rem] text-slate-500">Aucun élément de paie configuré.</p>
    </div>
  {:else}

    <div class="overflow-hidden rounded-xl border border-slate-100">
      <Table>
        <TableHeader class="bg-slate-50">
          <TableRow>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Libellé</TableHead>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Catégorie</TableHead>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Calcul</TableHead>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500">Traitement</TableHead>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500 text-center">Actif</TableHead>
            <TableHead class="text-[0.7rem] font-bold uppercase tracking-widest text-slate-500 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {#each filteredAdjustments as adjustment (adjustment.id)}
            <TableRow class="hover:bg-slate-50/50 transition-colors">

              <TableCell class="py-2.5 min-w-0 whitespace-normal">
                <div class="flex flex-col min-w-0">
                  <p class="text-[0.84rem] font-medium text-slate-700 wrap-break-word">{adjustment.name}</p>
                  {#if adjustment.formula_description}
                    <p class="text-[0.84rem] text-slate-500 wrap-break-word min-w-0">{adjustment.formula_description}</p>
                  {:else}
                    <p class="text-[0.84rem] font-medium text-slate-500">
                      Conventionnel
                    </p>
                  {/if}
                </div>
              </TableCell>

              <TableCell class="py-2.5">
                {@const style = getTypeStyle(adjustment.adjustment_type)}
                <Badge variant="outline" class={cn('border-0 text-[0.7rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', style.class)}>
                  <AppIcon name={adjustment.adjustment_type === 'BONUS' ? 'award' : 'circle-x'} size={13} />
                  {style.label}
                </Badge>
              </TableCell>

              <TableCell class="py-2.5">
                <span class={cn('text-[0.72rem] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md', MODE_STYLES[adjustment.calculation_mode] ?? 'bg-slate-50 text-slate-500')}>
                  {adjustment.calculation_mode === 'PERCENTAGE' && adjustment.percentage !== null
                    ? `${adjustment.percentage}%`
                    : adjustment.amount !== null
                      ? adjustment.amount.toLocaleString('fr-FR')
                      : adjustment.calculation_mode}
                </span>
              </TableCell>

              <TableCell class="py-2.5 whitespace-normal">
                <div class="flex flex-wrap gap-1.5">
                  <Badge variant="outline" class={cn('border-0 text-[0.66rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', adjustment.is_taxable ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700')}>
                    <AppIcon name={adjustment.is_taxable ? 'receipt' : 'shield-check'} size={12} />
                    {adjustment.is_taxable ? 'IRPP' : 'IRPP exclu'}
                  </Badge>
                  <Badge variant="outline" class={cn('border-0 text-[0.66rem] font-bold uppercase tracking-wider px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors', adjustment.is_cnss_subject ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500')}>
                    <AppIcon name={adjustment.is_cnss_subject ? 'shield' : 'circle-x'} size={12} />
                    {adjustment.is_cnss_subject ? 'CNSS' : 'CNSS exclu'}
                  </Badge>
                </div>
              </TableCell>

              <TableCell class="py-2.5 text-center">
                <div class="flex justify-center">
                  <Switch
                    checked={adjustment.is_active}
                    onCheckedChange={(checked) => onToggle?.(adjustment, checked)}
                    aria-label={`Activer ${adjustment.name}`}
                  />
                </div>
              </TableCell>

              <TableCell class="py-2.5">
                <div class="flex items-center justify-end gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    class="h-8 w-8 p-0 text-slate-500 hover:text-slate-700"
                    onclick={() => openEdit(adjustment)}
                    aria-label={`Modifier ${adjustment.name}`}
                  >
                    <AppIcon name="edit" size={15} />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    class="h-8 w-8 p-0 text-slate-400 hover:text-rose-600"
                    onclick={() => requestDelete(adjustment)}
                    aria-label={`Supprimer ${adjustment.name}`}
                  >
                    <AppIcon name="trash-2" size={15} />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          {/each}
        </TableBody>
      </Table>
    </div>

    <!-- Confirmation de suppression via notification.confirm (global) -->

    <p class="text-[0.85rem] text-slate-500 mt-3 flex items-center gap-1">
      <AppIcon name="info" size={12} />
      Éléments conventionnels imposables et cotisables. Les allocations légales (familiale, logement, transport) sont gérées dans l'onglet Paramètres légaux.
    </p>
  {/if}

  <!-- Modal création / édition -->
  <Dialog open={dialogOpen} onOpenChange={(o) => !o && closeDialog()}>
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{editingId ? 'Modifier l\'élément' : 'Nouvel élément'}</DialogTitle>
        <DialogDescription>
          {editingId
            ? 'Modifiez les caractéristiques de l\'élément de paie.'
            : 'Définissez un nouvel élément conventionnel (prime ou retenue).'}
        </DialogDescription>
      </DialogHeader>

      <div class="grid gap-4 py-2">
        <div class="grid gap-1.5">
          <Label for="adj-name" class="text-[0.82rem] font-semibold text-slate-700">Libellé</Label>
          <Input
            id="adj-name"
            type="text"
            bind:value={form.name}
            placeholder="Ex. : Prime de performance"
            class="h-9 w-full text-[0.84rem] bg-white border-slate-200 rounded-md shadow-fine focus:ring-1 focus:ring-primary focus:border-primary"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="grid gap-1.5">
            <Label class="text-[0.82rem] font-semibold text-slate-700">Catégorie</Label>
            <Select
              type="single"
              value={form.adjustment_type}
              onValueChange={(v) => (form.adjustment_type = v as 'BONUS' | 'CONTRIBUTION')}
            >
              <SelectTrigger class="h-9 w-full text-[0.82rem] bg-white border-slate-200 rounded-md shadow-fine">
                {form.adjustment_type === 'BONUS' ? 'Bonus' : 'Retenue'}
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="BONUS">Bonus</SelectItem>
                <SelectItem value="CONTRIBUTION">Retenue</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="grid gap-1.5">
            <Label class="text-[0.82rem] font-semibold text-slate-700">Mode de calcul</Label>
            <Select
              type="single"
              value={form.calculation_mode}
              onValueChange={(v) => (form.calculation_mode = v as 'FIXED' | 'PERCENTAGE')}
            >
              <SelectTrigger class="h-9 w-full text-[0.82rem] bg-white border-slate-200 rounded-md shadow-fine">
                {form.calculation_mode === 'FIXED' ? 'Montant fixe' : 'Pourcentage'}
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="FIXED">Montant fixe</SelectItem>
                <SelectItem value="PERCENTAGE">Pourcentage</SelectItem>
              </SelectContent>
            </Select>
          </div> 
        </div>

        {#if form.calculation_mode === 'FIXED'}
          <div class="grid gap-1.5">
            <Label for="adj-amount" class="text-[0.82rem] font-semibold text-slate-700">Montant (CDF)</Label>
            <Input
              id="adj-amount"
              type="number"
              min="0"
              bind:value={form.amount}
              placeholder="Ex. : 50 000"
              class="h-9 w-full text-[0.84rem] bg-white border-slate-200 rounded-md shadow-fine focus:ring-1 focus:ring-primary focus:border-primary"
            />
          </div>
        {:else}
          <div class="grid gap-1.5">
            <Label for="adj-percentage" class="text-[0.82rem] font-semibold text-slate-700">Pourcentage (%)</Label>
            <Input
              id="adj-percentage"
              type="number"
              min="0"
              max="100"
              step="0.01"
              bind:value={form.percentage}
              placeholder="Ex. : 5"
              class="h-9 w-full text-[0.84rem] bg-white border-slate-200 rounded-md shadow-fine focus:ring-1 focus:ring-primary focus:border-primary"
            />
          </div>
        {/if}

        <div class="grid gap-1.5">
          <Label for="adj-desc" class="text-[0.82rem] font-semibold text-slate-700">Description / formule</Label>
          <textarea
            id="adj-desc"
            bind:value={form.formula_description}
            rows={3}
            placeholder="Expliquez la formule ou la base de calcul..."
            class="w-full text-[0.84rem] bg-white border border-slate-200 rounded-md shadow-fine px-3 py-2 focus:ring-1 focus:ring-primary focus:border-primary resize-y wrap-break-word"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <label class="flex items-center gap-2 cursor-pointer">
            <Switch bind:checked={form.is_taxable} aria-label="Imposable IRPP" />
            <span class="text-[0.84rem] text-slate-600">Imposable IRPP</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <Switch bind:checked={form.is_cnss_subject} aria-label="Soumis CNSS" />
            <span class="text-[0.84rem] text-slate-600">Soumis CNSS</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <Switch bind:checked={form.is_mandatory} aria-label="Obligatoire" />
            <span class="text-[0.84rem] text-slate-600">Obligatoire</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer">
            <Switch bind:checked={form.is_active} aria-label="Actif" />
            <span class="text-[0.84rem] text-slate-600">Actif</span>
          </label>
        </div>
      </div>

      <DialogFooter>
        <Button size="sm" variant="ghost" class="h-9 px-3 text-[0.82rem]" onclick={closeDialog}>
          Annuler
        </Button>
        <Button
          size="sm"
          class="h-9 px-4 text-[0.82rem] bg-primary text-white hover:text-white shadow-fine rounded-lg disabled:opacity-50"
          disabled={!form.name.trim() || submitting}
          onclick={submitForm}
        >
          {#if submitting}
            <AnimateSpin text="Enregistrement…" textPosition="right" class="border-white size-3.5" />
          {:else}
            {editingId ? 'Enregistrer' : 'Créer'}
          {/if}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</SettingSection>
