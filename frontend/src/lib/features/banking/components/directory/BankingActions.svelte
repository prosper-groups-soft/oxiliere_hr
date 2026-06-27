<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { bankingStore } from "@/features/banking/stores/banking.svelte";
  import { useSeedBanksMutation } from "@/features/banking/queries/bankingQueries";
  import SeedBanksDialog from "./SeedBanksDialog.svelte";


  let isSeedDialogOpen = $state(false);

  const seedMutation = useSeedBanksMutation();

  async function handleSeed(codes?: string[]) {
    await $seedMutation.mutateAsync(codes);
  }

  const typeOptions = [
    { value: 'bank' as const, label: 'Banques' },
    { value: 'mobile_money' as const, label: 'Mobile Money' },
  ];

  const statusOptions = [
    { value: true as const, label: 'Actifs' },
    { value: false as const, label: 'Inactifs' },
  ];

  const activeFiltersCount = $derived(
    bankingStore.institutionFilters.type.length
    + (bankingStore.institutionFilters.search ? 1 : 0)
    + (bankingStore.institutionFilters.isActive !== null ? 1 : 0)
  );

  function clearType() {
    bankingStore.institutionFilters.type = [];
  }

  function isTypeActive(value: string): boolean {
    return bankingStore.institutionFilters.type?.includes(value as any) || false;
  }

  function setStatus(value: boolean | null) {
    bankingStore.institutionFilters.isActive = value;
  }
</script>


<div class="flex items-center gap-2 pr-3">
  <!-- Seed default institutions button -->
  <Button
    variant="ghost"
    size="sm"
    onclick={() => isSeedDialogOpen = true}
    class="h-7 px-2.5 text-[0.84rem] text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
  >
    <AppIcon name="plus" size={15} class="mr-1.5" />
    Institutions par défaut
  </Button>

  <div class="w-px h-5 bg-slate-200"></div>

  <!-- Type Filter Button -->
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="bank" size={15} class="mr-1.5" />
        Type
        {#if (bankingStore.institutionFilters.type?.length || 0) > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {bankingStore.institutionFilters.type?.length || 0}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Type d'entité
      </DropdownMenu.Label>

      {#each typeOptions as option}
        {@const active = isTypeActive(option.value)}
        <DropdownMenu.Item
          onclick={() => bankingStore.toggleInstitutionType(option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if (bankingStore.institutionFilters.type?.length || 0) > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => clearType()}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
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
        <AppIcon name="power" size={15} class="mr-1.5" />
        Statut
        {#if bankingStore.institutionFilters.isActive !== null}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">1</span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Statut de l'institution
      </DropdownMenu.Label>

      {#each statusOptions as option}
        {@const active = bankingStore.institutionFilters.isActive === option.value}
        <DropdownMenu.Item
          onclick={() => setStatus(active ? null : option.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{option.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <!-- Active Filters Badge -->
  {#if activeFiltersCount > 0}
    <button
      onclick={() => bankingStore.resetInstitutionFilters()}
      class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
    >
      <span class="text-[0.8rem]">{activeFiltersCount} filtre{activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}
</div>

<SeedBanksDialog bind:open={isSeedDialogOpen} onSeed={handleSeed} />

