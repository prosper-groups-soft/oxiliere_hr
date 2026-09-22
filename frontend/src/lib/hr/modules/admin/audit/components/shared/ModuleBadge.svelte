<script lang="ts">
  import { MODULE_LABELS, MODULE_COLORS } from '../../types/types';
  import type { AuditModule } from '../../types/types';
  import { cn } from '@/hr/utilities/common/css';

  let { module: mod }: { module: AuditModule } = $props();
  const colors = $derived(MODULE_COLORS[mod]);
  const label  = $derived(MODULE_LABELS[mod]);
</script>


<span class={cn(
  "inline-flex items-center px-2 py-0.5 rounded-full text-[0.7rem] font-medium whitespace-nowrap",
  colors.bg, colors.text
)}>
  {label}
</span>

