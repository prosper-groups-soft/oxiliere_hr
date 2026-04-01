<script lang="ts">
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { userSettingsStore } from "@/features/admin/settings/stores/userSettingsStore.svelte";
  import UserListItem from "@/features/admin/settings/components/users/UserListItem.svelte";
  import UserDetail from "@/features/admin/settings/components/users/UserDetail.svelte";
  import UserCreateSheet from "@/features/admin/settings/components/users/sheets/UserCreateSheet.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { USER_ROLES } from "@/features/admin/settings/types/user.types";
  import { cn } from "@/utilities/common/css";

  let isSheetOpen = $state(false);

  // Helpers
  function getRoleDotColor(colorClass: string): string {
    return colorClass.split(' ')[0].replace('bg-', 'bg-').replace('100', '500');
  }

  function handleFilterRemove(key: string, value: string | boolean | number | null) {
    if (key === 'role') userSettingsStore.toggleRoleFilter(value as any);
    if (key === 'department') userSettingsStore.toggleDepartmentFilter(value as string);
    if (key === 'isActive') {
      userSettingsStore.setActiveFilter(null);
    }
  }
  const roleLabels: Record<string, string> = {
    'RH_ADMIN': 'RH Admin',
    'MANAGER': 'Manager',
    'EMPLOYEE': 'Employé'
  };
</script>


<svelte:head>
  <title>Paramètres - Utilisateurs | Oxiliere HR</title>
</svelte:head>


