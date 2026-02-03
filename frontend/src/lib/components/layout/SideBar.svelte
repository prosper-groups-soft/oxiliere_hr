<script lang="ts">
  import {
      Database,
      Layers,
      GraduationCap,
      LayoutGrid,
      MessageCircleQuestion,
      User,
      LucideHome,
      ChevronLeft,
      ChevronRight,
      Users,
      Send,
      Activity
  } from "@lucide/svelte";

  import { Button } from "$lib/components/ui/button";
  import { Separator } from "$lib/components/ui/separator";
  import TooltipWrapper from "$lib/components/shared/TooltipWrapper.svelte";
  import { cn } from "$lib/utils";
  import Logo from "$lib/components/layout/Logo.svelte";
  import { MENU_ITEM_TYPE } from "./constant";
  import type { MouseEventHandler } from "svelte/elements";
  import isNumber from "lodash/isNumber";
	import { goto } from "$app/navigation";
  import { selectedMenuItem } from "$lib/stores/ui";



  let { expanded, setExpanded } = $props();

  let selected_menu: string | null = $state(null);

  

  $effect(() => {
    const unsub_selected_menu = selectedMenuItem.subscribe((value) => {
      selected_menu = value;
    });

    return () => {
      unsub_selected_menu();
    };
  });


  const bottomMenuItems: MenuItem[] = [
    {
      id: "quickstart",
      type: MENU_ITEM_TYPE.button,
      icon: GraduationCap,
      label: "Quickstart guide",
      onClick: () => {},
    },
  ];


  type MenuItem = {
    id: string;
    path?: string;
    type: MENU_ITEM_TYPE;
    icon: any;
    label: string;
    count?: string;
    onClick?: MouseEventHandler<HTMLButtonElement>;
  };

  type MenuItemGroup = {
    id: string;
    label?: string;
    items: MenuItem[];
  };


  const countDataMap: Record<string, number | undefined> = {
    projects: 1,
    datasets: 1,
    experiments: 1,
    prompts: 1,
    help_desk: 1,
    invitations: 1,
  };

  const HOME_PATH = "/";

  const MENU_ITEMS: MenuItemGroup[] = [
    {
      id: "home",
      items: [
        {
          id: "home",
          path: "/auth/login",
          type: MENU_ITEM_TYPE.router,
          icon: LucideHome,
          label: "Accueil",
          onClick: () => {
            goto("/s");
          },
        },
      ]
    },
    {
      id: "projects_group",
      label: "Projects",
      items: [
        {
          id: "projects",
          path: "/s/projects",
          type: MENU_ITEM_TYPE.router,
          icon: LayoutGrid,
          label: "Projects",
          onClick: () => {
            goto("/s/projects");
          },
        },
        {
          id: "spreadsheets",
          path: "/s/spreadsheets",
          type: MENU_ITEM_TYPE.router,
          icon: Layers,
          label: "Spreadsheets",
          count: "spreadsheet",
          onClick: () => {
            goto("/s/spreadsheets");
          },
        },
        {
          id: "datasets",
          path: "/s/datasets",
          type: MENU_ITEM_TYPE.router,
          icon: Database,
          label: "Datasets",
          onClick: () => {
            goto("/s/datasets");
          },
        },
      ],
    },
    {
      id: "organizations",
      label: "Organizations",
      items: [
        {
          id: "organizations",
          path: "/s/organizations",
          type: MENU_ITEM_TYPE.router,
          icon: Users,
          label: "Organizations",
          onClick: () => {
            goto("/s/organizations");
          },
        },
        {
          id: "invitations",
          path: "/s/invitations",
          type: MENU_ITEM_TYPE.router,
          icon: Send,
          label: "Invitations",
          // count: "invitations", // TODO: get count from API
          onClick: () => {
            goto("/s/invitations");
          },
        },
        {
          id: "activities",
          path: "/s/activities",
          type: MENU_ITEM_TYPE.router,
          icon: Activity,
          label: "Activities",
          count: "activities",
          onClick: () => {
            goto("/s/activities");
          },
        },
      ],
    },
    {
      id: "admin",
      label: "Admin & Users",
      items: [
        {
          id: "accounts",
          path: "/s/admin/users",
          type: MENU_ITEM_TYPE.router,
          icon: User,
          label: "Accounts",
          onClick: () => {
            goto("/s/admin/users");
          },
        },
        {
          id: "admin_organizations",
          path: "/s/admin/organizations",
          type: MENU_ITEM_TYPE.router,
          icon: Users,
          label: "Organizations",
          onClick: () => {
            goto("/s/admin/organizations");
          },
        },
        {
          id: "help_desk",
          path: "/s/help-desk",
          type: MENU_ITEM_TYPE.router,
          icon: MessageCircleQuestion,
          label: "Help Desk",
          onClick: () => {
            goto("/s/help-desk");
          },
        },
      ],
    }
  ];

  const linkClasses = cn(
      "comet-body-s flex h-9 w-full items-center gap-2 text-foreground rounded-md hover:bg-primary-foreground data-[status=active]:bg-primary-100 data-[status=active]:text-primary",
      expanded ? "pl-2.5 pr-3" : "w-9 justify-center");

