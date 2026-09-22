<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import Empty from "@/hr/components/shared/containers/empty/Empty.svelte";
  import type { OrgUnit } from "../../types/org.types";
  import { jobsStore } from "../../stores/jobs.svelte";
  import { useOrgTreeQuery } from "../../queries/orgQueries";
  import { fade, fly } from "svelte/transition";
  import { 
    ERROR_MESSAGES, 
    getFriendlyErrorMessage 
  } from "@/hr/constants/errors";
  import OrgNode from "./elements/OrgNode.svelte";
  import OrgConnector from "./elements/OrgConnector.svelte";
  import OrgStructureSheet from "./sheets/OrgStructureSheet.svelte";
  

  let { onSelect } = $props<{ onSelect?: (orgUnit: OrgUnit) => void }>();

  // Charger les données depuis le backend
  const orgTreeQuery = useOrgTreeQuery();

  // Synchroniser avec le store
  $effect(() => {
    const data = $orgTreeQuery.data;
    if (data?.orgUnits) {
      jobsStore.setOrgUnits(data.orgUnits);
    }
  });

  // UI state
  let showStructureSheet = $state(false);
  let preselectedParentId = $state<string | null>(null);
  let editingOrgUnitId = $state<string | null>(null);

  // Zoom/Pan state
  let containerWidth = $state(0);
  let scale = $state(0.85);
  let translateX = $state(0);
  let translateY = $state(50);
  let isDragging = $state(false);
  let lastMousePos = { x: 0, y: 0 };

  const NODE_WIDTH = 300; // Augmenté pour accommoder manager + adjoint sans superposition
  const NODE_HEIGHT = 150; // Augmenté pour accommoder manager + adjoint
  const GAP_X = 90;
  const GAP_Y = 130;

  /**
   * This returns a map of orgUnitId -> { x, y, width } and the total width
   */
  let layoutData = $derived.by(() => {
    // Dépendance explicite pour forcer le recalcul quand orgUnits change
    const _orgUnits = jobsStore.orgUnits;
    const _selectedId = jobsStore.selectedOrgUnitId;

    const coords = new Map<string, { x: number, y: number, totalWidth: number }>();

    function calculateWidths(orgUnitId: string): number {
      const children = jobsStore.getChildOrgUnits(orgUnitId);
      if (children.length === 0) {
        return NODE_WIDTH;
      }
      
      let totalWidth = 0;
      children.forEach((child, i) => {
        totalWidth += calculateWidths(child.id);
        if (i < children.length - 1) totalWidth += GAP_X;
      });
      
      return Math.max(NODE_WIDTH, totalWidth);
    }

    function positionNodes(orgUnitId: string, startX: number, depth: number) {
      const children = jobsStore.getChildOrgUnits(orgUnitId);
      const totalWidth = calculateWidths(orgUnitId);
      
      const x = startX + (totalWidth - NODE_WIDTH) / 2;
      const y = depth * (NODE_HEIGHT + GAP_Y);
      
      coords.set(orgUnitId, { x, y, totalWidth });
      
      let currentX = startX;
      children.forEach(child => {
        const childWidth = calculateWidths(child.id);
        positionNodes(child.id, currentX, depth + 1);
        currentX += childWidth + GAP_X;
      });
    }

    function calculateChildWidth(id: string): number {
      const children = jobsStore.getChildOrgUnits(id);
      if (children.length === 0) return NODE_WIDTH;
      let w = 0;
      children.forEach((c, i) => {
        w += calculateChildWidth(c.id);
        if (i < children.length - 1) w += GAP_X;
      });
      return Math.max(NODE_WIDTH, w);
    }

    // Initialize layout for each root
    let offset = 0;
    jobsStore.rootOrgUnits.forEach((root, i) => {
      const rootWidth = calculateChildWidth(root.id);
      positionNodes(root.id, offset, 0);
      offset += rootWidth;
      if (i < jobsStore.rootOrgUnits.length - 1) offset += (GAP_X * 2);
    });

    return { coords, totalWidth: offset };
  });

  const layout = $derived(layoutData.coords);
  const totalWidth = $derived(layoutData.totalWidth);

  function resetView() {
    scale = 0.85;
    translateX = (containerWidth - totalWidth * scale) / 2;
    translateY = 50;
  }

  // Auto-center on first load or when data changes
  let isInitialized = $state(false);
  let isReady = $state(false);
  $effect(() => {
    if (containerWidth > 0 && totalWidth > 0 && !isInitialized) {
      resetView();
      isInitialized = true;
      // Small delay to allow the browser to apply the initial position before showing
      setTimeout(() => isReady = true, 50);
    }
  });

  // --- Interaction Handlers ---
  
  function handleWheel(e: WheelEvent) {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      scale = Math.min(Math.max(0.1, scale * delta), 3);
    } else {
      translateX -= e.deltaX;
      translateY -= e.deltaY;
    }
  }

  function handleMouseDown(e: MouseEvent) {
    if (e.button === 0) { // Left click
      isDragging = true;
      lastMousePos = { x: e.clientX, y: e.clientY };
    }
  }

  function handleMouseMove(e: MouseEvent) {
    if (isDragging) {
      translateX += e.clientX - lastMousePos.x;
      translateY += e.clientY - lastMousePos.y;
      lastMousePos = { x: e.clientX, y: e.clientY };
    }
  }

  function handleMouseUp() {
    isDragging = false;
  }

  function handleKeyDown(e: KeyboardEvent) {
    const step = 40;
    if (e.key === 'ArrowUp') translateY += step;
    if (e.key === 'ArrowDown') translateY -= step;
    if (e.key === 'ArrowLeft') translateX += step;
    if (e.key === 'ArrowRight') translateX -= step;
    if (e.key === '+') scale = Math.min(3, scale + 0.1);
    if (e.key === '-') scale = Math.max(0.1, scale - 0.1);
    if (e.key === 'r') resetView();
  }
