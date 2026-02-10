<script lang="ts">
  import { cn } from "@/utils";
  export let expanded: boolean;
</script>


<img
  class={cn("h-10 object-contain", 
    expanded ? "object-left -ml-[3px] mr-[3px] w-auto" : "w-[30px] object-center"
  )}
  src={expanded ? "/images/logo-15.png" : "/images/logo-1.png"}
  alt="Oxiliere Logo"
/>

