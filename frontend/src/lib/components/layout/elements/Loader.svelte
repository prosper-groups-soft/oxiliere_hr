<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import StartSpinner from "./StartSpinner.svelte";

  type LoaderProps = {
    message?: string;
    class?: string;
  };

  let { message = "...", class : className = "" } : LoaderProps = $props();
</script>


<div class={cn(
    "flex h-full flex-col items-center justify-center",
    className,
)}>
  <StartSpinner />
  <div class="py-2 mt-2 text-center">{message}</div>
</div>