{#snippet Header()}
  <div class="flex items-center justify-between pl-2.5 pr-8 py-1 border-b border-slate-100">
    <div class="flex items-center gap-4">
      <div class="flex items-center gap-1.5">
        <Badge variant="secondary" class="bg-blue-50 text-blue-700 border-blue-100 text-[0.75rem] rounded-full">
          {userSettingsStore.stats.total} utilisateurs
        </Badge>
        <Badge variant="secondary" class="bg-green-50 text-green-700 border-green-100 text-[0.75rem] rounded-full">
          {userSettingsStore.stats.active} actifs
        </Badge>
        {#if userSettingsStore.stats.inactive > 0}
          <Badge variant="secondary" class="bg-slate-100 text-slate-600 border-slate-200 text-[0.75rem] rounded-full">
            {userSettingsStore.stats.inactive} inactifs
          </Badge>
        {/if}
      </div>
    </div>

    <Button onclick={() => isSheetOpen = true} class="bg-blue-600 hover:bg-blue-700 h-7.5">
      <AppIcon name="plus" size={17} />
      Nouvel utilisateur
    </Button>
  </div>
{/snippet}


{#snippet FilterBar()}
  <div class="flex items-center gap-3 pl-2.5 pr-8 py-3">
    <div class="flex-1">
      <SearchBar
        bind:value={userSettingsStore.filters.search}
        placeholder="Rechercher un utilisateur..."
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
        onClear={() => userSettingsStore.setSearch('')}
      />
    </div>

    <DropdownMenu.Root>
      <DropdownMenu.Trigger class={cn("inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all")}>
        <AppIcon name="shield" size={16} class={userSettingsStore.filters.role.length > 0 ? "text-blue-500" : "text-slate-400"} />
        <span class="text-[0.84rem] text-slate-700">Rôle</span>
        {#if userSettingsStore.filters.role.length > 0}
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {userSettingsStore.filters.role.length}
          </Badge>
        {/if}
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="w-56 p-2 rounded-lg shadow-fine border-slate-100 bg-white">
        <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
          Filtrer par rôle
        </DropdownMenu.Label>
        {#each USER_ROLES as role}
          <DropdownMenu.CheckboxItem
            checked={userSettingsStore.filters.role.includes(role.role)}
            onCheckedChange={() => userSettingsStore.toggleRoleFilter(role.role)}
            class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
          >
            {@render RoleFilterItem(role)}
          </DropdownMenu.CheckboxItem>
        {/each}
      </DropdownMenu.Content>
    </DropdownMenu.Root>

    <DropdownMenu.Root>
      <DropdownMenu.Trigger class={cn("inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all")}>
        <AppIcon name="activity" size={16} class={userSettingsStore.filters.isActive !== null ? "text-blue-500" : "text-slate-400"} />
        <span class="text-[0.84rem] text-slate-700">Statut</span>
      </DropdownMenu.Trigger>
      <DropdownMenu.Content align="end" class="w-48 p-2 rounded-lg shadow-fine border-slate-100 bg-white">
        <DropdownMenu.RadioGroup
          value={userSettingsStore.filters.isActive?.toString() || 'all'}
          onValueChange={(v) => userSettingsStore.setActiveFilter(v === 'all' ? null : v === 'true')}
        >
          <DropdownMenu.RadioItem value="all" class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7">Tous</DropdownMenu.RadioItem>
          <DropdownMenu.RadioItem value="true" class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7">Actifs</DropdownMenu.RadioItem>
          <DropdownMenu.RadioItem value="false" class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7">Inactifs</DropdownMenu.RadioItem>
        </DropdownMenu.RadioGroup>
      </DropdownMenu.Content>
    </DropdownMenu.Root>
  </div>
{/snippet}


{#snippet RoleFilterItem(role: typeof USER_ROLES[0])}
  <span class="inline-flex items-center gap-2">
    <span class={cn("w-2 h-2 rounded-full", getRoleDotColor(role.color))}></span>
    {role.label}
  </span>
{/snippet}


{#snippet UserListSection()}
  <div class="lg:col-span-6 flex flex-col overflow-hidden border-t border-b border-slate-100">
    <div class="flex-1 overflow-y-auto divide-y divide-slate-100">
      <FilterChips
        filters={{
          ...userSettingsStore.filters,
          isActive: userSettingsStore.filters.isActive !== null ? [userSettingsStore.filters.isActive ? 'Actif' : 'Inactif'] : []
        }}
        activeFiltersCount={userSettingsStore.activeFiltersCount}
        getDisplayLabel={(key, value) => {
          if (key === 'role') return roleLabels[value as string] || value;
          return String(value);
        }}
        onRemove={handleFilterRemove}
        onReset={() => userSettingsStore.resetFilters()}
        class="px-6 py-2 border-b border-slate-50 bg-white/50"
      />
      {#if userSettingsStore.paginatedUsers.length > 0}
        {#each userSettingsStore.paginatedUsers as user (user.id)}
          <UserListItem
            {user}
            isSelected={userSettingsStore.selectedUser?.id === user.id}
            onSelect={(u) => userSettingsStore.selectUser(u)}
            onToggleActive={(id) => userSettingsStore.toggleUserActive(id)}
          />
        {/each}
      {:else}
        <Empty icon="users" title="Aucun utilisateur trouvé" description="Essayez d'ajuster vos filtres" iconClass="text-slate-300" iconSize={26} />
      {/if}
    </div>

    {#if userSettingsStore.totalCount > 0}
      <div class="border-t border-slate-100 px-4 py-0 bg-white">
        <DataPagination
          currentCount={userSettingsStore.paginatedUsers.length}
          totalCount={userSettingsStore.totalCount}
          currentPage={userSettingsStore.currentPage}
          totalPages={userSettingsStore.totalPages}
          perPage={userSettingsStore.perPage}
          onPageChange={(p) => userSettingsStore.setPage(p)}
          onPerPageChange={(s) => userSettingsStore.setPerPage(s)}
          onNext={() => userSettingsStore.setPage(userSettingsStore.currentPage + 1)}
          onPrev={() => userSettingsStore.setPage(userSettingsStore.currentPage - 1)}
          unitLabel="utilisateurs"
        />
      </div>
    {/if}
  </div>
{/snippet}


{#snippet DetailSection()}
  <div class="lg:col-span-4 overflow-y-auto border border-r-0 border-b-0 border-slate-100 bg-slate-50/30">
    {#if userSettingsStore.selectedUser}
      <div class="bg-white rounded-none border-none shadow-none">
        <UserDetail
          user={userSettingsStore.selectedUser}
          onClose={() => userSettingsStore.selectUser(null)}
          onSave={(id, data) => userSettingsStore.updateUser(id, data)}
        />
      </div>
    {:else}
      <Empty icon="user" title="" description="Sélectionnez un utilisateur pour voir les détails" iconClass="text-blue-400" iconSize={26} />
    {/if}
  </div>
{/snippet}


<div class="flex flex-col h-full">
  {@render Header()}

  {@render FilterBar()}

  <div class="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-10">
    {@render UserListSection()}
    {@render DetailSection()}
  </div>
</div>


<UserCreateSheet
  bind:open={isSheetOpen}
  onSave={(data) => userSettingsStore.createUser(data)}
/>

