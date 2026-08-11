<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { payrollStore } from "../../../stores/payroll.svelte";
  import type { Advance, AdvanceDeductionBase, AdvanceDeductionWindow, AdvanceTaxTiming } from "../../../types/types";
  import { fade } from "svelte/transition";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";


  // ── Configuration de déduction saisie par la RH à l'approbation ──
  let repaymentPercentage = $state(20);
  let deductionBase = $state<AdvanceDeductionBase>('NET');
  let taxTiming = $state<AdvanceTaxTiming>('AFTER_TAX');
  let deductionWindow = $state<AdvanceDeductionWindow>('ALL_MONTHS');
  let deductionStart = $state('');
  let deductionEnd = $state('');
  let priorityOrder = $state(1);
  let isSavingConfig = $state(false);
  

  let {
    advance = null as Advance | null,
    open = $bindable(false),
    onApproved
  }: {
    advance: Advance | null;
    open: boolean;
    onApproved?: (advance: Advance) => void;
  } = $props();

  // Initialiser depuis l'avance quand elle change
  $effect(() => {
    if (advance) {
      repaymentPercentage = advance.repayment_percentage ?? 20;
      deductionBase = (advance.salary_base_for_deduction as AdvanceDeductionBase) ?? 'NET';
      taxTiming = (advance.tax_timing as AdvanceTaxTiming) ?? 'AFTER_TAX';
      deductionWindow = (advance.deduction_window as AdvanceDeductionWindow) ?? 'ALL_MONTHS';
      deductionStart = advance.deduction_start_date ?? '';
      deductionEnd = advance.deduction_end_date ?? '';
    }
  });

  function formatAmount(v: number): string {
    return v.toLocaleString('fr-FR', { maximumFractionDigits: 0 });
  }

  async function handleApprove() {
    if (!advance) return;
    isSavingConfig = true;
    try {
      // 1. Enregistrer la configuration de déduction via la route dédiée
      const configPayload = {
        repayment_percentage: repaymentPercentage,
        salary_base_for_deduction: deductionBase,
        tax_timing: taxTiming,
        deduction_window: deductionWindow,
        ...(deductionWindow === 'CUSTOM_PERIOD' ? { deduction_start_date: deductionStart, deduction_end_date: deductionEnd } : {}),
        priority_order: priorityOrder,
        is_active: true,
      };
      await payrollStore.updateAdvanceConfig(advance.id, configPayload);

      // 2. Approuver directement (pas de confirmation — le sheet est la confirmation)
      const updated = await payrollStore.approveAdvance(advance.id);
      notification.toast.success("Demande d'avance approuvée");
      onApproved?.(updated ?? advance);
      open = false;
    } catch {
      notification.toast.error("Erreur lors de l'approbation de l'avance");
    } finally {
      isSavingConfig = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
    {#if advance}
      <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/60 flex flex-row items-center justify-between">
        <Sheet.Title class="text-base font-bold text-slate-900 text-left">
          Approuver l'avance
        </Sheet.Title>
      </Sheet.Header>

      <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        <!-- Récapitulatif -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-[0.85rem] font-medium text-slate-500 uppercase tracking-wider">Montant</span>
            <span class="text-lg font-medium text-slate-900">{formatAmount(advance.amount)} {advance.currency || 'CDF'}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[0.85rem] font-medium text-slate-500 uppercase tracking-wider">Employé</span>
            <span class="text-sm font-semibold text-slate-900">{advance.employee_name}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[0.85rem] font-medium text-slate-500 uppercase tracking-wider">Prélèvement proposé</span>
            <span class="text-sm font-semibold text-slate-800">{advance.repayment_percentage}% / mois</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-[0.85rem] font-medium text-slate-500 uppercase tracking-wider">Date de demande</span>
            <span class="text-sm font-semibold text-slate-800">{new Date(advance.requested_date).toLocaleDateString('fr-FR')}</span>
          </div>
        </div>

        <!-- Configuration de la déduction (saisie RH à l'approbation) -->
        <div class="space-y-3 mt-4">
          <div class="flex items-center gap-2">
            <AppIcon name="settings" size={15} class="text-slate-500" />
            <h4 class="text-[0.85rem] font-bold text-slate-700 uppercase tracking-wider">Configuration de la déduction</h4>
            <span class="ml-auto text-[0.85rem] text-slate-400">Saisie RH</span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <!-- % du salaire -->
            <div class="space-y-1.5">
              <Label for="config-percentage" class="text-[0.85rem] text-slate-600">% du salaire / mois</Label>
              <Input
                id="config-percentage"
                type="number"
                min="1"
                max="100"
                bind:value={repaymentPercentage}
                class="h-9 bg-white border-slate-200 rounded-md text-[0.85rem]"
              />
            </div>

            <!-- Priorité (multi-avances) -->
            <div class="space-y-1.5">
              <Label for="config-priority" class="text-[0.85rem] text-slate-600">Priorité</Label>
              <Input
                id="config-priority"
                type="number"
                min="1"
                bind:value={priorityOrder}
                class="h-9 bg-white border-slate-200 rounded-md text-[0.85rem]"
              />
            </div>

            <!-- Base de déduction -->
            <div class="space-y-1.5">
              <Label class="text-[0.85rem] text-slate-600">Base de déduction</Label>
              <Select type="single" value={deductionBase} onValueChange={(v) => deductionBase = v as AdvanceDeductionBase}>
                <SelectTrigger class="h-9 w-full bg-white border-slate-200 rounded-md text-[0.85rem] cursor-pointer">
                  {deductionBase === 'GROSS' ? 'Salaire brut' : 'Salaire net'}
                </SelectTrigger>
                <SelectContent class="z-9999">
                  <SelectItem value="GROSS" label="Salaire brut" class="text-[0.85rem]">Salaire brut</SelectItem>
                  <SelectItem value="NET" label="Salaire net" class="text-[0.85rem]">Salaire net</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- Moment de la retenue -->
            <div class="space-y-1.5">
              <Label class="text-[0.85rem] text-slate-600">Moment de la retenue</Label>
              <Select type="single" value={taxTiming} onValueChange={(v) => taxTiming = v as AdvanceTaxTiming}>
                <SelectTrigger class="h-9 w-full bg-white border-slate-200 rounded-md text-[0.85rem] cursor-pointer">
                  {taxTiming === 'BEFORE_TAX' ? 'Avant impôt' : 'Après impôt'}
                </SelectTrigger>
                <SelectContent class="z-9999">
                  <SelectItem value="BEFORE_TAX" label="Avant impôt" class="text-[0.85rem]">Avant impôt (réduit le taxable)</SelectItem>
                  <SelectItem value="AFTER_TAX" label="Après impôt" class="text-[0.85rem]">Après impôt (sans impact fiscal)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <!-- Fenêtre de déduction -->
          <div class="space-y-1.5">
            <Label class="text-[0.85rem] text-slate-600">Fenêtre de déduction</Label>
            <Select type="single" value={deductionWindow} onValueChange={(v) => deductionWindow = v as AdvanceDeductionWindow}>
              <SelectTrigger class="h-9 w-full bg-white border-slate-200 rounded-md text-[0.85rem] cursor-pointer">
                {deductionWindow === 'ALL_MONTHS' ? "Tous les mois (jusqu'au remboursement)" : 'Période personnalisée'}
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="ALL_MONTHS" label="Tous les mois" class="text-[0.85rem]">Tous les mois (jusqu'à remboursement)</SelectItem>
                <SelectItem value="CUSTOM_PERIOD" label="Période personnalisée" class="text-[0.85rem]">Période personnalisée</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {#if deductionWindow === 'CUSTOM_PERIOD'}
            <div class="grid grid-cols-2 gap-3" in:fade={{ duration: 150 }}>
              <div class="space-y-1.5">
                <Label for="config-start" class="text-[0.85rem] text-slate-600">Début</Label>
                <Input id="config-start" type="date" bind:value={deductionStart} class="h-9 bg-white border-slate-200 rounded-md text-[0.85rem]" />
              </div>
              <div class="space-y-1.5">
                <Label for="config-end" class="text-[0.85rem] text-slate-600">Fin</Label>
                <Input id="config-end" type="date" bind:value={deductionEnd} class="h-9 bg-white border-slate-200 rounded-md text-[0.85rem]" />
              </div>
            </div>
          {/if}
        </div>
      </div>

      <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 bg-slate-50/60">
        <Button
          variant="outline"
          onclick={() => open = false}
          class="flex-1 h-9 border-slate-200 text-slate-600 hover:bg-slate-50 font-medium cursor-pointer"
        >
          <AppIcon name="x" size={16} />
          Annuler
        </Button>
        <Button
          onclick={handleApprove}
          disabled={isSavingConfig}
          class="flex-1 h-9 bg-emerald-600 hover:bg-emerald-700 text-white font-medium shadow-fine cursor-pointer disabled:opacity-60"
        >
          {#if isSavingConfig}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check-circle" size={16} />
          {/if}
          Approuver
        </Button>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>
