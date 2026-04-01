<script lang="ts">
  import { type Payslip } from "@/features/payroll/types/types";
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


<div class="divide-y divide-slate-100 bg-white shadow-none overflow-hidden">
  {#each groups as group (group.period)}
    {#each group.payslips as payslip (payslip.id)}
      <EmployeePayslip {payslip} onClick={viewPayslipDetail} />
    {/each}
  {/each}
</div>

