<script lang="ts">
  import type { Snippet } from "svelte";
  import { buttonVariants } from "@/components/ui/button";
  import * as Tooltip from "@/components/ui/tooltip";
  import { cn } from "@/utilities/common/css";

  
  const { 
  content,
  children,
  side,
  hotkeys = null,
  delayDuration = 300,
  defaultOpen = false,
  stopClickPropagation = true,
  asChild = false,
  contentClass = '',
  }: {
    content: string;
    children: Snippet<[any]>;
    contentClass?: string;
    side?: "top" | "bottom" | "left" | "right";
    hotkeys?: [string, number][] | null;
    delayDuration?: number;
    defaultOpen?: boolean;
    stopClickPropagation?: boolean;
    asChild?: boolean;
  } = $props();
</script>


<Tooltip.Provider {delayDuration}>
  <Tooltip.Root open={defaultOpen}>
    <Tooltip.Trigger>
      {#snippet child({ props })}
        {#if asChild}
          {@render children?.(props)}
        {:else}
          <button 
            {...props} 
            class={cn(buttonVariants({ variant: "ghost" }), 'px-0 w-full cursor-pointer hover:bg-white!')}
          >
            {@render children?.(undefined)}
          </button>
        {/if}
      {/snippet}
    </Tooltip.Trigger>
    <Tooltip.Content 
      class={cn('z-200', contentClass)} 
      side={side} 
      collisionPadding={16} 
      {...(stopClickPropagation && { onClick: (event: Event) => event.stopPropagation() })}
    >
      <div class="flex items-center gap-3">
        <span class="text-[0.83rem]">{content}</span>

        {#if hotkeys}
          <div class="flex gap-1">
            {#each hotkeys as [hotkey, idx] (idx)}
              <div class="flex h-5 min-w-5 items-center justify-center rounded-sm border border-slate-700 bg-slate-800 px-1 text-[0.83rem] text-slate-400">
                {hotkey}
              </div>
              {#if idx < hotkeys.length - 1}
                <span class="text-slate-500">+</span>
              {/if}
            {/each}
          </div>
        {/if}
      </div>
    </Tooltip.Content>
  </Tooltip.Root>
</Tooltip.Provider>

