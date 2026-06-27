<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";

  interface User {
    id: string;
    first_name?: string;
    last_name?: string;
    email: string;
    is_active?: boolean;
  }

  interface Props {
    user: User;
    selected?: boolean;
    disabled?: boolean;
    disabledReason?: string;
    onSelect?: () => void;
    icon?: {
      name: string;
      class?: string;
    } | null;
  }

  let { 
    user, 
    selected = false, 
    disabled = false,
    disabledReason = "",
    onSelect,
    icon = null
  }: Props = $props();

  const initials = $derived(getInitials(user.first_name || '', user.last_name || ''));
  const palette = $derived(getAvatarPalette((user.first_name || '') + ' ' + (user.last_name || '')));
  
  import { fade } from 'svelte/transition';
</script>

<button
  class="w-full flex items-center gap-3 p-2.5 hover:bg-indigo-50 transition-colors text-left border-b border-slate-100 last:border-b-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
  class:bg-indigo-50={selected}
  onclick={onSelect}
  disabled={disabled}
  title={disabled ? disabledReason : ""}
  in:fade={{ duration: 150 }}
>
  <div class="h-9.5 w-9.5 rounded-full flex items-center justify-center text-[0.8rem] font-medium shrink-0 border {palette.bg} {palette.text} {palette.borderColor}">
    {initials}
  </div>
  <div class="flex-1 min-w-0">
    <p class="text-[0.86rem] font-medium text-slate-800 truncate">
      {user.first_name} {user.last_name}
      {#if disabled}<span class="text-[0.83rem] text-slate-500 ml-1">({disabledReason})</span>{/if}
    </p>
    <p class="text-[0.875rem] text-slate-500 truncate">{user.email}</p>
  </div>
  
  {#if icon}
    <div in:fade={{ duration: 200, delay: 50 }}>
      <AppIcon name={icon.name} size={selected ? 17 : 10} class={icon.class || (selected ? "text-emerald-500 shrink-0" : "text-slate-400 shrink-0")} />
    </div>
  {/if}
</button>

