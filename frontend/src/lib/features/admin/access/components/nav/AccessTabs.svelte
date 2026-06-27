<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import * as Tabs from '@/components/ui/tabs';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';

  interface Tab {
    id: string;
    label: string;
    icon: string;
  }

  interface Props {
    tabs: Tab[];
    activeTabId: string;
    onTabChange: (tabId: string) => void;
  }

  const { tabs, activeTabId, onTabChange }: Props = $props();

  let tabElements = $state<Record<string, HTMLElement | null>>({
    users: null, groups: null, roles: null
  });
  let indicatorStyle = $state('');

  function handleValueChange(value: string) {
    onTabChange(value);
  }

  // Keep $effect for indicator position updates
  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


<Tabs.Root value={activeTabId} onValueChange={handleValueChange} class="w-full">
  <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none overflow-visible">
    {#each tabs as tab}
      <Tabs.Trigger
        value={tab.id}
        bind:ref={tabElements[tab.id]}
        class={cn(
          "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-200",
          "rounded-none border-none px-1 pb-2.5 pt-1 outline-none focus-visible:ring-0",
          "group cursor-pointer text-slate-700",
          "data-[state=active]:text-primary data-[state=active]:bg-transparent",
          "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
          "data-[state=active]:focus:bg-transparent"
        )}
      >
        <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary" />
        <span class="text-[0.879rem] tracking-tight">{tab.label}</span>
      </Tabs.Trigger>
    {/each}

    <!-- Sliding Indicator -->
    <div
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10"
      style={indicatorStyle}
    ></div>
  </Tabs.List>
</Tabs.Root>

