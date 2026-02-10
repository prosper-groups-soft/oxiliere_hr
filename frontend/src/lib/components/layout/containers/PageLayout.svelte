<script lang="ts">
  import SideBar from "@/components/layout/shell/SideBar.svelte";
  import TopBar from "@/components/layout/shell/TopBar.svelte";
  import { sideBarExpanded } from "@/stores/ui";

  let expanded = $state(true);
  let { children } = $props();

  const setExpanded = (_expanded: boolean) => {
    sideBarExpanded.set(_expanded);
    expanded = _expanded;
  }
</script>


<div class="flex h-screen w-screen overflow-hidden">
    
  <aside class="shrink-0 z-[100] relative bg-white h-full">
    <SideBar {expanded} {setExpanded} />
  </aside>

  <div class="flex flex-col flex-1 min-w-0 overflow-hidden" style="background-color: #ffffff;">
    <header class="z-50 bg-white">
      <TopBar />
    </header>
        
    <main class="flex-1 min-w-0 overflow-y-auto py-2 sm:px-6">
      <div class="mx-auto max-w-7xl h-full flex flex-col">
        {@render children?.()}
      </div>
    </main>
  </div>
</div>

