<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import * as Tabs from '@/components/ui/tabs';

  
  interface TabDef {
    id: string;
    label: string;
    icon: string;
  }

  let {
    tabs,
    activeTab,
    onTabChange,
  }: {
    tabs: TabDef[];
    activeTab: string;
    onTabChange: (value: string) => void;
  } = $props();

  /** Références DOM des triggers pour mesurer la largeur de l'indicateur */
  let tabRefs = $state<(HTMLElement | null)[]>([]);

  /**
   * Pré-remplit le tableau avec null AVANT le rendu.
   * bind:ref exige null (pas undefined) : sans ceci, le premier rendu
   * déclencherait props_invalid_value (Cannot do bind:ref={undefined}).
   */
  $effect.pre(() => {
    tabRefs = tabs.map(() => null);
  });

  const activeTabIndex = $derived(tabs.findIndex((t) => t.id === activeTab));
  const activeTabWidth = $derived(tabRefs[activeTabIndex]?.offsetWidth ?? 0);
  const activeTabLeft = $derived(
    tabRefs.slice(0, activeTabIndex).reduce((acc, el) => acc + (el?.offsetWidth ?? 0), 0)
  );
</script>


<Tabs.Root value={activeTab} onValueChange={onTabChange} class="mb-6">
  <div class="relative w-fit">
    <Tabs.List variant="default" class="w-fit gap-0 bg-slate-100/80 rounded-xl p-1">
      {#each tabs as tab, i}
        <Tabs.Trigger
          bind:ref={tabRefs[i]}
          value={tab.id}
          class="gap-2 px-4 py-1.5 text-[0.84rem] font-semibold cursor-pointer rounded-lg bg-transparent transition-colors duration-200 data-[state=active]:bg-transparent data-[state=active]:text-primary data-[state=active]:hover:text-primary data-[state=active]:hover:bg-transparent relative z-10"
        >
          <AppIcon name={tab.icon} size={16} />
          {tab.label}
        </Tabs.Trigger>
      {/each}
    </Tabs.List>

    <!-- Indicateur qui glisse -->
    <div
      class="absolute top-1 bottom-1 left-1 rounded-lg bg-white shadow-xs border border-slate-200/80 transition-[left,width] duration-300 ease-out z-0"
      style={`left: ${activeTabLeft + 4}px; width: ${activeTabWidth}px;`}
    >
    </div>
  </div>
</Tabs.Root>

