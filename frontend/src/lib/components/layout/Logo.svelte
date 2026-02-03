<script lang="ts">
    import { cn } from "$lib/utils";
    export let expanded: boolean;

</script>


<img
    class={cn("h-8 object-contain object-left -ml-[3px] mr-[3px]", {
    "w-[32px]": !expanded,
    "hidden": expanded,
    })}
    src="/images/logo-5.png"
    alt="Oxiliere Logo"
/>

<img
    class={cn("h-8 object-contain object-left -ml-[3px] mr-[3px]", {
    "w-[32px]": !expanded,
    "hidden": !expanded,
    })}
    src="/images/logo-5.png"
    alt="Oxiliere Logo"
/>