</script>


<div
  role="button"
  aria-label="Espace de navigation de l'organigramme"
  tabindex="0"
  class="relative w-full h-full overflow-hidden bg-white cursor-grab active:cursor-grabbing select-none outline-none focus-visible:ring-2 focus-visible:ring-primary/20"
  style="
    background-image:
      linear-gradient(to right, rgba(0, 0, 0, 0.025) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(0, 0, 0, 0.025) 1px, transparent 1px);
    background-size: {50 * scale}px {50 * scale}px;
    background-position: {translateX}px {translateY}px;
  "
  bind:clientWidth={containerWidth}
  onwheel={handleWheel}
  onmousedown={handleMouseDown}
  onmousemove={handleMouseMove}
  onmouseup={handleMouseUp}
  onmouseleave={handleMouseUp}
  onkeydown={handleKeyDown}
>
  <!-- Loading state -->
  {#if $orgTreeQuery.isLoading && jobsStore.orgUnits.length === 0}
    <div class="absolute inset-0 flex justify-center items-center bg-white z-10" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement de l'organigramme" />
    </div>
  {/if}

  <!-- Error state -->
  {#if $orgTreeQuery.error && jobsStore.orgUnits.length === 0}
    <div class="absolute inset-0 flex justify-center items-center bg-white z-10" in:fade={{ duration: 200 }}>
      <Empty
        icon="alert-circle"
        title="Erreur de chargement"
        description={getFriendlyErrorMessage($orgTreeQuery.error) || ERROR_MESSAGES.NETWORK.UNKNOWN}
        iconClass="text-red-400"
        iconContainerClass="bg-red-50/30"
        iconSize={28}
        iconStrokeWidth={1.3}
      >
        <Button
          onclick={() => $orgTreeQuery.refetch()}
          variant="outline"
          class="h-7 mt-2 rounded-lg transition-colors"
        >
          <AppIcon name="refresh-cw" />
          Réessayer
        </Button>
      </Empty>
    </div>
  {/if}

  <!-- Main Transform Group -->
  <div
    class="absolute inset-0 will-change-transform {isReady ? 'transition-all duration-500 ease-out' : ''}"
    style="transform: translate({translateX}px, {translateY}px) scale({scale}); transform-origin: top left; opacity: {isReady ? 1 : 0};"
  >
    <!-- SVG Connections Layer -->
    <svg class="absolute inset-0 w-full h-full pointer-events-none overflow-visible">
      {#each jobsStore.orgUnits as orgUnit}
        {#each jobsStore.getChildOrgUnits(orgUnit.id) as child}
          {@const p = layout.get(orgUnit.id)}
          {@const c = layout.get(child.id)}
          {#if p && c}
            <OrgConnector 
              startX={p.x + NODE_WIDTH / 2} 
              startY={p.y + NODE_HEIGHT} 
              endX={c.x + NODE_WIDTH / 2} 
              endY={c.y} 
            />
          {/if}
        {/each}
      {/each}
    </svg>

    <!-- Nodes Layer -->
    <div class="absolute inset-0">
      {#each jobsStore.orgUnits as orgUnit (orgUnit.id)}
        {@const pos = layout.get(orgUnit.id)}
        {#if pos}
          <div 
            class="absolute"
            style="left: {pos.x}px; top: {pos.y}px; width: {NODE_WIDTH}px; height: {NODE_HEIGHT}px;"
          >
            <OrgNode 
              orgUnit={orgUnit} 
              isSelected={jobsStore.selectedOrgUnitId === orgUnit.id}
              onClick={(d) => {
                jobsStore.setOrgUnit(d.id);
                // Passer une copie fraîche depuis le store pour éviter les références proxy
                const freshUnit = jobsStore.getOrgUnitById(d.id);
                if (freshUnit) onSelect?.({ ...freshUnit });
              }}
              onAddChild={(parent) => {
                preselectedParentId = parent.id;
                showStructureSheet = true;
              }}
              onEdit={(unit) => {
                editingOrgUnitId = unit.id;
              }}
            />
          </div>
        {/if}
      {/each}
    </div>
  </div>

  {#if jobsStore.orgUnits.length === 0}
    {@render EmptyState()}  
  {/if}

  {@render FloatingControls()}
  <OrgStructureSheet bind:open={showStructureSheet} bind:preselectedParentId bind:editingOrgUnitId />
</div>


{#snippet EmptyState()}
  <div class="absolute inset-0 flex items-center justify-center p-8" in:fade={{ duration: 200 }}>
    <div class="max-w-sm w-full text-center bg-white/80 backdrop-blur border border-slate-200 rounded-2xl p-6 shadow-soft">
      <div class="mx-auto w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-4">
        <AppIcon name="network" size={24} class="text-primary" strokeWidth={1.2} />
      </div>
      <h3 class="text-sm font-bold text-slate-900">Aucune  unité</h3>
      <p class="mt-1 text-[0.86rem] text-slate-600">Commence par créer ta première unité pour construire l'arborescence.</p>
      <button
        onclick={() => (showStructureSheet = true)}
        class="mt-4 w-full h-9 rounded-xl bg-primary cursor-pointer text-white text-sm hover:opacity-95 transition-opacity flex items-center justify-center gap-2"
      >
        <AppIcon name="plus" size={17} />
        Créer le première unité
      </button>
    </div>
  </div>
{/snippet}


{#snippet FloatingControls()}
  <!-- Perspective Controls (Floating) -->
  <div
    class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-1 p-0.5 bg-primary border border-primary/20 rounded-full shadow-sm shadow-primary/20 z-20"
    in:fly={{ y: 60, duration: 400, delay: 200, opacity: 0 }}
  >
    <button 
      onclick={() => showStructureSheet = true}
      class="px-4 py-1.5 hover:bg-white! hover:text-primary! text-white rounded-full transition-colors flex items-center gap-2 group cursor-pointer"
      title="Gérer la structure"
    >
      <AppIcon name="layers" size={19} />
      <span class="text-[0.875rem] font-medium">Gérer</span>
    </button>
    <div class="w-px h-6 bg-white/20 mx-1"></div>
    <button 
      onclick={() => scale = Math.min(3, scale + 0.1)}
      class="p-1.5 hover:bg-white! hover:text-primary! text-white rounded-full transition-colors cursor-pointer"
      title="Zoom avant (+)"
    >
      <AppIcon name="plus" size={20} />
    </button>
    <div class="w-px h-6 bg-white/20 mx-1"></div>
    <button 
      onclick={() => scale = Math.max(0.2, scale - 0.1)}
      class="p-1.5 hover:bg-white! hover:text-primary! text-white rounded-full transition-colors cursor-pointer"
      title="Zoom arrière (-)"
    >
      <AppIcon name="minus" size={20} />
    </button>
    <div class="w-px h-6 bg-white/20 mx-1"></div>
    <button 
       onclick={resetView}
       class="p-1.5 hover:bg-white! hover:text-primary! text-white rounded-full transition-colors cursor-pointer"
       title="Réinitialiser la vue (r)"
    >
      <AppIcon name="maximize" size={19} />
    </button>
  </div>
{/snippet}

