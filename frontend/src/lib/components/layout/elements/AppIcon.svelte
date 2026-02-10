<script lang="ts">
  import { getAppIcon } from '$lib/utilities/ui/icons';
  import { cn } from '$lib/utils';
  import type { IconProps } from '@lucide/svelte';
  import type { Component } from 'svelte';

  interface Props {
    name: string;
    class?: string;
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
    fallback?: Component<IconProps, {}>;
    [key: string]: any;
  }

  let { 
    name, 
    class: className = '', 
    size = 18, 
    color, 
    strokeWidth = 2,
    fallback,
    ...rest 
  }: Props = $props();

  const IconComponent = $derived(getAppIcon(name, fallback));
</script>


<IconComponent 
  class={cn('shrink-0', className)} 
  {size} 
  {color} 
  {strokeWidth}
  style="width: {typeof size === 'number' ? size + 'px' : size}; height: {typeof size === 'number' ? size + 'px' : size};"
  {...rest}
/>
