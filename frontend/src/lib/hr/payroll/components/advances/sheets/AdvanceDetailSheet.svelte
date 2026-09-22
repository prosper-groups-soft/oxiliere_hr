<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { ADVANCE_STATUS_LABELS, ADVANCE_STATUS_COLORS, ADVANCE_RISK_LABELS, type Advance } from "../../../types/types";


  /** Normalise l'info employé (objet enrichi ou UUID legacy) pour garder la rétro-compatibilité */
  const employeeInfo = $derived.by(() => {
    if (!advance) return null;
    const emp = advance.employee;
    if (emp && typeof emp === 'object' && 'id' in emp) return emp;
    return null;
  });

  let {
    advance = null as Advance | null,
    open = $bindable(false),
  }: {
    advance: Advance | null;
    open: boolean;
  } = $props();

  function getRiskColor(risk: Advance['risk_level']) {
    switch (risk) {
      case 'LOW': return 'text-emerald-700 bg-emerald-50 border-emerald-200';
      case 'MEDIUM': return 'text-amber-700 bg-amber-50 border-amber-200';
      case 'HIGH': return 'text-rose-700 bg-rose-50 border-rose-200';
    }
  }

  function getRiskIcon(risk: Advance['risk_level']) {
    switch (risk) {
      case 'HIGH': return 'alert-circle';
      case 'MEDIUM': return 'alert-triangle';
      case 'LOW': return 'shield-check';
    }
  }

  /** Formate un montant dans la devise de l'avance (CDF par défaut) */
  function fmtMoney(v: number): string {
    return (v || 0).toLocaleString('fr-FR', { maximumFractionDigits: 0 });
  }

  const displayCurrency = $derived(advance?.currency || 'CDF');

  const displayRequestedDate = $derived(
    advance?.requested_date
      ? new Date(advance.requested_date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
      : '-'
  );

  const isRepaying = $derived(
    !!advance && (advance.status === 'APPROVED' || advance.status === 'ACTIVE' || advance.status === 'CLOSED')
  );

  /** Génère un plan prévisionnel de remboursement sur la durée calculée */
  const repaymentSchedule = $derived.by(() => {
    if (!advance) return [];

    const total = advance.amount;
    const monthly = Math.max(1, Math.ceil(total * (advance.repayment_percentage / 100)));
    const duration = Math.max(1, Math.ceil(total / monthly));
    const paidCount = Math.floor((total - advance.remaining_balance) / monthly);

    const schedule = [];
    let currentBalance = total;

    const baseDate = new Date(advance.requested_date || Date.now());

    for (let i = 1; i <= duration; i++) {
      const lineAmount = Math.min(monthly, currentBalance);
      currentBalance = Math.max(0, currentBalance - lineAmount);
      const isPaid = i <= paidCount || advance.status === 'CLOSED';

      // Mois suivant
      const scheduleDate = new Date(baseDate);
      scheduleDate.setMonth(baseDate.getMonth() + (i - 1));
      const periodLabel = scheduleDate.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });

      schedule.push({
        index: i,
        periodLabel: periodLabel.charAt(0).toUpperCase() + periodLabel.slice(1),
        amount: lineAmount,
        remainingAfter: currentBalance,
        status: isPaid ? ('paid' as const) : ('scheduled' as const)
      });
    }

    return schedule;
  });

  const progressPercentage = $derived.by(() => {
    if (!advance || advance.amount <= 0) return 0;
    return Math.round(((advance.amount - advance.remaining_balance) / advance.amount) * 100);
  });
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
    {#if advance}
      <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/60 flex flex-row items-center">
        <Sheet.Title class="text-base font-bold text-slate-900 text-left">
          Détail de l'avance
        </Sheet.Title>
      </Sheet.Header>

      <div class="flex-1 overflow-y-auto p-5 space-y-0.5 custom-scrollbar bg-slate-50/40">

        <!-- Statut -->
        <div class="flex items-center gap-2 pb-1">
          <span class="inline-flex items-center px-2.5 py-1 rounded-full text-sm font-semibold {ADVANCE_STATUS_COLORS[advance.status].bg} {ADVANCE_STATUS_COLORS[advance.status].text}">
            {ADVANCE_STATUS_LABELS[advance.status]}
          </span>
        </div>

        <!-- Récapitulatif financier -->
        <Card class="shadow-none py-4">
          <CardHeader>
            <CardTitle class="flex items-center gap-2 text-[0.98rem]">
              <AppIcon name="wallet" size={18} class="text-slate-500" />
              Avance
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-sm font-medium text-slate-500">Montant total</div>
                <p class="text-lg font-bold text-slate-900 mt-1">{fmtMoney(advance.amount)} {displayCurrency}</p>
              </div>
              <div>
                <div class="text-sm font-medium text-slate-500">Prélèvement mensuel</div>
                <p class="text-sm text-slate-900 mt-1">
                  {#if isRepaying}
                    {advance.repayment_percentage}% du salaire / mois
                  {:else}
                    <span class="text-slate-400 text-sm">Défini à l'approbation</span>
                  {/if}
                </p>
              </div>
              <div>
                <div class="text-sm font-medium text-slate-500">Solde restant</div>
                <p class="text-sm text-slate-900 mt-1">{fmtMoney(advance.remaining_balance)} {displayCurrency}</p>
              </div>
              <div>
                <div class="text-sm font-medium text-slate-500">Risque</div>
                <div class="mt-1">
                  <span class={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-sm font-medium border", getRiskColor(advance.risk_level))}>
                    <AppIcon name={getRiskIcon(advance.risk_level)} size={12} />
                    {ADVANCE_RISK_LABELS[advance.risk_level]}
                  </span>
                </div>
              </div>
            </div>

            {#if isRepaying}
              <div class="pt-4 border-t border-slate-100">
                <div class="flex justify-between items-center">
                  <div class="text-sm font-medium text-slate-500">Progression du remboursement</div>
                  <div class="text-sm font-bold text-slate-900">{progressPercentage} %</div>
                </div>
                <div class="h-2 bg-slate-200 rounded-full overflow-hidden mt-2">
                  <div class="h-full bg-emerald-500 rounded-full transition-all duration-300" style="width: {progressPercentage}%"></div>
                </div>
                <div class="flex justify-between mt-2">
                  <span class="text-sm text-slate-500">Remboursé : {fmtMoney(advance.amount - advance.remaining_balance)} {displayCurrency}</span>
                  <span class="text-sm font-semibold text-slate-700">Reste : {fmtMoney(advance.remaining_balance)} {displayCurrency}</span>
                </div>
              </div>
            {/if}
          </CardContent>
        </Card>

        <!-- Employé -->
        <Card class="shadow-none py-4">
          <CardHeader>
            <CardTitle class="flex items-center gap-2 text-[0.98rem]">
              <AppIcon name="user" size={18} class="text-slate-500" />
              Employé
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="flex items-center gap-3 min-w-0">
              {#if advance}
                {@const empFullName = advance.employee_name || ''}
                {@const empPalette = getAvatarPalette(empFullName)}
                <Avatar class="h-11 w-11 rounded-full border border-slate-200 shrink-0">
                  {#if employeeInfo?.avatar_url}
                    <AvatarImage src={getMediaUrl(employeeInfo.avatar_url)} alt={empFullName} class="object-cover" />
                  {/if}
                  <AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
                    {employeeInfo && employeeInfo.last_name
                      ? getInitials(employeeInfo.last_name || '', employeeInfo.middle_name || '', employeeInfo.first_name || '')
                      : getInitials(empFullName)}
                  </AvatarFallback>
                </Avatar>
              {/if}
              <div class="min-w-0">
                <h3 class="text-base font-bold text-slate-900 truncate">{advance.employee_name}</h3>
                <div class="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-1">
                  {#if employeeInfo?.job_title}
                    <span class="text-sm font-medium text-slate-600 flex items-center gap-1">
                      <AppIcon name="briefcase" size={11} class="text-slate-400" />
                      {employeeInfo.job_title}
                    </span>
                  {/if}
                  {#if employeeInfo?.org_unit}
                    <span class="text-sm font-medium text-slate-500 bg-blue-50 border border-blue-100 rounded px-1.5 py-0.5">
                      {employeeInfo.org_unit}
                    </span>
                  {/if}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Demande -->
        <Card class="shadow-none py-4">
          <CardHeader>
            <CardTitle class="flex items-center gap-2 text-[0.98rem]">
              <AppIcon name="file-text" size={18} class="text-slate-500" />
              Demande
            </CardTitle>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-sm font-medium text-slate-500">Date de demande</div>
                <p class="text-sm text-slate-900 mt-1">{displayRequestedDate}</p>
              </div>
              <div>
                <div class="text-sm font-medium text-slate-500">Devise</div>
                <p class="text-sm text-slate-900 mt-1">{displayCurrency}</p>
              </div>
            </div>
            <div>
              <div class="text-sm font-medium text-slate-500">Motif de la demande</div>
              <p class="text-sm text-slate-900 mt-1 leading-relaxed">
                {advance.reason || 'Pas de motif renseigné'}
              </p>
            </div>
            {#if advance.rejection_reason}
              <div class="rounded-lg border border-rose-200 bg-rose-50 p-3">
                <div class="text-sm font-medium text-rose-700">Motif du rejet</div>
                <p class="text-sm text-rose-900 mt-1">{advance.rejection_reason}</p>
              </div>
            {/if}
          </CardContent>
        </Card>

        <!-- Plan prévisionnel de remboursement -->
        <Card class="shadow-none py-4">
          <CardHeader>
            <CardTitle class="flex items-center gap-2 text-[0.98rem]">
              <AppIcon name="calendar" size={18} class="text-slate-500" />
              Plan prévisionnel de remboursement
              <span class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-[0.85rem] font-semibold bg-slate-100 text-slate-600">
                {repaymentSchedule.length} échéances
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {#if isRepaying && repaymentSchedule.length > 0}
              <div class="overflow-hidden rounded-lg border border-slate-200">
                <table class="w-full">
                  <thead class="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                    <tr>
                      <th class="text-sm px-3 py-2 text-left">N°</th>
                      <th class="text-sm px-3 py-2 text-left">Échéance</th>
                      <th class="text-sm px-3 py-2 text-right">Mensualité</th>
                      <th class="text-sm px-3 py-2 text-right">Solde restant</th>
                      <th class="text-sm px-3 py-2 text-center">Statut</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100">
                    {#each repaymentSchedule as item}
                      <tr class="hover:bg-slate-50/50">
                        <td class="text-sm px-3 py-2 font-medium text-slate-600">#{item.index}</td>
                        <td class="text-sm px-3 py-2 font-semibold text-slate-800">{item.periodLabel}</td>
                        <td class="text-sm px-3 py-2 text-right tabular-nums text-slate-700">{fmtMoney(item.amount)} {displayCurrency}</td>
                        <td class="text-sm px-3 py-2 text-right tabular-nums text-slate-500">{fmtMoney(item.remainingAfter)} {displayCurrency}</td>
                        <td class="text-sm px-3 py-2 text-center">
                          {#if item.status === 'paid'}
                            <Badge class="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[0.85rem] px-2 py-0.5">
                              <AppIcon name="check-circle" size={12} class="mr-1" /> Déduit
                            </Badge>
                          {:else}
                            <Badge variant="outline" class="bg-slate-50 text-slate-600 border-slate-200 text-[0.85rem] px-2 py-0.5">
                              Prévisionnel
                            </Badge>
                          {/if}
                        </td>
                      </tr>
                    {/each}
                  </tbody>
                </table>
              </div>
            {:else}
              <p class="text-sm text-slate-400">
                Le plan de remboursement sera disponible après l'approbation de la demande.
              </p>
            {/if}
          </CardContent>
        </Card>
      </div>

      <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-between bg-slate-50/60">
        <Sheet.Close class="w-full">
          <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Fermer
          </Button>
        </Sheet.Close>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>
