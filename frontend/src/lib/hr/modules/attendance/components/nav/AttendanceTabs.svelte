<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { page } from '$app/state';
  import { hr } from '@/hr/constants/navigation/navigation';


  const TABS = [
    { id: 'register', label: 'Suivi', icon: 'clipboard-list', path: hr('/attendance/register') },
    { id: 'config', label: 'Planning', icon: 'calendar-days', path: hr('/attendance/config') },
    { id: 'policies', label: 'Modèles', icon: 'layout-template', path: hr('/attendance/policies') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/attendance/settings') },
  ];

  // Active Tab derived from current URL
  const activeTabId = $derived.by(() => {
    const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'register';
  });

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLAnchorElement | null>>({
    register: null,
    config: null,
    policies: null,
    settings: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <nav class="relative flex items-center gap-5 pt-0.5">
    {#each TABS as tab}
      <a 
        bind:this={tabElements[tab.id]}
        href={tab.path}
        data-sveltekit-noscroll
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
      </a>
    {/each}

    <!-- Sliding Indicator -->
    <div 
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out"
      style={indicatorStyle}
    ></div>
  </nav>
</div>

