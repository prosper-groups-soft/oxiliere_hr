<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import type { Currency } from "../../types/types";
  import { CURRENCY_COLORS } from "../../types/types";

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
  currency === 'USD' ? "bg-blue-50 border-blue-100 text-blue-700" :
  currency === 'CDF' ? "bg-emerald-50 border-emerald-100 text-emerald-700" :
  "bg-amber-50 border-amber-100 text-amber-700",
  className
)}>
  {currency}
</div>
