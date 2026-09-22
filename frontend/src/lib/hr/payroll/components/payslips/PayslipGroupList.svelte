<script lang="ts">
  import { type Payslip } from "@/hr/payroll/types/types";
  import EmployeePayslip from "./views/EmployeePayslip.svelte";

  type PayslipGroup = {
    period: string;
    label: string;
    payslips: Payslip[];
    count: number;
    totalNet: number;
  };

  let { groups, onSelect }: { groups: PayslipGroup[]; onSelect: (payslipId: string) => void } = $props();

  function viewPayslipDetail(payslipId: string) {
    onSelect(payslipId);
  }
</script>



<div class="bg-white overflow-hidden">
  <!-- Column Headers -->
  <div class="sticky top-0 z-10 flex items-center h-9! px-6 bg-white border-b border-slate-100">
    <span class="w-[30%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
    <span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Unité</span>
    <span class="w-[22%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-2">Montant (net)</span>
    <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-center">Présence</span>
    <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Statut</span>
    <span class="w-[8%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Actions</span>
  </div>
  <div class="divide-y divide-slate-100">
    {#each groups as group (group.period)}
      {#each group.payslips as payslip (payslip.id)}
        <EmployeePayslip {payslip} onClick={viewPayslipDetail} />
      {/each}
    {/each}
  </div>
</div>

