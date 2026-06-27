<script lang="ts">
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";


  const sortOptions: { label: string; sortBy: string; order: 'asc' | 'desc' }[] = [
    { label: "Nom (A-Z)", sortBy: "name", order: "asc" },
    { label: "Nom (Z-A)", sortBy: "name", order: "desc" },
    { label: "Date de création", sortBy: "created", order: "asc" },
    { label: "Jours actifs", sortBy: "activeDays", order: "asc" },
  ];

  const activeFiltersCount = $derived(
    (attendanceStore.policySearch ? 1 : 0)
  );
</script>


<div class="flex items-center gap-2">
  <!-- Sort Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="arrow-down-up" size={15} class="mr-1.5" />
        Tri
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Trier par
      </DropdownMenu.Label>

      {#each sortOptions as option}
        {@const isActive = attendanceStore.policySortBy === option.sortBy && attendanceStore.policySortOrder === option.order}
        <DropdownMenu.Item
          onclick={() => {
            attendanceStore.policySortBy = option.sortBy;
            attendanceStore.policySortOrder = option.order;
          }}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            isActive && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if isActive}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => attendanceStore.policySearch = ''}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}

  <div class="w-px h-5 bg-slate-200 mx-1"></div>
</div>
