<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import * as Collapsible from '@/components/ui/collapsible';
  import { cn } from '@/utilities/common/css';


  let {
    icon,
    title,
    description,
    iconClass = '',
    collapsible = true,
    defaultOpen = true,
    class: className,
    children,
  }: {
    icon: string;
    title: string;
    description?: string;
    iconClass?: string;
    /** Si true, la section peut être repliée/dépliée en cliquant sur l'en-tête. */
    collapsible?: boolean;
    /** État initial de la section (dépliée par défaut). */
    defaultOpen?: boolean;
    class?: string;
    children?: import('svelte').Snippet;
  } = $props();

  // `open` suit `defaultOpen` via l'effet (référence dans une closure →
  // pas de warning state_referenced_locally, et réagit aux changements de prop).
  let open = $state(false);
  $effect(() => {
    open = defaultOpen;
  });
</script>


<Card class={cn('border shadow-fine py-3.5!', className)}>
  <Collapsible.Root bind:open>
    <CardHeader class="pb-0">
      {#if collapsible}
        <button
          type="button"
          class="w-full flex items-center gap-3 text-left cursor-pointer group"
          onclick={() => (open = !open)}
          aria-expanded={open}
        >
          <div class={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0', iconClass)}>
            <AppIcon name={icon} size={18} />
          </div>
          <div class="flex-1 min-w-0">
            <CardTitle class="text-[0.92rem] font-bold text-slate-800 leading-tight">{title}</CardTitle>
            {#if description}
              <p class="text-[0.85rem] text-slate-500 mt-0.5">{description}</p>
            {/if}
          </div>
          <AppIcon
            name="chevron-down"
            size={16}
            class="text-slate-400 shrink-0 transition-transform duration-200 group-hover:text-slate-600 {open
              ? 'rotate-180'
              : ''}"
          />
        </button>
      {:else}
        <div class="flex items-center gap-3">
          <div class={cn('w-9 h-9 rounded-lg flex items-center justify-center shrink-0', iconClass)}>
            <AppIcon name={icon} size={18} />
          </div>
          <div>
            <CardTitle class="text-[0.92rem] font-bold text-slate-800 leading-tight">{title}</CardTitle>
            {#if description}
              <p class="text-[0.85rem] text-slate-500 mt-0.5">{description}</p>
            {/if}
          </div>
        </div>
      {/if}
    </CardHeader>

    <Collapsible.Content
      forceMount
      class="grid overflow-hidden transition-all duration-300 ease-in-out data-[state=closed]:grid-rows-[0fr] data-[state=open]:grid-rows-[1fr]"
    >
      <div class="min-h-0">
        <CardContent class={open ? 'pt-4 pb-4' : 'p-0'}>
          {@render children?.()}
        </CardContent>
      </div>
    </Collapsible.Content>
  </Collapsible.Root>
</Card>

