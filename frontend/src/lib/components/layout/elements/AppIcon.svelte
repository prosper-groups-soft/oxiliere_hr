<script lang="ts">
  import { getAppIconAsync, hasAppIcon } from '@/utilities/ui/icons';
  import { cn } from '@/utilities/common/css';
  import type { Component } from 'svelte';
  import { Package, type IconProps } from '@lucide/svelte';

  type Icon = Component<IconProps, {}>;

  interface Props {
    name: string;
    class?: string;
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
    fallback?: Icon;
    [key: string]: any;
  }

  let { 
    name, 
    class: className = '', 
    size = 18, 
    color, 
    strokeWidth = 1.6,
    fallback = Package,
    ...rest 
  }: Props = $props();

  let IconComponent: Icon | null = $state(null);
  let isLoading = $state(true);

  $effect(() => {
    isLoading = true;
    IconComponent = null;
    
    // Check if icon exists first
    if (!name || !hasAppIcon(name)) {
      IconComponent = fallback;
      isLoading = false;
      return;
    }
    
    // Load icon asynchronously
    getAppIconAsync(name)
      .then((icon) => {
        IconComponent = icon;
      })
      .catch(() => {
        IconComponent = fallback;
      })
      .finally(() => {
        isLoading = false;
      });
  });
</script>

{#if isLoading}
  <!-- Loading placeholder with X icon -->
  <div 
    class={cn('shrink-0 flex items-center justify-center text-[#b0bec5]!', className)} 
    style="width: {typeof size === 'number' ? size + 'px' : size}; height: {typeof size === 'number' ? size + 'px' : size};"
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="{typeof size === 'number' ? size * 0.6 : '60%'}" height="{typeof size === 'number' ? size * 0.6 : '60%'}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M18 6 6 18"/>
      <path d="m6 6 12 12"/>
    </svg>
  </div>
{:else if IconComponent}
  {@const Icon = IconComponent}
  <Icon 
    class={cn('shrink-0', className)} 
    {size} 
    {color} 
    {strokeWidth}
    style="width: {typeof size === 'number' ? size + 'px' : size}; height: {typeof size === 'number' ? size + 'px' : size};"
    {...rest}
  />
{:else}
  {@const Fallback = fallback}
  <Fallback 
    class={cn('shrink-0', className)} 
    {size} 
    {color} 
    {strokeWidth}
    style="width: {typeof size === 'number' ? size + 'px' : size}; height: {typeof size === 'number' ? size + 'px' : size};"
    {...rest}
  />
{/if}

