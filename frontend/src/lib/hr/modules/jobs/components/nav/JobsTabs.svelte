<script lang="ts">
  import { crossfade } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import { page } from '$app/state';
  import { hr } from '@/hr/constants/navigation/navigation';
  import { goto, preloadData } from '$app/navigation';
  import { cn } from '@/hr/utilities/common/css'; 
  import * as Tabs from '@/components/ui/tabs';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  

  const TABS = [
    { id: 'chart', label: 'Organigramme', icon: 'network', path: hr('/jobs/chart') },
    { id: 'careers', label: 'Carrières', icon: 'graduation-cap', path: hr('/jobs/careers') },
    { id: 'mobility', label: 'Mobilité', icon: 'refresh-cw', path: hr('/jobs/mobility') },
  ];
 
  /**
   * Reactive value for the active tab ID based on the current path segment.
   */
  const activeTabId = $derived(() => {
    const path = page.url.pathname.replace(/\/$/, '');
    
    const currentTab = TABS.find(t => path.includes(t.path));
    return currentTab ? currentTab.id : 'chart';
  });

  const handleTabChange = (value: string) => {
    const targetTab = TABS.find(t => t.id === value);
    if (targetTab) {
      // Defer URL update using requestIdleCallback
      const scheduleUpdate = typeof requestIdleCallback !== 'undefined' 
        ? (cb: () => void) => requestIdleCallback(cb, { timeout: 100 })
        : (cb: () => void) => setTimeout(cb, 0);
      
      scheduleUpdate(() => {
        goto(targetTab.path);
      });
    }
  };

  const [send, receive] = crossfade({
    duration: 300,
    easing: cubicInOut
  });
</script>


{#snippet TabTrigger(tab: typeof TABS[0])}
  <Tabs.Trigger 
    value={tab.id}
    onmouseenter={() => preloadData(tab.path)}
    data-sveltekit-preload-data="tap"
    class={cn(
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-2 pb-2 outline-none focus-visible:ring-0",
      "group cursor-pointer text-slate-800",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="group-data-[state=active]:text-primary text-slate-500" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>  

    {#if activeTabId() === tab.id}
      <div 
        in:receive={{ key: 'active-bar' }}
        out:send={{ key: 'active-bar' }}
        class="absolute bottom-0 left-0 right-0 h-1 rounded-full bg-primary z-10"
      ></div>
    {/if}
  </Tabs.Trigger>
{/snippet}


<div class="bg-white border-b border-slate-100 mb-2 mt-1.5 px-4">
  <div class="flex items-center justify-between">
    <Tabs.Root value={activeTabId()} onValueChange={handleTabChange} class="w-full">
      <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-5 border-none">
        {#each TABS as tab}
          {@render TabTrigger(tab)}
        {/each}
      </Tabs.List>
    </Tabs.Root>
    
    <!-- Add buttons here -->
    <div>
    </div>
  </div>
</div>

