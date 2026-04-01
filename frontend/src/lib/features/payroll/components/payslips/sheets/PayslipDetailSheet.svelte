<script lang="ts">
  import { Button } from '@/components/ui/button';
  import * as Sheet from '@/components/ui/sheet';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { PAYROLL_STATUS_COLORS, PAYROLL_STATUS_LABELS, type Payslip, type PayslipLine } from '@/features/payroll/types/types';
  import { cn } from '@/utilities/common/css';
  import { Separator } from '@/components/ui/separator';

  interface Props {
    open: boolean;
    payslip: Payslip | null;
  }

  let { open = $bindable(false), payslip }: Props = $props();

  const earnings = $derived(payslip?.lines.filter(l => l.type === 'earning') || []);
  const deductions = $derived(payslip?.lines.filter(l => l.type === 'deduction') || []);

  function formatCurrency(amount: number) {
    return amount.toLocaleString('fr-FR', { style: 'currency', currency: 'USD' });
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg flex flex-col h-full overflow-hidden p-0">
    {#if payslip}
      <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
        <Sheet.Title class="font-bold text-[1rem] flex items-center gap-2">
          Bulletin de paie
        </Sheet.Title>
        <p class="text-[0.85rem] text-slate-500 mt-1">
          {payslip.employeeName} — {payslip.period}
        </p>
      </Sheet.Header>

      <div class="flex-1 overflow-y-auto px-6 py-2 space-y-6 custom-scrollbar">
        <!-- Status Badge -->
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

        <!-- Employee Info -->
        <div class="space-y-3">
          <h4 class="text-[0.8rem] font-semibold text-slate-700 uppercase tracking-wider">Employé</h4>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm font-medium text-slate-500">Nom</div>
              <p class="text-sm text-slate-900">{payslip.employeeName}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Département</div>
              <p class="text-sm text-slate-900">{payslip.department}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Période</div>
              <p class="text-sm text-slate-900">{payslip.period}</p>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Salaire de base</div>
              <p class="text-sm text-slate-900">{formatCurrency(payslip.baseSalary)}</p>
            </div>
          </div>
        </div>

        <Separator />

        <!-- Earnings -->
        <div class="space-y-3">
          <h4 class="text-sm font-semibold text-emerald-700 uppercase tracking-wider flex items-center gap-2">
            <AppIcon name="plus-circle" size={15} class="text-emerald-500" />
            Gains
          </h4>
          <div class="space-y-2">
            {#each earnings as line}
              <div class="flex items-center justify-between py-1">
                <span class="text-sm text-slate-700">{line.label}</span>
                <span class="text-sm font-medium text-slate-900">+{formatCurrency(line.amount)}</span>
              </div>
            {/each}
          </div>
        </div>

        <!-- Deductions -->
        <div class="space-y-3">
          <h4 class="text-sm font-semibold text-rose-700 uppercase tracking-wider flex items-center gap-2">
            <AppIcon name="minus-circle" size={15} class="text-rose-500" />
            Retenues
          </h4>
          <div class="space-y-2">
            {#each deductions as line}
              <div class="flex items-center justify-between py-1">
                <span class="text-sm text-slate-700">{line.label}</span>
                <span class="text-sm font-medium text-rose-600">-{formatCurrency(line.amount)}</span>
              </div>
            {/each}
          </div>
        </div>

        <Separator />

        <!-- Totals -->
        <div class="space-y-3">
          <div class="flex items-center justify-between py-1">
            <span class="text-sm font-medium text-slate-700">Salaire brut</span>
            <span class="text-sm font-semibold text-slate-900">{formatCurrency(payslip.grossPay)}</span>
          </div>
          <div class="flex items-center justify-between py-1">
            <span class="text-sm font-medium text-slate-700">Salaire net</span>
            <span class="text-sm font-bold text-emerald-600">{formatCurrency(payslip.netPay)}</span>
          </div>
        </div>
      </div>

      <!-- Footer -->
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

