<script lang="ts">
  import { buttonVariants } from "@/components/ui/button";
  import * as Tooltip from "@/components/ui/tooltip";
  import { cn } from "@/utils";

  const { 
  content,
  children,
  side,
  hotkeys = null,
  delayDuration = 300,
  defaultOpen = false,
  stopClickPropagation = true,
  } = $props();
</script>


<Tooltip.Provider>
  <Tooltip.Root>
    <Tooltip.Trigger class={cn(buttonVariants({ variant: "ghost" }), 'px-0 w-full cursor-pointer')}>
      {@render children?.()}
    </Tooltip.Trigger>
    <Tooltip.Content class="z-[200]" side={side} collisionPadding={16} {...(stopClickPropagation && { onClick: (event: Event) => event.stopPropagation() })}>
      {content}

      {#if hotkeys}
        <div class="ml-2 flex gap-1">
          {#each hotkeys as [hotkey, idx] (idx)}
            <div class="flex h-5 min-w-5 items-center justify-center rounded-sm border border-light-slate px-1 text-light-slate">
              {hotkey}
            </div>
            {#if idx < hotkeys.length - 1}
              <div class="text-light-slate">+</div>
            {/if}
          {/each}
        </div>
      {/if}

      {#if hotkeys?.length} 
        ARROW
      {/if}
    </Tooltip.Content>
  </Tooltip.Root>
</Tooltip.Provider>

