<script lang="ts">
  let { 
    startX, 
    startY, 
    endX, 
    endY 
  } = $props<{
    startX: number,
    startY: number,
    endX: number,
    endY: number
  }>();

  // Draw an orthogonal path with rounded corners
  const path = $derived(() => {
    const r = 12; // corner radius
    const midY = startY + (endY - startY) / 2;
    
    // Directional signs
    const dx = endX > startX ? 1 : -1;
    const dy = endY > startY ? 1 : -1;

    // If start and end are too close, just draw a straight line
    if (Math.abs(endX - startX) < r * 2 || Math.abs(endY - startY) < r * 2) {
      return `M ${startX} ${startY} L ${startX} ${midY} L ${endX} ${midY} L ${endX} ${endY}`;
    }

    return `
      M ${startX} ${startY} 
      L ${startX} ${midY - r * dy}
      Q ${startX} ${midY} ${startX + r * dx} ${midY}
      L ${endX - r * dx} ${midY}
      Q ${endX} ${midY} ${endX} ${midY + r * dy}
      L ${endX} ${endY}
    `.replace(/\s+/g, ' ').trim();
  });
</script>


<path 
  d={path()} 
  fill="none" 
  stroke="currentColor" 
  stroke-width="1.5" 
  class="text-slate-300 transition-all duration-300"
/>

