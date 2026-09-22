<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { useOrgUnitsQuery } from "@/hr/modules/jobs/queries/orgQueries";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";
  import { CONTRACT_TYPES } from "@/hr/modules/employees/constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/hr/modules/employees/constants/employeeStatus";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";

  let { onAdd, onToggleViewMode, filterState } = $props<{ onAdd: () => void; onToggleViewMode: () => void; filterState: any }>();

  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  const filterDefs = $derived([
    { key: 'orgUnit', label: 'Unité', icon: 'building-2', mode: 'multi' as const, options: orgUnits.map((u: any) => ({ value: u.id, label: u.name, icon: getOrgUnitIcon(u.type) })) },
    { key: 'status', label: 'Statut', icon: 'user-check', mode: 'multi' as const, options: Object.entries(EMPLOYEE_STATUS_CONFIG).map(([value, c]: any) => ({ value, label: c.label })) },
    { key: 'contractType', label: 'Contrat', icon: 'file-text', mode: 'multi' as const, options: CONTRACT_TYPES.map(o => ({ value: o.value, label: o.label })) },
    { key: 'location', label: 'Localité', icon: 'map-pin', mode: 'multi' as const, options: [] }
  ]);

  const sortDefs = { options: [{ value: 'name', label: 'Nom (A-Z)' }, { value: 'joinDate', label: 'Date d\'embauche' }, { value: 'status', label: 'Statut' }] };
</script>

<ActionBar>
  <FilterMenu {filterDefs} {filterState} />
  <SortMenu {sortDefs} {filterState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onToggleViewMode} variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100">
    {#if filterState.viewMode === 'list'}<AppIcon name="layout-grid" size={15} class="mr-1.5" />Grille{:else}<AppIcon name="list" size={15} class="mr-1.5" />Liste{/if}
  </Button>
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} />Onboarding</Button>
</ActionBar>
