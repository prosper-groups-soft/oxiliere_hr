<script lang="ts">
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Badge } from '@/components/ui/badge';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import EmployeePayslipItem from '../items/EmployeePayslipItem.svelte';
  import PayslipDetailSheet from '@/hr/modules/payroll/components/payslips/sheets/PayslipDetailSheet.svelte';
  import { get_api_base_origin } from '@/hr/utilities/http/urls';
  import { useEmployeePayslipsQuery, usePayslipDetailQuery } from '@/hr/modules/employees/queries/employeePayslipsQueries';


  let { employeeId } = $props<{ employeeId: string | number }>();

  let selectedPayslipId = $state<string | null>(null);
  let isPreviewOpen = $state(false);

  const idStr = $derived(String(employeeId ?? '').trim());

  const payslipsQuery = useEmployeePayslipsQuery(() => idStr);

  let qp = $state<any>({ data: undefined, isPending: true, isFetching: false, isError: false, error: null } as any);
  $effect(() => {
    const unsub = (payslipsQuery as any).subscribe((v: any) => { qp = v; });
    return () => unsub();
  });

  const payslips = $derived((qp as any)?.data?.results ?? []);
  const count = $derived((qp as any)?.data?.count ?? payslips.length);
  const isLoading = $derived((qp as any).isPending ?? true);
  const isError = $derived((qp as any).isError ?? false);

  function handlePreview(id: string) {
    selectedPayslipId = id;
    isPreviewOpen = true;
  }

  const detailQuery = usePayslipDetailQuery(
    () => selectedPayslipId,
    () => payslips.find((p: any) => String(p.id) === String(selectedPayslipId)) ?? null
  );
  
  let dq = $state<any>({ data: null } as any);
  
  $effect(() => {
    const unsub = (detailQuery as any).subscribe((v: any) => { dq = v; });
    return () => unsub();
  });
  
  const selectedPayslipFromList = $derived(payslips.find((p: any) => String(p.id) === String(selectedPayslipId)) ?? null);
  const selectedPayslip = $derived((dq as any).data ?? selectedPayslipFromList ?? null);

  function handleExportAllFiltered() {
    if (!payslips.length) return;
    const ids = payslips.map((p: any) => String(p.id)).join(',');
    const url = `${get_api_base_origin()}/api/payroll/payslips/export/zip/?ids=${encodeURIComponent(ids)}`;
    window.open(url, '_blank');
  }
</script>


<Card class="rounded-xl border-slate-200 bg-white overflow-hidden flex flex-col border-0 shadow-none mt-1.5">
  <CardHeader class="pb-0! shrink-0 border-0 shadow-none">
    <div class="flex items-center justify-between gap-3">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0">
          <AppIcon name="receipt" size={18} class="text-emerald-600" />
        </span>
        Bulletins de paie
        {#if !isLoading}
          <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-0 rounded-full font-bold text-[0.85rem] px-2.5 py-0 h-5">
            {count}
          </Badge>
        {/if}
      </CardTitle>

      {#if payslips.length > 1}
        <button
          onclick={handleExportAllFiltered}
          class="h-8 px-3.5 cursor-pointer bg-white border border-slate-200 rounded-full font-medium text-[0.85rem] text-slate-700 hover:border-emerald-200 hover:text-emerald-700 hover:bg-emerald-50/60 transition-all inline-flex items-center justify-center gap-1.5 shrink-0 shadow-fine"
        >
          <AppIcon name="download" size={16} />
          Exporter ZIP
        </button>
      {/if}
    </div>
    <p class="text-[0.85rem] text-slate-500 leading-snug mt-1">Historique des bulletins édités pour cet employé — lecture seule, export PDF disponible.</p>
  </CardHeader>

  <CardContent class="pt-2 pb-6 border-0 shadow-none">
    {#if isLoading}
      <div class="flex flex-col gap-2">
        {#each Array(3) as _}
          <div class="h-[72px] rounded-xl border border-slate-200 bg-slate-50 animate-pulse"></div>
        {/each}
      </div>
    {:else if isError}
      <div class="text-center py-6 border-2 border-dashed border-amber-200 rounded-xl bg-amber-50/40">
        <p class="text-[0.85rem] font-medium text-amber-700">Impossible de charger les bulletins.</p>
        <p class="text-[0.85rem] text-slate-500 mt-1">Réessayez ou vérifiez la paie.</p>
      </div>
    {:else if payslips.length === 0}
      <div class="flex items-center justify-center">
        <Empty
          title="Aucun bulletin de paie"
          description="Les bulletins apparaîtront ici après clôture de la paie."
          icon="receipt"
          iconSize={24}
          iconStrokeWidth={1.1}
          iconClass="text-emerald-500"
        />
      </div>
    {:else}
      <div class="flex flex-col gap-2">
        {#each payslips as p (p.id)}
          <EmployeePayslipItem payslip={p} onPreview={handlePreview} />
        {/each}
      </div>
      {#if count > payslips.length}
        <p class="text-[0.85rem] text-slate-400 text-center mt-3">
          {payslips.length} sur {count} affichés — utilisez la paie globale pour voir tout l'historique.
        </p>
      {/if}
    {/if}
  </CardContent>
</Card>


{#if selectedPayslipId}
  <PayslipDetailSheet payslip={selectedPayslip} bind:open={isPreviewOpen} />
{/if}

