<script lang="ts">
  import { Checkbox } from "@/components/ui/checkbox";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";

  export interface Props {
    id: string;
    title: string;
    subtitle?: string;
    checked: boolean;
    onToggle: () => void;
    disabled?: boolean;
    class?: string;
    expandButton?: {
      isExpanded: boolean;
      onToggle: (e: Event) => void;
      title?: string;
    } | null;
  }

  let { 
    id, 
    title, 
    subtitle, 
    checked, 
    onToggle, 
    disabled = false,
    class: className,
    expandButton = null 
  }: Props = $props();
</script>

<div class={cn("flex items-center gap-3 p-3 transition-opacity", className)} class:cursor-pointer={!disabled} class:opacity-50={disabled} onclick={(e) => !disabled && expandButton?.onToggle(e)} role="none">
  <div onclick={(e) => { e.stopPropagation(); }} role="none">
    <Checkbox 
      {id}
      {checked}
      onCheckedChange={!disabled ? onToggle : () => {}}
      disabled={disabled}
      class="data-[state=checked]:bg-indigo-600 data-[state=checked]:border-indigo-600 h-4 w-4 rounded-sm shrink-0 {disabled ? 'cursor-not-allowed' : 'cursor-pointer'}"
    />
  </div>
  <div class="flex-1 min-w-0">
    <p class="text-[0.86rem] text-slate-800 truncate">
      {title}
    </p>
    {#if subtitle}
      <p class="text-[0.82rem] text-slate-500 truncate">
        {subtitle}
      </p>
    {/if}
  </div>
  {#if expandButton}
    <button
      class="p-1.5 rounded-md hover:bg-slate-100 transition-colors shrink-0"
      class:text-indigo-600={expandButton.isExpanded}
      class:text-slate-400={!expandButton.isExpanded}
      onclick={expandButton.onToggle}
      title={expandButton.title || "Voir plus"}
    >
      <AppIcon 
        name="chevron-down" 
        size={16} 
        class="transition-transform duration-200 {expandButton.isExpanded ? 'rotate-180' : ''}" 
      />
    </button>
  {/if}
</div>

