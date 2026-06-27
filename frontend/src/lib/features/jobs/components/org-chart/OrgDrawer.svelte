<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import * as Collapsible from "@/components/ui/collapsible";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as Avatar from "@/components/ui/avatar";
  import { Badge } from "@/components/ui/badge";
  import { goto } from "$app/navigation";
  import { jobsStore } from "../../stores/jobs.svelte";
  import { useEmployeesByOrgUnitQuery } from "@/features/employees/queries/employeeQueries";
  import { usePositionsByOrgUnitQuery } from "@/features/jobs/queries/orgQueries";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { formatEmployeeName } from "@/utilities/common/employee.utils";
  import { slide } from "svelte/transition";
  import { cn } from "@/utilities/common/css";
  import EmployeeAssignmentSheet from "./sheets/EmployeeAssignmentSheet.svelte";
  import type { OrgUnit } from "../../types/org.types";
  import type { NodeType } from "../../types/types";
  import { SENIORITY_LABELS } from "../../types/types";
  import { useQueryClient } from "@tanstack/svelte-query";

  
  const slideParams = { duration: 250 };

  let {
    open = $bindable(false),
    orgUnit
  } = $props<{
    open: boolean,
    orgUnit: OrgUnit | null
  }>();

  let isAssignmentSheetOpen = $state(false);

  // $state intermédiaire pour tracker l'ID
  let orgUnitId = $state<string | null>(null);

  $effect(() => {
    orgUnitId = orgUnit?.id ?? null;
  });

  // Version fraîche depuis le store (se met à jour automatiquement après mutation)
  const freshOrgUnit = $derived(
    orgUnitId ? jobsStore.getOrgUnitById(orgUnitId) ?? orgUnit : orgUnit
  );

  // Manager - utilise freshOrgUnit pour réactivité
  const managerName = $derived(formatEmployeeName(freshOrgUnit?.manager ?? null));
  const managerAvatarUrl = $derived(freshOrgUnit?.manager?.photo || '');
  const managerExists = $derived(!!freshOrgUnit?.manager);

  // Adjoint - utilise freshOrgUnit pour réactivité
  const affointName = $derived(formatEmployeeName(freshOrgUnit?.affoint ?? null));
  const affointAvatarUrl = $derived(freshOrgUnit?.affoint?.photo || '');
  const affointExists = $derived(!!freshOrgUnit?.affoint);

  // Requêtes pour charger toutes les données de l'unité (avec grande pagination)
  // Recréer les queries chaque fois que orgUnitId change pour forcer le recalcul du queryKey
  let positionsQuery = $state<any>(null);
  let employeesQuery = $state<any>(null);

  $effect(() => {
    if (orgUnitId) {
      positionsQuery = usePositionsByOrgUnitQuery(() => orgUnitId);
      employeesQuery = useEmployeesByOrgUnitQuery(() => orgUnitId);
    } else {
      positionsQuery = null;
      employeesQuery = null;
    }
  });

  // Membres depuis la query (charge tous les employés de l'unité)
  const members = $derived.by(() => $employeesQuery?.data ?? []);

  // Positions depuis la query (charge toutes les positions, pas seulement la page courante)
  const relatedPositions = $derived.by(() => $positionsQuery?.data ?? []);

  const parentUnit = $derived(
    orgUnit?.parentId ? jobsStore.getOrgUnitById(orgUnit.parentId) : null
  );

  const childUnits = $derived(
    orgUnit ? jobsStore.getChildOrgUnits(orgUnit.id) : []
  );

  let expandedStats = $state(true);
  let expandedHierarchy = $state(true);
  let expandedMembers = $state(true);
  let expandedPositions = $state(true);

  // Seniority color mapping (clés = enum values du backend)
  const seniorityColorMap: Record<string, string> = {
    'TRAINEE': 'bg-slate-100 text-slate-700 border-slate-200',
    'APPRENTICE': 'bg-slate-100 text-slate-700 border-slate-200',
    'JUNIOR': 'bg-green-100 text-green-700 border-green-200',
    'INTERMEDIATE': 'bg-blue-100 text-blue-700 border-blue-200',
    'SENIOR': 'bg-purple-100 text-purple-700 border-purple-200',
    'LEAD': 'bg-amber-100 text-amber-700 border-amber-200',
    'MANAGER': 'bg-amber-100 text-amber-700 border-amber-200',
    'DIRECTOR': 'bg-rose-100 text-rose-700 border-rose-200',
    'EXECUTIVE': 'bg-rose-100 text-rose-700 border-rose-200'
  };

  // Type badge config
  const nodeTypeConfig = $derived.by(() => {
    const type = (orgUnit?.type as NodeType) || 'DEPARTMENT';
    const config: Record<NodeType, { label: string; icon: string; colorClass: string }> = {
      'DEPARTMENT': { label: 'Département', icon: 'business', colorClass: 'bg-blue-100 text-blue-700 border-blue-200' },
      'DIVISION': { label: 'Division', icon: 'corporate_fare', colorClass: 'bg-purple-100 text-purple-700 border-purple-200' },
      'TEAM': { label: 'Équipe', icon: 'team', colorClass: 'bg-orange-100 text-orange-700 border-orange-200' },
      'FUNCTION': { label: 'Fonction', icon: 'settings', colorClass: 'bg-slate-100 text-slate-700 border-slate-200' },
      'BRANCH': { label: 'Succursale', icon: 'store', colorClass: 'bg-green-100 text-green-700 border-green-200' },
      'PROJECT': { label: 'Projet', icon: 'folder', colorClass: 'bg-pink-100 text-pink-700 border-pink-200' }
    };
    return config[type] || config['DEPARTMENT'];
  });

