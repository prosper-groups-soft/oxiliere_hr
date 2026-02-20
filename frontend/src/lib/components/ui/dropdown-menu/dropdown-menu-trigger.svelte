<script lang="ts">
  import { DropdownMenu as DropdownMenuPrimitive } from "bits-ui";
  import type { Snippet } from "svelte";

  let { 
    ref = $bindable(null), 
    asChild = false, 
    children,
    child,
    ...restProps 
  }: {
    ref?: HTMLElement | null;
    asChild?: boolean;
    children?: Snippet;
    child?: Snippet<[{ props: Record<string, any> }]>;
    [key: string]: any;
  } = $props();
</script>


<DropdownMenuPrimitive.Trigger 
  bind:ref 
  {children}
  {child}
  data-slot="dropdown-menu-trigger" 
  {...restProps} 
/>

