<script lang="ts">
  import FilterMenu from '@/hr/actions/components/FilterMenu.svelte';
  import ActionBar from '@/hr/actions/components/ActionBar.svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { ADVANCE_RISK_LABELS, ADVANCE_STATUS_LABELS } from '@/hr/modules/payroll/types/types';
  import type { FilterDef } from '@/hr/actions/types';

  let { filterState, onAdd }: { filterState: any; onAdd: () => void } = $props();

  const filterDefs: FilterDef[] = [
    { key:'riskLevel', label:'Risque', icon:'shield-check', mode:'multi', options: Object.entries(ADVANCE_RISK_LABELS).map(([value,label])=>({value,label})) },
    { key:'status', label:'Statut', icon:'list-filter', mode:'multi', options: Object.entries(ADVANCE_STATUS_LABELS).map(([value,label])=>({value,label})) },
  ];
</script>

<ActionBar>
  <FilterMenu {filterDefs} {filterState} />
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} /> Nouvelle demande</Button>
</ActionBar>
