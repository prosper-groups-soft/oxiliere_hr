<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import type { Snippet } from "svelte";

  let { 
    open = $bindable(false), 
    title, 
    children,
    footer
  } = $props<{
    open: boolean;
    title: string;
    children: Snippet;
    footer?: Snippet;
  }>();
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem]">{title}</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6">
      {@render children()}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      {#if footer}
        {@render footer()}
      {/if}
      <Sheet.Close class="flex-1 cursor-pointer">
        <div class="inline-flex h-9 w-full items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring">
          Fermer
        </div>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>

