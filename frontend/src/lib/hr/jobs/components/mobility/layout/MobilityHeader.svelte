<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import { cn } from "@/utilities/common/css";

  let {
    searchQuery = $bindable(''),
    activeTab = $bindable('transitions'),
    onSearchQueryChange
  } = $props<{
    searchQuery?: string;
    activeTab?: 'transitions' | 'vacancies';
    onSearchQueryChange?: (value: string) => void;
  }>();

  function handleTabChange(tab: 'transitions' | 'vacancies') {
    activeTab = tab;
  }

  function handleSearchChange(value: string) {
    searchQuery = value;
    onSearchQueryChange?.(value);
  }
</script>


<div class="flex items-center justify-between gap-4 pb-2 pt-0.5 border-b border-slate-100 px-4 bg-white/50 backdrop-blur-md pr-6">
  {@render Nav()}

  <!-- Search Bar -->
  <div class="flex-1 max-w-125">
    <SearchBar
      bind:value={searchQuery}
      onSearch={handleSearchChange}
      onClear={() => { onSearchQueryChange?.(''); }}
      placeholder={activeTab === 'transitions' ? 'Chercher un mouvement...' : 'Chercher un besoin...'}
      class="w-full"
      inputClass="h-9 pl-9 pr-9 rounded-[14px] text-[0.85rem] bg-[#f5f6f7]"
      iconSize={20}
    />
  </div>
</div>


{#snippet Nav()}
  <!-- Tabs Navigation -->
  <div class="relative inline-grid grid-cols-2 bg-slate-100 rounded-lg p-1 w-64 overflow-hidden">
    <!-- Sliding indicator -->
    <div class="absolute top-0.5 bottom-0.5 left-0.5 right-0.5 grid grid-cols-2 pointer-events-none">
      <div
        class={cn(
          "bg-white rounded-md shadow-fine border border-slate-200 transition-transform duration-300 ease-[cubic-bezier(0.22,1,0.36,1)]",
          activeTab === 'vacancies' && "translate-x-full"
        )}
      ></div>
    </div>

    <!-- Transitions Tab -->
    <button
      onclick={() => handleTabChange('transitions')}
      class={cn(
        "relative z-10 flex items-center justify-center gap-2 px-1.5 py-0.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
        activeTab === 'transitions' ? "text-primary" : "text-slate-600 hover:text-slate-800"
      )}
    >
      <AppIcon 
        name="refresh" 
        size={17} 
        strokeWidth={activeTab === 'transitions' ? 2 : 1.5}
        class={activeTab === 'transitions' ? "text-primary" : "text-slate-400"} 
      />
      Mouvements
    </button>

    <!-- Vacancies Tab -->
    <button
      onclick={() => handleTabChange('vacancies')}
      class={cn(
        "relative z-10 flex items-center justify-center gap-2 px-1.5 py-0.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
        activeTab === 'vacancies' ? "text-primary" : "text-slate-600 hover:text-slate-800"
      )}
    >
      <AppIcon 
        name="inbox" 
        size={17} 
        strokeWidth={activeTab === 'vacancies' ? 2 : 1.5}
        class={activeTab === 'vacancies' ? "text-primary" : "text-slate-400"} 
      />
      Besoins
    </button>
  </div>
{/snippet}

