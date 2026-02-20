<script lang="ts">
  import { slide, fade, scale } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { Button } from "@/components/ui/button";
  import { Separator } from "@/components/ui/separator";
  import TooltipWrapper from "@/components/shared/containers/TooltipWrapper.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { 
    NAV_CONFIG,
    MENU_ITEM_TYPE, 
    type MenuItem, 
    MENU_ITEMS, 
    bottomMenuItems 
  } from "@/constants/features/navigation";
  
  // Using the reactive UI store for selected menu item tracking
  import { ui } from "@/stores/ui.svelte"; 
  import Logo from "./Logo.svelte";

  // --- Props ---
  // Explicitly receiving state from PageLayout
  let { 
    expanded = NAV_CONFIG.defaultExpanded, 
    setExpanded 
  } = $props();

  // --- State ---
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

  const toggleGroup = (id: string) => {
    if (!expanded) return; 
    openGroups[id] = !openGroups[id];
  };

  /**
   * Generates tailwind classes based on expansion state
   */
  const getLinkClasses = (isSubItem = false) => cn(
    "relative flex h-8 w-full items-center gap-2 rounded-md hover:bg-primary/10 cursor-pointer data-[status=active]:font-medium data-[status=active]:!text-primary transition-all",
    expanded ? (isSubItem ? "pl-2 pr-2" : "pl-2.5 pr-3") : "w-9 justify-center",
    isSubItem && expanded ? "text-[0.875rem]" : "text-[0.875rem]"
  );
</script>


{#snippet ItemContent(item: MenuItem)}
  <div class={cn("relative z-10 flex items-center gap-2 w-full", !expanded && "justify-center")}>
    <AppIcon 
      name={item.icon} 
      size={expanded ? 20 : 22}
      strokeWidth={
        (ui.selectedMenuItem === item.id ? 2 : 1.6) + (expanded ? 0 : 0.1)
      }
      class={cn(
        "text-gray-500 transition-colors", 
        ui.selectedMenuItem === item.id && "text-primary"
      )} 
    />
    {#if expanded}
      <div in:fade={{ duration: 150, delay: 100 }} class="grow truncate text-[0.89rem]">
        {item.label}
      </div>
      {#if item.countKey && countDataMap[item.countKey]}
        <div class="h-4.5 min-w-4.5 rounded-full bg-primary text-[0.77rem] font-medium text-primary-foreground flex items-center justify-center">
          {countDataMap[item.countKey]}
        </div>
      {/if}
    {/if}
  </div>
  {#if ui.selectedMenuItem === item.id}
    <div
      in:scale={{ duration: 200, start: 0.96, easing: cubicOut }}
      out:fade={{ duration: 150 }}
      class="absolute inset-0 bg-primary/15 rounded-md z-0"
    ></div>
  {/if}
{/snippet}


{#snippet Item(item: MenuItem, isSubItem = false)}
  {@const classes = getLinkClasses(isSubItem)}
  <li class="flex list-none">
    {#if item.type === MENU_ITEM_TYPE.router || item.type === MENU_ITEM_TYPE.button}
      <button 
        data-status={ui.selectedMenuItem === item.id ? "active" : ""} 
        onclick={item.onClick} 
        class={cn(classes, "text-left border-none bg-transparent")}
      >
        {@render ItemContent(item)}
      </button>
    {:else}
      <a 
        href={item.path}
        data-status={ui.selectedMenuItem === item.id ? "active" : ""}
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
    <TooltipWrapper content={item.label} side="right" asChild={true}>
      {#snippet children(props: Record<string, any>)}
        <div {...props}>{@render Item(item, isSubItem)}</div>
      {/snippet}
    </TooltipWrapper>
  {/if}
{/snippet}


{#snippet GroupHeader(label: string | undefined, isOpen: boolean, groupId: string)}
  <button 
    onclick={() => toggleGroup(groupId)}
    aria-expanded={isOpen}
    class="w-full flex items-center justify-between group/title mb-2 pl-2 pr-2 cursor-pointer border-none bg-transparent"
  >
    <span class="text-[0.82rem] font-semibold uppercase text-foreground/70 tracking-wide group-hover/title:text-primary transition-colors">
      {label}
    </span>
    <AppIcon 
      name="chevron" 
      size={16} 
      class={cn("text-muted-foreground transition-transform duration-200", !isOpen && "-rotate-90")} 
    />
  </button>
{/snippet}


{#snippet ToggleButton()}
  <Button
    variant="outline"
    size="icon"
    onclick={() => setExpanded(!expanded)}
    class="absolute -right-3 top-4 w-6 h-6 rounded-full z-20 bg-background border border-gray-300 hover:bg-slate-50 transition-all shadow-sm"
  >
    <AppIcon 
      name="prev" 
      size={17} 
      class={cn("transition-transform", !expanded && "rotate-180")} 
      style="transition-duration: {NAV_CONFIG.transitionSpeed}ms"
    />
  </Button>
{/snippet}


<aside 
  class="sidebar-container h-full border-r bg-card relative shrink-0 z-10"
  class:expanded={expanded}
  style="
    --sidebar-width: {NAV_CONFIG.sidebarWidth}px;
    --sidebar-collapsed: {NAV_CONFIG.sidebarCollapsedWidth}px;
    --transition-speed: {NAV_CONFIG.transitionSpeed}ms;
  "
>
  {@render ToggleButton()}

  <div class={cn("flex flex-col h-full py-4 transition-all overflow-hidden", expanded ? "px-3" : "px-2 items-center")}>
    <div class="flex items-center justify-center mb-5 w-full shrink-0 h-10">
      <Logo {expanded} />
    </div>

    <div class="flex-1 overflow-y-auto no-scrollbar w-full">
      <ul class={cn("flex flex-col gap-6", !expanded && "items-center")}>
        {#each MENU_ITEMS as group (group.id)}
          {@const isOpen = openGroups[group.id] ?? true}
          {@const hasLabel = !!group.label}
          <li class="list-none">
            {#if hasLabel && expanded}
              {@render GroupHeader(group.label!, isOpen, group.id)}
            {/if}

            {#if !expanded || (expanded && isOpen)}
              <div 
                transition:slide={{ duration: NAV_CONFIG.transitionSpeed - 50, easing: cubicOut }} 
                class={cn(
                  "overflow-hidden",
                  expanded && hasLabel && "ml-3 border-l border-slate-200 pl-2"
                )}
              >
                <ul class="flex flex-col gap-1.5 mt-1 pb-1"> 
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

    <div class="mt-auto pt-4 flex flex-col gap-2 w-full shrink-0">
      <Separator class="bg-slate-100" />
      <ul class={cn("flex flex-col gap-1.5", !expanded && "items-center")}>
        {#each bottomMenuItems as item (item.id)}
          {@render SmartItem(item)}
        {/each}
      </ul>
    </div>
  </div>
</aside>


<style>
  .sidebar-container {
    width: var(--sidebar-collapsed);
    transition: width var(--transition-speed) cubic-bezier(0.4, 0, 0.2, 1);
  }

  .sidebar-container.expanded {
    width: var(--sidebar-width);
  }

  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>

