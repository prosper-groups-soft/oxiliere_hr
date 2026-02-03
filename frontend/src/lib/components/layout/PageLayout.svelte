<script lang="ts">
    // import SideBar from "$lib/components/layout/SideBar.svelte";
    import TopBar from "$lib/components/layout/TopBar.svelte";
    import { cn } from "$lib/utils";
    import { sideBarExpanded } from "$lib/stores/ui";

    
    
    let expanded = $state(true);
    let bannerHeight = $state(0);

    const setExpanded = (_expanded: boolean) => {
        sideBarExpanded.set(_expanded);
        expanded = _expanded;
    }

    let { children } = $props();


</script>

<section class={cn(
    "relative flex h-screen bg-linear-to-br from-slate-50 via-blue-50 to-indigo-50 min-h-0 w-screen min-w-0 flex-col " + (expanded ? "comet-expanded" : ""),
    )}
    style:--banner-height={`${bannerHeight}px`}>

    <!-- <SideBar expanded={expanded} setExpanded={setExpanded} />
    <main class="comet-content-inset absolute bottom-0 right-0 top-[var(--banner-height)] flex transition-all"> -->
    
    <main class="grow w-full absolute bottom-0 right-0 top-(--banner-height) flex transition-all">
        <TopBar />
        <section class="comet-header-inset absolute inset-x-0 bottom-0 scrollable overflow-auto bg-soft-background sm:px-6">
            {@render children?.()}
        </section>
    </main>
</section>
