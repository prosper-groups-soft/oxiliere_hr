<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import { STICKY_ATTRIBUTE_VERTICAL, STICKY_DIRECTION } from "@/constants/ui/ui";

  let { 
    children,
    class:className = "", 
    direction = STICKY_DIRECTION.vertical,
    limitWidth = false
  } = $props();
</script>


<div
  {...((direction === STICKY_DIRECTION.vertical ||
  direction === STICKY_DIRECTION.bidirectional) && {
    [STICKY_ATTRIBUTE_VERTICAL]: direction,
  })}
  class={cn(
    "sticky z-10 bg-soft-background px-6",
    direction === STICKY_DIRECTION.horizontal && "left-0",
    direction === STICKY_DIRECTION.vertical && "top-0",
    direction === STICKY_DIRECTION.bidirectional && "left-0 top-0",
    limitWidth &&
        "w-(--scroll-body-client-width,var(--comet-content-width))",
    className,
  )}
>
  {@render children?.()}
</div>

