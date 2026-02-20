<script lang="ts">
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import * as Breadcrumb from "@/components/ui/breadcrumb";
  import { NAV_CONFIG } from "@/constants/features/navigation";

  // --- Props ---
  let { items = [] } = $props();

  // --- Reactive Logic ---
  const displayItems = $derived.by(() => {
    const max = NAV_CONFIG.maxBreadcrumbItems;
    
    if (items.length <= max) return items;

    const first = items[0];
    const last = items[items.length - 1];
    const middleCount = max - 2;
    const middleItems = items.slice(items.length - 1 - middleCount, items.length - 1);

    return [
      first,
      { label: '...', href: '#', isEllipsis: true },
      ...middleItems,
      last
    ];
  });
</script>


<div class="flex items-center h-10 px-4 border-b border-slate-100 bg-white overflow-hidden">
  <Breadcrumb.Root>
    <Breadcrumb.List class="flex items-center">
      
      <!-- Stable Home Anchor: Never animates to provide a visual focal point -->
      <Breadcrumb.Item>
        <Breadcrumb.Link href="/" class="flex items-center px-1 hover:text-primary transition-colors">
          <AppIcon name="home" size={16} class="text-slate-600"/>
        </Breadcrumb.Link>
      </Breadcrumb.Item>

      {#each displayItems as item, i (item.href + item.label)}
        <!-- Structural Separator: Static or animated based on position -->
        <Breadcrumb.Separator class="text-slate-500 mx-1" />
        
        <Breadcrumb.Item>
          <!-- 
            Label Transition: 
            - Animation is disabled for the first item (i === 0) to keep the start of the chain stable
            - Fly effect is also disabled if only one item is present
          -->
          <div 
            in:fly={{ 
              y: (items.length > 1 && i !== 0) ? 6 : 0, 
              duration: i === 0 ? 0 : 450, 
              delay: i === 0 ? 0 : i * 30, 
              easing: quintOut 
            }}
          >
            {#if item.isEllipsis}
              <Breadcrumb.Ellipsis class="size-4 text-slate-500" />
            {:else if i === displayItems.length - 1}
              <Breadcrumb.Page class="text-[0.84rem] font-medium text-slate-900 leading-none px-1">
                {item.label}
              </Breadcrumb.Page>
            {:else}
              <Breadcrumb.Link 
                href={item.href} 
                class="text-[0.84rem] text-slate-700 hover:text-indigo-800 transition-colors leading-none px-1"
              >
                {item.label}
              </Breadcrumb.Link>
            {/if}
          </div>
        </Breadcrumb.Item>
      {/each}
    </Breadcrumb.List>
  </Breadcrumb.Root>
</div>

