<script lang="ts">
  import * as Tabs from "@/components/ui/tabs";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import type { TabDef, NavVariant } from "../types";
  import { goto } from "$app/navigation";

  let { tabs, activeId, variant = 'underline', onChange }: { tabs: TabDef[]; activeId: string; variant?: NavVariant; onChange?: (id: string) => void } = $props();

  let tabElements = $state<Record<string, HTMLElement | null>>({});
  let indicatorStyle = $state('');

  $effect(() => {
    const el = tabElements[activeId];
    if (el && variant === 'underline') indicatorStyle = `left:${el.offsetLeft}px; width:${el.offsetWidth}px;`;
  });

  function handleChange(value: string) {
    const tab = tabs.find(t => t.id === value);
    if (tab?.path) goto(tab.path);
    onChange?.(value);
  }
</script>

<Tabs.Root value={activeId} onValueChange={handleChange}>
  <Tabs.List class={cn("relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none", variant === 'pill' && "bg-slate-100/80 rounded-xl p-1 gap-0")}>
    {#each tabs as tab (tab.id)}
      <Tabs.Trigger bind:ref={tabElements[tab.id]} value={tab.id} class={cn("relative flex items-center gap-2.5 bg-transparent shadow-none rounded-none border-none px-1 pb-2.5 pt-1 outline-none focus-visible:ring-0 group cursor-pointer text-slate-700 data-[state=active]:text-primary", variant === 'pill' && "rounded-lg data-[state=active]:bg-white data-[state=active]:shadow-xs")}>
        <AppIcon name={tab.icon} size={16} class="group-data-[state=active]:text-primary text-slate-500" />
        <span class="text-[0.879rem] tracking-tight">{tab.label}</span>
        {#if tab.count !== undefined && tab.count > 0}<span class="rounded-full bg-primary text-white text-[0.7rem] px-1.5 py-0.5 font-medium">{tab.count}</span>{/if}
      </Tabs.Trigger>
    {/each}
    {#if variant === 'underline'}<div class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10" style={indicatorStyle}></div>{/if}
  </Tabs.List>
</Tabs.Root>
