<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import type { Currency } from "../../types/types";
  import { CURRENCY_COLORS } from "../../constants";

  let { 
    currency, 
    class: className = "" 
  }: { 
    currency: Currency; 
    class?: string 
  } = $props();
</script>

<div class={cn(
  "inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[0.65rem] font-bold border",
  CURRENCY_COLORS[currency],
  className
)}>
  {currency}
</div>
