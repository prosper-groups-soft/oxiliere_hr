<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { bankingStore } from "../../stores/banking.svelte";
  import { VERIFICATION_STATUS_LABELS } from "../../constants";
  import { CURRENCIES } from "@/hr/constants/finance";
  

  const sortOptions: { value: string; label: string }[] = [
    { value: 'created_at', label: 'Date de création' },
    { value: 'account_name', label: 'Nom du compte' },
  ];

  const currencyOptions = Object.values(CURRENCIES);

  const activeFiltersCount = $derived(bankingStore.activeFiltersCount);

  function clearStatus() {
    bankingStore.filters.status = [];
  }

  function clearCurrency() {
    bankingStore.filters.currency = [];
  }

  function clearInstitution() {
    bankingStore.filters.institutionId = [];
  }

  function isStatusActive(value: string): boolean {
    return bankingStore.filters.status?.includes(value as any) || false;
  }

  function isCurrencyActive(value: string): boolean {
    return bankingStore.filters.currency?.includes(value as any) || false;
  }

  function isInstitutionActive(value: string): boolean {
    return bankingStore.filters.institutionId?.includes(value as any) || false;
  }
</script>


<div class="flex items-center gap-2 pr-3">
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

      {#each sortOptions as { value, label }}
        {@const isActive = bankingStore.sortBy === value}
        <DropdownMenu.Item
          onclick={() => { bankingStore.setSort(value); }}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            isActive && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{label}</span>
          {#if isActive}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      <DropdownMenu.Separator />
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Ordre
      </DropdownMenu.Label>
      <DropdownMenu.Item
        onclick={() => {
          if (bankingStore.sortOrder !== 'asc') bankingStore.toggleSortOrder();
        }}
        class={[
          "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
          bankingStore.sortOrder === 'asc' && "bg-slate-50 font-medium"
        ]}
      >
        <span class="text-[0.86rem]">ASC</span>
        {#if bankingStore.sortOrder === 'asc'}
          <AppIcon name="check" size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>
      <DropdownMenu.Item
        onclick={() => {
          if (bankingStore.sortOrder !== 'desc') bankingStore.toggleSortOrder();
        }}
        class={[
          "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
          bankingStore.sortOrder === 'desc' && "bg-slate-50 font-medium"
        ]}
      >
        <span class="text-[0.86rem]">DESC</span>
        {#if bankingStore.sortOrder === 'desc'}
          <AppIcon name="check" size={14} class="text-slate-600" />
        {/if}
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Status Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="user-check" size={15} class="mr-1.5" />
        Statut
        {#if (bankingStore.filters.status?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {bankingStore.filters.status?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut
      </DropdownMenu.Label>

      {#each Object.entries(VERIFICATION_STATUS_LABELS) as [value, label]}
        {@const active = isStatusActive(value)}
        <DropdownMenu.Item
          onclick={() => bankingStore.toggleFilter('status', value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (bankingStore.filters.status?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearStatus()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Currency Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="coins" size={15} class="mr-1.5" />
        Devise
        {#if (bankingStore.filters.currency?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {bankingStore.filters.currency?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Devise
      </DropdownMenu.Label>

      {#each currencyOptions as currency}
        {@const active = isCurrencyActive(currency)}
        <DropdownMenu.Item
          onclick={() => bankingStore.toggleFilter('currency', currency)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{currency}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (bankingStore.filters.currency?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearCurrency()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Institution Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="building-2" size={15} class="mr-1.5" />
        Institution
        {#if (bankingStore.filters.institutionId?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {bankingStore.filters.institutionId?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-64 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Institution
      </DropdownMenu.Label>

      {#each bankingStore.institutions as inst}
        {@const active = isInstitutionActive(inst.id)}
        <DropdownMenu.Item
          onclick={() => bankingStore.toggleFilter('institutionId', inst.id)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{inst.name}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (bankingStore.filters.institutionId?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearInstitution()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => bankingStore.resetFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}
</div>

