<script lang="ts">
  import type { LeaveStatus } from '../../types/types';
  import { LEAVE_STATUS_LABELS, LEAVE_STATUS_COLORS } from '../../constants/leaves';
  import { cn } from '@/utilities/common/css';

  let { status }: { status: LeaveStatus } = $props();
  const colors = $derived(LEAVE_STATUS_COLORS[status]);
  const label = $derived(LEAVE_STATUS_LABELS[status]);
</script>


<span
  class={cn(
    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
    colors.bg,
    colors.text
  )}
>
  {label}
</span>

