<script lang="ts">
  import { Badge } from "@/components/ui/badge";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { scale } from "svelte/transition";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import type { SystemUser, Group } from "../../types/access.types";
  import { accessUserStore } from "../../stores/accessUserStore.svelte";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";

  interface Props {
    user: SystemUser;
    isSelected?: boolean;
    onSelect?: (user: SystemUser) => void;
    onToggleActive?: (id: string) => void;
  }

  let { 
    user, 
    isSelected = false, 
    onSelect, 
    onToggleActive 
  }: Props = $props();

  // Local state for user groups
  let userGroupsList = $state<Group[]>([]);
  let isLoadingGroups = $state(false);

  // Fetch groups when component mounts or user changes
  $effect(() => {
    const userId = user.user.id;
    const cached = accessUserStore.userGroupsCache.get(userId);
    
    if (cached) {
      userGroupsList = cached;
    } else {
      isLoadingGroups = true;
      accessUserStore.fetchAndCacheUserGroups(userId).then(groups => {
        userGroupsList = groups;
        isLoadingGroups = false;
      });
    }
  });

  const initials = $derived(
    getInitials(user.user.first_name, user.user.last_name)
  );

  const avatarPalette = $derived(
    getAvatarPalette(user.user.first_name + ' ' + user.user.last_name)
  );

  const fullName = $derived(
    `${user.user.first_name} ${user.user.last_name}`.trim() || user.user.email
  );
</script>


<div
  class={cn(
    "flex items-center gap-3 p-3 py-4 rounded-none cursor-pointer transition-all",
    isSelected
      ? "bg-indigo-50/30 shadow-none"
      : "bg-white hover:bg-slate-50"
  )}
  onclick={() => onSelect?.(user)}
  role="none"
>
  <!-- Avatar -->
  <div class="relative shrink-0 w-12">
    <div class="w-10.5 h-10.5 rounded-full flex items-center justify-center font-semibold text-[0.87rem] border {avatarPalette.bg} {avatarPalette.text} {avatarPalette.borderColor}">
      {initials}
    </div>
    <div
      class={cn(
        "absolute -bottom-0.5 right-1 w-[15px] h-[15px] rounded-full border-3 border-white",
        user.user.is_active ? "bg-emerald-600" : "bg-slate-400"
      )}
    ></div>
  </div>

  <!-- Info -->
  <div class="flex-1 min-w-0">
    <div class="flex items-center gap-2">
      <span class="font-medium text-slate-900 truncate text-[0.86rem]">
        {fullName}
      </span>
    </div>
    <div class="text-[0.88rem] text-slate-500 truncate">
      {user.user.email}
    </div>
  </div>

  <!-- Groups -->
  <div class="w-[35%] flex flex-wrap gap-1 justify-end">
    {#if isLoadingGroups}
      <AnimateSpin text="" class="border-slate-400 size-4" />
    {:else if userGroupsList.length === 0}
      <span class="text-[0.84rem] text-slate-400">Aucun groupe</span>
    {:else}
      {#each userGroupsList.slice(0, 2) as group}
        <Badge
          class="text-[0.8rem] px-2 py-0.5 font-medium border rounded-full bg-slate-100 text-slate-700 border-slate-200"
        >
          {group.name}
        </Badge>
      {/each}
      {#if userGroupsList.length > 2}
        <Badge class="text-[0.8rem] px-2 py-0.5 font-medium border rounded-full bg-slate-100 text-slate-600 border-slate-200">
          +{userGroupsList.length - 2}
        </Badge>
      {/if}
    {/if}
  </div>

  <!-- Actions --> 
  <div class="flex items-center gap-2 w-20 justify-end">
    <button
      onclick={(e) => {
        e.stopPropagation();
        onToggleActive?.(user.user.id);
      }}
      class={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
        user.user.is_active
          ? "text-emerald-600 hover:bg-emerald-50"
          : "text-slate-400 hover:bg-slate-100"
      )}
      title={user.user.is_active ? "Désactiver" : "Activer"}
    >
      <AppIcon
        name={user.user.is_active ? "circle-check" : "circle"}
        size={18}
        strokeWidth={1.5}
      />
    </button>
    {#if isSelected}
      <div in:scale={{ duration: 150 }}>
        <AppIcon name="chevron-right" size={16} class="text-indigo-500" />
      </div>
    {/if}
  </div>
</div>

