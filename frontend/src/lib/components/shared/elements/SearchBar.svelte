<script lang="ts">
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { cn } from "@/utilities/common/css";

  
  let { 
    value = $bindable(), 
    placeholder = "Rechercher...", 
    class: className = "",
    inputClass = "",
    iconSize = 20,
    debounceMs = 350,
    onSearch = (query: string) => {},
    onClear = () => value = ""
  } = $props<{
    value: string;
    placeholder?: string;
    class?: string;
    inputClass?: string;
    iconSize?: number;
    debounceMs?: number;
    onSearch?: (query: string) => void;
    onClear?: () => void;
  }>();

  // Internal state for debounce loading
  let isSearching = $state(false);
  let searchTimeout: ReturnType<typeof setTimeout> | null = null;

  function handleInput() {
    isSearching = true;
    if (searchTimeout) clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      isSearching = false;
      onSearch(value);
    }, debounceMs);
  }

  function handleClear() {
    if (searchTimeout) clearTimeout(searchTimeout);
    isSearching = false;
    onClear();
  }
</script>


<div class={cn("relative group shrink-0", className)}>
  <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-all">
    {#if isSearching}
      <AnimateSpin class="border-primary size-4" text="" />
    {:else}
      <AppIcon name="search" size={iconSize} />
    {/if}
  </div>

  <Input 
    type="text" 
    {placeholder} 
    oninput={handleInput}
    class={cn(
      "w-full bg-slate-50 border-slate-100 focus:bg-white focus:ring-4 focus:ring-primary/5 transition-all shadow-none",
      inputClass
    )}
    bind:value
  />

  {#if value}
    <button 
      class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
      onclick={handleClear}
    >
      <AppIcon name="x" size={iconSize - 2} />
    </button>
  {/if}
</div>

