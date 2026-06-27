<script lang="ts">
  import { STATUS_LABELS, RECURRENCE_LABELS } from "../../constants/event.constants";
  import { EVENT_TYPE_COLORS, EVENT_TYPE_LABELS } from "../../types/types";
  import type { CalendarEvent } from "../../types/types";

  
  let {
    event,
    placement = "top",
    children,
  }: {
    event: CalendarEvent;
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

  const typeColor = $derived(EVENT_TYPE_COLORS[event.type] || EVENT_TYPE_COLORS.holiday);

  const details = $derived.by(() => {
    const items: { label: string; value: string }[] = [];
    items.push({ label: "Statut", value: STATUS_LABELS[event.status || "APPROVED"] || event.status || "Inconnu" });

    const fmt = (d: string) => new Date(d + 'T00:00:00').toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'long', year: 'numeric'
    });
    let dateStr = fmt(event.defaultDate);
    if (event.endDate && event.endDate !== event.defaultDate) {
      dateStr += " → " + fmt(event.endDate);
    }
    items.push({ label: "Date", value: dateStr });
    if (event.startTime) {
      let timeStr = event.startTime.slice(0, 5);
      if (event.endTime) timeStr += " → " + event.endTime.slice(0, 5);
      items.push({ label: "Horaire", value: timeStr });
    }
    if (event.description) {
      items.push({ label: "Description", value: event.description });
    }
    if (event.recurrent && event.recurrent !== "NONE") {
      items.push({ label: "Récurrence", value: RECURRENCE_LABELS[event.recurrent] || event.recurrent });
    }
    if (event.isWorkable === false) {
      items.push({ label: "", value: "🚫 Jour non travaillé" });
    }
    return items;
  });

  function show() {
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

    // Correction horizontale : éviter le débordement à gauche/droite
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

    // Position fixed : on calcule top/left absolus
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
  class="tooltip-wrapper"
  role="none"
  onmouseenter={show}
  onmouseleave={scheduleHide}
>
  <div class="trigger-inner">
    {@render children()}
  </div>

  {#if isVisible}
    <div
      bind:this={tooltipEl}
      class="tooltip-content {resolvedPlacement === 'bottom' ? 'placement-bottom' : 'placement-top'}"
      role="tooltip"
      onmouseenter={show}
      onmouseleave={scheduleHide}
    >
      <div class="tooltip-arrow"></div>
      <div class="tooltip-header">
        <div class="tooltip-title-row">
          <div class="tooltip-type-dot {typeColor.dot} w-2.5! h-2.5!">
          </div>
          <span class="tooltip-title text-sm">{event.title}</span>
        </div>
      </div>
      <div class="tooltip-divider"></div>
      <div class="tooltip-body">
        {#each details as detail}
          <div class="tooltip-row">
            {#if detail.label}
              <span class="tooltip-label text-sm">{detail.label}</span>
              <span class="tooltip-value text-sm">{detail.value}</span>
            {:else}
              <span class="tooltip-value-full text-sm">{detail.value}</span>
            {/if}
          </div>
        {/each}
      </div>
      <div class="tooltip-footer">
        <span
          class="tooltip-status-badge text-sm"
          class:status-pending={event.status === "PENDING"}
          class:status-approved={event.status === "APPROVED"}
          class:status-rejected={event.status === "REJECTED"}
          class:status-cancelled={event.status === "CANCELLED" || event.status === "TAKEN"}
        >
          {STATUS_LABELS[event.status || "APPROVED"] || event.status}
        </span>
        <span class="tooltip-type-label text-sm">{EVENT_TYPE_LABELS[event.type] || event.type}</span>
      </div>
    </div>
  {/if}
</div>


<style>
  .tooltip-wrapper { position: relative; display: inline-block; }
  .trigger-inner { display: inline; }

  .tooltip-content {
    position: fixed; z-index: 9999; min-width: 220px; max-width: 320px; padding: 0;
    border-radius: 14px; font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    pointer-events: auto; animation: tooltipFadeIn 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.9);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.08),
      0 2px 8px rgba(0, 0, 0, 0.04),
      inset 0 1px 0 rgba(255, 255, 255, 0.8);
    color: #1e293b;
  }

  .tooltip-content .tooltip-label { color: #94a3b8; }
  .tooltip-content .tooltip-value { color: #475569; }
  .tooltip-content .tooltip-title { color: #0f172a; }
  .tooltip-content .tooltip-divider { height: 1px; margin: 10px 16px; background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.25), transparent); }

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

  .tooltip-header { padding: 14px 16px 0; }
  .tooltip-title-row { display: flex; align-items: center; gap: 10px; }

  .tooltip-type-dot {
    flex-shrink: 0; width: 10px; height: 10px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
  }

  .tooltip-title {
    font-size: 0.85rem; font-weight: 600; line-height: 1.3; letter-spacing: -0.01em;
  }

  .tooltip-body { padding: 0 16px 8px; display: flex; flex-direction: column; gap: 4px; }

  .tooltip-row {
    display: grid; grid-template-columns: 90px 1fr; gap: 12px;
    font-size: 0.75rem; line-height: 1.5;
  }
  .tooltip-label {
    font-weight: 600; font-size: 0.75rem;
    text-transform: uppercase; letter-spacing: 0.05em;
  }
  .tooltip-value { font-weight: 400; word-break: break-word; }
  .tooltip-value-full { font-weight: 400; word-break: keep-all; grid-column: 1 / -1; }

  .tooltip-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 16px 14px; gap: 8px;
  }
  .tooltip-status-badge {
    font-size: 0.62rem; font-weight: 700; padding: 3px 10px; border-radius: 6px;
    letter-spacing: 0.03em; text-transform: uppercase;
  }

  .tooltip-status-badge.status-pending { background: #fef3c7; color: #d97706; }
  .tooltip-status-badge.status-approved { background: #d1fae5; color: #059669; }
  .tooltip-status-badge.status-rejected { background: #fee2e2; color: #dc2626; }
  .tooltip-status-badge.status-cancelled { background: #f1f5f9; color: #64748b; }

  .tooltip-type-label {
    font-size: 0.78rem; font-weight: 400; text-transform: capitalize;
    color: #9198a0; letter-spacing: 0.03em;
  }

  @keyframes tooltipFadeIn {
    0% { opacity: 0; transform: scale(0.92); }
    100% { opacity: 1; transform: scale(1); }
  }

</style>

