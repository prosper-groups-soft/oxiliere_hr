<script lang="ts">
  import { cn } from "@/utilities/common/css";
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

  let tabElements = $state<Record<string, HTMLButtonElement | null>>({});
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


<nav class="relative flex items-center gap-5">
  {#each tabs as tab}
    <button 
      bind:this={tabElements[tab.id]}
      onclick={() => onTabChange(tab.id)}
      class={cn(
        "relative flex items-center gap-2.5 bg-transparent transition-colors duration-200",
        "px-1 pb-2.5 pt-1 outline-none focus-visible:ring-0",
        "group cursor-pointer",
        activeTabId === tab.id
          ? "text-primary"
          : "text-slate-700 hover:text-slate-800"
      )}
    >
      <AppIcon name={tab.icon} size={18} />
      <span class="text-[0.879rem] tracking-tight">{tab.label}</span>
    </button>
  {/each}

  <!-- Sliding Indicator -->
  <div 
    class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out"
    style={indicatorStyle}
  ></div>
</nav>
