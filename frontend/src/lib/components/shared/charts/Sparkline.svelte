<script lang="ts">
  /**
   * Sparkline.svelte
   * A lightweight SVG-based sparkline component specifically for Svelte 5.
   * Replaces svelte-chartjs to avoid Svelte 4 internal compatibility issues.
   */
  let { 
    data = [], 
    color = "#3b82f6", 
    fillColor = "rgba(59, 130, 246, 0.1)",
    lineWidth = 2
  } = $props<{
    data: number[];
    color?: string;
    fillColor?: string;
    lineWidth?: number;
  }>();

  // Calculate SVG path points
  const points = $derived.by(() => {
    if (data.length === 0) return "";
    
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    const width = 100;
    const height = 40;
    
    return data.map((val: number, i: number) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    }).join(" ");
  });

  const areaPath = $derived(`M 0,40 L ${points} L 100,40 Z`);
  const linePath = $derived(`M ${points}`);
</script>

<svg 
  viewBox="0 0 100 40" 
  preserveAspectRatio="none" 
  class="w-full h-full overflow-visible"
>
  <path 
    d={areaPath} 
    fill={fillColor} 
    stroke="none"
  />
  <path 
    d={linePath} 
    fill="none" 
    stroke={color} 
    stroke-width={lineWidth} 
    stroke-linecap="round" 
    stroke-linejoin="round"
  />
</svg>