</script>


{#snippet getItemElementByType(item:MenuItem, linkClasses: string)}
  {#if item.type === MENU_ITEM_TYPE.router}
    <li class="flex">
      <button data-status={selected_menu === item.id ? "active" : ""} onclick={item.onClick} class={cn(linkClasses, "text-left")}>
        {@render ItemContent(item)}
      </button>
    </li>
  {:else if item.type === MENU_ITEM_TYPE.link}
    <li class="flex">
      <a data-status={selected_menu === item.id ? "active" : ""}
        href={item.path}
        target="_blank"
        rel="noreferrer"
        class={linkClasses}
      >
      {@render ItemContent(item)}
      </a>
    </li>
  {:else if item.type === MENU_ITEM_TYPE.button}
    <li class="flex">
      <button data-status={selected_menu === item.id ? "active" : ""} onclick={item.onClick} class={cn(linkClasses, "text-left")}>
        {@render ItemContent(item)}
      </button>
    </li>
  {/if}
{/snippet}


{#snippet ItemContent(item: MenuItem)}
  {@const hasCount = item.count && isNumber(countDataMap[item.count])}
  {@const count = hasCount ? countDataMap[item.count!] : ""}
  <item.icon class="size-4 shrink-0" />

  {#if expanded}
    <div class="ml-1 font-medium grow truncate"> {item.label}</div>
    {#if hasCount}
      <div class="h-6 shrink-0 leading-6">{count}</div>
    {/if}
  {/if}
{/snippet}


{#snippet Item(item: MenuItem, linkClasses: string)}
  {#if expanded}
    {@render getItemElementByType(item, linkClasses)}
  {:else}
    <TooltipWrapper content={item.label} side="left">
      {@render getItemElementByType(item, linkClasses)}
    </TooltipWrapper>
  {/if}
{/snippet}


{#snippet ItemGroup(groups: MenuItemGroup[])}
  {#each groups as group (group.id)}
    <li class={cn(expanded && "mb-1")}>
      <div>
        {#if group.label && expanded}
          <div class="comet-body-s font-medium truncate pb-1 pl-2.5 pr-3 pt-3 text-light-slate">
            {group.label}
          </div>
        {/if}

        <ul>
          {#each group.items as item}
            {@render Item(item, linkClasses)}
          {/each}
        </ul>
      </div>
    </li>
  {/each}
{/snippet}


{#snippet ExpandCollapseButton()}
  <Button
    variant="outline"
    size="sm"
    onclick={() => setExpanded(!expanded)}
    class={cn(
      "absolute -right-4 w-6 h-6 cursor-pointer top-1 hidden rounded-full z-50 group-hover:flex",
    )}
  >
    {#if expanded}
      <ChevronLeft size={12}/>
    {:else}
      <ChevronRight size={12}/>
    {/if}
  </Button>
{/snippet}


  



<aside class="comet-sidebar-width group h-[calc(100vh-var(--banner-height))] border-r transition-all">
  <div class="comet-header-height relative flex w-full items-center justify-between gap-6 border-b">
    <a
      href={HOME_PATH}
      class="absolute left-[18px] z-10 block"
    >
      <Logo expanded={expanded} />
  </a>
  </div>
  <div class="relative flex h-[calc(100%-var(--header-height))]">
    {@render ExpandCollapseButton()}
    <div class="flex min-h-0 grow flex-col scrollable justify-between overflow-auto px-3 py-4">
      <ul class="flex flex-col gap-1 pb-2">
        {@render ItemGroup(MENU_ITEMS)}
      </ul>
      <div class="flex flex-col gap-4">
        <Separator orientation="horizontal" />
        <ul class="flex flex-col gap-1">
          {#each bottomMenuItems as bItems}
            {@render Item(bItems, linkClasses)}
          {/each}
        </ul>
      </div>
    </div>
  </div>
</aside>
