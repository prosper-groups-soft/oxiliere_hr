<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import { cn } from "@/utilities/common/css";

  let {
    searchQuery = $bindable(''),
    activeTab = $bindable('positions'),
    onSearchQueryChange,
    onClear
  } = $props<{
    searchQuery?: string;
    activeTab?: 'positions' | 'seniority';
    onSearchQueryChange?: (value: string) => void;
    onClear?: () => void;
  }>();

  function handleTabChange(tab: 'positions' | 'seniority') {
    activeTab = tab;
  }

  function handleSearchChange(value: string) {
    searchQuery = value;
    onSearchQueryChange?.(value);
  }

  function handleClear() {
    searchQuery = '';
    onClear?.();
  }
</script>


<div class="flex items-center justify-between gap-4 pb-2 pt-0.5 border-b border-slate-100 px-4 bg-white/50 backdrop-blur-md pr-6">
  {@render Nav()}
  <!-- Search Bar -->
  <div class="flex-1 max-w-125">
    <SearchBar
      bind:value={searchQuery}
      onSearch={handleSearchChange}
      onClear={handleClear}
      placeholder={activeTab === 'positions' ? 'Chercher un poste...' : 'Chercher un niveau...'}
      class="w-full"
      inputClass="h-9 pl-9 pr-9 rounded-[14px] text-[0.85rem] bg-[#f5f6f7]"
      iconSize={20}
    />
  </div>
</div>


{#snippet Nav()}
  <!-- Tabs Navigation -->
  <div class="relative inline-grid grid-cols-2 bg-slate-100 rounded-lg p-1 w-55 overflow-hidden">
    <!-- Sliding indicator -->
    <div class="absolute top-0.5 bottom-0.5 left-0.5 right-0.5 grid grid-cols-2 pointer-events-none">
      <div
        class={cn(
          "bg-white rounded-md shadow-fine border border-slate-200 transition-transform duration-300 ease-[cubic-bezier(0.22,1,0.36,1)]",
          activeTab === 'seniority' && "translate-x-full"
        )}
      ></div>
    </div>

    <!-- Positions Tab -->
    <button
      onclick={() => handleTabChange('positions')}
      class={cn(
        "relative z-10 flex items-center justify-center gap-2 px-1.5 py-0.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
        activeTab === 'positions' ? "text-primary" : "text-slate-600 hover:text-slate-800"
      )}
    >
      <AppIcon 
        name="briefcase" 
        size={17} 
        strokeWidth={activeTab === 'positions' ? 2 : 1.5}
        class={activeTab === 'positions' ? "text-primary" : "text-slate-500"} 
      />
      Postes
    </button>

    <!-- Seniority Tab -->
    <button
      onclick={() => handleTabChange('seniority')}
      class={cn(
        "relative z-10 flex items-center justify-center gap-2 px-1.5 py-0.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
        activeTab === 'seniority' ? "text-primary" : "text-slate-600 hover:text-slate-800"
      )}
    >
      <AppIcon 
        name="layers" 
        size={17} 
        strokeWidth={activeTab === 'seniority' ? 2 : 1.5}
        class={activeTab === 'seniority' ? "text-primary" : "text-slate-500"} 
      />
      Niveaux
    </button>
  </div>
{/snippet}

