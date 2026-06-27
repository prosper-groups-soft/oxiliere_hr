<script lang="ts">
  /**
   * Validation Error Component
   * 
   * Displays validation errors from Zod schema validation
   * Shows error message with icon when there's an error for the specified field
   */
  
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { slide } from "svelte/transition";
  
  interface Props {
    errors: Record<string, string>;
    field: string;
    class?: string;
  }
  
  let { 
    errors,
    field,
    class: className = ''
  }: Props = $props();
  
  const errorMessage = $derived.by(() => errors?.[field]);
  const hasError = $derived.by(() => !!errorMessage);
</script>


{#if hasError}
  <div class="flex items-center gap-1 text-red-500 mt-1 {className}" transition:slide={{ duration: 200 }}>
    <AppIcon name="circle-x" size={14} />
    <span class="text-[0.85rem]">{errorMessage}</span>
  </div>
{/if}

