<script lang="ts">
  import { ACTION_LABELS, ACTION_COLORS } from '../../types/types';
  import type { AuditAction } from '../../types/types';
  import { cn } from '@/hr/utilities/common/css';

  let { action }: { action: AuditAction } = $props();
  const colors = $derived(ACTION_COLORS[action]);
  const label  = $derived(ACTION_LABELS[action]);
</script>


<span class={cn(
  "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[0.72rem] font-medium whitespace-nowrap",
  colors.bg, colors.text
)}>
  <span class={cn("h-1.5 w-1.5 rounded-full shrink-0", colors.dot)}></span>
  {label}
</span>

