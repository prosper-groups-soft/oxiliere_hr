<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import type { WorkPolicy, PolicyAssignment } from "../../../../types/types";
  import type { Employee } from "@/hr/modules/employees/types/types";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import PolicyVisualizer from "../../elements/PolicyVisualizer.svelte";
  import { formatDate } from "date-fns";
  import { usePoliciesQuery } from "../../../../queries/attendanceQueries";
  import { backendToWorkPolicy } from "../../../../constants/attendance.helpers";

  
  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }
  

  let { 
    open = $bindable(false),
    employee = null
  } = $props<{ 
    open: boolean;
    employee: EmployeeWithAssignment | null;
  }>();

  const policiesQuery = usePoliciesQuery();

  // Resolve full WorkPolicy objects with pattern from the API query cache.
  // ShiftPolicyOut has 'details' not 'pattern' → convert with backendToWorkPolicy().
  // If the policy is not in the cache (fallback to incomplete object), trigger a refetch.
  const fullBasePolicy = $derived(
    employee?.basePolicy
      ? (() => {
          const found = ($policiesQuery.data ?? []).find(p => p.id === employee.basePolicy!.id);
          return found ? backendToWorkPolicy(found) : employee.basePolicy;
        })()
      : null
  );
  const fullOverridePolicy = $derived(
    employee?.overridePolicy
      ? (() => {
          const found = ($policiesQuery.data ?? []).find(p => p.id === employee.overridePolicy!.id);
          return found ? backendToWorkPolicy(found) : employee.overridePolicy;
        })()
      : null
  );

  // If either policy is not fully found in the cache, ensure we have fetched policies
  $effect(() => {
    const policies = $policiesQuery.data ?? [];
    const baseMissing = employee?.basePolicy && !policies.find(p => p.id === employee.basePolicy.id);
    const overrideMissing = employee?.overridePolicy && !policies.find(p => p.id === employee.overridePolicy.id);
    if ((baseMissing || overrideMissing) && !$policiesQuery.isFetching) {
      $policiesQuery.refetch();
    }
  });

</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0 bg-white font-sans border-l border-slate-200">
    
    <Sheet.Header class="px-6 py-2.5 border-b bg-white shrink-0">
      <Sheet.Title class="text-[1rem] font-semibold text-slate-700 leading-tight">
        Comparaison des plannings — <span class="text-slate-900 font-bold text-[0.9rem]">{employee?.name}</span>
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar bg-white" style="--scrollbar-size: 6px">
    
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-md bg-amber-50/50 border border-amber-100/50">
        <AppIcon name="zap" size={13} class="text-amber-500" />
        <span class="text-[0.79rem] font-medium text-amber-700">
          Remplacement actif : 
          {#if employee?.overrideAssignment?.endDate}
            <span class="font-bold text-[0.79rem]">jusqu'au {formatDate(new Date(employee.overrideAssignment.endDate), 'dd/MM/yyyy')}</span>
          {:else}
            <span class="text-amber-600/70 text-[0.79rem]">Durée indéterminée</span>
          {/if}
        </span>
      </div>

      {#if employee && employee.basePolicy}
        <!-- Simple Legend -->
        <div class="p-2 rounded-md border border-slate-100 bg-slate-50/30 flex items-center justify-between">
          <div class="flex items-center gap-2.5 mr-2">
            <div class="text-slate-300">
              <AppIcon name="info" size={18} />
            </div>
            <p class="text-[0.8rem] text-slate-500 font-medium tracking-tight">Comparaison : planning de base vs remplacement</p>
          </div>
          
          <div class="flex gap-5">
            <div class="flex flex-col items-start">
              <span class="text-[0.6rem] font-bold text-slate-300 uppercase tracking-widest leading-none mb-1">Base</span>
              <div class="text-[0.8rem] font-medium text-slate-600 leading-none">{employee.basePolicy.name}</div>
            </div>
            <div class="flex flex-col items-start">
              <span class="text-[0.6rem] font-bold text-primary/60 uppercase tracking-widest leading-none mb-1">Remplacement</span>
              <div class="text-[0.8rem] font-bold text-primary leading-none">{fullOverridePolicy?.name || 'Inconnu'}</div>
            </div>
          </div>
        </div>

        <!-- The Visualizer -->
        <PolicyVisualizer 
          policy={fullBasePolicy} 
          overlayPolicy={fullOverridePolicy} 
          showDetails={true}
        />
      {:else}
        <div class="flex flex-col items-center justify-center h-full text-slate-300 gap-3">
          <AppIcon name="alert-circle" size={40} strokeWidth={1} />
          <p class="text-[0.9rem] font-medium">Données de comparaison indisponibles</p>
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 shrink-0">
      <Sheet.Close class="w-full">
        <button class="w-full h-9.5 rounded-md bg-white border border-slate-200 text-[0.875rem] text-slate-700 hover:bg-slate-50 transition-all cursor-pointer shadow-fine flex justify-center items-center gap-2">
          <AppIcon name="x" size={17} class="text-slate-400" />
          Fermer
        </button>
      </Sheet.Close>
    </Sheet.Footer>

  </Sheet.Content>
</Sheet.Root>

