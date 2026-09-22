<script lang="ts">
  import { EVENT_TYPE_COLORS, EVENT_TYPE_LABELS } from "../../types/types";
  import type { CalendarEvent } from "../../types/types";
  import { formatTimeDisplay, formatDateRange } from "../../constants/event.helpers";

  
  let {
    date,
    events,
    placement = "top",
    children,
  }: {
    date: Date;
    events: CalendarEvent[];
    placement?: "top" | "bottom";
    children: import("svelte").Snippet;
  } = $props();

  let isVisible = $state(false);
  let tooltipEl = $state<HTMLDivElement>();
  let wrapperEl = $state<HTMLDivElement>();
  let resolvedPlacement = $state<"top" | "bottom">("top");
  let hideTimeout: ReturnType<typeof setTimeout> | undefined = $state(undefined);

  $effect(() => {
    resolvedPlacement = placement;
  });

  const formattedDate = $derived(
    date.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  );

  function show() {
    if (events.length === 0) return;
    clearTimeout(hideTimeout);
    isVisible = true;
    requestAnimationFrame(() => computePlacement());
  }

  function scheduleHide() {
    hideTimeout = setTimeout(() => {
      isVisible = false;
    }, 120);
  }

  function computePlacement() {
    if (!tooltipEl || !wrapperEl) return;
    const wrapperRect = wrapperEl.getBoundingClientRect();
    const tooltipRect = tooltipEl.getBoundingClientRect();
    const spaceBelow = window.innerHeight - wrapperRect.bottom;
    const spaceAbove = wrapperRect.top;

    if (placement === "top" && spaceAbove < tooltipRect.height + 16 && spaceBelow >= tooltipRect.height + 16) {
      resolvedPlacement = "bottom";
    } else if (placement === "bottom" && spaceBelow < tooltipRect.height + 16 && spaceAbove >= tooltipRect.height + 16) {
      resolvedPlacement = "top";
    } else {
      resolvedPlacement = placement;
    }

    const tooltipWidth = tooltipRect.width;
    const halfWidth = tooltipWidth / 2;
    const wrapperCenterX = wrapperRect.left + wrapperRect.width / 2;
    let offsetX = 0;

    const leftEdge = wrapperCenterX - halfWidth;
    const rightEdge = wrapperCenterX + halfWidth;
    const margin = 12;

    if (leftEdge < margin) {
      offsetX = margin - leftEdge;
    } else if (rightEdge > window.innerWidth - margin) {
      offsetX = (window.innerWidth - margin) - rightEdge;
    }

    const finalX = wrapperCenterX - halfWidth + offsetX;
    let finalY: number;

    if (resolvedPlacement === "top") {
      finalY = wrapperRect.top - tooltipRect.height - 10;
    } else {
      finalY = wrapperRect.bottom + 10;
    }

    tooltipEl.style.left = finalX + 'px';
    tooltipEl.style.top = finalY + 'px';
  }
</script>

<div
  bind:this={wrapperEl}
  class="tooltip-wrapper w-full h-full"
  role="none"
  onmouseenter={show}
  onmouseleave={scheduleHide}
>
  <div class="trigger-inner w-full h-full">
    {@render children()}
  </div>

  {#if isVisible && events.length > 0}
    <div
      bind:this={tooltipEl}
      class="tooltip-content {resolvedPlacement === 'bottom' ? 'placement-bottom' : 'placement-top'}"
      role="tooltip"
      onmouseenter={show}
      onmouseleave={scheduleHide}
    >
      <div class="tooltip-arrow"></div>
      <div class="tooltip-header">
        <span class="tooltip-title text-sm capitalize">{formattedDate}</span>
      </div>
      <div class="tooltip-divider"></div>
      <div class="tooltip-body">
        {#each events as event}
          {@const typeColor = EVENT_TYPE_COLORS[event.type] || EVENT_TYPE_COLORS.holiday}
          {@const timeDisplay = formatTimeDisplay(event)}
          {@const rangeDisplay = formatDateRange(event)}
          {@const hasRange = event.endDate && event.endDate !== event.defaultDate}
          
          <div class="event-row">
            <div class="event-indicator">
              <div class="tooltip-type-dot {typeColor.dot}"></div>
            </div>
            <div class="event-details">
              <span class="event-title">{event.title}</span>
              {#if timeDisplay}
                <span class="event-meta">{timeDisplay}</span>
              {:else if hasRange}
                <span class="event-meta">{rangeDisplay}</span>
              {:else}
                <span class="event-meta">Toute la journée</span>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .tooltip-wrapper { position: relative; display: inline-block; }
  .trigger-inner { display: flex; align-items: center; justify-content: center; }

  .tooltip-content {
    position: fixed; z-index: 9999; min-width: 200px; max-width: 280px; padding: 0;
    border-radius: 12px; font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    pointer-events: auto; animation: tooltipFadeIn 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.08),
      0 2px 8px rgba(0, 0, 0, 0.04),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);
    color: #1e293b;
  }

  .tooltip-content .tooltip-title { color: #0f172a; font-weight: 600; font-size: 0.8rem; }
  .tooltip-content .tooltip-divider { height: 1px; margin: 8px 14px; background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.25), transparent); }

  .tooltip-arrow { position: absolute; width: 12px; height: 12px; left: 50%; translate: -50% 0; rotate: 45deg; z-index: -1; }

  .placement-top .tooltip-arrow {
    bottom: -6px;
    background: #ffffff;
    border-right: 1px solid rgba(226, 232, 240, 0.9);
    border-bottom: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.04);
  }

  .placement-bottom .tooltip-arrow {
    top: -6px;
    background: #ffffff;
    border-left: 1px solid rgba(226, 232, 240, 0.9);
    border-top: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow: -4px -4px 8px rgba(0, 0, 0, 0.04);
  }

  .tooltip-header { padding: 12px 14px 0; text-align: center; }

  .tooltip-body { padding: 0 14px 12px; display: flex; flex-direction: column; gap: 8px; }

  .event-row { display: flex; gap: 8px; align-items: flex-start; }
  
  .event-indicator { padding-top: 4px; }
  
  .tooltip-type-dot {
    width: 8px; height: 8px; border-radius: 50%;
  }

  .event-details { display: flex; flex-direction: column; gap: 2px; }
  
  .event-title {
    font-size: 0.75rem; font-weight: 600; line-height: 1.2; color: #334155;
  }
  
  .event-meta {
    font-size: 0.65rem; color: #64748b; line-height: 1;
  }

  @keyframes tooltipFadeIn {
    0% { opacity: 0; transform: scale(0.92); }
    100% { opacity: 1; transform: scale(1); }
  }
</style>
