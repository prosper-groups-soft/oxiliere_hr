<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { LEAVE_TYPE_OPTIONS, LEAVE_STATUS_OPTIONS } from "../../../constants/leaves";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";

  let { onAdd, filterState, requests = [] } = $props<{ onAdd: () => void; filterState: any; requests?: any[] }>();

  const orgUnits = $derived([...new Set((requests ?? []).map((r: any) => r.orgUnit).filter(Boolean))].map(v => ({ value: v, label: v })));

  const filterDefs = $derived([
    { key: 'type', label: 'Type', icon: 'calendar', mode: 'multi' as const, options: LEAVE_TYPE_OPTIONS.map(o => ({ value: o.value, label: o.label })) },
    { key: 'status', label: 'Statut', icon: 'user-check', mode: 'multi' as const, options: LEAVE_STATUS_OPTIONS.map(o => ({ value: o.value, label: o.label })) },
    { key: 'orgUnit', label: 'Unité', icon: 'building-2', mode: 'multi' as const, options: orgUnits as any }
  ]);
  const sortDefs = { options: [{ value: 'createdAt', label: 'Date de création' }, { value: 'startDate', label: 'Date de début' }, { value: 'name', label: 'Nom (A-Z)' }, { value: 'days', label: 'Durée' }] };
</script>

<ActionBar>
  <FilterMenu {filterDefs} {filterState} />
  <SortMenu {sortDefs} {filterState} />
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} />Nouvelle demande</Button>
</ActionBar>