</script>


{#snippet StatsSection()}
  <Collapsible.Root bind:open={expandedStats}>
    <Collapsible.Trigger class="group flex items-center gap-2 w-full px-3 py-2 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100">
      <AppIcon name="chevron-down" size={16} class="text-slate-400 transition-transform duration-200 {expandedStats ? '' : '-rotate-90'}" />
      <span class="text-[0.85rem] text-slate-500 uppercase font-bold">Informations</span>
    </Collapsible.Trigger>
    {#if expandedStats}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pl-8 pr-4 py-3 space-y-2">

          <!-- Effectif -->
          <div class="flex items-center justify-between py-1">
            <span class="text-[0.875rem] text-slate-600 font-medium">Effectif actuel</span>
            <span class="text-[0.875rem] text-slate-900">{orgUnit?.employeeCount ?? 0} / {orgUnit?.authorizedHeadcount ?? 0}</span>
          </div>

          <!-- Responsable -->
          <div class="flex items-center justify-between py-1">
            <span class="text-[0.875rem] text-slate-600 font-medium">Responsable</span>
            {#if managerExists}
              {@const managerPalette = getAvatarPalette(managerName)}
              <div class="flex items-center gap-2">
                <Avatar.Root class="h-7 w-7 border border-slate-200 rounded-full shrink-0">
                  <Avatar.Image src={managerAvatarUrl} alt={managerName} />
                  <Avatar.Fallback class={cn("text-[0.82rem] font-medium", managerPalette.bg, managerPalette.text)}>
                    {getInitials(...managerName.split(' '))}
                  </Avatar.Fallback>
                </Avatar.Root>
                <span class="text-[0.86rem] text-slate-700 truncate">{managerName}</span>
              </div>
            {:else}
              <span class="text-[0.83rem] text-slate-400 pl-4 flex items-center justify-center gap-1">
                <AppIcon name="circle-x" size={20} />
                Non assigné
              </span>
            {/if}
          </div>

          <!-- Adjoint -->
          <div class="flex items-center justify-between py-1">
            <span class="text-[0.875rem] text-slate-600 font-medium">Adjoint</span>
            {#if affointExists}
              {@const affointPalette = getAvatarPalette(affointName)}
              <div class="flex items-center gap-2">
                <Avatar.Root class="h-7 w-7 border border-slate-200 rounded-full shrink-0">
                  <Avatar.Image src={affointAvatarUrl} alt={affointName} />
                  <Avatar.Fallback class={cn("text-[0.82rem] font-medium", affointPalette.bg, affointPalette.text)}>
                    {getInitials(...affointName.split(' '))}
                  </Avatar.Fallback>
                </Avatar.Root>
                <span class="text-[0.86rem] text-slate-700 truncate">{affointName}</span>
              </div>
            {:else}
              <span class="text-[0.83rem] text-slate-400 pl-4 flex items-center justify-center gap-1">
                <AppIcon name="circle-x" size={20} />
                Non assigné
              </span>
            {/if}
          </div>
          
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet HierarchySection()}
  <Collapsible.Root bind:open={expandedHierarchy}>
    <Collapsible.Trigger class="group flex items-center gap-2 w-full px-3 py-2 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100">
      <AppIcon name="chevron-down" size={16} class="text-slate-400 transition-transform duration-200 {expandedHierarchy ? '' : '-rotate-90'}" />
      <span class="text-[0.85rem] text-slate-500 uppercase font-bold">Hiérarchie</span>
    </Collapsible.Trigger>
    {#if expandedHierarchy}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pl-8 pr-4 py-3 space-y-0">
          <!-- Unité parente -->
          <div class="flex items-center justify-between py-2 border-b border-slate-100">
            <span class="text-[0.875rem] text-slate-600 font-medium">Unité parente</span>
            <span class="text-[0.875rem] font-medium text-slate-900 truncate">{parentUnit?.name ?? 'Racine'}</span>
          </div>

          <!-- Sous-unités avec mini-arbre -->
          <div class="py-2">
            <div class="flex items-center justify-between mb-2">
              <span class="text-[0.875rem] text-slate-600 font-medium">Sous-unités</span>
              <span class="text-[0.875rem] font-medium text-slate-900">{childUnits.length}</span>
            </div>
            {#if childUnits.length > 0}
              <div class="pl-4 space-y-1">
                {#each childUnits as child, i}
                  <div class="flex items-center gap-2">
                    <span class="text-slate-300 text-[0.875rem]">
                      {i === childUnits.length - 1 ? '└─' : '├─'}
                    </span>
                    <span class="text-slate-700 truncate text-[0.875rem]">{child.name}</span>
                  </div>
                {/each}
              </div>
            {:else}
              <span class="text-[0.875rem] text-slate-400 pl-4 flex items-center justify-center gap-1">
                <AppIcon name="circle-x" size={20} />
                Aucune sous-unité
              </span>
            {/if}
          </div>
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet MembersSection()}
  <Collapsible.Root bind:open={expandedMembers}>
    <Collapsible.Trigger class="group flex items-center gap-2 w-full px-3 py-2 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100">
      <AppIcon name="chevron-down" size={16} class="text-slate-400 transition-transform duration-200 {expandedMembers ? '' : '-rotate-90'}" />
      <div class="flex items-center justify-between flex-1">
        <div class="flex items-center gap-2">
          <span class="text-[0.85rem] text-slate-500 uppercase font-bold">Membres</span>
          <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-indigo-50 text-indigo-600 text-[0.75rem] font-medium">
            {members.length}
          </span>
        </div>
        <Button
          variant="default"
          size="sm"
          class="h-7 px-2 text-[0.875rem]"
          onclick={(e) => { e.stopPropagation(); isAssignmentSheetOpen = true; }}
        >
          <AppIcon name="settings" size={17} class="mr-1" />
          Gérer
        </Button>
      </div>
    </Collapsible.Trigger>
    {#if expandedMembers}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pl-8 pr-4 py-3">
          {#if members.length > 0}
            <!-- Liste détaillée avec séparateurs -->
            <div class="divide-y divide-slate-100">
              {#each members as member, i}
                {@const palette = getAvatarPalette(member.name)}
                <div class="flex items-center gap-3 py-2.5">
                  <Avatar.Root class="h-10 w-10 border border-slate-200 rounded-full shrink-0">
                    <Avatar.Image src={member.avatarUrl} alt={member.name} />
                    <Avatar.Fallback class={cn("text-[0.85rem] font-medium", palette?.bg, palette?.text)}>
                      {getInitials(...member.name.split(' '))}
                    </Avatar.Fallback>
                  </Avatar.Root>
                  <div class="flex flex-col min-w-0 flex-1">
                    <span class="text-[0.875rem] font-medium text-slate-900 truncate">{member.name}</span>
                    <span class="text-[0.85rem] text-slate-500 truncate">{member.jobTitle}</span>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="py-6 text-center">
              <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
                <AppIcon name="users" size={24} class="text-slate-400" strokeWidth={1} />
              </div>
              <p class="text-[0.875rem] text-slate-600 mb-3">Aucun membre assigné</p>
              <Button
                variant="default"
                size="sm"
                class="h-7 px-3 text-[0.875rem]"
                onclick={() => isAssignmentSheetOpen = true}
              >
                <AppIcon name="plus" size={17} class="mr-1.5" />
                Affecter un membre
              </Button>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


{#snippet PositionsSection()}
  <Collapsible.Root bind:open={expandedPositions}>
    <Collapsible.Trigger class="group flex items-center gap-2 w-full px-3 py-2 hover:bg-slate-50 transition-colors cursor-pointer border-b border-slate-100">
      <AppIcon name="chevron-down" size={16} class="text-slate-400 transition-transform duration-200 {expandedPositions ? '' : '-rotate-90'}" />
      <div class="flex items-center gap-2">
        <span class="text-[0.85rem] text-slate-500 uppercase font-bold">Postes</span>
        <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-emerald-50 text-emerald-600 text-[0.75rem] font-medium">
          {relatedPositions.length}
        </span>
      </div>
      <button
        onclick={(e) => { e.stopPropagation(); goto('/jobs/careers'); }}
        class="ml-auto mr-1 flex items-center gap-1 text-[0.82rem] text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 px-2 py-0.5 rounded-full transition-colors cursor-pointer"
        title="Voir tous les postes"
      >
        Aller aux postes
        <AppIcon name="arrow-up-right" size={14} />
      </button>
    </Collapsible.Trigger>
    {#if expandedPositions}
      <div class="overflow-hidden" transition:slide={slideParams}>
        <div class="pl-8 pr-4 py-3">
          {#if relatedPositions.length > 0}
            <div class="divide-y divide-slate-100">
              {#each relatedPositions as pos}
                {@const seniorityColor = seniorityColorMap[pos.level] ?? 'bg-slate-100 text-slate-700 border-slate-200'}
                {@const seniorityLabel = SENIORITY_LABELS[pos.level as keyof typeof SENIORITY_LABELS] || pos.level_display || pos.level}
                <div class="flex items-center justify-between py-2.5">
                  <span class="text-[0.875rem] font-medium text-slate-900 truncate">{pos.name}</span>
                  <Badge class={cn("px-2 py-0.5 rounded-full border text-[0.83rem] font-medium shrink-0 ml-2", seniorityColor)}>
                    {seniorityLabel}
                  </Badge>
                </div>
              {/each}
            </div>
          {:else}
            <div class="py-6 text-center">
              <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
                <AppIcon name="briefcase" size={24} class="text-slate-400" strokeWidth={1} />
              </div>
              <p class="text-[0.875rem] text-slate-600 mb-3">Aucune position définie</p>
              <Button
                variant="default"
                size="sm"
                class="h-7 px-3 text-[0.875rem]"
                onclick={() => goto("/jobs/careers")}
              >
                <AppIcon name="plus" size={17} class="mr-1.5" />
                Ajouter un poste
              </Button>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </Collapsible.Root>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    {#if orgUnit}
      <!-- Header -->
      <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 space-y-3">
            <!-- Badge type + Nom -->
            <div class="flex flex-col items-start gap-1.5">
              <Sheet.Title class="text-[1rem] font-semibold text-slate-900">{orgUnit.name}</Sheet.Title>
              <Badge class={cn("px-2.5 py-0 rounded-full border font-medium text-[0.82rem]", nodeTypeConfig.colorClass)}>
                <AppIcon name={nodeTypeConfig.icon} size={15} class="mr-1.5" />
                {nodeTypeConfig.label}
              </Badge>
            </div>
          </div>
        </div>
      </Sheet.Header>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto px-4 pt-0 py-4 space-y-4 custom-scrollbar">

        {@render StatsSection()}
        {@render HierarchySection()}
        {@render MembersSection()}
        {@render PositionsSection()}

      </div>

      <!-- Footer -->
      <Sheet.Footer class="px-6 py-2.5 border-t border-slate-200 bg-slate-50">
        <Sheet.Close class="w-full cursor-pointer">
          <Button variant="outline" class="w-full h-9 text-[0.85rem] border-slate-200 hover:bg-slate-100">
            <AppIcon name="x" class="text-slate-400" size={16} />
            Fermer
          </Button>
        </Sheet.Close>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>


<EmployeeAssignmentSheet bind:open={isAssignmentSheetOpen} orgUnit={freshOrgUnit} {members} />


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>

