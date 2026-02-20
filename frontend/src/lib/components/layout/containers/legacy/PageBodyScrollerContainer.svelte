<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import { useObserveResizeNode } from "@/hooks/useObserveResizeNode.svelte";
  import { pageBodyScrollState } from "./usePageBodyScroller.svelte";
  import { TABLE_WRAPPER_ATTRIBUTE, STICKY_ATTRIBUTE_VERTICAL } from "@/constants/ui/ui";

  let { 
    children,
    class:className = "",
  } = $props();

  let width = $state(0);
  let tableOffset = $state(0); 

  const calculateOffsets = (node: HTMLDivElement) => {
    const tableWrapper = node.querySelector(`[${TABLE_WRAPPER_ATTRIBUTE}]`);
    let tableOffset = 0;
    
    if (tableWrapper instanceof HTMLElement) {
      tableOffset = tableWrapper.offsetTop;
    }
    const verticalElements = node.querySelectorAll(
      `[${STICKY_ATTRIBUTE_VERTICAL}]`,
    );
    let offset = 0;
    verticalElements.forEach((element) => {
      element.setAttribute("style", `top: ${offset}px`);
      offset += element.clientHeight;
    });

    return { width: node.clientWidth, tableOffset: tableOffset };
  };


  let { ref } = useObserveResizeNode<HTMLDivElement>(
    (node: HTMLDivElement) => {
      const { width:_width, tableOffset:to } = calculateOffsets(node);
      width = _width;
      tableOffset = to;

      pageBodyScrollState.state.scrollContainer = node;
      pageBodyScrollState.state.tableOffset = to;
    },
  );

</script>


<div bind:this={ref} style:--scroll-body-client-width={width > 0 ? `${width}px` : undefined}
  class={cn(
    "relative h-[calc(100vh-var(--header-height)-var(--banner-height))] scrollable overflow-auto -mx-6",
    className,
  )}>
  {@render children?.()}
</div>

