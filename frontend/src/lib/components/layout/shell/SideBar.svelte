<script lang="ts">
  import { slide, crossfade } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { Button } from "@/components/ui/button";
  import { Separator } from "@/components/ui/separator";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utils";
  import { 
    MENU_ITEM_TYPE, 
    type MenuItem, 
    MENU_ITEMS, 
    bottomMenuItems 
  } from "@/constants/navigation";
  import { page } from "$app/stores";
  import Logo from "./Logo.svelte";

  // --- Props ---
  let { expanded, setExpanded } = $props();

  // --- State ---
  let selected_menu: string | null = $state(null);
  
  let openGroups = $state<Record<string, boolean>>({
    talent_group: true,
    ops_group: true,
    finance_group: true,
    admin_group: true
  });

  const countDataMap: Record<string, number | undefined> = {
    leaves_pending: 5,
    onboarding_active: 2
  };

  // --- Logic ---
  const [send, receive] = crossfade({
    duration: 250,
    easing: cubicOut
  });

  const toggleGroup = (id: string) => {
    if (!expanded) return; 
    openGroups[id] = !openGroups[id];
  };

  $effect(() => {
    const pathname = $page.url.pathname;
    let bestMatchId: string | null = null;
    let maxMatchLength = -1;

    const checkMatch = (item: MenuItem) => {
      if (item.type === MENU_ITEM_TYPE.router && item.path) {
        const itemPath = item.path;
        // Match if exact path or starts with path + separator (to avoid partial word matches)
        // Exception: root '/' matches all, so we rely on length to override it with more specific matches
        const isMatch = pathname === itemPath || 
                        (pathname.startsWith(itemPath) && (itemPath === '/' || pathname[itemPath.length] === '/'));
        
        if (isMatch) {
          if (itemPath.length > maxMatchLength) {
            maxMatchLength = itemPath.length;
            bestMatchId = item.id;
          }
        }
      }
    };

    MENU_ITEMS.forEach(group => {
      group.items.forEach(checkMatch);
    });
    bottomMenuItems.forEach(checkMatch);

    selected_menu = bestMatchId;
  });

  const getLinkClasses = (isSubItem = false) => cn(
    "relative flex h-8 w-full items-center gap-2 rounded-md hover:bg-primary/10 cursor-pointer data-[status=active]:font-medium data-[status=active]:!text-primary transition-all duration-300",
    expanded ? (isSubItem ? "pl-2 pr-2" : "pl-2.5 pr-3") : "w-9 justify-center",
    isSubItem && expanded ? "text-[13px]" : "text-[14px]"
  );
</script>


{#snippet ItemContent(item: MenuItem)}
  <div class={cn("relative z-10 flex items-center gap-2 w-full", !expanded && "justify-center")}>
    <AppIcon 
      name={item.icon} 
      class={cn("text-gray-500", selected_menu === item.id && "text-primary")} 
    />
    {#if expanded}
      <div class="grow truncate text-[13.1px]">{item.label}</div>
      {#if item.countKey && countDataMap[item.countKey]}
        <div class="h-4.5 min-w-4.5 rounded-full bg-primary text-[10.5px] font-medium text-primary-foreground flex items-center justify-center">
          {countDataMap[item.countKey]}
        </div>
      {/if}
    {/if}
  </div>
  {#if selected_menu === item.id}
    <div
      in:receive={{ key: "active-item" }}
      out:send={{ key: "active-item" }}
      class="absolute inset-0 bg-primary/15 rounded-md z-0"
    ></div>
  {/if}
{/snippet}


{#snippet Item(item: MenuItem, isSubItem = false)}
  {@const classes = getLinkClasses(isSubItem)}
  <li class="flex list-none">
    {#if item.type === MENU_ITEM_TYPE.router || item.type === MENU_ITEM_TYPE.button}
      <button 
        data-status={selected_menu === item.id ? "active" : ""} 
        onclick={item.onClick} 
        class={cn(classes, "text-left")}
      >
        {@render ItemContent(item)}
      </button>
    {:else}
      <a 
        href={item.path}
        data-status={selected_menu === item.id ? "active" : ""}
        class={classes}
      >
        {@render ItemContent(item)}
      </a>
    {/if}
  </li>
{/snippet}


{#snippet SmartItem(item: MenuItem, isSubItem = false)}
  {#if expanded}
    {@render Item(item, isSubItem)}
  {:else}
    <TooltipWrapper content={item.label} side="right">
      <div>{@render Item(item, isSubItem)}</div>
    </TooltipWrapper>
  {/if}
{/snippet}


{#snippet GroupHeader(label: string | undefined, isOpen: boolean, groupId: string)}
  <button 
    onclick={() => toggleGroup(groupId)}
    aria-expanded={isOpen}
    class="w-full flex items-center justify-between group/title mb-2 pl-2 pr-2 cursor-pointer"
  >
    <span class="text-[11px] font-semibold uppercase text-foreground tracking-wide group-hover/title:text-primary transition-colors">
      {label}
    </span>
    <AppIcon 
      name="chevron" 
      size={12} 
      class={cn("text-muted-foreground transition-transform duration-200", !isOpen && "-rotate-90")} 
    />
  </button>
{/snippet}


{#snippet ToggleButton()}
  <Button
    variant="outline"
    size="icon"
    onclick={() => setExpanded(!expanded)}
    class="absolute -right-3 top-4 w-6 h-6 rounded-full z-50 bg-background border border-[1px] border-gray-400"
  >
    <AppIcon 
      name="prev" 
      size={14} 
      class={cn("transition-transform duration-300", !expanded && "rotate-180")} 
    />
  </Button>
{/snippet}


<aside 
  class={cn(
    "h-full border-r bg-card transition-all duration-300 relative shrink-0 z-20",
    expanded ? "w-62" : "w-16"
  )}
>
  {@render ToggleButton()}

  <div class={cn("flex flex-col h-full py-4", expanded ? "px-4" : "px-2 items-center")}>

    <div class="flex items-center justify-center mb-5 w-full">
      <Logo expanded={expanded} />
    </div>

    <div class="flex-1 overflow-y-auto no-scrollbar w-full">
      <ul class={cn("flex flex-col gap-4", !expanded && "items-center")}>
        {#each MENU_ITEMS as group (group.id)}
          {@const isOpen = openGroups[group.id] ?? true}
          {@const hasLabel = !!group.label}
          <li class="list-none">
            {#if hasLabel && expanded}
              {@render GroupHeader(group.label!, isOpen, group.id)}
            {/if}

            {#if !expanded || isOpen}
              <div 
                transition:slide={{ duration: 230, easing: cubicOut }} 
                class={cn(
                  "overflow-hidden",
                  expanded && hasLabel && "ml-3.5 border-l border-gray-300 pl-2"
                )}
              >
                <ul class="flex flex-col gap-1 mt-1 pb-1"> 
                  {#each group.items as item (item.id)}
                    {@render SmartItem(item, hasLabel)}
                  {/each}
                </ul>
              </div>
            {/if}
          </li>
        {/each}
      </ul>
    </div>

    <div class="mt-auto pt-4 flex flex-col gap-2 w-full">
      <Separator />
      <ul class={cn("flex flex-col gap-1", !expanded && "items-center")}>
        {#each bottomMenuItems as item (item.id)}
          {@render SmartItem(item)}
        {/each}
      </ul>
    </div>
  </div>
</aside>


<style>
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width   : none;
  }
</style>

