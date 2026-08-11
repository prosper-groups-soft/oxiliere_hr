<script lang="ts">
  import { Button } from '@/components/ui/button';
  import * as Sheet from '@/components/ui/sheet';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Separator } from '@/components/ui/separator';
  import CurrencyConversionBanner from './CurrencyConversionBanner.svelte';
  import {
    PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS,
    type Payslip, type PayslipSection
  } from '@/features/payroll/types/types';
  import { cn } from '@/utilities/common/css';

  
  interface Props {
    open: boolean;
    payslip: Payslip | null;
    /** Index dans la liste (pour navigation ← →) */
    currentIndex?: number;
    /** Nombre total de bulletins dans la liste */
    totalCount?: number;
    /** Callback pour passer au bulletin précédent */
    onPrevious?: () => void;
    /** Callback pour passer au bulletin suivant */
    onNext?: () => void;
    /** Callback pour ouvrir le panneau d'audit (Ctrl+A) */
    onAudit?: () => void;
  }

  let {
    open = $bindable(false),
    payslip,
    currentIndex,
    totalCount,
    onPrevious,
    onNext,
    onAudit
  }: Props = $props();

  /** Gestionnaire clavier : ← → pour navigation, Ctrl+A pour l'audit */
  function handleKeydown(e: KeyboardEvent) {
    if (!open) return;
    if (e.key === 'ArrowLeft' && onPrevious) {
      e.preventDefault();
      onPrevious();
    } else if (e.key === 'ArrowRight' && onNext) {
      e.preventDefault();
      onNext();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'a' && onAudit) {
      e.preventDefault();
      onAudit();
    }
  }

  /** Étiquette lisible du type de contrat */
  const contractTypeLabel = $derived.by(() => {
    if (!payslip) return '';
    const labels: Record<string, string> = {
      CDI: 'CDI — Contrat à Durée Indéterminée',
      CDD: 'CDD — Contrat à Durée Déterminée',
      CTR: 'CTR — Contrat de Prestation',
    };
    return labels[payslip.contract.type] ?? payslip.contract.type;
  });

  /** Étiquette du régime de travail */
  const workRegimeLabel = $derived.by(() => {
    if (!payslip) return '';
    return payslip.contract.workRegime === 'TEMPS_PLEIN' ? 'Temps plein' : 'Temps partiel';
  });

  /**
   * Formate un montant en devise (USD) selon les conventions françaises.
   * Exemple : 2500 -> "2 500,00 $US"
   */
  function formatCurrency(amount: number) {
    return amount.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' });
  }

  /** Couleurs de fond pour chaque section */
  const sectionStyles: Record<PayslipSection['sectionType'], { heading: string; icon: string; iconName: string }> = {
    earning:  { heading: 'text-emerald-700', icon: 'text-emerald-500', iconName: 'plus-circle' },
    deduction: { heading: 'text-rose-700', icon: 'text-rose-500', iconName: 'minus-circle' },
  };
</script>


