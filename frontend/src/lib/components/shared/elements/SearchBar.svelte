<script lang="ts">
  import { Input } from "@/components/ui/input";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";

  let { 
    value = $bindable(), 
    placeholder = "Rechercher...", 
    class: className = "",
    inputClass = "",
    iconSize = 20,
    onClear = () => value = "",
    onInput = () => {}
  } = $props<{
    value: string;
    placeholder?: string;
    class?: string;
    inputClass?: string;
    iconSize?: number;
    onClear?: () => void;
    onInput?: (e: Event) => void;
  }>();
</script>


<div class={cn("relative group shrink-0", className)}>
  <div class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-all">
    <AppIcon name="search" size={iconSize} />
  </div>

  <Input 
    type="text" 
    {placeholder} 
    oninput={onInput}
    class={cn(
      "w-full bg-slate-50 border-slate-100 focus:bg-white focus:ring-4 focus:ring-primary/5 transition-all shadow-none",
      inputClass
    )}
    bind:value
  />

  {#if value}
    <button 
      class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
      onclick={onClear}
    >
      <AppIcon name="x" size={iconSize - 2} />
    </button>
  {/if}
</div>

