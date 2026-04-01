<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import * as Collapsible from "@/components/ui/collapsible";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { goto } from "$app/navigation";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { jobsStore } from "../../stores/jobs.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { slide } from "svelte/transition";
  import EmployeeAssignmentSheet from "./sheets/EmployeeAssignmentSheet.svelte";
  import type { Department } from "../../types/types";


  const slideParams = { duration: 250 };

  let {
    open = $bindable(false),
    department 
  } = $props<{
    open: boolean,
    department: Department | null
  }>();

  let isAssignmentSheetOpen = $state(false);

  const members = $derived(
    department 
      ? employeeStore.employees.filter(e => e.department === department.name || e.departmentId === department.id) 
      : []
  );

  const relatedPositions = $derived(
    department ? jobsStore.positions.filter(p => p.departmentId === department.id) : []
  );

  const parentDept = $derived(
    department?.parentId ? jobsStore.getDepartmentById(department.parentId) : null
  );

  const childDepts = $derived(
    department ? jobsStore.getChildDepartments(department.id) : []
  );

  let expandedStats = $state(true);
  let expandedHierarchy = $state(true);
  let expandedMembers = $state(true);
  let expandedPositions = $state(true);

</script>


{#snippet StatsSection()}
  <Collapsible.Root bind:open={expandedStats}>
    <Collapsible.Trigger class="group gap-1.5 flex items-center justify-start w-full px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors">
      <AppIcon name="chevron-down" size={16} class="text-slate-500 transition-transform duration-250 {expandedStats ? '' : '-rotate-90'}" />
      <span class="text-[0.78rem] text-medium text-slate-900 group-hover:text-indigo-600 font-medium uppercase transition-all">Statistiques</span>
    </Collapsible.Trigger>
    {#if expandedStats}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pt-2 pl-7 pr-4 grid grid-cols-2 gap-3">
          <div class="p-3 rounded-xl border border-slate-200 bg-linear-to-br from-slate-50 to-slate-100/50">
            <span class="block text-[0.65rem] font-medium text-slate-700 uppercase tracking-widest mb-1">Effectif</span>
            <span class="text-[1.1rem] font-black text-slate-900">{department.headcount}</span>
          </div>
          <div class="p-3 rounded-xl border border-slate-200 bg-linear-to-br from-slate-50 to-slate-100/50">
            <span class="block text-[0.65rem] font-medium text-slate-700 uppercase tracking-widest mb-1">Responsable</span>
            <span class="text-[0.85rem] font-bold text-slate-900 truncate block">{department.managerName || '—'}</span>
          </div>
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet HierarchySection()}
  <Collapsible.Root bind:open={expandedHierarchy}>
    <Collapsible.Trigger class="group gap-1.5 flex items-center justify-start w-full px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors">
      <AppIcon name="chevron-down" size={16} class="text-slate-500 transition-transform duration-250 {expandedHierarchy ? '' : '-rotate-90'}" />
      <span class="text-[0.78rem] text-medium text-slate-900 group-hover:text-indigo-600 uppercase font-medium transition-all">Hiérarchie</span>
    </Collapsible.Trigger>
    {#if expandedHierarchy}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pt-2 space-y-2 pl-7 pr-4">
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <div class="flex items-center gap-2 text-slate-700">
              <AppIcon name="arrow-up" size={14} />
              <span class="text-[0.82rem] font-medium">Parent</span>
            </div>
            <span class="text-[0.82rem] font-medium text-slate-900">
              {parentDept?.name ?? 'Aucun (racine)'}
            </span>
          </div>
          <div class="flex items-center justify-between py-2">
            <div class="flex items-center gap-2 text-slate-700">
              <AppIcon name="git-branch" size={14} />
              <span class="text-[0.82rem] font-medium">Sous-unités</span>
            </div>
            <span class="text-[0.82rem] font-bold text-slate-900">{childDepts.length}</span>
          </div>
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet MembersSection()}
  <Collapsible.Root bind:open={expandedMembers}>
    <Collapsible.Trigger class="group gap-1.5 flex items-center justify-start w-full px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors">
      <AppIcon name="chevron-down" size={16} class="text-slate-500 transition-transform duration-250 {expandedMembers ? '' : '-rotate-90'}" />
      <div class="flex items-center justify-between flex-1">
        <div class="flex items-center gap-2">
          <span class="text-[0.78rem] text-medium text-slate-900 group-hover:text-indigo-600 uppercase font-medium transition-all">Membres</span>
          <Badge variant="secondary" class="bg-indigo-100 rounded-full text-gray-800 font-bold text-[0.7rem]">{members.length}</Badge>
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          class="h-6 px-2 text-[0.65rem] font-bold text-indigo-600 border border-indigo-100 hover:bg-indigo-50"
          onclick={(e) => { e.stopPropagation(); isAssignmentSheetOpen = true; }}
        >
          Gérer
        </Button>
      </div>
    </Collapsible.Trigger>
    {#if expandedMembers}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pt-2 space-y-2 pl-7 pr-4">
          {#each members as member}
            <div class="flex items-center gap-3 p-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-all">
              <div class="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center overflow-hidden border border-slate-300">
                {#if member.avatarUrl}
                  <img src={member.avatarUrl} alt={member.name} class="w-full h-full object-cover" />
                {:else}
                  <AppIcon name="user" size={14} class="text-slate-600" />
                {/if}
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-[0.8rem] font-bold text-slate-900 truncate">{member.name}</span>
                <span class="text-[0.65rem] text-slate-600 truncate">{member.jobTitle}</span>
              </div>
            </div>
          {:else}
            <Empty
              title="Aucun membre"
              description="Aucun collaborateur n'est assigné à ce département."
              icon="users"
              iconSize={24}
              iconStrokeWidth={1.1}
              iconClass="text-primary"
              titleSize="0.85rem"
              descriptionSize="0.8rem"
            >
              <Button 
                variant="default" 
                class="h-7 text-[0.8rem]" 
                onclick={() => isAssignmentSheetOpen = true}
              >
                <AppIcon name="plus" size={15} />
                Affecter un collaborateur
              </Button>
            </Empty>
          {/each}
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet PositionsSection()}
  <Collapsible.Root bind:open={expandedPositions}>
    <Collapsible.Trigger class="group gap-1.5 flex items-center justify-start w-full px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors">
      <AppIcon name="chevron-down" size={16} class="text-slate-500 transition-transform duration-250 {expandedPositions ? '' : '-rotate-90'}" />
      <div class="flex items-center gap-2">
        <span class="text-[0.78rem] text-medium text-slate-900 group-hover:text-indigo-600 uppercase font-medium transition-all">
          Postes définis
        </span>
        <Badge variant="secondary" class="bg-indigo-100 rounded-full text-gray-800 font-bold text-[0.7rem]">
          {relatedPositions.length}
        </Badge>
      </div>
    </Collapsible.Trigger>
    {#if expandedPositions}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pt-2 space-y-1.5 pl-7 pr-4">
          {#each relatedPositions as pos}
            <div class="flex items-center justify-between p-3 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all cursor-pointer group">
              <div class="flex items-center gap-2.5">
                <AppIcon name="briefcase" size={15} class="text-slate-600" />
                <div>
                  <span class="block text-[0.82rem] font-bold text-slate-900">{pos.title}</span>
                  <span class="text-[0.7rem] text-slate-600">{pos.seniority}</span>
                </div>
              </div>
              <AppIcon name="chevron-right" size={14} class="text-slate-300 group-hover:text-slate-700 transition-colors" />
            </div>
          {:else}
            <Empty
              title="Aucun poste défini"
              description="Aucune fiche de poste n'est associée à ce département."
              icon="inbox"
              iconSize={24}
              iconStrokeWidth={1.1}
              iconClass="text-primary"
              titleSize="0.85rem"
              descriptionSize="0.8rem"
            >
              <Button 
                variant="default" 
                class="h-7 text-[0.8rem]" 
                onclick={() => goto("/jobs/careers")}
              >
                <AppIcon name="plus" size={17} strokeWidth={1.1} />
                Ajouter un poste
              </Button>
            </Empty>
          {/each}
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md flex flex-col h-full overflow-hidden p-0">
    {#if department}
      <!-- Header -->
      <Sheet.Header class="px-6 py-4 border-b border-slate-200 bg-slate-50/50 flex items-between justify-center bg-linear-to-r">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg bg-indigo-700 text-slate-50">
            <AppIcon name="network" size={22} />
          </div>
          <div>
            <Sheet.Title class="text-[1rem] font-black">{department.name}</Sheet.Title>
            <Sheet.Description class="text-[0.78rem] text-slate-600">{department.type}</Sheet.Description>
          </div>
        </div>
      </Sheet.Header>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto px-4 py-2 space-y-3 custom-scrollbar">

        {@render StatsSection()}

        {@render HierarchySection()}

        {@render MembersSection()}

        {@render PositionsSection()}

      </div>

      <!-- Footer -->
      <Sheet.Footer class="px-6 py-4 border-t border-slate-200 bg-slate-50/50 bg-linear-to-r">
        <Sheet.Close class="w-full cursor-pointer">
          <Button variant="outline" class="w-full shadow-fine h-9">
            Fermer
          </Button>
        </Sheet.Close>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>


<EmployeeAssignmentSheet bind:open={isAssignmentSheetOpen} {department} />


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>