<Sheet.Root bind:open>
  <Sheet.Content
    side="right"
    class="sm:max-w-lg flex flex-col h-full overflow-hidden p-0"
    onkeydown={handleKeydown}
  >
  {#if payslip}
    <div class="px-6 py-4 pr-12 border-b bg-slate-50/50">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-bold text-[1rem] flex items-center gap-2">
            Bulletin de paie
          </h2>
          <p class="text-[0.85rem] text-slate-500 mt-1">
            {payslip.employee.fullName} — {payslip.period.start} au {payslip.period.end}
          </p>
        </div>
        {#if totalCount != null && totalCount > 1}
          <div class="flex items-center gap-1">
            <span class="text-[0.72rem] text-slate-400 tabular-nums">
              {currentIndex != null ? currentIndex + 1 : '?'} / {totalCount}
            </span>
            <button
              onclick={onPrevious}
              disabled={currentIndex == null || currentIndex <= 0}
              class="w-7 h-7 flex items-center justify-center rounded-md border border-slate-200 text-slate-500
                     hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer">
              <AppIcon name="chevron-left" size={14} />
            </button>
            <button
              onclick={onNext}
              disabled={currentIndex == null || totalCount == null || currentIndex >= totalCount - 1}
              class="w-7 h-7 flex items-center justify-center rounded-md border border-slate-200 text-slate-500
                     hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors cursor-pointer">
              <AppIcon name="chevron-right" size={14} />
            </button>
          </div>
        {/if}
      </div>
    </div>

      <div class="flex-1 overflow-y-auto px-6 py-2 space-y-6 custom-scrollbar">
        <!-- Badge de statut -->
        <div class="flex items-center justify-between">
          <span class="text-sm text-slate-500">Statut</span>
          <span class={cn(
            "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.75rem] font-medium",
            PAYROLL_STATUS_COLORS[payslip.status].bg,
            PAYROLL_STATUS_COLORS[payslip.status].text
          )}>
            <span class={cn("h-1.5 w-1.5 rounded-full", PAYROLL_STATUS_COLORS[payslip.status].dot)}></span>
            {PAYROLL_STATUS_LABELS[payslip.status]}
          </span>
        </div>

        <Separator />

        <!-- Informations employé + contrat -->
        <div class="space-y-3">
          <h4 class="text-[0.8rem] font-semibold text-slate-700 uppercase tracking-wider">Employé</h4>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm font-medium text-slate-500">Nom</div>
              <p class="text-sm text-slate-900">{payslip.employee.fullName}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Matricule</div>
              <p class="text-sm text-slate-900">{payslip.employee.matricule}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Département</div>
              <p class="text-sm text-slate-900">{payslip.employee.orgUnit}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Date d'entrée</div>
              <p class="text-sm text-slate-900">{payslip.employee.entryDate ?? '—'}</p>
            </div>
          </div>
        </div>

        <!-- Informations contrat -->
        <div class="space-y-3">
          <h4 class="text-[0.8rem] font-semibold text-slate-700 uppercase tracking-wider">Contrat</h4>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm font-medium text-slate-500">Type de contrat</div>
              <p class="text-sm text-slate-900">{contractTypeLabel}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Catégorie</div>
              <p class="text-sm text-slate-900">{payslip.contract.professionalCategory}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Grade</div>
              <p class="text-sm text-slate-900">{payslip.contract.grade}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Régime</div>
              <p class="text-sm text-slate-900">{workRegimeLabel}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Devise</div>
              <p class="text-sm text-slate-900">{payslip.contract.currency}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Salaire de base</div>
              <p class="text-sm text-slate-900">{formatCurrency(payslip.contract.baseSalary)}</p>
            </div>
          </div>
        </div>

        <Separator />

        <!-- Bannière taux de change (USD seulement) -->
        {#if payslip.currency === 'USD'}
          <CurrencyConversionBanner exchangeRate={payslip.exchangeRate} />
        {/if}

        <!-- Sections de la fiche de paie (gains / retenues) -->
        {#each payslip.sections as section (section.code)}
          <div class="space-y-3">
            <h4 class={cn(
              "text-sm font-semibold uppercase tracking-wider flex items-center gap-2",
              sectionStyles[section.sectionType].heading
            )}>
              <AppIcon name={sectionStyles[section.sectionType].iconName} size={15} class={sectionStyles[section.sectionType].icon} />
              {section.label}
            </h4>
            <div class="space-y-2">
              {#each section.lines as line}
                <div class="flex items-center justify-between py-1">
                  <span class="text-sm text-slate-700">{line.label}</span>
                  <span class={cn(
                    "text-sm font-medium",
                    section.sectionType === 'earning' ? 'text-slate-900' : 'text-rose-600'
                  )}>
                    {section.sectionType === 'earning'
                      ? '+' + formatCurrency(line.amount)
                      : '-' + formatCurrency(Math.abs(line.amount))}
                  </span>
                </div>
              {/each}
            </div>
            <!-- Total de la section -->
            <div class="flex items-center justify-between py-1.5 border-t border-slate-100">
              <span class="text-sm font-semibold text-slate-700">Total {section.label.toLowerCase()}</span>
              <span class={cn(
                "text-sm font-bold",
                section.sectionType === 'earning' ? 'text-emerald-600' : 'text-rose-700'
              )}>
                {section.sectionType === 'earning'
                  ? formatCurrency(section.total)
                  : '-' + formatCurrency(section.total)}
              </span>
            </div>
          </div>
        {/each}

        <Separator />

        <!-- Résumé financier complet -->
        <div class="space-y-3">
          <h4 class="text-[0.8rem] font-semibold text-slate-700 uppercase tracking-wider">Résumé</h4>
          <div class="space-y-2.5">
            <div class="flex items-center justify-between py-1">
              <span class="text-sm font-medium text-slate-700">Salaire brut</span>
              <span class="text-sm font-semibold text-slate-900">{formatCurrency(payslip.summary.grossSalary)}</span>
            </div>
            <div class="flex items-center justify-between py-1">
              <span class="text-sm font-medium text-slate-700">Total retenues</span>
              <span class="text-sm font-semibold text-rose-600">-{formatCurrency(payslip.summary.totalDeductions)}</span>
            </div>
            {#if payslip.summary.postNetDeductions > 0}
              <div class="flex items-center justify-between py-1">
                <span class="text-sm font-medium text-slate-700">Déductions post-nette</span>
                <span class="text-sm font-semibold text-rose-600">-{formatCurrency(payslip.summary.postNetDeductions)}</span>
              </div>
            {/if}
            <div class="flex items-center justify-between py-1.5 border-t border-slate-100">
              <span class="text-sm font-bold text-slate-800">Salaire net à payer</span>
              <span class="text-sm font-bold text-emerald-600">{formatCurrency(payslip.summary.netPay)}</span>
            </div>
          </div>

          <!-- Coût employeur -->
          <div class="mt-4 pt-3 border-t border-dashed border-slate-200 space-y-2.5">
            <h5 class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider">Coût employeur</h5>
            <div class="flex items-center justify-between py-1">
              <span class="text-sm font-medium text-slate-700">Cotisations employeur</span>
              <span class="text-sm font-semibold text-slate-900">{formatCurrency(payslip.summary.employerCosts)}</span>
            </div>
            <div class="flex items-center justify-between py-1.5 border-t border-dashed border-slate-100">
              <span class="text-sm font-bold text-slate-800">Coût total employeur</span>
              <span class="text-sm font-bold text-indigo-600">{formatCurrency(payslip.summary.totalEmployerCost)}</span>
            </div>
          </div>
        </div>

        <!-- Snapshot d'audit (optionnel — présent après finalisation) -->
        {#if payslip.immutableSnapshot}
          <Separator />
          <div class="space-y-2">
            <h4 class="text-[0.8rem] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
              <AppIcon name="shield-check" size={14} class="text-slate-400" />
              Snapshot d'audit
            </h4>
            <div class="bg-slate-50 rounded-lg p-3 space-y-1.5">
              <div class="flex items-center justify-between text-[0.75rem]">
                <span class="text-slate-500">Signé le</span>
                <span class="text-slate-700 font-mono">{payslip.immutableSnapshot.signedAt}</span>
              </div>
              <div class="flex items-center justify-between text-[0.75rem]">
                <span class="text-slate-500">SHA-256</span>
                <span class="text-slate-700 font-mono text-[0.65rem] truncate max-w-[180px]" title={payslip.immutableSnapshot.sha256}>
                  {payslip.immutableSnapshot.sha256}
                </span>
              </div>
              <div class="flex items-center justify-between text-[0.75rem]">
                <span class="text-slate-500">SMIG</span>
                <span class="text-slate-700 font-mono">{formatCurrency(payslip.immutableSnapshot.parametersFrozen.smig)}</span>
              </div>
              <div class="flex items-center justify-between text-[0.75rem]">
                <span class="text-slate-500">Taux CNSS</span>
                <span class="text-slate-700 font-mono">{payslip.immutableSnapshot.parametersFrozen.cnssRate}%</span>
              </div>
              <div class="flex items-center justify-between text-[0.75rem]">
                <span class="text-slate-500">Taux de change</span>
                <span class="text-slate-700 font-mono">{payslip.immutableSnapshot.parametersFrozen.exchangeRate}</span>
              </div>
            </div>
          </div>
        {/if}
      </div>

      <!-- Pied de page avec boutons d'action -->
      <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
        <Button variant="outline" onclick={() => open = false} class="flex-1 h-9.5 text-[0.85rem]">
          Fermer
        </Button>
        <Button class="flex-1 h-9.5 text-[0.85rem] bg-blue-600 hover:bg-blue-700">
          <AppIcon name="download" size={16} class="mr-2" />
          Télécharger PDF
        </Button>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>

