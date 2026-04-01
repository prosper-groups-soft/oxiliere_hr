<script lang="ts">
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { scale } from "svelte/transition";
  import type { User } from "../../types/user.types";
  import { USER_ROLES } from "../../types/user.types";
  import { getAvatarColors } from "../../utilities/avatar.utils";

  interface Props {
    user: User;
    isSelected?: boolean;
    onSelect?: (user: User) => void;
    onToggleActive?: (id: string) => void;
  }

  let { 
    user, 
    isSelected = false, 
    onSelect, 
    onToggleActive 
  }: Props = $props();

  const roleConfig = $derived(
    USER_ROLES.find(r => r.role === user.role) || USER_ROLES[2]
  );

  const initials = $derived(
    `${user.firstName[0]}${user.lastName[0]}`.toUpperCase()
  );

  const lastLoginText = $derived(() => {
    if (!user.lastLogin) return "Jamais connecté";
    const loginDate = typeof user.lastLogin === 'string' ? new Date(user.lastLogin) : user.lastLogin;
    const days = Math.floor((Date.now() - loginDate.getTime()) / (1000 * 60 * 60 * 24));
    if (days === 0) return "Aujourd'hui";
    if (days === 1) return "Hier";
    if (days < 30) return `Il y a ${days} jours`;
    return "Il y a plus d'un mois";
  });
</script>


<div
  class={cn(
    "flex items-center gap-3 p-2 py-4 rounded-none cursor-pointer transition-all",
    isSelected
      ? "bg-blue-50/30 shadow-none"
      : "bg-white hover:bg-slate-50"
  )}
  onclick={() => onSelect?.(user)}
  role="none"
>
  <!-- Avatar -->
  <div class="relative shrink-0 w-[8%] min-w-12">
    {#if user.avatarUrl}
      <img
        src={user.avatarUrl}
        alt={`${user.firstName} ${user.lastName}`}
        class="w-10.5 h-10.5 rounded-full object-cover"
      />
    {:else}
      <div class="w-10.5 h-10.5 rounded-full {getAvatarColors(user.role).bg} {getAvatarColors(user.role).text} {getAvatarColors(user.role).border} border flex items-center justify-center font-semibold text-[0.87rem]">
        {initials}
      </div>
    {/if}
    <div
      class={cn(
        "absolute -bottom-0.5 right-4 w-3 h-3 rounded-full border",
        user.isActive ? "bg-green-500 border-green-500" : "bg-slate-400 border-slate-400"
      )}
    ></div>
  </div>

  <!-- Info -->
  <div class="w-[30%] min-w-0">
    <div class="flex items-center gap-2.5">
      <span class="font-medium text-slate-900 truncate text-[0.878rem]">
        {user.firstName} {user.lastName}
      </span>
    </div>
    <div class="text-[0.85rem] text-slate-600 truncate">
      {user.email}
    </div>
  </div>

  <!-- Last login -->
  <div class="w-[27%] text-[0.85rem] text-muted-foreground truncate">
    {lastLoginText()}
  </div>

  <!-- Role -->
  <div class="w-[15%] flex justify-center">
    <Badge
      class={cn(
        "text-[0.7rem] px-1.5 py-1 h-4.5 font-medium border rounded-full",
        roleConfig.color
      )}
    >
      {roleConfig.label}
    </Badge>
  </div>

  <!-- Actions -->
  <div class="flex items-center gap-1 w-[20%] justify-end">
    <button
      onclick={(e) => {
        e.stopPropagation();
        onToggleActive?.(String(user.id));
      }}
      class={cn(
        "w-8 h-8 rounded-md flex items-center justify-center transition-colors",
        user.isActive
          ? "text-green-600 hover:bg-green-50"
          : "text-slate-400 hover:bg-slate-100"
      )}
    >
      <AppIcon
        name={user.isActive ? "circle-check" : "circle"}
        size={18}
        strokeWidth={1.4}
      />
    </button>
    {#if isSelected}
      <div in:scale={{ duration: 150 }}>
        <div class="inline-block">
          <Button
            variant="link"
            size="sm"
            onclick={(e) => { e.stopPropagation(); onToggleActive?.(String(user.id)); }}
            class={cn(
              "h-auto p-0 font-medium text-[0.8rem] decoration-transparent hover:no-underline flex items-center gap-1 transition-colors",
              user.isActive
                ? "text-rose-500 hover:text-rose-700"
                : "text-emerald-600 hover:text-emerald-800"
            )}
          >
            <AppIcon name={user.isActive ? "circle-x" : "circle-check"} size={16} />
            {user.isActive ? "Désactiver" : "Activer"}
          </Button>
        </div>
      </div>
    {/if}
  </div>
</div>

